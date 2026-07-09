import Foundation
import Security
import CryptoKit
import ADBCore

/// Keychain-backed RSA-2048 identity used to authenticate with adbd.
/// The private key never leaves the Keychain; only ADB-format signatures and
/// the mincrypt-encoded public key are produced from it.
final class KeychainSigner: ADBSigner, @unchecked Sendable {

    static let shared = KeychainSigner()

    private static let keyTag = Data("com.mxqremote.adb.privatekey".utf8)
    private let lock = NSLock()
    private var cachedKey: SecKey?

    enum KeyError: LocalizedError {
        case generation(String)
        case signing(String)
        case export(String)

        var errorDescription: String? {
            switch self {
            case .generation(let detail): return "Key generation failed: \(detail)"
            case .signing(let detail): return "Signing failed: \(detail)"
            case .export(let detail): return "Public key export failed: \(detail)"
            }
        }
    }

    // MARK: ADBSigner

    func sign(token: Data) throws -> Data {
        let key = try privateKey()
        var error: Unmanaged<CFError>?
        // ADB signature = PKCS#1 v1.5 over the raw 20-byte token, treating it
        // as a SHA-1 digest (the DigestInfo prefix is added by Security).
        guard let signature = SecKeyCreateSignature(
            key, .rsaSignatureDigestPKCS1v15SHA1, token as CFData, &error
        ) as Data? else {
            throw KeyError.signing(Self.describe(error))
        }
        return signature
    }

    func publicKeyAuthPayload() throws -> Data {
        let (modulus, exponent) = try publicKeyComponents()
        return try ADBPublicKey.authPayload(modulus: modulus, exponent: exponent)
    }

    // MARK: Key management

    /// Short fingerprint shown in Settings so the user can recognize the key.
    func publicKeyFingerprint() -> String? {
        guard let (modulus, _) = try? publicKeyComponents() else { return nil }
        let digest = SHA256.hash(data: modulus)
        return digest.prefix(8).map { String(format: "%02X", $0) }.joined(separator: ":")
    }

    /// Deletes the stored key; the next connection generates a fresh one and
    /// the box will show the authorization dialog again.
    func regenerateKey() {
        lock.lock()
        defer { lock.unlock() }
        cachedKey = nil
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: Self.keyTag
        ]
        SecItemDelete(query as CFDictionary)
    }

    // MARK: Internals

    private func publicKeyComponents() throws -> (modulus: Data, exponent: UInt32) {
        let key = try privateKey()
        guard let publicKey = SecKeyCopyPublicKey(key) else {
            throw KeyError.export("no public key")
        }
        var error: Unmanaged<CFError>?
        guard let der = SecKeyCopyExternalRepresentation(publicKey, &error) as Data? else {
            throw KeyError.export(Self.describe(error))
        }
        return try DERParser.parseRSAPublicKeyPKCS1(der)
    }

    private func privateKey() throws -> SecKey {
        lock.lock()
        defer { lock.unlock() }
        if let cachedKey { return cachedKey }
        if let existing = Self.loadKey() {
            cachedKey = existing
            return existing
        }
        let created = try Self.createKey()
        cachedKey = created
        return created
    }

    private static func loadKey() -> SecKey? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: keyTag,
            kSecAttrKeyType as String: kSecAttrKeyTypeRSA,
            kSecReturnRef as String: true
        ]
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess else { return nil }
        return (item as! SecKey)
    }

    private static func createKey() throws -> SecKey {
        let attributes: [String: Any] = [
            kSecAttrKeyType as String: kSecAttrKeyTypeRSA,
            kSecAttrKeySizeInBits as String: 2048,
            kSecPrivateKeyAttrs as String: [
                kSecAttrIsPermanent as String: true,
                kSecAttrApplicationTag as String: keyTag
            ]
        ]
        var error: Unmanaged<CFError>?
        guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else {
            throw KeyError.generation(describe(error))
        }
        return key
    }

    private static func describe(_ error: Unmanaged<CFError>?) -> String {
        guard let error = error?.takeRetainedValue() else { return "unknown error" }
        return CFErrorCopyDescription(error) as String? ?? "unknown error"
    }
}
