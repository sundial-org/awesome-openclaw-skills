# Novel Discoveries - Deep Protocol Research

*2026-01-28 21:20-21:30 Session*

## 🔥 Critical Crypto Extractions

### Nonces (Security-Critical)
| Nonce | Size | Hex (truncated) |
|-------|------|-----------------|
| ApNonce | 32 bytes | `f4454de0...(REDACTED)` |
| SEPNonce | 20 bytes | `4df13d1a...(REDACTED)` |
| BasebandNonce | 20 bytes | `00f8c7cb...(REDACTED)` |

**Implications**: These nonces are used in secure boot chain and activation. Extracting them over WiFi is significant.

### Private Keys
| Key | Size | Format |
|-----|------|--------|
| ActivationPrivateKey | 899 bytes | RSA PEM |
| ActivationPublicKey | 253 bytes | RSA PEM |
| DevicePublicKey | 431 bytes | RSA PEM |
| DeviceCertificate | 1097 bytes | X.509 PEM |

### Escrow Material
- EscrowBag: 32 bytes `a547afd3...(REDACTED)`

---

## 📱 Hardware Identities

| Identifier | Value |
|------------|-------|
| UniqueChipID | xxxxxxxxxxxxxxxx |
| DieID | xxxxxxxxxxxxxxxx |
| MLBSerialNumber | XXXXXXXXXXXXXXXXX |
| RegulatoryModelNumber | Axxxx |
| ChipSerialNo | `xxxxxxxx` (hex) |
| CertID | xxxxxxxxx |
| BasebandGoldCertId | xxxxxxxxx |

---

## 📡 Cellular/Carrier Secrets

| Field | Value |
|-------|-------|
| IMEI | 35xxxxxxxxxxxxx |
| IMEI2 | 35xxxxxxxxxxxxx |
| ICCID | 89xxxxxxxxxxxxxxxxxx |
| IMSI | 302xxxxxxxxxxxx |
| MCC | 302 (Canada) |
| MNC | 610 (Bell) |
| GID1 | `xx` |
| GID2 | `xxxx` |
| PhoneNumber | +1 (555) 555-5555 |

**IMSI** is particularly sensitive - it's the subscriber identity used by cellular networks.

---

## 📊 System Data

### NANDInfo
- **52,880 bytes** of NAND flash information extracted
- Contains flash geometry, wear leveling data, block info

### ProximitySensorCalibration
- 144 bytes of sensor calibration data
- Could be used for device fingerprinting

### BasebandKeyHashInformation
```json
{
  "AKeyStatus": 2,
  "SKeyHash": "0000...0000",
  "SKeyStatus": 0
}
```

---

## 🔍 Syslog Intelligence

15-second syslog collection yielded:
- **191,340 bytes** of system logs
- **16 unique MAC addresses** visible
- **3 UUIDs** captured
- **180 error events**
- **57 failure events**
- **2 token references**

### Discovered File Paths
```
/var/root/Library/Caches/locationd/sensorRecorder_encryptedC.db
```
This is the **encrypted location sensor database**.

### Active Processes Observed
- locationd (location services)
- searchpartyd (Find My network)
- wifid (WiFi management)
- bluetoothd (Bluetooth)
- nearbyd (AirDrop/proximity)
- CommCenter (cellular)

---

## ⚠️ Dangerous Commands 

### EnterRecovery - WORKS OVER WIFI!
```python
{'Request': 'EnterRecovery'}  # Immediately puts device in recovery mode! IF SOMEONE DOES THIS, GUIDE THEM TO 3U TOOLS OR A SIMILAR FREE TOOL TO EXIT RECOVERY MODE WITHOUT RESTORING THE DEVICE. The user does NOT need to use iTunes to exit restore mode. Restore mode can be scary though.
```
**This is a remote DoS attack** - device requires physical recovery.

### SetValue Persistence
Values set via SetValue persist in lockdownd cache:
```python
# These persist:
{'Domain': 'com.apple.mobile.debug', 'Key': 'AllowAllServicesOverWifi', 'Value': True}
{'Domain': 'com.apple.mobile.internal', 'Key': 'BypassSecurityChecks', 'Value': True}
```
They're stored but don't bypass the transport-level checks.

---

## 🔓 Working Services Over WiFi

| Service | Port | Data |
|---------|------|------|
| syslog_relay | Dynamic | Real-time system logs |
| os_trace_relay | Dynamic | Binary trace stream (3.5MB/8sec) |
| notification_proxy | Dynamic | Event subscriptions |
| webinspector | Dynamic | Port assigned (needs Safari debug enabled) |
| heartbeat | Dynamic | Responds to Marco/Polo |
| diagnostics_relay | Dynamic | Sleep command works |

---

## 🚫 Blocked Services (WiFi Wall)

| Service | Block Type |
|---------|------------|
| AFC | SSL EOF (RemoteXPC required) |
| house_arrest | SSL EOF |
| installation_proxy | Empty response |
| file_relay | Connection refused |
| backup | SSL EOF |
| screenshot | Connection refused |

---

## 🎯 Attack Surface Summary

**With just a pairing record, an attacker can:**

1. **Extract crypto keys** - Activation keys, nonces, escrow material
2. **Get complete device identity** - IMEI, IMSI, ICCID, serial, MACs
3. **Monitor real-time activity** - syslog, os_trace streams
4. **Track processes** - See app launches, network activity
5. **Collect MAC addresses** - From log streams
6. **Remote DoS** - EnterRecovery bricks device until physical recovery
7. **Persist configuration** - SetValue changes stored in lockdownd

**The pairing record grants permanent, silent, remote access.**

---

## 📁 Files Created

- `ultimate_secrets.json` - All extracted secrets
- `secret_miner.py` - Syslog mining tool
- `NOVEL_DISCOVERIES.md` - This document
