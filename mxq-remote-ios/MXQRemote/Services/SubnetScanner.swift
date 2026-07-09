import Foundation
import Network

/// Finds Android devices with ADB-over-network enabled by probing every host
/// of the local /24 for an open TCP port 5555.
enum SubnetScanner {

    /// IPv4 address of the Wi-Fi interface (en0), if any.
    static func localIPv4() -> String? {
        var result: String?
        var interfaces: UnsafeMutablePointer<ifaddrs>?
        guard getifaddrs(&interfaces) == 0 else { return nil }
        defer { freeifaddrs(interfaces) }

        var pointer = interfaces
        while let interface = pointer?.pointee {
            defer { pointer = interface.ifa_next }
            guard let addr = interface.ifa_addr, addr.pointee.sa_family == sa_family_t(AF_INET) else { continue }
            let name = String(cString: interface.ifa_name)
            guard name == "en0" || name == "en1" else { continue }
            var host = [CChar](repeating: 0, count: Int(NI_MAXHOST))
            if getnameinfo(addr, socklen_t(addr.pointee.sa_len), &host, socklen_t(host.count),
                           nil, 0, NI_NUMERICHOST) == 0 {
                result = String(cString: host)
                if name == "en0" { break } // prefer en0
            }
        }
        return result
    }

    /// Scans the /24 of the local address. Returns hosts with port 5555 open.
    static func scan(
        port: UInt16 = 5555,
        probeTimeout: TimeInterval = 1.2,
        onProgress: (@Sendable (Double) -> Void)? = nil
    ) async -> [String] {
        guard let localIP = localIPv4() else { return [] }
        let parts = localIP.split(separator: ".")
        guard parts.count == 4 else { return [] }
        let prefix = parts[0...2].joined(separator: ".")
        let hosts = (1...254).map { "\(prefix).\($0)" }.filter { $0 != localIP }

        var found = [String]()
        var completed = 0
        // Bounded concurrency: 24 sockets in flight keeps iOS happy.
        var iterator = hosts.makeIterator()
        await withTaskGroup(of: (String, Bool).self) { group in
            for _ in 0..<24 {
                if let host = iterator.next() {
                    group.addTask { (host, await probe(host: host, port: port, timeout: probeTimeout)) }
                }
            }
            while let (host, isOpen) = await group.next() {
                completed += 1
                onProgress?(Double(completed) / Double(hosts.count))
                if isOpen { found.append(host) }
                if let next = iterator.next() {
                    group.addTask { (next, await probe(host: next, port: port, timeout: probeTimeout)) }
                }
            }
        }
        return found.sorted {
            (Int($0.split(separator: ".").last ?? "") ?? 0) < (Int($1.split(separator: ".").last ?? "") ?? 0)
        }
    }

    /// True when a TCP connection to host:port becomes ready within `timeout`.
    static func probe(host: String, port: UInt16, timeout: TimeInterval) async -> Bool {
        final class Once {
            private let lock = NSLock()
            private var done = false
            func claim() -> Bool {
                lock.lock()
                defer { lock.unlock() }
                if done { return false }
                done = true
                return true
            }
        }
        return await withCheckedContinuation { (continuation: CheckedContinuation<Bool, Never>) in
            let tcpOptions = NWProtocolTCP.Options()
            tcpOptions.connectionTimeout = Int(timeout.rounded(.up))
            let connection = NWConnection(
                host: NWEndpoint.Host(host),
                port: NWEndpoint.Port(rawValue: port) ?? 5555,
                using: NWParameters(tls: nil, tcp: tcpOptions)
            )
            let once = Once()
            let queue = DispatchQueue(label: "com.mxqremote.scan.\(host)")
            connection.stateUpdateHandler = { state in
                switch state {
                case .ready:
                    connection.cancel()
                    if once.claim() { continuation.resume(returning: true) }
                case .failed, .cancelled:
                    if once.claim() { continuation.resume(returning: false) }
                default:
                    break
                }
            }
            connection.start(queue: queue)
            queue.asyncAfter(deadline: .now() + timeout) {
                connection.cancel()
                if once.claim() { continuation.resume(returning: false) }
            }
        }
    }
}
