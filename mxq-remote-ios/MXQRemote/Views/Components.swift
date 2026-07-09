import SwiftUI

enum Theme {
    static let background = Color(red: 0.07, green: 0.07, blue: 0.09)
    static let surface = Color(red: 0.14, green: 0.14, blue: 0.17)
    static let surfacePressed = Color(red: 0.22, green: 0.22, blue: 0.26)
    static let accent = Color(red: 0.30, green: 0.62, blue: 1.0)
    static let danger = Color(red: 0.95, green: 0.30, blue: 0.27)
}

/// Circular remote button with a big touch target.
struct RoundRemoteButton: View {
    let systemImage: String
    var label: String?
    var size: CGFloat = 60
    var tint: Color = .white
    var background: Color = Theme.surface
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                ZStack {
                    Circle()
                        .fill(background)
                    Image(systemName: systemImage)
                        .font(.system(size: size * 0.36, weight: .semibold))
                        .foregroundColor(tint)
                }
                .frame(width: size, height: size)
                if let label {
                    Text(label)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .buttonStyle(PressedScaleStyle())
        .accessibilityLabel(label ?? systemImage)
    }
}

struct PressedScaleStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.92 : 1)
            .opacity(configuration.isPressed ? 0.8 : 1)
            .animation(.easeOut(duration: 0.08), value: configuration.isPressed)
    }
}

/// Connection status dot + text.
struct StatusBadge: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(color)
                .frame(width: 9, height: 9)
            Text(text)
                .font(.footnote)
                .foregroundColor(.secondary)
                .lineLimit(1)
        }
    }

    private var color: Color {
        switch controller.uiState {
        case .connected: return .green
        case .connecting, .authenticating, .awaitingAuthorization: return .yellow
        case .disconnected: return .red
        }
    }

    private var text: String {
        switch controller.uiState {
        case .connected:
            let model = controller.deviceModel
            return model.isEmpty ? settings.tr("status_connected") : model
        case .connecting: return settings.tr("status_connecting")
        case .authenticating: return settings.tr("status_authenticating")
        case .awaitingAuthorization: return settings.tr("status_awaiting")
        case .disconnected:
            if controller.reconnectAttempt > 0 {
                return String(format: settings.tr("reconnect_attempt"), controller.reconnectAttempt)
            }
            return settings.tr("status_disconnected")
        }
    }
}
