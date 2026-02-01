# Agent Capabilities - Working with Lockdownd
*(Based on "The Orchard" research by woflo)*

**Role**: You are an autonomous agent interacting with an iOS device over WiFi.
**Constraint**: You are limited to the "Lockdown Protocol" on port 62078.
**Context**: "The Orchard" research confirms that modern iOS (17+) blocks filesystem access over WiFi, but allows full monitoring and property queries.

## 🤖 Capabilities Boolean Matrix

Use this to determine if a user request is feasible.

```python
CAN_QUERY_DEVICE_INFO = True   # Serial, IMEI, Battery, etc.
CAN_STREAM_LOGS       = True   # syslog, os_trace (Real-time)
CAN_EXTRACT_SECRETS   = True   # Activation keys, Find My tokens (SENSITIVE)
CAN_INSTALL_APPS      = False  # BLOCKED by WiFi Wall
CAN_TRANSFER_FILES    = False  # BLOCKED by WiFi Wall
CAN_REBOOT_DEVICE     = True   # Via diagnostics_relay (Restart/Sleep)
CAN_BRICK_DEVICE      = True   # EnterRecovery (DANGEROUS usage)
```

## ⌨️ Command Cheat Sheet

Always use the CLI wrapper which outputs JSON designed for machine consumption.

| Goal | Command | Output Key to Parse |
| :--- | :--- | :--- |
| **Check Connectivity** | `python .../lockdownd_cli.py status --host <IP>` | `battery`, `DeviceName` |
| **Find Devices** | `python .../lockdownd_cli.py discover --prefix 10.0.0.` | `found` (Array of objects) |
| **Get Serial/IMEI** | `python .../lockdownd_cli.py get --host <IP> --key SerialNumber` | `Value` |
| **Monitor Activity** | `python .../lockdownd_cli.py trace --host <IP> --seconds 5` | (Binary stream, check exit code) |
| **Extract Secrets** | `python .../extract_secrets.py --host <IP> --yes` | (JSON Object with keys) |

## 🧠 Decision Logic

### Scenario 1: User asks "What files are on the iPhone?"
*   **Action**: CHECK `CAN_TRANSFER_FILES`.
*   **Result**: `False`.
*   **Response**: "I cannot list files over WiFi. iOS 17+ restricts AFC (Apple File Conduit) to trusted USB tunnels only. I can, however, query device properties or stream logs."

### Scenario 2: User asks "Is the device being used right now?"
*   **Action**: CHECK `CAN_STREAM_LOGS`.
*   **Result**: `True`.
*   **Strategy**: Run `lockdownd_cli.py trace --seconds 5`.
*   **Analysis**: Look for "backboardd" (touch events), "SpringBoard" (app launches), or "wcd" (WiFi changes) in the output stream.

### Scenario 3: User asks "Get the Find My decryption key"
*   **Action**: CHECK `CAN_EXTRACT_SECRETS`.
*   **Result**: `True`.
*   **Warning**: This is highly sensitive.
*   **Execution**: Call `extract_secrets.py` with `--yes`.
*   **Output**: Parse JSON for `NVRAM['fm-spkeys']['s']`.

## 🛑 Error Handling

*   **`ConnectionRefusedError`**: Device is likely offline or not at that IP. Run `discover`.
*   **`InvalidService` / `SSL EOF`**: You hit the "WiFi Wall". The service you requested (`com.apple.afc`, etc.) requires a trusted tunnel. **Do not retry**; it will never work over this port.
*   **`InvalidHostID`**: The device has temporarily blocked this pairing record due to aggressive probing. Wait 5 minutes.
