import SwiftUI
import ADBCore

enum RemotePanel: String, CaseIterable, Identifiable {
    case remote
    case numpad
    case trackpad
    case keyboard

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .remote: return "dpad"
        case .numpad: return "number.square"
        case .trackpad: return "hand.point.up.left"
        case .keyboard: return "keyboard"
        }
    }
}

struct RemoteView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings
    @State private var panel: RemotePanel = .remote

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                header
                Divider().overlay(Color.white.opacity(0.08))
                Group {
                    switch panel {
                    case .remote: RemoteControlPanel()
                    case .numpad: NumpadView()
                    case .trackpad: TrackpadView()
                    case .keyboard: TextInputView()
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                panelBar
            }
            .background(Theme.background.ignoresSafeArea())
        }
    }

    private var header: some View {
        HStack(spacing: 12) {
            StatusBadge()
            Spacer()
            NavigationLink {
                HelpView()
            } label: {
                Image(systemName: "questionmark.circle")
                    .foregroundColor(.secondary)
            }
            NavigationLink {
                SettingsView()
            } label: {
                Image(systemName: "gearshape")
                    .foregroundColor(.secondary)
            }
            Button {
                controller.disconnect()
            } label: {
                Text(settings.tr("disconnect"))
                    .font(.footnote)
                    .foregroundColor(Theme.danger)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }

    private var panelBar: some View {
        HStack {
            ForEach(RemotePanel.allCases) { item in
                Button {
                    panel = item
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: item.systemImage)
                            .font(.system(size: 20, weight: .medium))
                        Text(settings.tr(item.rawValue))
                            .font(.caption2)
                    }
                    .foregroundColor(panel == item ? Theme.accent : .secondary)
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .padding(.vertical, 8)
        .background(Theme.surface.opacity(0.6))
    }
}

/// Main remote layout: power, D-pad + OK, nav row, volume and media.
struct RemoteControlPanel: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        ScrollView {
            VStack(spacing: 22) {
                HStack {
                    Spacer()
                    RoundRemoteButton(
                        systemImage: "power",
                        size: 54,
                        tint: Theme.danger,
                        background: Theme.surface
                    ) {
                        controller.send(.power)
                    }
                }
                .padding(.horizontal, 28)

                DPadView()

                HStack(spacing: 26) {
                    RoundRemoteButton(systemImage: "arrow.uturn.backward", label: settings.tr("btn_back")) {
                        controller.send(.back)
                    }
                    RoundRemoteButton(systemImage: "house", label: settings.tr("btn_home")) {
                        controller.send(.home)
                    }
                    RoundRemoteButton(systemImage: "line.3.horizontal", label: settings.tr("btn_menu")) {
                        controller.send(.menu)
                    }
                    RoundRemoteButton(systemImage: "square.on.square", label: settings.tr("btn_recents")) {
                        controller.send(.appSwitch)
                    }
                }

                volumeRow
                mediaRow
            }
            .padding(.vertical, 18)
        }
    }

    private var volumeRow: some View {
        HStack(spacing: 20) {
            HStack(spacing: 0) {
                Button {
                    controller.send(.volumeDown)
                } label: {
                    Image(systemName: "minus")
                        .font(.title3.weight(.semibold))
                        .frame(width: 64, height: 52)
                }
                Text(settings.tr("volume"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(width: 64)
                Button {
                    controller.send(.volumeUp)
                } label: {
                    Image(systemName: "plus")
                        .font(.title3.weight(.semibold))
                        .frame(width: 64, height: 52)
                }
            }
            .foregroundColor(.white)
            .background(Theme.surface)
            .clipShape(Capsule())
            .buttonStyle(PressedScaleStyle())

            RoundRemoteButton(systemImage: "speaker.slash", label: settings.tr("btn_mute"), size: 52) {
                controller.send(.mute)
            }
        }
    }

    private var mediaRow: some View {
        HStack(spacing: 16) {
            RoundRemoteButton(systemImage: "backward.end", size: 46) { controller.send(.mediaPrevious) }
            RoundRemoteButton(systemImage: "backward", size: 46) { controller.send(.mediaRewind) }
            RoundRemoteButton(systemImage: "playpause", size: 54, tint: Theme.accent) { controller.send(.mediaPlayPause) }
            RoundRemoteButton(systemImage: "forward", size: 46) { controller.send(.mediaFastForward) }
            RoundRemoteButton(systemImage: "forward.end", size: 46) { controller.send(.mediaNext) }
        }
    }
}

/// Big thumb-friendly D-pad with a central OK button.
struct DPadView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    private let padSize: CGFloat = 250

    var body: some View {
        ZStack {
            Circle()
                .fill(Theme.surface)
                .frame(width: padSize, height: padSize)

            VStack {
                directionButton("chevron.up", key: .dpadUp)
                Spacer()
                directionButton("chevron.down", key: .dpadDown)
            }
            .frame(height: padSize - 18)

            HStack {
                directionButton("chevron.left", key: .dpadLeft)
                Spacer()
                directionButton("chevron.right", key: .dpadRight)
            }
            .frame(width: padSize - 18)

            Button {
                controller.send(.dpadCenter)
            } label: {
                ZStack {
                    Circle()
                        .fill(Theme.accent)
                    Text(settings.tr("btn_ok"))
                        .font(.title3.weight(.bold))
                        .foregroundColor(.black)
                }
                .frame(width: 84, height: 84)
            }
            .buttonStyle(PressedScaleStyle())
            .accessibilityLabel(settings.tr("btn_ok"))
        }
        .frame(width: padSize, height: padSize)
    }

    private func directionButton(_ systemImage: String, key: AndroidKey) -> some View {
        Button {
            controller.send(key)
        } label: {
            Image(systemName: systemImage)
                .font(.system(size: 26, weight: .bold))
                .foregroundColor(.white)
                .frame(width: 66, height: 66)
                .contentShape(Rectangle())
        }
        .buttonStyle(PressedScaleStyle())
    }
}
