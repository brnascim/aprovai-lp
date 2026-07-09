import XCTest
@testable import ADBCore

final class DERParserTests: XCTestCase {

    /// Builds a PKCS#1 RSAPublicKey DER by hand:
    /// SEQUENCE { INTEGER modulus, INTEGER exponent }
    private func makeDER(modulus: [UInt8], exponent: [UInt8]) -> Data {
        func integer(_ value: [UInt8]) -> [UInt8] {
            // Prepend a zero sign byte if the high bit is set (positive int).
            var body = value
            if let first = body.first, first & 0x80 != 0 {
                body.insert(0x00, at: 0)
            }
            return [0x02] + length(body.count) + body
        }
        func length(_ count: Int) -> [UInt8] {
            if count < 0x80 { return [UInt8(count)] }
            if count <= 0xFF { return [0x81, UInt8(count)] }
            return [0x82, UInt8(count >> 8), UInt8(count & 0xFF)]
        }
        let body = integer(modulus) + integer(exponent)
        return Data([0x30] + length(body.count) + body)
    }

    func testParsesTypical2048BitKey() throws {
        var modulus = [UInt8](repeating: 0, count: 256)
        for i in 0..<256 { modulus[i] = UInt8((i &+ 3) & 0xFF) }
        modulus[0] |= 0x80 // forces the sign byte + long-form length in DER

        let der = makeDER(modulus: modulus, exponent: [0x01, 0x00, 0x01])
        let parsed = try DERParser.parseRSAPublicKeyPKCS1(der)

        XCTAssertEqual([UInt8](parsed.modulus), modulus, "sign byte must be stripped")
        XCTAssertEqual(parsed.exponent, 65537)
    }

    func testParsesShortKeyWithoutSignByte() throws {
        let modulus: [UInt8] = [0x75, 0x23, 0x11, 0x01] // high bit clear
        let der = makeDER(modulus: modulus, exponent: [0x03])
        let parsed = try DERParser.parseRSAPublicKeyPKCS1(der)
        XCTAssertEqual([UInt8](parsed.modulus), modulus)
        XCTAssertEqual(parsed.exponent, 3)
    }

    func testRejectsGarbage() {
        XCTAssertThrowsError(try DERParser.parseRSAPublicKeyPKCS1(Data([0x02, 0x01, 0x00])))
        XCTAssertThrowsError(try DERParser.parseRSAPublicKeyPKCS1(Data()))
        // Truncated sequence body.
        XCTAssertThrowsError(try DERParser.parseRSAPublicKeyPKCS1(Data([0x30, 0x10, 0x02, 0x01])))
    }
}
