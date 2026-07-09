import Foundation

/// Encodes an RSA-2048 public key in the ADB/mincrypt binary format and the
/// base64 payload adbd expects in an AUTH(RSAPUBLICKEY) message.
///
/// Binary layout (all little-endian UInt32):
///   len (words = 64) | n0inv (-1/n[0] mod 2^32) | n[64] | rr[64] (R^2 mod n) | exponent
/// where R = 2^2048, so rr = 2^4096 mod n.
public enum ADBPublicKey {

    public static let modulusBits = 2048
    public static let words = modulusBits / 32 // 64
    public static let encodedSize = 4 + 4 + words * 4 + words * 4 + 4 // 524 bytes

    public enum EncodeError: Error, Equatable {
        case unsupportedModulusSize(Int)
        case evenModulus
    }

    /// - Parameters:
    ///   - modulus: big-endian modulus bytes with any leading zero stripped
    ///              (must be exactly 256 bytes / 2048 bits).
    ///   - exponent: public exponent (normally 65537).
    public static func encode(modulus: Data, exponent: UInt32) throws -> Data {
        guard modulus.count == words * 4 else {
            throw EncodeError.unsupportedModulusSize(modulus.count)
        }
        let bytes = [UInt8](modulus)
        // Convert big-endian bytes to little-endian 32-bit words.
        var n = [UInt32](repeating: 0, count: words)
        for i in 0..<words {
            let base = bytes.count - 4 * (i + 1)
            n[i] = UInt32(bytes[base]) << 24
                | UInt32(bytes[base + 1]) << 16
                | UInt32(bytes[base + 2]) << 8
                | UInt32(bytes[base + 3])
        }
        guard n[0] & 1 == 1 else { throw EncodeError.evenModulus }

        let n0inv = BigUInt32.negativeInverseMod2Pow32(n[0])
        let rr = BigUInt32.powerOfTwoMod(n, exponentBits: modulusBits * 2)

        var out = Data(capacity: encodedSize)
        out.appendLEUInt32(UInt32(words))
        out.appendLEUInt32(n0inv)
        for word in n { out.appendLEUInt32(word) }
        for word in rr { out.appendLEUInt32(word) }
        out.appendLEUInt32(exponent)
        return out
    }

    /// Full AUTH(RSAPUBLICKEY) payload: base64(mincrypt key) + " name" + NUL.
    public static func authPayload(modulus: Data, exponent: UInt32, name: String = "mxqremote@iphone") throws -> Data {
        let raw = try encode(modulus: modulus, exponent: exponent)
        var payload = Data((raw.base64EncodedString() + " " + name).utf8)
        payload.append(0)
        return payload
    }
}
