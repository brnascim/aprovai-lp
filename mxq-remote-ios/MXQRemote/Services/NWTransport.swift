import Foundation
import Network
import ADBCore

/// `ADBTransport` backed by Network.framework (raw TCP to <box>:5555).
final class NWTransport: ADBTransport, @unchecked Sendable {

    /// Guards one-shot continuation resumption across NW callbacks.
    private final class ResumeOnce {
        private let lock = NSLock()
        private var done = false
        /// Returns true only for the first caller.
        func claim() -> Bool {
            lock.lock()
            defer { lock.unlock() }
            if done { return false }
            done = true
            return true
        }
    }

    private let connection: NWConnection
    private let queue = DispatchQueue(label: "com.mxqremote.adb-transport")
    private let connectTimeout: TimeInterval

    init(host: String, port: UInt16 = 5555, connectTimeout: TimeInterval = 8) {
        let tcpOptions = NWProtocolTCP.Options()
        tcpOptions.noDelay = true // latency matters more than throughput here
        tcpOptions.connectionTimeout = Int(connectTimeout)
        let parameters = NWParameters(tls: nil, tcp: tcpOptions)
        self.connection = NWConnection(
            host: NWEndpoint.Host(host),
            port: NWEndpoint.Port(rawValue: port) ?? 5555,
            using: parameters
        )
        self.connectTimeout = connectTimeout
    }

    func connect() async throws {
        let connection = self.connection
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            let once = ResumeOnce()
            connection.stateUpdateHandler = { state in
                switch state {
                case .ready:
                    connection.stateUpdateHandler = nil
                    if once.claim() { continuation.resume() }
                case .failed(let error):
                    connection.cancel()
                    if once.claim() { continuation.resume(throwing: ADBError.transport(error.localizedDescription)) }
                case .cancelled:
                    if once.claim() { continuation.resume(throwing: ADBError.connectionClosed) }
                default:
                    break // .waiting retries until the timeout below fires
                }
            }
            connection.start(queue: queue)
            // NWConnection can sit in .waiting forever (host down / no route);
            // enforce our own deadline.
            queue.asyncAfter(deadline: .now() + connectTimeout + 2) {
                if once.claim() {
                    connection.cancel()
                    continuation.resume(throwing: ADBError.timeout)
                }
            }
        }
    }

    func send(_ data: Data) async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            connection.send(content: data, completion: .contentProcessed { error in
                if let error {
                    continuation.resume(throwing: ADBError.transport(error.localizedDescription))
                } else {
                    continuation.resume()
                }
            })
        }
    }

    func receive() async throws -> Data {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Data, Error>) in
            connection.receive(minimumIncompleteLength: 1, maximumLength: 128 * 1024) { data, _, isComplete, error in
                if let data, !data.isEmpty {
                    continuation.resume(returning: data)
                } else if let error {
                    continuation.resume(throwing: ADBError.transport(error.localizedDescription))
                } else {
                    // EOF (isComplete) or empty read on a dead connection.
                    _ = isComplete
                    continuation.resume(throwing: ADBError.connectionClosed)
                }
            }
        }
    }

    func cancel() {
        connection.cancel()
    }
}
