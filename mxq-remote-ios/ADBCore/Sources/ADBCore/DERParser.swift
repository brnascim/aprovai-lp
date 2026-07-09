import Foundation

/// Just enough DER to parse a PKCS#1 RSAPublicKey:
///   RSAPublicKey ::= SEQUENCE { modulus INTEGER, publicExponent INTEGER }
/// This is the format `SecKeyCopyExternalRepresentation` returns for RSA
/// public keys on Apple platforms.
public enum DERParser {

    public enum DERError: Error, Equatable {
        case truncated
        case unexpectedTag(UInt8)
        case invalidLength
        case exponentTooLarge
    }

    public static func parseRSAPublicKeyPKCS1(_ der: Data) throws -> (modulus: Data, exponent: UInt32) {
        let bytes = [UInt8](der)
        var cursor = 0

        let (seqTag, seqLen) = try readTagLength(bytes, &cursor)
        guard seqTag == 0x30 else { throw DERError.unexpectedTag(seqTag) }
        guard cursor + seqLen <= bytes.count else { throw DERError.truncated }

        let modulus = try readInteger(bytes, &cursor)
        let exponentBytes = try readInteger(bytes, &cursor)

        guard exponentBytes.count <= 4 else { throw DERError.exponentTooLarge }
        var exponent: UInt32 = 0
        for byte in exponentBytes { exponent = exponent << 8 | UInt32(byte) }

        return (Data(modulus), exponent)
    }

    private static func readTagLength(_ bytes: [UInt8], _ cursor: inout Int) throws -> (tag: UInt8, length: Int) {
        guard cursor + 2 <= bytes.count else { throw DERError.truncated }
        let tag = bytes[cursor]
        cursor += 1
        var length = Int(bytes[cursor])
        cursor += 1
        if length & 0x80 != 0 {
            let byteCount = length & 0x7F
            guard byteCount > 0, byteCount <= 4, cursor + byteCount <= bytes.count else {
                throw DERError.invalidLength
            }
            length = 0
            for _ in 0..<byteCount {
                length = length << 8 | Int(bytes[cursor])
                cursor += 1
            }
        }
        return (tag, length)
    }

    /// Reads an INTEGER, stripping a single leading zero sign byte if present.
    private static func readInteger(_ bytes: [UInt8], _ cursor: inout Int) throws -> [UInt8] {
        let (tag, length) = try readTagLength(bytes, &cursor)
        guard tag == 0x02 else { throw DERError.unexpectedTag(tag) }
        guard length > 0, cursor + length <= bytes.count else { throw DERError.truncated }
        var value = Array(bytes[cursor..<(cursor + length)])
        cursor += length
        if value.count > 1 && value[0] == 0 {
            value.removeFirst()
        }
        return value
    }
}
