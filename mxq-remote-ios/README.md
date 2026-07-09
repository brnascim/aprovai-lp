# MXQ Remote — iOS remote control for the MXQ-4K Android TV box

A native iOS app (SwiftUI, iOS 16+) that replaces the broken IR remote of an
MXQ-4K / OTT TV BOX by controlling it **over the local Wi-Fi network** using
**ADB (Android Debug Bridge) on TCP port 5555**. No cloud, no accounts, no
paid services — everything stays on your LAN.

> iPhones have no IR blaster, so emulating the original IR remote is
> physically impossible. ADB over Wi-Fi injects input events at the Android
> system level (`input keyevent / tap / swipe / text`), which works on any
> app or launcher, needs no root, and gives features the IR remote never had
> (trackpad and text input).

## Features

- **D-pad + OK**, Back / Home / Menu / Recents, volume rocker + mute, Power
- **Media transport** (rew, play/pause, ff, prev/next) and numeric keypad
- **Trackpad mode**: absolute mapping of the touch area to the TV screen
  (resolution auto-discovered via `wm size`, falls back to 1920×1080);
  tap = click, drag = swipe
- **Text input**: types into the focused field on the box (`input text`)
- **Device discovery**: scans the local /24 subnet for open port 5555
- **Persistent ADB auth**: RSA-2048 key generated on first run and stored in
  the iOS Keychain; after the first authorization the app reconnects silently
- **Auto-reconnect** with exponential backoff + shell keep-alive heartbeat
- **Low latency**: a single persistent `shell:` stream stays open and each
  button press is one TCP write (no per-key stream setup), TCP_NODELAY on
- UI in Brazilian Portuguese with an English toggle, dark theme, haptics

## Project layout

```
mxq-remote-ios/
├── MXQRemote.xcodeproj        # Xcode project (Xcode 16+, uses synchronized folders)
├── MXQRemote/                 # iOS app target (SwiftUI, MVVM)
│   ├── MXQRemoteApp.swift     # entry point + root view
│   ├── RemoteController.swift # top-level view model (connection, devices, actions)
│   ├── AppSettings.swift      # preferences + PT/EN localization table
│   ├── Services/
│   │   ├── NWTransport.swift      # ADBTransport over Network.framework (TCP 5555)
│   │   ├── KeychainSigner.swift   # ADBSigner: RSA-2048 in the Keychain (SecKey)
│   │   ├── SubnetScanner.swift    # /24 scan for port 5555
│   │   ├── DeviceStore.swift      # saved devices (UserDefaults)
│   │   └── Haptics.swift
│   └── Views/                 # Connection, Remote, D-pad, Numpad, Trackpad,
│                              # Text input, Settings, Help
└── ADBCore/                   # Platform-neutral Swift package: the ADB protocol
    ├── Sources/ADBCore/
    │   ├── ADBMessage.swift       # 24-byte framing, checksums, incremental reader
    │   ├── ADBConnection.swift    # CNXN/AUTH handshake + stream multiplexing (actor)
    │   ├── ADBTransport.swift     # transport/signer abstractions
    │   ├── ADBPublicKey.swift     # mincrypt RSA public key encoding (n0inv, rr)
    │   ├── BigUInt32.swift        # minimal bignum (2^k mod n, -n^-1 mod 2^32)
    │   ├── DERParser.swift        # PKCS#1 RSAPublicKey DER parsing
    │   ├── AndroidKey.swift       # Android KeyEvent codes
    │   └── RemoteCommand.swift    # shell command builders + wm size parsing
    └── Tests/ADBCoreTests/    # unit tests (framing, crypto encoding, commands,
                               # full scripted handshake against a fake transport)
```

`ADBCore` has zero external dependencies and no Apple-only APIs, so its tests
also run on Linux/macOS with plain `swift test`.

## Build & run

1. Open `MXQRemote.xcodeproj` in **Xcode 16 or newer** (the project uses
   file-system-synchronized groups).
2. Select the *MXQRemote* scheme, set your development team under
   *Signing & Capabilities* (bundle id defaults to `com.example.mxqremote`
   — change it to something unique).
3. Run on a real iPhone (iOS 16+). The simulator builds and runs, but you
   need a device on the same Wi-Fi as the box for real control.

Run the protocol unit tests either from Xcode (the ADBCore package tests) or:

```bash
cd ADBCore && swift test
```

## One-time setup on the box (documented in-app under "Ajuda")

Since the physical remote is broken, plug a **USB mouse** into the box to
navigate these steps:

1. Put the iPhone and the box on the **same network** (box may be on Ethernet
   from the same router).
2. On the box: *Settings > About* → tap **Build number 7 times** to unlock
   Developer options.
3. In *Developer options*, enable **USB debugging** and, if present,
   **ADB over network / Network ADB** (opens TCP port 5555).
4. Note the box IP under *Settings > Network* (e.g. `192.168.0.123`).
   Tip: reserve that IP in your router (DHCP reservation) so it never changes.
5. If the firmware has **no** "ADB over network" toggle: connect the box to a
   computer over USB once and run `adb tcpip 5555`. This persists until the
   box reboots.

### First connection

Enter the IP in the app and tap **Conectar**. iOS asks for **Local Network**
permission — accept it. The TV then shows *"Allow USB debugging?"* with the
app's key fingerprint: use the USB mouse, check **"Always allow from this
computer"** and confirm. From then on the app authenticates silently with the
key stored in the Keychain.

## How it works (protocol notes)

- **Framing**: every ADB message is a 24-byte little-endian header
  (`command, arg0, arg1, length, checksum, magic`) + payload. The legacy
  "CRC" field is actually a byte-wise sum; `magic = command XOR 0xFFFFFFFF`.
- **Handshake**: the app sends `CNXN` (version `0x01000000`, banner
  `host::features=cmd,shell_v2`). The box replies `AUTH(TOKEN)` with a
  20-byte challenge. The app signs it (RSA PKCS#1 v1.5 over the raw token as
  a SHA-1 digest — `SecKeyCreateSignature(.rsaSignatureDigestPKCS1v15SHA1)`)
  and replies `AUTH(SIGNATURE)`. If the key is unknown the box challenges
  again; the app then sends `AUTH(RSAPUBLICKEY)` with the base64
  mincrypt-encoded key (`len, n0inv, n[64], rr[64], exponent` + ` user@host`)
  which triggers the on-screen authorization dialog. After acceptance the box
  issues a fresh token, the signature verifies, and `CNXN` completes the
  session.
- **Commands**: a persistent `shell:` stream is opened once; every action is
  `WRTE "<command>\n"` on it (OKAY-acked). Commands whose output matters
  (`wm size`) use a one-shot `shell:<cmd>` stream collected until `CLSE`.
- **Keep-alive**: a `:` no-op is written every 20 s; if the TCP link dies the
  reader loop surfaces it and the controller reconnects with backoff
  (1, 2, 4, 8, 16 s; up to 5 attempts).

### Key mappings (Android `KeyEvent`)

| Action | Code | Action | Code |
|---|---|---|---|
| DPAD UP/DOWN | 19/20 | VOLUME +/− | 24/25 |
| DPAD LEFT/RIGHT | 21/22 | MUTE | 164 |
| OK (DPAD_CENTER) | 23 | POWER (standby) | 26 |
| BACK / HOME / MENU | 4 / 3 / 82 | PLAY-PAUSE | 85 |
| RECENTS | 187 | NEXT/PREV | 87/88 |
| ENTER / DEL | 66 / 67 | FF/REW | 90/89 |
| Digits 0–9 | 7–16 | | |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Timeout connecting | Same Wi-Fi? Correct IP? Network ADB enabled? |
| Port 5555 refused | Re-enable ADB over network, or run `adb tcpip 5555` once via USB (resets on reboot) |
| Authorization dialog never appears | It's behind the current app on the TV — press Home with the USB mouse; or the key was previously denied: regenerate the key in Settings |
| Worked, then stopped after reboot | `adb tcpip 5555` does not persist on some firmwares — redo step 5 |
| IP changed | Use "Procurar na rede" (scan) and save the new IP; pin the IP in the router |
| iOS Local Network denied | Settings > Privacy & Security > Local Network > MXQ Remote |
| Device requires TLS pairing | Android 11+ boxes use ADB pairing, out of scope here (the MXQ-4K is Android 7 and uses classic ADB) |

## Security & privacy

- The RSA private key lives in the iOS **Keychain** and never leaves the app.
- Nothing leaves the LAN; there is no telemetry, cloud or account.
- No root required on the box — the standard `shell` user can inject input.
- Note that classic ADB (pre-Android 11) is unauthenticated-then-authorized
  plain TCP; only enable network ADB on networks you trust.

## Non-goals

- IR emulation (no IR hardware on iPhones)
- Google's Android TV Remote protocol v2 (ports 6466/6467) — MXQ boxes run
  plain AOSP without the Android TV Remote Service, so it is not the primary
  path; it could be added later as an optional fallback
- Bluetooth HID pairing, media playback, rooting the box
