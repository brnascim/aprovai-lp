import XCTest
@testable import ADBCore

/// Scripted in-memory transport playing the role of the box's adbd.
final class FakeTransport: ADBTransport, @unchecked Sendable {
    private let lock = NSLock()
    private let sentReader = ADBMessageReader()
    private var sent: [ADBMessage] = []
    private var pendingIncoming: [Data] = []
    private var receiveContinuation: CheckedContinuation<Data, Error>?
    private var cancelled = false

    func connect() async throws {}

    func send(_ data: Data) async throws {
        lock.lock()
        defer { lock.unlock() }
        if cancelled { throw ADBError.connectionClosed }
        sent.append(contentsOf: (try? sentReader.append(data)) ?? [])
    }

    func receive() async throws -> Data {
        return try await withCheckedThrowingContinuation { continuation in
            lock.lock()
            if cancelled {
                lock.unlock()
                continuation.resume(throwing: ADBError.connectionClosed)
            } else if !pendingIncoming.isEmpty {
                let data = pendingIncoming.removeFirst()
                lock.unlock()
                continuation.resume(returning: data)
            } else {
                receiveContinuation = continuation
                lock.unlock()
            }
        }
    }

    func cancel() {
        lock.lock()
        cancelled = true
        let continuation = receiveContinuation
        receiveContinuation = nil
        lock.unlock()
        continuation?.resume(throwing: ADBError.connectionClosed)
    }

    // MARK: Test driver API

    func inject(_ message: ADBMessage) {
        lock.lock()
        if let continuation = receiveContinuation {
            receiveContinuation = nil
            lock.unlock()
            continuation.resume(returning: message.encoded())
        } else {
            pendingIncoming.append(message.encoded())
            lock.unlock()
        }
    }

    func sentMessages() -> [ADBMessage] {
        lock.lock()
        defer { lock.unlock() }
        return sent
    }

    /// Polls until at least `count` messages were sent by the client.
    func waitForSent(_ count: Int, timeout: Double = 2) async throws -> [ADBMessage] {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            let snapshot = sentMessages()
            if snapshot.count >= count { return snapshot }
            try await Task.sleep(nanoseconds: 10_000_000)
        }
        throw ADBError.timeout
    }
}

struct FakeSigner: ADBSigner {
    static let signature = Data(repeating: 0x5A, count: 256)
    static let publicKeyPayload = Data("FAKEKEY mxqremote@iphone\0".utf8)

    func sign(token: Data) throws -> Data { Self.signature }
    func publicKeyAuthPayload() throws -> Data { Self.publicKeyPayload }
}

final class StateRecorder: @unchecked Sendable {
    private let lock = NSLock()
    private var states: [ADBConnectionState] = []

    func record(_ state: ADBConnectionState) {
        lock.lock()
        states.append(state)
        lock.unlock()
    }

    func all() -> [ADBConnectionState] {
        lock.lock()
        defer { lock.unlock() }
        return states
    }
}

final class ADBConnectionTests: XCTestCase {

    private func makeToken() -> ADBMessage {
        ADBMessage(command: .auth, arg0: ADBAuthType.token.rawValue, payload: Data(repeating: 0x07, count: 20))
    }

    private func makeDeviceCNXN() -> ADBMessage {
        var banner = Data("device::ro.product.name=mxq;ro.product.model=MXQ-4K;".utf8)
        banner.append(0)
        return ADBMessage(command: .cnxn, arg0: 0x0100_0000, arg1: 0x0004_0000, payload: banner)
    }

    /// Full first-connection flow: signature rejected → public key sent
    /// (authorization dialog) → user accepts → new token → signature accepted
    /// → CNXN → persistent shell opened → keyevent written.
    func testFirstConnectionHandshakeAndShellCommand() async throws {
        let transport = FakeTransport()
        let recorder = StateRecorder()
        let connection = ADBConnection(transport: transport, signer: FakeSigner()) { recorder.record($0) }

        let connectTask = Task { try await connection.connect() }

        // 1. Client greets with CNXN.
        var sent = try await transport.waitForSent(1)
        XCTAssertEqual(sent[0].command, .cnxn)
        XCTAssertEqual(sent[0].arg0, 0x0100_0000)
        XCTAssertTrue(sent[0].payloadString.hasPrefix("host::"))

        // 2. Device challenges; client answers with a signature.
        transport.inject(makeToken())
        sent = try await transport.waitForSent(2)
        XCTAssertEqual(sent[1].command, .auth)
        XCTAssertEqual(sent[1].arg0, ADBAuthType.signature.rawValue)
        XCTAssertEqual(sent[1].payload, FakeSigner.signature)

        // 3. Signature unknown — device re-challenges; client sends its
        //    public key and reports "awaiting authorization".
        transport.inject(makeToken())
        sent = try await transport.waitForSent(3)
        XCTAssertEqual(sent[2].command, .auth)
        XCTAssertEqual(sent[2].arg0, ADBAuthType.rsaPublicKey.rawValue)
        XCTAssertEqual(sent[2].payload, FakeSigner.publicKeyPayload)

        // 4. User accepted on the box: fresh token, signature now accepted.
        transport.inject(makeToken())
        sent = try await transport.waitForSent(4)
        XCTAssertEqual(sent[3].command, .auth)
        XCTAssertEqual(sent[3].arg0, ADBAuthType.signature.rawValue)

        // 5. Device confirms the session and the client opens `shell:`.
        transport.inject(makeDeviceCNXN())
        sent = try await transport.waitForSent(5)
        XCTAssertEqual(sent[4].command, .open)
        XCTAssertEqual(sent[4].payloadString, "shell:")
        let shellLocalID = sent[4].arg0

        transport.inject(ADBMessage(command: .okay, arg0: 99, arg1: shellLocalID))
        try await connectTask.value

        // 6. A remote key press becomes one WRTE on the persistent shell.
        await connection.execShell(RemoteCommand.keyEvent(.dpadCenter))
        sent = try await transport.waitForSent(6)
        XCTAssertEqual(sent[5].command, .wrte)
        XCTAssertEqual(sent[5].arg0, shellLocalID)
        XCTAssertEqual(sent[5].arg1, 99)
        XCTAssertEqual(String(decoding: sent[5].payload, as: UTF8.self), "input keyevent 23\n")

        let states = recorder.all()
        XCTAssertTrue(states.contains(.connecting))
        XCTAssertTrue(states.contains(.authenticating))
        XCTAssertTrue(states.contains(.awaitingAuthorization))
        XCTAssertTrue(states.contains(.connected(device: "MXQ-4K")))

        await connection.close()
    }

    /// One-shot command stream: OPEN → OKAY → WRTE(output) → CLSE returns
    /// the collected output.
    func testRunCommandCollectsOutput() async throws {
        let transport = FakeTransport()
        let connection = ADBConnection(transport: transport, signer: FakeSigner()) { _ in }

        let connectTask = Task { try await connection.connect() }
        _ = try await transport.waitForSent(1)
        transport.inject(makeDeviceCNXN()) // no-auth device
        var sent = try await transport.waitForSent(2) // shell: OPEN
        transport.inject(ADBMessage(command: .okay, arg0: 50, arg1: sent[1].arg0))
        try await connectTask.value

        let outputTask = Task { try await connection.runCommand(RemoteCommand.wmSize) }
        sent = try await transport.waitForSent(3)
        XCTAssertEqual(sent[2].command, .open)
        XCTAssertEqual(sent[2].payloadString, "shell:wm size")
        let localID = sent[2].arg0

        transport.inject(ADBMessage(command: .okay, arg0: 60, arg1: localID))
        transport.inject(ADBMessage(
            command: .wrte, arg0: 60, arg1: localID, payload: Data("Physical size: 1280x720\n".utf8)
        ))
        // Client must ACK the WRTE.
        sent = try await transport.waitForSent(4)
        XCTAssertEqual(sent[3].command, .okay)
        XCTAssertEqual(sent[3].arg0, localID)
        XCTAssertEqual(sent[3].arg1, 60)

        transport.inject(ADBMessage(command: .clse, arg0: 60, arg1: localID))
        let output = try await outputTask.value
        XCTAssertEqual(RemoteCommand.parseWmSize(output)?.width, 1280)

        await connection.close()
    }

    func testTransportDropReportsDisconnected() async throws {
        let transport = FakeTransport()
        let recorder = StateRecorder()
        let connection = ADBConnection(transport: transport, signer: FakeSigner()) { recorder.record($0) }

        let connectTask = Task { try await connection.connect() }
        _ = try await transport.waitForSent(1)
        transport.cancel() // simulate the box vanishing mid-handshake

        do {
            try await connectTask.value
            XCTFail("connect must throw when the transport drops")
        } catch {
            // expected
        }
        let deadline = Date().addingTimeInterval(2)
        while Date() < deadline {
            if recorder.all().contains(where: {
                if case .disconnected = $0 { return true } else { return false }
            }) { break }
            try await Task.sleep(nanoseconds: 10_000_000)
        }
        XCTAssertTrue(recorder.all().contains(where: {
            if case .disconnected = $0 { return true } else { return false }
        }))
    }
}
