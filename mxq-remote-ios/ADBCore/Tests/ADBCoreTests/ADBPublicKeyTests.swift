import XCTest
@testable import ADBCore

final class ADBPublicKeyTests: XCTestCase {

    // MARK: BigUInt32

    func testNegativeInverseMod2Pow32() {
        for n0: UInt32 in [1, 3, 0x10001, 0xDEAD_BEEF | 1, 0xFFFF_FFFF] {
            let n0inv = BigUInt32.negativeInverseMod2Pow32(n0)
            // n0 * (-n0inv) ≡ 1 (mod 2^32)  ⇔  n0 * n0inv ≡ -1 (mod 2^32)
            XCTAssertEqual(n0 &* n0inv, 0xFFFF_FFFF, "failed for n0=\(String(n0, radix: 16))")
        }
    }

    func testPowerOfTwoModAgainstUInt64Reference() {
        // Moduli under 2^63 let us compute the reference with plain UInt64
        // doubling. Words are little-endian 32-bit limbs.
        let moduli: [UInt64] = [
            (1 << 62) + 12_345_678_901,
            0x7FFF_FFFF_FFFF_FFC5, // large prime-ish
            (1 << 40) + 987_654_321
        ]
        for modulus in moduli {
            let words = [UInt32(truncatingIfNeeded: modulus), UInt32(truncatingIfNeeded: modulus >> 32)]
            let result = BigUInt32.powerOfTwoMod(words, exponentBits: 128)
            let resultValue = UInt64(result[0]) | UInt64(result[1]) << 32

            var reference: UInt64 = 1
            for _ in 0..<128 {
                reference = (reference << 1) % modulus
            }
            XCTAssertEqual(resultValue, reference, "failed for modulus \(modulus)")
        }
    }

    func testCompareAndSubtract() {
        var a: [UInt32] = [0, 1] // 2^32
        let b: [UInt32] = [1, 0] // 1
        XCTAssertEqual(BigUInt32.compare(a, b), 1)
        XCTAssertEqual(BigUInt32.compare(b, a), -1)
        XCTAssertEqual(BigUInt32.compare(a, [0, 1]), 0)
        BigUInt32.subtract(&a, b)
        XCTAssertEqual(a, [0xFFFF_FFFF, 0]) // 2^32 - 1
    }

    // MARK: ADB key encoding

    /// Deterministic 2048-bit modulus: MSB set (true 2048 bits), odd LSB.
    private func fixtureModulus() -> Data {
        var bytes = [UInt8](repeating: 0, count: 256)
        for i in 0..<256 {
            bytes[i] = UInt8((i &* 37 &+ 11) & 0xFF)
        }
        bytes[0] |= 0x80
        bytes[255] |= 0x01
        return Data(bytes)
    }

    func testEncodeLayoutAndInvariants() throws {
        let modulus = fixtureModulus()
        let encoded = try ADBPublicKey.encode(modulus: modulus, exponent: 65537)

        XCTAssertEqual(encoded.count, ADBPublicKey.encodedSize) // 524
        let words = encoded.withUnsafeBytes { raw -> [UInt32] in
            (0..<(encoded.count / 4)).map { i in
                UInt32(littleEndian: raw.loadUnaligned(fromByteOffset: i * 4, as: UInt32.self))
            }
        }
        XCTAssertEqual(words[0], 64) // word count

        // n words: little-endian limbs of the big-endian modulus bytes.
        let modulusBytes = [UInt8](modulus)
        for i in 0..<64 {
            let base = 256 - 4 * (i + 1)
            let expected = UInt32(modulusBytes[base]) << 24
                | UInt32(modulusBytes[base + 1]) << 16
                | UInt32(modulusBytes[base + 2]) << 8
                | UInt32(modulusBytes[base + 3])
            XCTAssertEqual(words[2 + i], expected, "n[\(i)] mismatch")
        }

        // n0inv * n[0] ≡ -1 (mod 2^32)
        XCTAssertEqual(words[1] &* words[2], 0xFFFF_FFFF)

        // rr must be a properly reduced residue: 0 < rr < n.
        let n = Array(words[2..<66])
        let rr = Array(words[66..<130])
        XCTAssertEqual(BigUInt32.compare(rr, n), -1)
        XCTAssertNotEqual(rr, [UInt32](repeating: 0, count: 64))

        // exponent
        XCTAssertEqual(words[130], 65537)
    }

    func testEncodeRejectsWrongSizeAndEvenModulus() {
        XCTAssertThrowsError(try ADBPublicKey.encode(modulus: Data(repeating: 1, count: 128), exponent: 65537))
        var even = fixtureModulus()
        even[even.count - 1] = 0x02
        XCTAssertThrowsError(try ADBPublicKey.encode(modulus: even, exponent: 65537))
    }

    func testAuthPayloadFormat() throws {
        let payload = try ADBPublicKey.authPayload(
            modulus: fixtureModulus(), exponent: 65537, name: "mxqremote@iphone"
        )
        XCTAssertEqual(payload.last, 0, "payload must be NUL-terminated")
        let text = String(decoding: payload.dropLast(), as: UTF8.self)
        let parts = text.split(separator: " ")
        XCTAssertEqual(parts.count, 2)
        XCTAssertEqual(parts[1], "mxqremote@iphone")
        // base64 of 524 bytes -> ceil(524/3)*4 = 700 chars
        XCTAssertEqual(parts[0].count, 700)
        XCTAssertEqual(Data(base64Encoded: String(parts[0]))?.count, 524)
    }
}
