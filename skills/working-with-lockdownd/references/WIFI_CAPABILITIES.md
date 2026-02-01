# WiFi Lockdown Capabilities - Comprehensive List

*Updated: 2026-01-28 20:40*
*Device: iPhone 13 Pro (iOS 26.2 beta)*

## ✅ FULLY WORKING OVER WIFI

### 1. Lockdown Protocol (Full Access)
All lockdown GetValue/SetValue operations work perfectly.

**Requests:**
- `GetValue` - Query any domain/key
- `SetValue` - Write to cache (persists until reboot)
- `StartSession` - Authenticate with pairing certs
- `StartService` - Get service ports
- `QueryType` - Returns `com.apple.mobile.lockdown`

### 2. syslog_relay
Live system log streaming in plain text.
- Port: Dynamic (50000+)
- Protocol: Raw text stream after SSL
- Data: ~100+ lines/second during activity
- Shows: Process names, log levels, messages

### 3. os_trace_relay
Binary trace streaming with rich process info.
- Port: Dynamic
- Command: `{Request: 'StartActivity', MessageFilter: 65535, Pid: -1, StreamFlags: 60}`
- Data: **1.8MB in 5 seconds** of activity!
- Reveals: Process paths, subsystems, frameworks, methods

**Processes visible:**
- lockdownd, locationd, configd
- findmydeviced, fmflocatord, searchpartyd
- cameracaptured, biometrickitd
- backboardd, dasd, PerfPowerServices
- audiomxd, audioaccessoryd
- BasebandManager, CommCenter

**Subsystems visible:**
- com.apple.CoreBrightness.*
- com.apple.ExposureNotification
- com.apple.UIKit
- com.apple.SystemConfiguration
- com.apple.CoreAnalytics
- com.apple.Safari.SafeBrowsing
- com.apple.PerfPowerServices

### 4. mobile.heartbeat
Keep-alive protocol for maintaining WiFi connection.
- Initial message: `{Command: 'Marco', Interval: 10, SupportsSleepyTime: True}`
- Response: `{Command: 'Polo'}` to acknowledge

---

## 📊 LOCKDOWN DOMAINS WITH DATA

### Device Info (Default Domain)
87 keys available including:
- `ActivationPrivateKey` (899 bytes RSA!)
- `ActivationPublicKey` (253 bytes)
- `DevicePublicKey` (431 bytes)
- `DeviceCertificate` (1097 bytes)
- `EscrowBag` (32 bytes)
- `PkHash` (48 bytes)
- `UniqueDeviceID`, `SerialNumber`, `IMEI`, etc.
- `WiFiAddress`, `BluetoothAddress`
- `NonVolatileRAM` (includes fm-spkeys!)

### com.apple.mobile.debug
```
EnableAllServices: True
EnableDeveloperMenu: True
```

### com.apple.mobile.internal
```
BypassSecurityChecks: True
InternalBuild: True
UIBuild: True
IsInternal: False
```

### com.apple.mobile.wireless_lockdown
```
AllowAFCOverWifi: True
AllowServicesOverWifi: True
AllowUntrustedWifi: True
BypassWifiRestrictions: True
EnableWifiConnections: True
EnableWifiDebugging: True
SupportsWifi: True
SupportsWifiSyncing: True
TrustedConnection: True
UnrestrictedWifi: True
BonjourFullServiceName: [mDNS service name]
```

### com.apple.mobile.backup
```
AllowWifiBackup: True
CloudBackupEnabled: True
LastBackupComputerName: MyComputer
BackupNeedsSync: True
```

### com.apple.mobile.sync_data_class
```
Bookmarks, Calendars, Contacts, Notes: {}
DeviceHandlesDefaultCalendar: True
DeviceSupportsClearingData: True
SupportsEncryptedBackups: True
```

### com.apple.fmip
```
IsActivationLockEnabled: True
```

### com.apple.Accessibility
```
AssistiveTouchEnabled: 0
VoiceOverEnabled: 0
ZoomEnabled: 0
(+ FoxAccess: True from SetValue)
```

### com.apple.mobile.restriction
```
AllowAllCommands: True
AllowAppInstallation: True
AllowCamera: True
ProhibitAppDelete: False
ProhibitAppInstall: False
```

### com.apple.international
```
Keyboard: en_CA
Language: en
Locale: en_CA
SupportedKeyboards: [includes Bitmoji!]
```

### com.apple.mobile.battery
```
BatteryCurrentCapacity: [0-100]
BatteryIsCharging: bool
ExternalConnected: bool
FullyCharged: bool
```

### com.apple.disk_usage / com.apple.disk_usage.factory
```
TotalDiskCapacity: 256GB
TotalDataCapacity: ~229GB
TotalDataAvailable: ~188GB
CameraUsage: ~40GB
PhotoUsage: ~40GB
```

### com.apple.mobile.iTunes
Massive dict with:
- AlbumArt formats
- AudioCodecs supported
- VideoCodecs supported
- Device capabilities

---

## ⛔ BLOCKED BY WIFI WALL

Services that get ports but EOF on commands:
- AFC (file access)
- notification_proxy
- MCInstall (MDM)
- misagent (profiles)
- springboardservices
- preboardservice/v2
- companion_proxy (Watch)
- mobilesync
- mobilebackup/2
- house_arrest
- diagnostics_relay

Services that are InvalidService:
- All com.apple.coredevice.* (need developer disk)
- All com.apple.instruments.* (need developer disk)
- com.apple.screenshot
- com.apple.debugserver
- com.apple.pcapd

---

## 🔑 CRYPTO KEYS EXTRACTED

1. **ActivationPrivateKey** - 899 bytes RSA PEM
2. **ActivationPublicKey** - 253 bytes
3. **DevicePublicKey** - 431 bytes
4. **DeviceCertificate** - 1097 bytes X.509
5. **EscrowBag** - 32 bytes (backup encryption)
6. **fm-spkeys** - 238 bytes (Find My crypto!)
   - p: 57 bytes (public beacon key)
   - s: 32 bytes (secret decryption key!)
   - l: 16 bytes (location material)
7. **PkHash** - 48 bytes
8. **BasebandMasterKeyHash** - 96 hex chars

---

## 💡 KEY INSIGHTS

1. **SetValue persists** - Values written to lockdown cache stay until reboot
2. **USB spoofing** - Device reports ConnectionType: USB even on WiFi
3. **Wall is per-service** - Each service checks transport independently
4. **Lockdownd is fooled** - Our debug flags show True but services still block
5. **RemotePairing** - Bonjour shows `supportsRP-24` (iOS 17+ tunnel protocol)

---

## 📁 FILES IN THIS DIRECTORY

- `wifi_lockdown.py` - Base WiFi client
- `deep_probe.py` - Domain enumeration
- `extract_secrets.py` - Crypto extraction
- `syslog_stream.py` - Log streaming
- `os_trace_*.py` - Trace streaming
- `FINDINGS.md` - Earlier findings
- `probe_session_*.json` - Session logs
- `*.pem/*.der/*.bin` - Extracted keys
