import SwiftUI

@main
struct MXQRemoteApp: App {
    @StateObject private var settings: AppSettings
    @StateObject private var controller: RemoteController

    init() {
        let settings = AppSettings()
        _settings = StateObject(wrappedValue: settings)
        _controller = StateObject(wrappedValue: RemoteController(settings: settings))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(settings)
                .environmentObject(controller)
                .preferredColorScheme(.dark) // TV-room context: dark by default
        }
    }
}

struct RootView: View {
    @EnvironmentObject private var controller: RemoteController

    var body: some View {
        Group {
            if controller.isConnected {
                RemoteView()
            } else {
                ConnectionView()
            }
        }
        .animation(.easeInOut(duration: 0.25), value: controller.isConnected)
    }
}
