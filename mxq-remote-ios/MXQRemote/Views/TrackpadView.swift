import SwiftUI
import ADBCore

/// Absolute-mapping trackpad: the touch area maps 1:1 to the TV screen
/// (resolution discovered via `wm size`). A short touch is a tap; a drag
/// becomes a swipe with the real gesture duration.
struct TrackpadView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    @State private var dragStartTime: Date?
    @State private var lastTouch: CGPoint?

    private let tapDistanceThreshold: CGFloat = 14

    var body: some View {
        VStack(spacing: 14) {
            Text(settings.tr("trackpad_hint"))
                .font(.footnote)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            GeometryReader { geometry in
                ZStack {
                    RoundedRectangle(cornerRadius: 22)
                        .fill(Theme.surface)
                    // 16:9 guide mirroring the TV shape
                    RoundedRectangle(cornerRadius: 22)
                        .strokeBorder(Color.white.opacity(0.08), lineWidth: 1)
                    if let touch = lastTouch {
                        Circle()
                            .fill(Theme.accent.opacity(0.5))
                            .frame(width: 26, height: 26)
                            .position(touch)
                            .allowsHitTesting(false)
                    }
                }
                .contentShape(RoundedRectangle(cornerRadius: 22))
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            if dragStartTime == nil {
                                dragStartTime = Date()
                            }
                            lastTouch = value.location
                        }
                        .onEnded { value in
                            handleGestureEnd(value, in: geometry.size)
                            dragStartTime = nil
                            withAnimation(.easeOut(duration: 0.3)) {
                                lastTouch = nil
                            }
                        }
                )
            }
            .padding(.horizontal, 14)

            volumeStrip
        }
        .padding(.vertical, 14)
    }

    private func handleGestureEnd(_ value: DragGesture.Value, in size: CGSize) {
        guard size.width > 0, size.height > 0 else { return }
        let start = value.startLocation
        let end = value.location
        let distance = hypot(end.x - start.x, end.y - start.y)
        if distance < tapDistanceThreshold {
            controller.tap(
                normalizedX: end.x / size.width,
                normalizedY: end.y / size.height
            )
        } else {
            let elapsedMS = Int((Date().timeIntervalSince(dragStartTime ?? Date()) * 1000).rounded())
            controller.swipe(
                fromX: start.x / size.width,
                fromY: start.y / size.height,
                toX: end.x / size.width,
                toY: end.y / size.height,
                durationMS: min(max(elapsedMS, 80), 1500)
            )
        }
    }

    /// Volume stays reachable in trackpad mode.
    private var volumeStrip: some View {
        HStack(spacing: 16) {
            RoundRemoteButton(systemImage: "speaker.wave.1", size: 48) { controller.send(.volumeDown) }
            RoundRemoteButton(systemImage: "speaker.slash", size: 48) { controller.send(.mute) }
            RoundRemoteButton(systemImage: "speaker.wave.3", size: 48) { controller.send(.volumeUp) }
            Spacer()
            Text("\(settings.tr("trackpad_res")): \(controller.resolution.width)×\(controller.resolution.height)")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal, 18)
    }
}
