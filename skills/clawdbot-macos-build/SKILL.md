---
name: clawdbot-macos-build
description: Build the Clawdbot macOS menu bar app from source. Use when you need to install the Clawdbot.app companion (for menu bar status, permissions, and Mac hardware access like camera/screen recording). Handles dependency installation, UI build, Swift compilation, code signing, and app packaging automatically.
---

# Clawdbot macOS App Build

The macOS companion app provides menu-bar status, native notifications, and access to Mac hardware (camera, screen recording, system commands). This skill builds it from source.

## Prerequisites

- macOS (10.14+)
- Xcode 15+ with Command Line Tools
- Node.js >= 22
- pnpm package manager
- 30+ GB free disk space (Swift build artifacts)
- Internet connection (large dependencies)

## Quick Build

```bash
# Clone repo
cd /tmp && rm -rf clawdbot-build && git clone https://github.com/clawdbot/clawdbot.git clawdbot-build

# Install + build
cd /tmp/clawdbot-build
pnpm install
pnpm ui:build

# Accept Xcode license (one-time)
sudo xcodebuild -license accept

# Build macOS app with ad-hoc signing
ALLOW_ADHOC_SIGNING=1 bash scripts/package-mac-app.sh

# Install to /Applications
cp -r dist/Clawdbot.app /Applications/Clawdbot.app

# Launch
open /Applications/Clawdbot.app
```

## Build Steps Explained

### 1. Clone Repository
Clones the latest Clawdbot source from GitHub. This includes the macOS app source in `apps/macos/`.

### 2. Install Dependencies (pnpm install)
Installs Node.js dependencies for the entire workspace (~1 minute). Warnings about missing binaries in some extensions are harmless.

### 3. Build UI (pnpm ui:build)
Compiles the Control UI (Vite → TypeScript/React). Output goes to `dist/control-ui/`. Takes ~30 seconds.

### 4. Accept Xcode License
Required once per Xcode update. If you get "license not agreed" errors during Swift build, run:
```bash
sudo xcodebuild -license accept
```

### 5. Package macOS App (scripts/package-mac-app.sh)
Runs the full Swift build pipeline:
- Fetches Swift package dependencies (SwiftUI libraries, etc.)
- Compiles the macOS app for your architecture (arm64 for M1+, x86_64 for Intel)
- Bundles resources (model catalog, localizations, etc.)
- Code-signs the app

**Signing options:**
- **Ad-hoc signing** (fastest): `ALLOW_ADHOC_SIGNING=1` — good for local testing, app won't notarize for distribution
- **Developer ID signing** (production): Set `SIGN_IDENTITY="Developer ID Application: <name>"` if you have a signing certificate

This step takes 10-20 minutes depending on your Mac.

### 6. Install to /Applications
Copies the built app to the system Applications folder so it runs like any other macOS app.

### 7. Launch
Opens the app. On first run, you'll see permission prompts (Notifications, Accessibility, Screen Recording, etc.) — approve them for full functionality.

## Troubleshooting

### "Invalid tools version"
Swift build requires 6.2+. Update Xcode:
```bash
softwareupdate -i -a
```

### "License not agreed"
```bash
sudo xcodebuild -license accept
```

### "No signing identity found"
Use ad-hoc signing for local builds:
```bash
ALLOW_ADHOC_SIGNING=1 bash scripts/package-mac-app.sh
```

### Swift compilation hangs or is very slow
- Ensure Xcode is fully updated: `xcode-select --install` or update via App Store
- Check disk space: `df -h` (need ~30GB free)
- Close other apps to free RAM

### App won't launch after build
Check that it's properly signed:
```bash
codesign -v /Applications/Clawdbot.app
```

If signing failed, rebuild with `ALLOW_ADHOC_SIGNING=1`.

## What the App Does

- **Menu bar status** — See Gateway health and receive notifications
- **Permission management** — Owns TTC prompts for Notifications, Accessibility, Screen Recording, Microphone, etc.
- **Local/Remote modes:**
  - **Local:** Gateway runs on your Mac; app manages launchd service
  - **Remote:** App connects to Gateway on another machine (VPS, home server) via SSH/Tailscale; keeps your Mac accessible even while sleeping
- **Mac hardware access:** Camera, screen recording, Canvas, voice wake-word
- **Deep linking:** Trigger agent requests via `clawdbot://` URL scheme

See the official docs: https://docs.clawd.bot/platforms/macos

## Building for Distribution

For production distribution, you'll need:
- Apple Developer ID certificate (paid)
- Notarization credentials
- See: https://docs.clawd.bot/platforms/mac/release

For personal use, ad-hoc signing is fine.

## Next Steps

After the app launches:
1. Complete the permission checklist (TCC prompts)
2. Choose **Local** or **Remote** mode
3. If Local: ensure the Gateway is running (`clawdbot gateway status`)
4. Open Clawdbot.app menu bar icon to configure

Then from the terminal, you can manage the Gateway:
```bash
clawdbot gateway status
clawdbot gateway restart
```
