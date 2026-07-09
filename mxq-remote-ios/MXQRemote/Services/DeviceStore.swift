import Foundation

struct SavedDevice: Codable, Identifiable, Equatable, Hashable {
    var id = UUID()
    var name: String
    var host: String

    var displayName: String {
        name.isEmpty ? host : name
    }
}

/// Persists the list of saved devices in UserDefaults (small, non-secret).
struct DeviceStore {
    private static let key = "com.mxqremote.savedDevices"

    func load() -> [SavedDevice] {
        guard let data = UserDefaults.standard.data(forKey: Self.key),
              let devices = try? JSONDecoder().decode([SavedDevice].self, from: data) else {
            return []
        }
        return devices
    }

    func save(_ devices: [SavedDevice]) {
        guard let data = try? JSONEncoder().encode(devices) else { return }
        UserDefaults.standard.set(data, forKey: Self.key)
    }
}
