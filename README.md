# ShareToMac

Stream your iPhone or iPad screen to your Mac over a local Wi-Fi network.

No cables required. The iOS app captures the screen using ReplayKit and sends
JPEG frames over UDP. The Mac app receives and displays them in real time with PyQt6.

```
share-to-mac/
├── .github/workflows/     # CI: builds .dmg and unsigned .ipa on every release tag
├── mobile/                # React Native app (iOS) + Swift native module
├── desktop/               # Python + PyQt6 receiver app for macOS
└── docs/
    └── INSTALL_IOS.md     # How to self-sign and install the iOS app
```

---

## Download (pre-built)

Go to the [Releases](../../releases) page and download:

| File | Platform |
|------|----------|
| `ShareToMac.dmg` | macOS — drag to Applications and run |
| `ShareToMac-unsigned.ipa` | iOS — requires self-signing (see below) |

**iOS install instructions**: [docs/INSTALL_IOS.md](docs/INSTALL_IOS.md)  
The easiest method is **AltStore** — free, no paid Apple account needed.

---

## Build from source

### Requirements

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Xcode | 15+ |
| Ruby | 3.0+ |
| CocoaPods | 1.13+ |
| Python | 3.11+ |
| macOS | 13 Ventura+ |

Both devices must be on the **same Wi-Fi network**.

---

### Desktop App (Mac)

```bash
cd desktop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The window shows your Mac's local IP address and a port selector (default `5005`).  
Click **Start Listening** before launching the mobile app.

---

### Mobile App (iPhone / iPad)

```bash
cd mobile

# Install JS dependencies
npm install

# Install Ruby gems (xcodeproj + CocoaPods)
bundle install

# Add the ScreenCapture Swift files to the Xcode project automatically
bundle exec ruby scripts/setup_xcode.rb

# Install CocoaPods
cd ios && bundle exec pod install && cd ..
```

#### Run directly on device (development)

```bash
npx react-native run-ios --device "Your iPhone Name"
```

> Screen recording does **not** work on the iOS Simulator. A physical device is required.

#### Build for distribution (sign in Xcode)

1. `open ios/ShareToMac.xcworkspace`
2. Select the `ShareToMac` target → **Signing & Capabilities** → choose your Team.
3. Change the Bundle Identifier to something unique (e.g. `com.yourname.sharetomac`).
4. Select your device, press **Run** (▶).

See [docs/INSTALL_IOS.md](docs/INSTALL_IOS.md) for full signing instructions.

---

## Usage

1. On your Mac, open the desktop app → click **Start Listening**.
2. Note the IP address shown (e.g. `192.168.1.42`).
3. On your iPhone/iPad, open ShareToMac.
4. Enter the Mac IP address → tap **Start Sharing**.
5. Accept the screen recording permission prompt.

Your screen appears on the Mac within a second or two.

---

## Architecture

```
[iPhone/iPad]
  ReplayKit → ScreenCaptureManager (Swift)
    → UDPSender (Swift / Network.framework)
      → UDP datagrams (JPEG frames, chunked at 1400 bytes)

[MacBook]
  UDPReceiver (Python) → reassembles chunks → JPEG bytes
    → FrameDisplay (PyQt6 QLabel) → rendered on screen
```

### UDP chunking protocol

Each datagram carries a 12-byte big-endian header:

| Field | Type | Bytes |
|-------|------|-------|
| `frameId` | uint32 | 4 |
| `chunkIndex` | uint16 | 2 |
| `totalChunks` | uint16 | 2 |
| `chunkSize` | uint32 | 4 |

Followed by the raw JPEG chunk payload.

---

## CI

Two GitHub Actions workflows run on every `v*` tag push:

| Workflow | Output |
|----------|--------|
| `build-desktop.yml` | `ShareToMac.dmg` attached to the GitHub Release |
| `build-mobile.yml` | `ShareToMac-unsigned.ipa` attached to the GitHub Release |

Trigger a release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Limitations

- The iOS app must remain in the **foreground** while sharing (ReplayKit restriction).
- Frames may be dropped on a congested network — acceptable for live mirroring.
- Apps self-signed with a free Apple ID expire every 7 days (AltStore can auto-refresh).
- USB cable transport is not implemented yet.

---

## Roadmap

- [ ] Auto-discover the Mac via mDNS (no manual IP entry)
- [ ] USB cable transport via `usbmuxd`
- [ ] Adjustable JPEG quality / resolution
