import Foundation

/// Android `KeyEvent` codes sent via `input keyevent <code>`.
public enum AndroidKey: Int, Sendable, CaseIterable {
    // Navigation
    case home = 3
    case back = 4
    case dpadUp = 19
    case dpadDown = 20
    case dpadLeft = 21
    case dpadRight = 22
    case dpadCenter = 23
    case menu = 82
    case search = 84
    case enter = 66
    case del = 67
    case appSwitch = 187

    // Volume / power
    case volumeUp = 24
    case volumeDown = 25
    case power = 26
    case mute = 164

    // Media transport
    case mediaPlayPause = 85
    case mediaStop = 86
    case mediaNext = 87
    case mediaPrevious = 88
    case mediaRewind = 89
    case mediaFastForward = 90
    case mediaPlay = 126
    case mediaPause = 127

    // Digits
    case num0 = 7
    case num1 = 8
    case num2 = 9
    case num3 = 10
    case num4 = 11
    case num5 = 12
    case num6 = 13
    case num7 = 14
    case num8 = 15
    case num9 = 16

    public static func digit(_ value: Int) -> AndroidKey? {
        guard (0...9).contains(value) else { return nil }
        return AndroidKey(rawValue: 7 + value)
    }
}
