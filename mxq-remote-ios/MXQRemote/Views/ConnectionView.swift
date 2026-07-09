import SwiftUI

struct ConnectionView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    @State private var host = ""
    @State private var nickname = ""

    private var isBusy: Bool {
        switch controller.uiState {
        case .connecting, .authenticating, .awaitingAuthorization: return true
        default: return false
        }
    }

    var body: some View {
        NavigationStack {
            List {
                statusSection
                if !isBusy {
                    manualSection
                    savedSection
                    scanSection
                }
            }
            .scrollContentBackground(.hidden)
            .background(Theme.background)
            .navigationTitle(settings.tr("app_name"))
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink {
                        SettingsView()
                    } label: {
                        Image(systemName: "gearshape")
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink {
                        HelpView()
                    } label: {
                        Image(systemName: "questionmark.circle")
                    }
                }
            }
        }
    }

    private var statusSection: some View {
        Section {
            HStack {
                StatusBadge()
                Spacer()
                if isBusy {
                    ProgressView()
                    Button(settings.tr("cancel")) {
                        controller.disconnect()
                    }
                    .foregroundColor(Theme.danger)
                }
            }
            if controller.uiState == .awaitingAuthorization {
                Label(settings.tr("awaiting_hint"), systemImage: "tv")
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            if case .disconnected(let errorKey?) = controller.uiState {
                Label(settings.tr(errorKey), systemImage: "exclamationmark.triangle")
                    .font(.footnote)
                    .foregroundColor(.orange)
            }
        }
        .listRowBackground(Theme.surface)
    }

    private var manualSection: some View {
        Section(settings.tr("device_ip")) {
            TextField(settings.tr("ip_placeholder"), text: $host)
                .keyboardType(.numbersAndPunctuation)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
            TextField(settings.tr("device_name"), text: $nickname)
            Button {
                controller.connect(host: host, name: nickname)
            } label: {
                Text(settings.tr("connect"))
                    .frame(maxWidth: .infinity)
                    .fontWeight(.semibold)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.accent)
            .disabled(host.trimmingCharacters(in: .whitespaces).isEmpty)
        }
        .listRowBackground(Theme.surface)
    }

    private var savedSection: some View {
        Section(settings.tr("saved_devices")) {
            if controller.savedDevices.isEmpty {
                Text(settings.tr("no_saved_devices"))
                    .font(.footnote)
                    .foregroundColor(.secondary)
            } else {
                ForEach(controller.savedDevices) { device in
                    Button {
                        controller.connect(to: device)
                    } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(device.displayName)
                                    .foregroundColor(.primary)
                                if !device.name.isEmpty {
                                    Text(device.host)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .onDelete { offsets in
                    controller.removeDevices(at: offsets)
                }
            }
        }
        .listRowBackground(Theme.surface)
    }

    private var scanSection: some View {
        Section(settings.tr("found_devices")) {
            Button {
                controller.scanNetwork()
            } label: {
                HStack {
                    Image(systemName: "dot.radiowaves.left.and.right")
                    Text(controller.isScanning ? settings.tr("scanning") : settings.tr("scan_network"))
                    Spacer()
                    if controller.isScanning {
                        ProgressView(value: controller.scanProgress)
                            .frame(width: 70)
                    }
                }
            }
            .disabled(controller.isScanning)

            ForEach(controller.scanResults, id: \.self) { foundHost in
                Button {
                    controller.connect(host: foundHost)
                } label: {
                    Label(foundHost, systemImage: "tv")
                        .foregroundColor(.primary)
                }
            }
            if !controller.isScanning && controller.scanResults.isEmpty && controller.scanProgress >= 1 {
                Text(settings.tr("scan_none"))
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
        }
        .listRowBackground(Theme.surface)
    }
}
