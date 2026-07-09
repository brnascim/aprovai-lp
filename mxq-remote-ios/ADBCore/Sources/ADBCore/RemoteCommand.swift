import Foundation

/// Builds the Android shell commands executed on the box. Every user action
/// in the app ultimately becomes one of these strings written to a shell
/// stream (`input` injects events system-wide, no root required).
public enum RemoteCommand {

    public static func keyEvent(_ key: AndroidKey) -> String {
        "input keyevent \(key.rawValue)"
    }

    public static func tap(x: Int, y: Int) -> String {
        "input tap \(x) \(y)"
    }

    public static func swipe(fromX: Int, fromY: Int, toX: Int, toY: Int, durationMS: Int) -> String {
        "input swipe \(fromX) \(fromY) \(toX) \(toY) \(max(1, durationMS))"
    }

    /// `input text` requires spaces encoded as %s; the argument is also
    /// single-quoted for the shell (with embedded quotes escaped) so other
    /// characters pass through literally. Newlines are not supported by
    /// `input text` and are converted to spaces.
    public static func text(_ text: String) -> String {
        let flattened = text
            .replacingOccurrences(of: "\r\n", with: " ")
            .replacingOccurrences(of: "\n", with: " ")
        let quoted = flattened
            .replacingOccurrences(of: "'", with: "'\\''")
            .replacingOccurrences(of: " ", with: "%s")
        return "input text '\(quoted)'"
    }

    /// Launches an app by package name using monkey (works without knowing
    /// the exact activity name).
    public static func launchPackage(_ package: String) -> String {
        "monkey -p \(package) -c android.intent.category.LAUNCHER 1"
    }

    public static let wmSize = "wm size"

    /// Parses `wm size` output. Prefers the override size when present:
    ///   Physical size: 1920x1080
    ///   Override size: 1280x720
    public static func parseWmSize(_ output: String) -> (width: Int, height: Int)? {
        var physical: (Int, Int)?
        var override: (Int, Int)?
        for line in output.split(whereSeparator: \.isNewline) {
            guard let colon = line.firstIndex(of: ":") else { continue }
            let value = line[line.index(after: colon)...].trimmingCharacters(in: .whitespaces)
            let parts = value.split(separator: "x")
            guard parts.count == 2, let w = Int(parts[0]), let h = Int(parts[1]), w > 0, h > 0 else { continue }
            if line.lowercased().contains("override") {
                override = (w, h)
            } else if line.lowercased().contains("physical") {
                physical = (w, h)
            }
        }
        return override ?? physical
    }
}
