# The Orchard Project 🍎

**iOS WiFi Sync Security Research**

> ⚠️ **WARNING**: Some lockdown commands have immediate device effects!
> `EnterRecovery` works over WiFi and WILL brick your device until physically recovered. This was discovered the hard way, let's not do it again.
> Always use read-only probing first.

Research into what's accessible on a paired iOS device over WiFi without user interaction.

## Quick Summary

Using only an existing pairing record (from previous iTunes/Finder sync), we can:

| Capability | Status | Notes |
|------------|--------|-------|
| Device fingerprint | ✅ Full | UDID, serial, IMEI, MACs, carrier info |
| Crypto key extraction | ✅ Full | Activation keys, Find My keys, escrow |
| System log streaming | ✅ Real-time | syslog_relay, os_trace_relay |
| Event subscription | ✅ Works | notification_proxy |
| Filesystem access | ❌ Blocked | AFC requires iOS 17 trusted tunnel |
| App installation | ❌ Blocked | Requires trusted tunnel |
| Screenshots | ❌ Blocked | Requires trusted tunnel |

## The iOS 17 Wall

Apple restructured device communication in iOS 17:

```
WiFi Connection (us)          USB Connection
       │                            │
       ▼                            ▼
   Port 62078                  USB Ethernet
   Legacy Lockdown                  │
       │                            ▼
       │                      Port 58783 (QUIC)
       │                      RemoteXPC RSD
       │                            │
       │                            ▼
       │                      SRP Pairing
       │                      (password: 000000)
       │                            │
       │                            ▼
       ▼                      Trusted QUIC Tunnel
   Limited Access             (TUN device)
   - Queries ✓                      │
   - Logs ✓                         ▼
   - AFC ✗                    Full Access
   - Install ✗                - AFC ✓
                              - Install ✓
                              - Debug ✓
```

## Files

| File | Description |
|------|-------------|
| `FINDINGS.md` | Complete technical findings |
| `WIFI_CAPABILITIES.md` | Service-by-service breakdown |
| `os_trace_analysis.md` | Real-time monitoring analysis |
| `extracted_secrets.json` | Extracted cryptographic material |
| `deep_results.json` | Full probe results |
| `activation_private.pem` | ⚠️ Device activation private key |
| `fm_spkeys.bin` | ⚠️ Find My network keys |
| `*.py` | Probe scripts |

## Key Discoveries

### 1. Crypto Extraction
- Activation private key (RSA)
- Find My beacon keys (can track/spoof device location)
- Escrow bag material
- Baseband master key hash

### 2. os_trace Monitoring
- 3.5MB/8sec of system activity
- 34+ processes visible
- 158+ subsystems
- See: WiFi connections, Bluetooth pairing, app activity, security decisions

### 3. iOS 17 Architecture
- New RemoteXPC stack over QUIC
- Trusted tunnel required for sensitive services
- Legacy lockdown still works for diagnostics
- SRP pairing with hardcoded password

## Research Value

This demonstrates the attack surface of iOS WiFi sync:
- **Pairing record = full credential** (stored in `C:\ProgramData\Apple\Lockdown\`)
- Any computer with the pairing record can query the device
- Real-time system monitoring without user knowledge
- Cryptographic secrets accessible over network

## Latest Findings (2026-01-28)

- **SetValue persistence**: Can write arbitrary domain values (JailbreakMode, DisableAMFI, etc.) - they persist but don't affect kernel
- **ConnectionType spoofing**: Can make lockdownd report USB connection over WiFi
- **Security lockout**: Aggressive probing triggers InvalidHostID (device detects abuse)
- **AMFI tracing**: Observed amfid behavior via os_trace - same WiFi wall pattern

See `MAGIC_HUNT.md` for detailed session notes.

## Requirements

- Windows/macOS with existing iOS pairing
- iPhone on same WiFi network
- Python 3.x
- Device UDID (from pairing plist filename)

## Legal Notice

This research is for educational purposes. Only test on devices you own.
