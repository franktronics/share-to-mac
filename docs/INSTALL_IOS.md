# Installing the iOS App

The `.ipa` distributed on the GitHub Releases page is **unsigned**.  
Apple requires every iOS app to be signed with a personal certificate before installation.

You have two options:

---

## Option A — AltStore (recommended, no Apple Developer account needed)

AltStore re-signs the app with your personal Apple ID certificate for free.  
The app must be refreshed every 7 days (AltStore can do this automatically in the background).

### 1. Install AltStore on your Mac

1. Download AltServer from **[altstore.io](https://altstore.io)**.
2. Open AltServer — a diamond icon appears in your Mac menu bar.
3. Connect your iPhone/iPad via USB.
4. Click the AltServer menu bar icon → **Install AltStore** → select your device.
5. Enter your Apple ID when prompted (a free Apple ID is enough).
6. On your iPhone: **Settings → General → VPN & Device Management** → trust the certificate.

### 2. Install ShareToMac via AltStore

1. Download `ShareToMac-unsigned.ipa` from the [Releases page](../../releases).
2. With your iPhone still connected (or on the same Wi-Fi as your Mac running AltServer):
   - Open AltStore on your iPhone.
   - Tap the **+** button (My Apps tab) → select the downloaded `.ipa`.
3. The app will be signed and installed automatically.

### Refreshing the app (every 7 days)

AltStore can refresh apps automatically if:
- Your iPhone and Mac are on the same Wi-Fi.
- AltServer is running in the background on your Mac.

Or refresh manually: open AltStore → long-press ShareToMac → **Refresh**.

---

## Option B — Compile from source with Xcode (free Apple ID)

This method signs the app directly on your device. No 7-day limit, but requires Xcode.

### Requirements

- macOS with Xcode 15+ installed (free from the App Store)
- A free Apple ID (no paid Developer account needed)
- Node.js 18+, Ruby 3+, CocoaPods

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/share-to-mac.git
cd share-to-mac/mobile

# 2. Install dependencies
npm install
bundle install
bundle exec ruby scripts/setup_xcode.rb   # adds Swift files to Xcode project
cd ios && bundle exec pod install && cd ..

# 3. Open in Xcode
open ios/ShareToMac.xcworkspace
```

In Xcode:

1. Select the `ShareToMac` project in the navigator.
2. Under **Signing & Capabilities** → **Team**, sign in with your Apple ID and select your personal team.
3. Change the **Bundle Identifier** to something unique, e.g. `com.yourname.sharetomac`.
4. Connect your iPhone/iPad, select it as the build destination.
5. Press **Run** (▶).

The app will be installed and trusted automatically.

> **Note:** Apps signed with a free Apple ID expire after 7 days and must be re-built.

---

## Trusting the developer certificate (both methods)

After installing for the first time, iOS may block the app with "Untrusted Developer":

1. Go to **Settings → General → VPN & Device Management**.
2. Find your Apple ID or developer name under **Developer App**.
3. Tap **Trust** → confirm.

The app will now open normally.
