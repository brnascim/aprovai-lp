import Foundation

/// ADB wire protocol command identifiers (ASCII fourcc, little-endian).
public enum ADBCommand: UInt32, Sendable {
    case cnxn = 0x4E58_4E43 // "CNXN"
    case auth = 0x4854_5541 // "AUTH"
    case open = 0x4E45_504F // "OPEN"
    case okay = 0x5941_4B4F // "OKAY"
    case wrte = 0x4554_5257 // "WRTE"
    case clse = 0x4553_4C43 // "CLSE"
    case sync = 0x434E_5953 // "SYNC"
    case stls = 0x534C_5453 // "STLS"
}

/// AUTH message subtypes (arg0).
public enum ADBAuthType: UInt32, Sendable {
    case token = 1
    case signature = 2
    case rsaPublicKey = 3
}

public enum ADBProtocolError: Error, Equatable, Sendable {
    case badMagic(command: UInt32, magic: UInt32)
    case unknownCommand(UInt32)
    case oversizedPayload(UInt32)
    case truncatedHeader
}

/// One ADB protocol message: 24-byte header + optional payload.
///
/// Header layout (all fields little-endian UInt32):
///   command | arg0 | arg1 | data_length | data_checksum | magic
/// where magic == command XOR 0xFFFFFFFF and data_checksum is the
/// byte-wise sum of the payload (the legacy ADB "crc32" field is, in
/// practice, a plain sum of bytes — see AOSP adb/transport.cpp).
public struct ADBMessage: Equatable, Sendable {
    public static let headerSize = 24
    /// Refuse to buffer payloads larger than this (sanity limit).
    public static let maxPayloadSize: UInt32 = 4 * 1024 * 1024

    public var command: ADBCommand
    public var arg0: UInt32
    public var arg1: UInt32
    public var payload: Data

    public init(command: ADBCommand, arg0: UInt32 = 0, arg1: UInt32 = 0, payload: Data = Data()) {
        self.command = command
        self.arg0 = arg0
        self.arg1 = arg1
        self.payload = payload
    }

    public static func checksum(_ data: Data) -> UInt32 {
        data.reduce(UInt32(0)) { $0 &+ UInt32($1) }
    }

    public func encoded() -> Data {
        var out = Data(capacity: Self.headerSize + payload.count)
        out.appendLEUInt32(command.rawValue)
        out.appendLEUInt32(arg0)
        out.appendLEUInt32(arg1)
        out.appendLEUInt32(UInt32(payload.count))
        out.appendLEUInt32(Self.checksum(payload))
        out.appendLEUInt32(command.rawValue ^ 0xFFFF_FFFF)
        out.append(payload)
        return out
    }

    public var payloadString: String {
        var data = payload
        if data.last == 0 { data.removeLast() }
        return String(decoding: data, as: UTF8.self)
    }
}

struct ADBMessageHeader {
    let commandRaw: UInt32
    let arg0: UInt32
    let arg1: UInt32
    let length: UInt32
    let checksum: UInt32
    let magic: UInt32

    /// Parses exactly 24 bytes. Throws if magic doesn't match or command unknown.
    static func parse(_ bytes: [UInt8]) throws -> ADBMessageHeader {
        guard bytes.count >= ADBMessage.headerSize else { throw ADBProtocolError.truncatedHeader }
        func le(_ offset: Int) -> UInt32 {
            UInt32(bytes[offset])
                | UInt32(bytes[offset + 1]) << 8
                | UInt32(bytes[offset + 2]) << 16
                | UInt32(bytes[offset + 3]) << 24
        }
        let header = ADBMessageHeader(
            commandRaw: le(0), arg0: le(4), arg1: le(8),
            length: le(12), checksum: le(16), magic: le(20)
        )
        guard header.magic == (header.commandRaw ^ 0xFFFF_FFFF) else {
            throw ADBProtocolError.badMagic(command: header.commandRaw, magic: header.magic)
        }
        guard ADBCommand(rawValue: header.commandRaw) != nil else {
            throw ADBProtocolError.unknownCommand(header.commandRaw)
        }
        guard header.length <= ADBMessage.maxPayloadSize else {
            throw ADBProtocolError.oversizedPayload(header.length)
        }
        return header
    }
}

/// Incremental parser: feed raw TCP chunks in, get complete messages out.
/// Incoming checksums are not verified (several adbd builds send 0).
public final class ADBMessageReader {
    private var buffer = [UInt8]()
    private var pending: ADBMessageHeader?

    public init() {}

    public func append(_ data: Data) throws -> [ADBMessage] {
        buffer.append(contentsOf: data)
        var messages = [ADBMessage]()
        while true {
            if pending == nil {
                guard buffer.count >= ADBMessage.headerSize else { break }
                pending = try ADBMessageHeader.parse(buffer)
                buffer.removeFirst(ADBMessage.headerSize)
            }
            guard let header = pending, buffer.count >= Int(header.length) else { break }
            let payload = Data(buffer.prefix(Int(header.length)))
            buffer.removeFirst(Int(header.length))
            pending = nil
            messages.append(ADBMessage(
                command: ADBCommand(rawValue: header.commandRaw)!,
                arg0: header.arg0,
                arg1: header.arg1,
                payload: payload
            ))
        }
        return messages
    }
}

extension Data {
    mutating func appendLEUInt32(_ value: UInt32) {
        append(UInt8(truncatingIfNeeded: value))
        append(UInt8(truncatingIfNeeded: value >> 8))
        append(UInt8(truncatingIfNeeded: value >> 16))
        append(UInt8(truncatingIfNeeded: value >> 24))
    }
}
