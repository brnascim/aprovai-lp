import Foundation

public enum ADBConnectionState: Equatable, Sendable {
    case idle
    case connecting
    case authenticating
    /// Public key sent; the box is showing the "Allow USB debugging?" dialog.
    case awaitingAuthorization
    case connected(device: String)
    case disconnected(reason: String?)
}

/// ADB protocol engine: performs the CNXN/AUTH handshake, then multiplexes
/// streams (OPEN/OKAY/WRTE/CLSE) over a single TCP transport.
///
/// Latency strategy: one persistent `shell:` stream stays open and every
/// remote-control action is a single WRTE of `<command>\n` — no per-keypress
/// stream setup. One-shot streams are used for commands whose output we need
/// (e.g. `wm size`).
///
/// A connection is single-use: create a new instance for every attempt.
public actor ADBConnection {

    // MARK: Wire constants
    private static let protocolVersion: UInt32 = 0x0100_0000
    private static let maxDataAdvertised: UInt32 = 256 * 1024
    private static let hostBanner = "host::features=cmd,shell_v2"

    private final class StreamBox {
        let localID: UInt32
        let collectsOutput: Bool
        var remoteID: UInt32?
        var isClosed = false
        var closedByUs = false
        /// WRTE acks processed by the reader before the writer suspended
        /// (actor reentrancy makes this ordering possible).
        var unclaimedWriteAcks = 0
        var output = Data()
        var openContinuation: CheckedContinuation<Void, Error>?
        var writeContinuation: CheckedContinuation<Void, Error>?
        var closeContinuation: CheckedContinuation<Data, Error>?

        init(localID: UInt32, collectsOutput: Bool) {
            self.localID = localID
            self.collectsOutput = collectsOutput
        }
    }

    private let transport: ADBTransport
    private let signer: ADBSigner
    private let onStateChange: @Sendable (ADBConnectionState) -> Void

    private(set) public var state: ADBConnectionState = .idle
    public private(set) var deviceMaxPayload: Int = 4096
    public private(set) var deviceBanner: String = ""

    private var readerTask: Task<Void, Never>?
    private var watchdogTask: Task<Void, Never>?
    private var connectedContinuation: CheckedContinuation<Void, Error>?
    private var didDisconnect = false
    private var triedSignatureThisCycle = false

    private var nextLocalID: UInt32 = 1
    private var streams: [UInt32: StreamBox] = [:]
    private var shellStream: StreamBox?
    private var shellQueue: [String] = []
    private var shellPumpRunning = false

    public init(
        transport: ADBTransport,
        signer: ADBSigner,
        onStateChange: @escaping @Sendable (ADBConnectionState) -> Void
    ) {
        self.transport = transport
        self.signer = signer
        self.onStateChange = onStateChange
    }

    // MARK: - Lifecycle

    /// Connects, authenticates and opens the persistent shell.
    ///
    /// `handshakeTimeout` applies to the TCP + CNXN/AUTH phases only; while
    /// the box shows the authorization dialog (`awaitingAuthorization`) the
    /// call waits indefinitely — cancel with `close()`.
    public func connect(handshakeTimeout: Double = 12) async throws {
        guard case .idle = state else { throw ADBError.notConnected }
        setState(.connecting)
        do {
            try await transport.connect()
            var payload = Data(Self.hostBanner.utf8)
            payload.append(0)
            try await sendMessage(ADBMessage(
                command: .cnxn,
                arg0: Self.protocolVersion,
                arg1: Self.maxDataAdvertised,
                payload: payload
            ))
        } catch {
            fail(reason: Self.describe(error))
            throw error
        }
        setState(.authenticating)

        readerTask = Task { await self.readLoop() }
        watchdogTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64(handshakeTimeout * 1_000_000_000))
            await self?.handshakeTimedOut()
        }

        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            connectedContinuation = continuation
        }
        watchdogTask?.cancel()
        watchdogTask = nil

        _ = try await openShellIfNeeded()
    }

    /// User-initiated teardown.
    public func close() {
        fail(reason: nil)
    }

    private func handshakeTimedOut() {
        switch state {
        case .connecting, .authenticating:
            fail(reason: "timeout")
        default:
            break // connected, or waiting on the authorization dialog
        }
    }

    // MARK: - Public commands

    /// Queues a fire-and-forget shell command on the persistent shell stream.
    /// Errors surface through the state callback (disconnection), keeping
    /// button taps latency-free.
    public func execShell(_ command: String) {
        guard case .connected = state else { return }
        shellQueue.append(command)
        pumpShellQueue()
    }

    /// Runs a command on its own `shell:<command>` stream and returns its
    /// output (used for `wm size` and similar).
    public func runCommand(_ command: String, timeout: Double = 5) async throws -> String {
        guard case .connected = state else { throw ADBError.notConnected }
        let box = try await openStream(destination: "shell:\(command)", collectsOutput: true)
        let localID = box.localID
        let watchdog = Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64(timeout * 1_000_000_000))
            await self?.abortStream(localID)
        }
        defer { watchdog.cancel() }
        if box.isClosed {
            return String(decoding: box.output, as: UTF8.self)
        }
        let output = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Data, Error>) in
            box.closeContinuation = continuation
        }
        return String(decoding: output, as: UTF8.self)
    }

    // MARK: - Shell queue

    private func pumpShellQueue() {
        guard !shellPumpRunning else { return }
        shellPumpRunning = true
        Task { await self.drainShellQueue() }
    }

    private func drainShellQueue() async {
        while !shellQueue.isEmpty, !didDisconnect {
            let command = shellQueue.removeFirst()
            do {
                let shell = try await openShellIfNeeded()
                var data = Data(command.utf8)
                data.append(0x0A) // "\n"
                try await write(data, to: shell)
            } catch {
                // Persistent shell died; drop it so the next command reopens
                // it (full disconnects are reported via the reader loop).
                shellStream = nil
            }
        }
        shellPumpRunning = false
    }

    private func openShellIfNeeded() async throws -> StreamBox {
        if let shell = shellStream, !shell.isClosed {
            return shell
        }
        let shell = try await openStream(destination: "shell:", collectsOutput: false)
        shellStream = shell
        return shell
    }

    // MARK: - Streams

    private func openStream(destination: String, collectsOutput: Bool) async throws -> StreamBox {
        let id = nextLocalID
        nextLocalID &+= 1
        let box = StreamBox(localID: id, collectsOutput: collectsOutput)
        streams[id] = box
        var payload = Data(destination.utf8)
        payload.append(0)
        try await sendMessage(ADBMessage(command: .open, arg0: id, payload: payload))
        // The reader may have already processed the device's OKAY (or CLSE)
        // while `sendMessage` was suspended — check before parking.
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            if box.isClosed {
                continuation.resume(throwing: ADBError.streamRefused(destination))
            } else if box.remoteID != nil {
                continuation.resume()
            } else {
                box.openContinuation = continuation
            }
        }
        return box
    }

    private func write(_ data: Data, to box: StreamBox) async throws {
        guard let remoteID = box.remoteID, !box.isClosed else { throw ADBError.connectionClosed }
        try await sendMessage(ADBMessage(command: .wrte, arg0: box.localID, arg1: remoteID, payload: data))
        // Same reentrancy caveat as `openStream`: the OKAY for this WRTE can
        // land before we suspend, in which case it was banked in
        // `unclaimedWriteAcks`.
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            if box.isClosed {
                continuation.resume(throwing: ADBError.connectionClosed)
            } else if box.unclaimedWriteAcks > 0 {
                box.unclaimedWriteAcks -= 1
                continuation.resume()
            } else {
                box.writeContinuation = continuation
            }
        }
    }

    private func abortStream(_ localID: UInt32) async {
        guard let box = streams[localID], !box.isClosed else { return }
        box.closedByUs = true
        if let remoteID = box.remoteID {
            try? await sendMessage(ADBMessage(command: .clse, arg0: localID, arg1: remoteID))
        }
        closeBox(box, error: ADBError.timeout)
        streams.removeValue(forKey: localID)
    }

    // MARK: - Reader

    private func readLoop() async {
        let reader = ADBMessageReader()
        do {
            while !Task.isCancelled {
                let chunk = try await transport.receive()
                for message in try reader.append(chunk) {
                    try await handle(message)
                }
            }
        } catch {
            if !didDisconnect {
                fail(reason: Self.describe(error))
            }
        }
    }

    private func handle(_ message: ADBMessage) async throws {
        switch message.command {
        case .cnxn:
            deviceBanner = message.payloadString
            if message.arg1 > 0 {
                deviceMaxPayload = Int(message.arg1)
            }
            setState(.connected(device: Self.deviceName(fromBanner: deviceBanner)))
            connectedContinuation?.resume()
            connectedContinuation = nil

        case .auth:
            guard message.arg0 == ADBAuthType.token.rawValue else { return }
            if !triedSignatureThisCycle {
                // First try the stored key: if the box already trusts it,
                // this succeeds silently (auto-reconnect path).
                triedSignatureThisCycle = true
                let signature = try signer.sign(token: message.payload)
                try await sendMessage(ADBMessage(
                    command: .auth, arg0: ADBAuthType.signature.rawValue, payload: signature
                ))
            } else {
                // Signature rejected: present the public key. The box now
                // shows the authorization dialog; when the user accepts it
                // sends a fresh token and the signature path succeeds.
                triedSignatureThisCycle = false
                let publicKey = try signer.publicKeyAuthPayload()
                try await sendMessage(ADBMessage(
                    command: .auth, arg0: ADBAuthType.rsaPublicKey.rawValue, payload: publicKey
                ))
                setState(.awaitingAuthorization)
            }

        case .okay:
            guard let box = streams[message.arg1] else { return }
            if box.remoteID == nil {
                // Ack for our OPEN.
                box.remoteID = message.arg0
                if let open = box.openContinuation {
                    box.openContinuation = nil
                    open.resume()
                }
            } else if let write = box.writeContinuation {
                box.writeContinuation = nil
                write.resume()
            } else {
                box.unclaimedWriteAcks += 1
            }

        case .wrte:
            guard let box = streams[message.arg1] else { return }
            if box.collectsOutput {
                box.output.append(message.payload)
            }
            if let remoteID = box.remoteID {
                try await sendMessage(ADBMessage(command: .okay, arg0: box.localID, arg1: remoteID))
            }

        case .clse:
            guard let box = streams[message.arg1] else { return }
            streams.removeValue(forKey: message.arg1)
            if box === shellStream { shellStream = nil }
            let remoteID = box.remoteID ?? (message.arg0 != 0 ? message.arg0 : nil)
            closeBox(box, error: ADBError.streamRefused("stream closed by device"))
            if !box.closedByUs, let remoteID {
                try? await sendMessage(ADBMessage(command: .clse, arg0: box.localID, arg1: remoteID))
            }

        case .stls:
            fail(reason: "tls-required")

        case .open, .sync:
            break // device-initiated streams are not expected here
        }
    }

    /// Resolves every continuation on the box: pending open/write fail with
    /// `error`, a pending close-wait succeeds with the collected output.
    private func closeBox(_ box: StreamBox, error: ADBError) {
        box.isClosed = true
        if let open = box.openContinuation {
            box.openContinuation = nil
            open.resume(throwing: error)
        }
        if let write = box.writeContinuation {
            box.writeContinuation = nil
            write.resume(throwing: error)
        }
        if let close = box.closeContinuation {
            box.closeContinuation = nil
            close.resume(returning: box.output)
        }
    }

    // MARK: - Teardown

    private func fail(reason: String?) {
        guard !didDisconnect else { return }
        didDisconnect = true
        transport.cancel()
        readerTask?.cancel()
        watchdogTask?.cancel()
        for box in streams.values {
            box.closedByUs = true
            closeBox(box, error: .connectionClosed)
        }
        streams.removeAll()
        shellStream = nil
        shellQueue.removeAll()
        if let continuation = connectedContinuation {
            connectedContinuation = nil
            continuation.resume(throwing: reason == "timeout" ? ADBError.timeout : ADBError.connectionClosed)
        }
        setState(.disconnected(reason: reason))
    }

    // MARK: - Helpers

    private func sendMessage(_ message: ADBMessage) async throws {
        try await transport.send(message.encoded())
    }

    private func setState(_ newState: ADBConnectionState) {
        state = newState
        onStateChange(newState)
    }

    /// Extracts something readable from a device banner like
    /// "device::ro.product.name=MXQ;ro.product.model=MXQ-4K;...".
    static func deviceName(fromBanner banner: String) -> String {
        let properties = banner.split(separator: ":").last.map(String.init) ?? banner
        for pair in properties.split(separator: ";") {
            let parts = pair.split(separator: "=", maxSplits: 1)
            if parts.count == 2, parts[0] == "ro.product.model" {
                return String(parts[1])
            }
        }
        return banner.split(separator: ":").first.map(String.init) ?? "device"
    }

    private static func describe(_ error: Error) -> String {
        if let adbError = error as? ADBError {
            switch adbError {
            case .timeout: return "timeout"
            case .connectionClosed: return "closed"
            case .transport(let detail): return detail
            default: return String(describing: adbError)
            }
        }
        return error.localizedDescription
    }
}
