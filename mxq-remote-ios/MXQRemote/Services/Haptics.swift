import UIKit

enum Haptics {
    private static let light = UIImpactFeedbackGenerator(style: .light)
    private static let medium = UIImpactFeedbackGenerator(style: .medium)

    static func buttonTap() {
        light.impactOccurred()
    }

    static func strongTap() {
        medium.impactOccurred()
    }
}
