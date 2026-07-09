import Foundation

/// Byte transport abstraction so the protocol engine stays platform-neutral
/// (the iOS app plugs in an NWConnection-based implementation; tests plug in
/// a scripted fake).
public protocol ADBTransport: AnyObject, Sendable {
    /// Establishes the TCP connection. Throws on failure.
    func connect() async throws
    /// Sends all bytes. Throws if the connection is gone.
    func send(_ data: Data) async throws
    /// Returns the next available chunk (at least 1 byte).
    /// Throws `ADBError.connectionClosed` on EOF or cancellation.
    func receive() async throws -> Data
    /// Tears the connection down. Pending receives must throw.
    func cancel()
}

/// Signs ADB auth tokens and provides the ADB-format public key.
/// The iOS app implements this with a Keychain-backed RSA-2048 key.
public protocol ADBSigner: Sendable {
    /// PKCS#1 v1.5 signature over the 20-byte token, treating the token as a
    /// SHA-1 digest (i.e. the standard ADB RSA signature).
    func sign(token: Data) throws -> Data
    /// AUTH(RSAPUBLICKEY) payload — see `ADBPublicKey.authPayload`.
    func publicKeyAuthPayload() throws -> Data
}

public enum ADBError: Error, Equatable, Sendable {
    case connectionClosed
    case timeout
    case notConnected
    case streamRefused(String)
    case authorizationFailed
    case transport(String)
}
