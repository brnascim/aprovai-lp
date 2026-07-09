import Foundation
import SwiftUI

enum AppLanguage: String, CaseIterable, Identifiable {
    case pt
    case en

    var id: String { rawValue }

    var label: String {
        switch self {
        case .pt: return "Português (BR)"
        case .en: return "English"
        }
    }
}

/// User preferences. UI text defaults to Brazilian Portuguese with an
/// optional English toggle (see `L10n`).
@MainActor
final class AppSettings: ObservableObject {
    @Published var language: AppLanguage {
        didSet { UserDefaults.standard.set(language.rawValue, forKey: "com.mxqremote.language") }
    }
    @Published var hapticsEnabled: Bool {
        didSet { UserDefaults.standard.set(hapticsEnabled, forKey: "com.mxqremote.haptics") }
    }

    init() {
        let storedLanguage = UserDefaults.standard.string(forKey: "com.mxqremote.language")
        language = storedLanguage.flatMap(AppLanguage.init(rawValue:)) ?? .pt
        hapticsEnabled = UserDefaults.standard.object(forKey: "com.mxqremote.haptics") as? Bool ?? true
    }

    /// Translated string for the current language.
    func tr(_ key: String) -> String {
        L10n.string(key, language)
    }
}

enum L10n {
    static func string(_ key: String, _ language: AppLanguage) -> String {
        let table = language == .pt ? pt : en
        return table[key] ?? pt[key] ?? key
    }

    // MARK: PT-BR (default)
    private static let pt: [String: String] = [
        "app_name": "MXQ Remote",

        "status_disconnected": "Desconectado",
        "status_connecting": "Conectando…",
        "status_authenticating": "Autenticando…",
        "status_awaiting": "Aguardando autorização no box…",
        "status_connected": "Conectado",
        "awaiting_hint": "Na TV, use o mouse USB para aceitar o aviso “Permitir depuração USB?”. Marque “Sempre permitir deste computador” e confirme.",
        "reconnect_attempt": "Reconectando… (tentativa %d)",

        "connect": "Conectar",
        "disconnect": "Desconectar",
        "cancel": "Cancelar",
        "save": "Salvar",
        "delete": "Excluir",
        "close": "Fechar",

        "device_ip": "IP do box",
        "ip_placeholder": "192.168.0.123",
        "device_name": "Apelido (opcional)",
        "saved_devices": "Dispositivos salvos",
        "no_saved_devices": "Nenhum dispositivo salvo ainda. Informe o IP do box acima.",
        "scan_network": "Procurar na rede",
        "scanning": "Procurando na rede…",
        "scan_none": "Nenhum aparelho com ADB (porta 5555) encontrado. Verifique se a depuração pela rede está ativa no box.",
        "found_devices": "Encontrados na rede",

        "help": "Ajuda",
        "settings": "Configurações",
        "remote": "Remoto",
        "numpad": "Números",
        "trackpad": "Trackpad",
        "keyboard": "Teclado",

        "btn_ok": "OK",
        "btn_back": "Voltar",
        "btn_home": "Início",
        "btn_menu": "Menu",
        "btn_recents": "Recentes",
        "btn_mute": "Mudo",
        "btn_power": "Ligar/Desligar",
        "volume": "Volume",
        "media": "Mídia",

        "trackpad_hint": "Toque para clicar • arraste para deslizar.\nA área corresponde à tela da TV.",
        "trackpad_res": "Resolução da TV",

        "text_title": "Enviar texto para a TV",
        "text_placeholder": "Digite o texto…",
        "text_send": "Enviar",
        "text_send_enter": "Pressionar Enter após enviar",
        "text_hint": "O texto é digitado no campo em foco no box (buscas, logins). Acentos podem não funcionar em algumas firmwares.",

        "settings_devices": "Dispositivos",
        "settings_prefs": "Preferências",
        "settings_haptics": "Feedback háptico",
        "settings_language": "Idioma",
        "settings_adbkey": "Chave ADB",
        "settings_fingerprint": "Impressão digital",
        "settings_regenerate": "Regenerar chave ADB",
        "settings_regenerate_title": "Regenerar a chave ADB?",
        "settings_regenerate_msg": "A chave atual será apagada e o box pedirá autorização novamente na próxima conexão.",
        "settings_about": "Sobre",
        "about_text": "Controle remoto via ADB Wi-Fi para Android TV box (MXQ-4K e similares). Sem nuvem e sem contas: tudo acontece na sua rede local.",

        "err_timeout": "Tempo esgotado. Verifique se o iPhone e o box estão na mesma rede Wi-Fi, se o IP está certo e se o ADB pela rede está ativo.",
        "err_closed": "A conexão foi encerrada ou recusada. Confira se a depuração ADB está ativa no box (ou rode “adb tcpip 5555” uma vez via USB).",
        "err_tls": "Este aparelho exige pareamento TLS (Android 11+), que não é suportado. O MXQ-4K usa o ADB clássico.",
        "err_auth": "Autorização negada no box. Conecte de novo e aceite “Sempre permitir” no aviso da TV.",
        "err_local_network": "Se o iOS perguntou sobre a Rede Local e você negou, permita em Ajustes > Privacidade e Segurança > Rede Local > MXQ Remote.",

        "help_title": "Preparar o box (uma única vez)",
        "help_intro": "O controle físico quebrou? Sem problema: plugue um mouse USB no box para fazer estes passos.",
        "help_step_1": "Conecte o iPhone e o box na MESMA rede Wi-Fi (o box pode estar no cabo de rede do mesmo roteador).",
        "help_step_2": "No box: Configurações > Sobre > toque 7 vezes em “Número da versão” para liberar as Opções do desenvolvedor.",
        "help_step_3": "Em Opções do desenvolvedor, ative “Depuração USB” e, se existir, “ADB pela rede” (Network ADB) — isso abre a porta 5555.",
        "help_step_4": "Anote o IP do box em Configurações > Rede (ex.: 192.168.0.123). Dica: reserve esse IP no roteador para ele não mudar.",
        "help_step_5": "No app, digite o IP e toque em Conectar. O iOS vai pedir permissão de “Rede Local” — aceite.",
        "help_step_6": "Se a firmware não tiver o botão “ADB pela rede”: conecte o box a um computador por USB uma vez e rode “adb tcpip 5555”. Vale até o box reiniciar.",
        "help_first_title": "Primeira conexão",
        "help_first_body": "Na primeira conexão a TV mostra “Permitir depuração USB?” com a impressão digital da chave deste app. Use o mouse USB, marque “Sempre permitir deste computador” e confirme. Depois disso o app reconecta sozinho, sem perguntar de novo.",
        "help_trouble_title": "Problemas comuns",
        "help_trouble_body": "• Porta 5555 fechada: reative o ADB pela rede ou rode “adb tcpip 5555”.\n• IP mudou: use “Procurar na rede” e salve o novo IP (ou fixe o IP no roteador).\n• Sem resposta: reinicie o box; o ADB pela rede pode desligar após reiniciar.\n• Permissão de Rede Local negada: Ajustes > Privacidade e Segurança > Rede Local."
    ]

    // MARK: English
    private static let en: [String: String] = [
        "app_name": "MXQ Remote",

        "status_disconnected": "Disconnected",
        "status_connecting": "Connecting…",
        "status_authenticating": "Authenticating…",
        "status_awaiting": "Waiting for authorization on the box…",
        "status_connected": "Connected",
        "awaiting_hint": "On the TV, use the USB mouse to accept the “Allow USB debugging?” prompt. Check “Always allow from this computer” and confirm.",
        "reconnect_attempt": "Reconnecting… (attempt %d)",

        "connect": "Connect",
        "disconnect": "Disconnect",
        "cancel": "Cancel",
        "save": "Save",
        "delete": "Delete",
        "close": "Close",

        "device_ip": "Box IP address",
        "ip_placeholder": "192.168.0.123",
        "device_name": "Nickname (optional)",
        "saved_devices": "Saved devices",
        "no_saved_devices": "No saved devices yet. Enter the box IP above.",
        "scan_network": "Scan network",
        "scanning": "Scanning the network…",
        "scan_none": "No device with ADB (port 5555) found. Make sure network debugging is enabled on the box.",
        "found_devices": "Found on the network",

        "help": "Help",
        "settings": "Settings",
        "remote": "Remote",
        "numpad": "Numbers",
        "trackpad": "Trackpad",
        "keyboard": "Keyboard",

        "btn_ok": "OK",
        "btn_back": "Back",
        "btn_home": "Home",
        "btn_menu": "Menu",
        "btn_recents": "Recents",
        "btn_mute": "Mute",
        "btn_power": "Power",
        "volume": "Volume",
        "media": "Media",

        "trackpad_hint": "Tap to click • drag to swipe.\nThe area maps to the TV screen.",
        "trackpad_res": "TV resolution",

        "text_title": "Send text to the TV",
        "text_placeholder": "Type text…",
        "text_send": "Send",
        "text_send_enter": "Press Enter after sending",
        "text_hint": "The text is typed into the focused field on the box (search, logins). Accents may not work on some firmwares.",

        "settings_devices": "Devices",
        "settings_prefs": "Preferences",
        "settings_haptics": "Haptic feedback",
        "settings_language": "Language",
        "settings_adbkey": "ADB key",
        "settings_fingerprint": "Fingerprint",
        "settings_regenerate": "Regenerate ADB key",
        "settings_regenerate_title": "Regenerate the ADB key?",
        "settings_regenerate_msg": "The current key will be deleted and the box will ask for authorization again on the next connection.",
        "settings_about": "About",
        "about_text": "ADB-over-Wi-Fi remote control for Android TV boxes (MXQ-4K and similar). No cloud, no accounts: everything stays on your local network.",

        "err_timeout": "Timed out. Check that the iPhone and the box are on the same Wi-Fi, the IP is correct and network ADB is enabled.",
        "err_closed": "The connection was closed or refused. Make sure ADB debugging is enabled on the box (or run “adb tcpip 5555” once over USB).",
        "err_tls": "This device requires TLS pairing (Android 11+), which is not supported. The MXQ-4K uses classic ADB.",
        "err_auth": "Authorization denied on the box. Connect again and accept “Always allow” on the TV prompt.",
        "err_local_network": "If iOS asked about Local Network and you denied it, allow it in Settings > Privacy & Security > Local Network > MXQ Remote.",

        "help_title": "Prepare the box (one time only)",
        "help_intro": "Broken physical remote? No problem: plug a USB mouse into the box to do these steps.",
        "help_step_1": "Connect the iPhone and the box to the SAME Wi-Fi network (the box may be on Ethernet from the same router).",
        "help_step_2": "On the box: Settings > About > tap “Build number” 7 times to unlock Developer options.",
        "help_step_3": "In Developer options, enable “USB debugging” and, if present, “ADB over network” — this opens port 5555.",
        "help_step_4": "Note the box IP in Settings > Network (e.g. 192.168.0.123). Tip: reserve that IP in your router so it never changes.",
        "help_step_5": "In the app, type the IP and tap Connect. iOS will ask for “Local Network” permission — accept it.",
        "help_step_6": "If the firmware has no “ADB over network” toggle: connect the box to a computer over USB once and run “adb tcpip 5555”. It lasts until the box reboots.",
        "help_first_title": "First connection",
        "help_first_body": "On the first connection the TV shows “Allow USB debugging?” with this app's key fingerprint. Use the USB mouse, check “Always allow from this computer” and confirm. After that the app reconnects silently.",
        "help_trouble_title": "Troubleshooting",
        "help_trouble_body": "• Port 5555 closed: re-enable network ADB or run “adb tcpip 5555”.\n• IP changed: use “Scan network” and save the new IP (or pin the IP in the router).\n• No response: reboot the box; network ADB may turn off after a reboot.\n• Local Network permission denied: Settings > Privacy & Security > Local Network."
    ]
}
