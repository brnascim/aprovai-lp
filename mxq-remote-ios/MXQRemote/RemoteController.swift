import Foundation
import SwiftUI
import ADBCore

struct DeviceResolution: Equatable {
    var width: Int
    var height: Int

    static let fallback = DeviceResolution(width: 1920, height: 1080)
}

/// Top-level view model: owns the ADB connection, saved devices, network
/// scan, auto-reconnect and translates UI gestures into shell commands.
@MainActor
final class RemoteController: ObservableObject {

    enum UIState: Equatable {
        case disconnected(errorKey: String?)
        case connecting
        case authenticating
        case awaitingAuthorization
        case connected
    }

    @Published private(set) var uiState: UIState = .disconnected(errorKey: nil)
    @Published private(set) var deviceModel = ""
    @Published private(set) var resolution = DeviceResolution.fallback
    @Published private(set) var reconnectAttempt = 0
    @Published var savedDevices: [SavedDevice] {
        didSet { store.save(savedDevices) }
    }
    @Published private(set) var isScanning = false
    @Published private(set) var scanResults: [String] = []
    @Published private(set) var scanProgress: Double = 0

    let settings: AppSettings
    private(set) var currentDevice: SavedDevice?

    private let store = DeviceStore()
    private var connection: ADBConnection?
    /// Identifies the active connection attempt so state callbacks from a
    /// replaced/closed connection can't stomp the current one.
    private var connectionGeneration = UUID()
    private var heartbeatTask: Task<Void, Never>?
    private var reconnectTask: Task<Void, Never>?
    private var userInitiatedDisconnect = false

    private static let maxReconnectAttempts = 5

    init(settings: AppSettings) {
        self.settings = settings
        self.savedDevices = store.load()
    }

    var isConnected: Bool { uiState == .connected }

    // MARK: - Connection lifecycle

    func connect(host: String, name: String = "") {
        let trimmedHost = host.trimmingCharacters(in: .whitespaces)
        guard !trimmedHost.isEmpty else { return }
        let device = savedDevices.first(where: { $0.host == trimmedHost })
            ?? SavedDevice(name: name.trimmingCharacters(in: .whitespaces), host: trimmedHost)
        if !savedDevices.contains(where: { $0.host == trimmedHost }) {
            savedDevices.append(device)
        }
        connect(to: device)
    }

    func connect(to device: SavedDevice) {
        reconnectTask?.cancel()
        heartbeatTask?.cancel()
        if let existing = connection {
            Task { await existing.close() }
        }
        userInitiatedDisconnect = false
        currentDevice = device

        let generation = UUID()
        connectionGeneration = generation
        let transport = NWTransport(host: device.host)
        let adb = ADBConnection(transport: transport, signer: KeychainSigner.shared) { [weak self] state in
            Task { @MainActor in
                guard let self, self.connectionGeneration == generation else { return }
                self.handleConnectionState(state)
            }
        }
        connection = adb
        Task {
            do {
                try await adb.connect()
                guard self.connectionGeneration == generation else { return }
                await self.afterConnected(adb)
            } catch {
                // Failure already surfaced through the state callback.
            }
        }
    }

    func disconnect() {
        userInitiatedDisconnect = true
        connectionGeneration = UUID() // ignore late callbacks from the closing connection
        reconnectAttempt = 0
        reconnectTask?.cancel()
        heartbeatTask?.cancel()
        let adb = connection
        connection = nil
        Task { await adb?.close() }
        uiState = .disconnected(errorKey: nil)
    }

    private func handleConnectionState(_ state: ADBConnectionState) {
        switch state {
        case .idle:
            break
        case .connecting:
            uiState = .connecting
        case .authenticating:
            uiState = .authenticating
        case .awaitingAuthorization:
            uiState = .awaitingAuthorization
        case .connected(let device):
            deviceModel = device
            reconnectAttempt = 0
            uiState = .connected
        case .disconnected(let reason):
            heartbeatTask?.cancel()
            if userInitiatedDisconnect {
                uiState = .disconnected(errorKey: nil)
            } else {
                uiState = .disconnected(errorKey: Self.errorKey(for: reason))
                scheduleReconnect()
            }
        }
    }

    private func afterConnected(_ adb: ADBConnection) async {
        // Calibrate the trackpad; keep the fallback resolution on failure.
        if let output = try? await adb.runCommand(RemoteCommand.wmSize),
           let size = RemoteCommand.parseWmSize(output) {
            resolution = DeviceResolution(width: size.width, height: size.height)
        }
        startHeartbeat(adb)
    }

    private func startHeartbeat(_ adb: ADBConnection) {
        heartbeatTask?.cancel()
        heartbeatTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 20_000_000_000)
                guard !Task.isCancelled, let self, self.connection === adb else { return }
                // Shell no-op keeps the TCP path warm; a dead link surfaces
                // in the reader loop and triggers auto-reconnect.
                await adb.execShell(":")
            }
        }
    }

    private func scheduleReconnect() {
        guard let device = currentDevice,
              reconnectAttempt < Self.maxReconnectAttempts else { return }
        reconnectAttempt += 1
        let delay = pow(2.0, Double(reconnectAttempt - 1)) // 1, 2, 4, 8, 16s
        reconnectTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            guard let self, !Task.isCancelled, !self.userInitiatedDisconnect else { return }
            self.connect(to: device)
        }
    }

    private static func errorKey(for reason: String?) -> String? {
        switch reason {
        case nil: return nil
        case "timeout": return "err_timeout"
        case "tls-required": return "err_tls"
        default: return "err_closed"
        }
    }

    // MARK: - Remote actions

    func send(_ key: AndroidKey) {
        hapticFeedback()
        exec(RemoteCommand.keyEvent(key))
    }

    func sendDigit(_ digit: Int) {
        guard let key = AndroidKey.digit(digit) else { return }
        send(key)
    }

    /// Trackpad tap with coordinates normalized to 0...1.
    func tap(normalizedX: Double, normalizedY: Double) {
        hapticFeedback()
        exec(RemoteCommand.tap(
            x: scaled(normalizedX, to: resolution.width),
            y: scaled(normalizedY, to: resolution.height)
        ))
    }

    func swipe(fromX: Double, fromY: Double, toX: Double, toY: Double, durationMS: Int) {
        hapticFeedback()
        exec(RemoteCommand.swipe(
            fromX: scaled(fromX, to: resolution.width),
            fromY: scaled(fromY, to: resolution.height),
            toX: scaled(toX, to: resolution.width),
            toY: scaled(toY, to: resolution.height),
            durationMS: durationMS
        ))
    }

    func sendText(_ text: String, pressEnter: Bool) {
        let trimmed = text
        guard !trimmed.isEmpty else { return }
        hapticFeedback()
        exec(RemoteCommand.text(trimmed))
        if pressEnter {
            exec(RemoteCommand.keyEvent(.enter))
        }
    }

    private func exec(_ command: String) {
        guard let adb = connection else { return }
        Task { await adb.execShell(command) }
    }

    private func scaled(_ normalized: Double, to dimension: Int) -> Int {
        let clamped = min(max(normalized, 0), 1)
        return Int((clamped * Double(dimension - 1)).rounded())
    }

    private func hapticFeedback() {
        if settings.hapticsEnabled {
            Haptics.buttonTap()
        }
    }

    // MARK: - Saved devices

    func removeDevices(at offsets: IndexSet) {
        savedDevices.remove(atOffsets: offsets)
    }

    func removeDevice(_ device: SavedDevice) {
        savedDevices.removeAll { $0.id == device.id }
    }

    // MARK: - Network scan

    func scanNetwork() {
        guard !isScanning else { return }
        isScanning = true
        scanProgress = 0
        scanResults = []
        Task {
            let found = await SubnetScanner.scan(onProgress: { [weak self] progress in
                Task { @MainActor in self?.scanProgress = progress }
            })
            self.scanResults = found
            self.isScanning = false
        }
    }
}
