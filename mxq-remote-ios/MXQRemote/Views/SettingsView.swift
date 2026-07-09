import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    @State private var showRegenerateConfirmation = false
    @State private var fingerprint: String?

    var body: some View {
        List {
            Section(settings.tr("settings_devices")) {
                if controller.savedDevices.isEmpty {
                    Text(settings.tr("no_saved_devices"))
                        .font(.footnote)
                        .foregroundColor(.secondary)
                } else {
                    ForEach(controller.savedDevices) { device in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(device.displayName)
                            Text(device.host)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .onDelete { controller.removeDevices(at: $0) }
                }
            }
            .listRowBackground(Theme.surface)

            Section(settings.tr("settings_prefs")) {
                Toggle(settings.tr("settings_haptics"), isOn: $settings.hapticsEnabled)
                    .tint(Theme.accent)
                Picker(settings.tr("settings_language"), selection: $settings.language) {
                    ForEach(AppLanguage.allCases) { language in
                        Text(language.label).tag(language)
                    }
                }
            }
            .listRowBackground(Theme.surface)

            Section(settings.tr("settings_adbkey")) {
                if let fingerprint {
                    LabeledContent(settings.tr("settings_fingerprint")) {
                        Text(fingerprint)
                            .font(.caption.monospaced())
                    }
                }
                Button(settings.tr("settings_regenerate"), role: .destructive) {
                    showRegenerateConfirmation = true
                }
            }
            .listRowBackground(Theme.surface)

            Section(settings.tr("settings_about")) {
                Text(settings.tr("about_text"))
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            .listRowBackground(Theme.surface)
        }
        .scrollContentBackground(.hidden)
        .background(Theme.background)
        .navigationTitle(settings.tr("settings"))
        .task {
            // Key generation on first access is slow (RSA-2048) — keep it
            // off the main thread.
            fingerprint = await Task.detached {
                KeychainSigner.shared.publicKeyFingerprint()
            }.value
        }
        .alert(settings.tr("settings_regenerate_title"), isPresented: $showRegenerateConfirmation) {
            Button(settings.tr("cancel"), role: .cancel) {}
            Button(settings.tr("settings_regenerate"), role: .destructive) {
                KeychainSigner.shared.regenerateKey()
                fingerprint = KeychainSigner.shared.publicKeyFingerprint()
            }
        } message: {
            Text(settings.tr("settings_regenerate_msg"))
        }
    }
}
