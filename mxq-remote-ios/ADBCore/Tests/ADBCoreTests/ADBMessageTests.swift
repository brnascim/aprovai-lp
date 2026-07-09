import XCTest
@testable import ADBCore

final class ADBMessageTests: XCTestCase {

    func testEncodedHeaderLayout() {
        let payload = Data("host::".utf8)
        let message = ADBMessage(command: .cnxn, arg0: 0x0100_0000, arg1: 0x0010_0000, payload: payload)
        let encoded = message.encoded()

        XCTAssertEqual(encoded.count, 24 + payload.count)
        // Little-endian fourcc serializes back to ASCII "CNXN".
        XCTAssertEqual(String(decoding: encoded.prefix(4), as: UTF8.self), "CNXN")
        // arg0
        XCTAssertEqual(Array(encoded[4..<8]), [0x00, 0x00, 0x00, 0x01])
        // data length
        XCTAssertEqual(Array(encoded[12..<16]), [UInt8(payload.count), 0, 0, 0])
        // checksum = byte sum of "host::"
        let expectedChecksum = payload.reduce(UInt32(0)) { $0 &+ UInt32($1) }
        let checksumBytes = Array(encoded[16..<20])
        let checksum = UInt32(checksumBytes[0])
            | UInt32(checksumBytes[1]) << 8
            | UInt32(checksumBytes[2]) << 16
            | UInt32(checksumBytes[3]) << 24
        XCTAssertEqual(checksum, expectedChecksum)
        // magic = command XOR 0xFFFFFFFF
        let magicBytes = Array(encoded[20..<24])
        let magic = UInt32(magicBytes[0])
            | UInt32(magicBytes[1]) << 8
            | UInt32(magicBytes[2]) << 16
            | UInt32(magicBytes[3]) << 24
        XCTAssertEqual(magic, 0x4E58_4E43 ^ 0xFFFF_FFFF)
    }

    func testChecksumEmptyPayloadIsZero() {
        XCTAssertEqual(ADBMessage.checksum(Data()), 0)
        XCTAssertEqual(ADBMessage.checksum(Data([0xFF, 0x01])), 0x100)
    }

    func testReaderRoundTripSingleMessage() throws {
        let original = ADBMessage(command: .wrte, arg0: 1, arg1: 2, payload: Data("input keyevent 23\n".utf8))
        let reader = ADBMessageReader()
        let messages = try reader.append(original.encoded())
        XCTAssertEqual(messages, [original])
    }

    func testReaderHandlesArbitraryChunking() throws {
        let first = ADBMessage(command: .okay, arg0: 5, arg1: 9)
        let second = ADBMessage(command: .wrte, arg0: 9, arg1: 5, payload: Data(repeating: 0xAB, count: 300))
        var stream = first.encoded()
        stream.append(second.encoded())

        let reader = ADBMessageReader()
        var collected = [ADBMessage]()
        // Feed one byte at a time — worst-case TCP fragmentation.
        for byte in stream {
            collected.append(contentsOf: try reader.append(Data([byte])))
        }
        XCTAssertEqual(collected, [first, second])
    }

    func testReaderRejectsBadMagic() {
        var corrupted = ADBMessage(command: .okay, arg0: 1, arg1: 1).encoded()
        corrupted[20] ^= 0xFF
        let reader = ADBMessageReader()
        XCTAssertThrowsError(try reader.append(corrupted)) { error in
            guard case ADBProtocolError.badMagic = error else {
                return XCTFail("expected badMagic, got \(error)")
            }
        }
    }

    func testReaderRejectsUnknownCommand() {
        // Craft a header with a bogus command but a valid magic.
        var data = Data()
        data.appendLEUInt32(0xDEAD_BEEF)
        data.appendLEUInt32(0)
        data.appendLEUInt32(0)
        data.appendLEUInt32(0)
        data.appendLEUInt32(0)
        data.appendLEUInt32(0xDEAD_BEEF ^ 0xFFFF_FFFF)
        let reader = ADBMessageReader()
        XCTAssertThrowsError(try reader.append(data)) { error in
            guard case ADBProtocolError.unknownCommand = error else {
                return XCTFail("expected unknownCommand, got \(error)")
            }
        }
    }

    func testPayloadStringStripsTrailingNul() {
        var payload = Data("shell:".utf8)
        payload.append(0)
        let message = ADBMessage(command: .open, arg0: 1, payload: payload)
        XCTAssertEqual(message.payloadString, "shell:")
    }
}
