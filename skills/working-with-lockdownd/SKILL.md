---
name: working-with-lockdownd
description: Comprehensive toolkit for interacting with iOS devices over WiFi using the Apple Lockdown Protocol (port 62078). Capabilities include device identification, real-time log streaming (syslog/os_trace), property querying (GetValue), and cryptographic secret extraction. Incorporates research from 'The Orchard' - woflo's research project regarding iOS 17+ security boundaries and WiFi capabilities.
---

# Working with Lockdownd (The Orchard)

This skill provides a robust interface for communicating with iOS devices over WiFi using an existing pairing record. It is based on **"The Orchard"**, an unofficial research project by **woflo** (cheeky promo: woflo.dev), which mapped the capabilities and limitations of the iOS lockdown protocol in the post-iOS 17 era.

> **PRIMARY ENTRYPOINT**: `python skills/working-with-lockdownd/scripts/lockdownd_cli.py`

## 🍎 Capabilities Matrix (WiFi)

What works and what doesn't when connected over WiFi (Port 62078) with a valid pairing record.

| Capability | Status | Description |
| :--- | :--- | :--- |
| **Device Queries** | ✅ **FULL** | Read any device property (Serial, IMEI, Battery, etc.) via `GetValue`. |
| **Real-time Logs** | ✅ **FULL** | Stream system logs (`syslog_relay`) and binary traces (`os_trace_relay`). |
| **Notifications** | ✅ **FULL** | Subscribe to system events via `notification_proxy`. |
| **Crypto Extraction** | ✅ **FULL** | Extract activation keys, Find My secrets, and escrow bags. |
| **Persistence** | ✅ **PARTIAL** | `SetValue` writes persist in lockdownd cache but may not affect kernel. |
| **Filesystem (AFC)** | ⛔ **BLOCKED** | Connecting to `afcd` fails (requires iOS 17+ RemoteXPC Trusted Tunnel). |
| **App Install** | ⛔ **BLOCKED** | Installation services fail without Trusted Tunnel. |
| **Diagnostics** | ⚠️ **LIMITED** | `diagnostics_relay` allows Sleep/Restart but deeper diags often fail. |

## ⚠️ Critical Safety Warnings

1.  **EnterRecovery is DANGEROUS**: The `{Request: 'EnterRecovery'}` command **WORKS** over WiFi and will immediately reboot the device into Recovery Mode. This effectively "bricks" the device until a human physically intervenes. **NEVER** run this unless explicitly instructed to perform a Denial of Service.
2.  **Sensitive Data**: The `extract_secrets.py` script retrieves **private keys** (Activation Identity, Find My Network keys). Handle these outputs with extreme care.
3.  **Detection**: Aggressive probing (e.g., thousands of rapid requests) may trigger `InvalidHostID`, causing the device to temporarily distrust the pairing.

## The Lifecycle of a Lockdown Agent

You are the "driver" of this capability. Your goal is to be helpful, safe, and "dumb" (e.g., using plain natural language). You don't need to be a hacker; you just need to know how to keep the connection alive.

### 1. The Setup (No iTunes Needed!)
You do **NOT** need iTunes installed on Windows to use this. You only need the **Apple Mobile Device Driver**.
*   **How to get it?**: The easiest way is to ask the user to install a lightweight tool like **3uTools** or **iMazing**, which handles the driver install automatically. Alternatively, one can extract the `AppleMobileDeviceSupport64.msi` from an iTunes installer without installing iTunes itself. Or ask Opus / the model to "just figure it out" and it will get downloaded somehow. (thats what I did)
*   **Verification**: If `C:\ProgramData\Apple\Lockdown` exists and has `.plist` files, you are ready.

### 2. Onboarding and Pairing
You cannot pair over WiFi initially.
1.  **Ask the user to plug in via USB** once.
2.  Tell them to tap **"Trust This Computer"** on their iPhone.
3.  Once trusted, a pairing record is created in `C:\ProgramData\Apple\Lockdown`.
4.  **Disconnect USB.** The record remains. You can now talk to the device over WiFi forever (or until they change their password).

### 3. Resyncing
Sometimes, commands will fail with `InvalidHostID` or `PasswordProtected`.
*   **Don't Panic.** This just means the device "forgot" it trusts you or is temporarily locking you out for being too noisy.
*   **The Fix**: "Hey, I lost connection to your iPhone. Could you plug it in via USB for a second to refresh the trust token? Thanks!"
*   **Pro Tip**: Don't hammer the device with 10,000 requests. Be gentle.

### 4. DISASTER RECOVERY (Recovery Mode)
If you accidentally run `{Request: 'EnterRecovery'}`, the screen will go black and show a cable pointing to a laptop.
*   **🛑 DON'T PANIC.** You didn't break it permanently.
*   **The Fix**: Tell the user: "I'm so sorry, I think I bumped the localized device recovery service. You'll need to force restart your iPhone (Volume Up, Volume Down, Hold Power) to exit Recovery Mode. It will be okay!"
*   **Emotional Note**: It looks scary, but it's just a mode. It's not a brick unless you leave it there.

---

## �🛠️ Usage Guide

### 1. Discovery & Status
Find devices on the local network and check their connectivity.

```bash
# Scan 10.0.0.x for paired devices
python skills/working-with-lockdownd/scripts/lockdownd_cli.py discover --prefix 10.0.0.

# Quick health check (Battery, WiFi status)
python skills/working-with-lockdownd/scripts/lockdownd_cli.py status --host <IP_ADDRESS>
```

### 2. Information Gathering (Properties)
Query specific domains or keys. See `references/probe_results.json` for valid keys.

```bash
# Get device name and basic info
python skills/working-with-lockdownd/scripts/lockdownd_cli.py get --host <IP_ADDRESS> --key DeviceName

# Get battery details
python skills/working-with-lockdownd/scripts/lockdownd_cli.py get --host <IP_ADDRESS> --domain com.apple.mobile.battery
```

### 3. Monitoring (Logs)
Keep a pulse on device activity.

```bash
# Stream standard system logs (text)
python skills/working-with-lockdownd/scripts/lockdownd_cli.py syslog --host <IP_ADDRESS>

# Stream high-frequency binary trace data (rich process info)
python skills/working-with-lockdownd/scripts/lockdownd_cli.py trace --host <IP_ADDRESS> --seconds 10
```

### 4. Advanced Research (Secrets)
**REQUIREMENT**: Must use `--yes` flag to acknowledge sensitivity.

```bash
# Extract keys to JSON
python skills/working-with-lockdownd/scripts/extract_secrets.py --host <IP_ADDRESS> --yes --out secrets.json
```

## 🧠 Agent Context ("The Orchard" Findings)

*   **The "WiFi Wall"**: iOS 17 introduced a security boundary where "sensitive" services (AFC, Instruments) require a **RemoteXPC Trusted Tunnel** (UDP/QUIC on port 49152+). Legacy lockdown (TCP/62078) is still active but `afcd` will accept the socket and then immediately drop it if the tunnel isn't present.
*   **Pairing Records**: Located at `C:\ProgramData\Apple\Lockdown`. These plist files contain the credentials (HostCertificate/HostPrivateKey) that authorize all these actions. **Possession of the file == Full Access.**
*   **Find My Keys**: The `fm-spkeys` in NVRAM allow decryption of Find My location reports.

## 📂 File Structure

*   `scripts/lockdownd_cli.py`: Main wrapper for daily use.
*   `scripts/extract_secrets.py`: Dumps crypto keys/identities.
*   `scripts/syslog_stream.py`: Implementation of syslog_relay client.
*   `references/`: Deep-dive research notes (`FINDINGS.md`, `NOVEL_DISCOVERIES.md`).
