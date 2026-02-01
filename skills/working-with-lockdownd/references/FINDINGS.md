# The Orchard - WiFi Lockdown Findings 🍎

> ⚠️ **DANGER ZONE WARNING** ⚠️
> 
> The `EnterRecovery` command **WORKS over WiFi** and will immediately put the device into recovery mode!
> ```python
> # DO NOT SEND THIS - IT WORKS!
> {'Request': 'EnterRecovery'}  # Device instantly enters recovery mode
> ```
> Recovery mode requires physical intervention to exit (force restart or iTunes).
> Be extremely careful when probing lockdown commands - some have immediate, disruptive effects.

## Executive Summary

**Over WiFi, without user interaction, using only an existing pairing record:**

We extracted **cryptographic private keys**, **Find My network secrets**, and **complete device fingerprints**.

---

## 🔑 Critical Crypto Extractions

### 1. Activation Private Key
```
File: activation_private.pem
Size: 899 bytes (PEM format)
Type: RSA Private Key
```
**Impact**: This is the device's activation identity key. With this:
- Could potentially clone device identity for activation servers
- May enable activation lock bypass research
- Device impersonation scenarios

### 2. Find My Network Keys (fm-spkeys)
```
File: fm_spkeys.bin (238 bytes plist)

Extracted:
  p (Public):  57 bytes - Beacon broadcast key
  s (Secret):  32 bytes - DECRYPTION KEY for Find My data!
  l (Location): 16 bytes - Location material
  i (Index):   1
  b (Birth):   2024-xx-xx xx:xx:xx
```
**Impact**: These are the actual cryptographic keys for Apple's Find My network:
- **s (secret key)**: Can decrypt Find My location reports
- **p (public key)**: The beacon that AirTags/devices broadcast
- Could track device through Find My network
- Could spoof device's Find My presence

### 3. EscrowBag
```
32 bytes: 7af75c4af16217bb... (REDACTED)
```
**Impact**: Used for backup encryption key escrow

### 4. Baseband Master Key Hash
```
96 hex chars: 1B41607650EB... (REDACTED)
```

---

## 📱 Device Fingerprint (Complete)

| Field | Value |
|-------|-------|
| UDID | 00008110-xxxxxxxxxxxxxxxx |
| Serial | XXXXXXXXXX |
| IMEI | 35xxxxxxxxxxxxx |
| IMEI2 | 35xxxxxxxxxxxxx |
| Phone | +1 (555) 555-5555 |
| WiFi MAC | 88:b9:45:xx:xx:xx |
| Bluetooth | 88:b9:45:xx:xx:xx |
| Ethernet | 88:b9:45:xx:xx:xx |
| DieID | xxxxxxxxxxxxxxxx |
| ChipID | 33040 |
| MLB Serial | XXXXXXXXXXXXXXXXX |
| Carrier | Carrier Name |
| ICCID | 89xxxxxxxxxxxxxxxxxx |
| IMSI | 302xxxxxxxxxxxx |

---

## 📡 Working Services Over WiFi

| Service | Status | Data |
|---------|--------|------|
| Lockdown GetValue | ✅ FULL | 89+ keys, all domains |
| syslog_relay | ✅ STREAMING | Live OS logs |
| os_trace_relay | ✅ STREAMING | Modern tracing with process/subsystem info |
| notification_proxy | ✅ SUBSCRIBE | Event subscriptions |

### os_trace_relay Achievements
- **Binary stream mode** activated with StartActivity
- **3.5MB in 8 seconds** of trace data
- **34+ processes** visible: backboardd, lockdownd, afcd, mDNSResponder, locationd, bluetoothd, sharingd, searchpartyd, wifid, geod, etc.
- **158+ subsystems**: com.apple.CoreBrightness, com.apple.WiFiManager, com.apple.WiFiPolicy, com.apple.PerfPowerServices, etc.
- **Real-time activity**: Bluetooth scanning, WiFi management, Find My beacons, location services

### os_trace Deep Analysis (2026-01-28)

**Visible Processes:**
```
/usr/libexec/lockdownd
/usr/libexec/afcd
/usr/libexec/PerfPowerServices
/usr/libexec/aonsensed
/usr/libexec/audioaccessoryd
/usr/libexec/backboardd
/usr/libexec/biometrickitd
/usr/libexec/bulletindistributord
/usr/libexec/cameracaptured
/usr/libexec/thermalmonitord
/usr/sbin/WirelessRadioManagerd
```

**WiFi Subsystems:**
- `com.apple.WiFiManager`
- `com.apple.WiFiPolicy`
- `com.apple.wifip`

**Security Patterns Observed:**
| Pattern | Count | Significance |
|---------|-------|--------------|
| wifi | 1377 | WiFi stack activity |
| session | 329 | Active sessions |
| pair | 164 | Pairing operations |
| trust | 104 | Trust evaluations |
| codesign | 35 | Code signature checks |
| sandbox | 14 | Sandbox extensions |
| lockdown | 4 | Lockdown decisions |

**XPC Endpoints Visible:**
- `aonsensed.xpc` (always-on sensors)
- `com.apple.afcd` (AFC daemon)
- Various lockdown peers

**MagicPairing (Bluetooth):**
```
WPPairingKeyName: Unknown
WPPairingKeyDeviceTime: 791343986
WPPairingKeyAdvertisingChannel: 39
WPPairingKeyRSSI: -78
```

This is essentially a **monitoring backdoor** into the entire iOS system.

### Services Blocked (WiFi Wall)
- AFC (file access) - Connection refused
- file_relay - Connection refused  
- diagnostics_relay - SSL EOF after connect
- installation_proxy - Empty response
- Most instrument services - SSL EOF

---

## 🔒 NVRAM Secrets

| Key | Value |
|-----|-------|
| fm-account-masked | user@example.com |
| fm-activation-locked | YES |
| fm-spstatus | YES |
| boot-args | (empty) |
| obliteration | EACS Done @xxxxxxxxxx |

---

## The WiFi Wall - EXPLAINED (iOS 17+)

### Architecture Discovery
iOS 17 fundamentally changed the device communication stack:

```
┌─────────────────────────────────────────────────────────┐
│                  iOS 17 RemoteXPC Stack                 │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Service Access (AFC, dev tools, etc.)         │
│     ↑ Requires: com.apple.mobile.lockdown.remote.trusted│
├─────────────────────────────────────────────────────────┤
│  Layer 3: Trusted QUIC Tunnel (TUN device: utun3, etc.) │
│     ↑ Created after SRP pairing succeeds                │
├─────────────────────────────────────────────────────────┤
│  Layer 2: RemotePairing (SRP, password: "000000")       │
│     ↑ Requires USB Ethernet connection                  │
├─────────────────────────────────────────────────────────┤
│  Layer 1: USB Ethernet (Ethernet-over-USB)              │
│     ↑ Physical USB connection creates network device    │
└─────────────────────────────────────────────────────────┘
```

### Key Daemons
| Daemon | Role |
|--------|------|
| `remoted` | Handles all RemoteXPC connections, service registry |
| `remotepairingd` | Manages pairing and trusted tunnel establishment |
| `lockdownd` | Legacy protocol (still works for some services) |
| `afcd` | AFC daemon (blocked without trusted tunnel) |

### Key Ports
| Port | Protocol | Purpose |
|------|----------|---------|
| 58783 | QUIC/HTTP2 | RSD (RemoteServiceDiscovery) - iOS 17+ only |
| 49152 | TCP/QUIC | Tunnel service / RemotePairing |
| 62078 | TCP+TLS | Legacy lockdown (our entry point) |

### Why AFC Fails Over WiFi
When we connect to AFC via legacy lockdown (port 62078):
1. ✅ TCP connection succeeds
2. ✅ TLS handshake succeeds
3. ✅ lockdownd gives us a service port
4. ✅ afcd accepts our connection
5. ❌ **afcd checks for trusted tunnel entitlement**
6. ❌ No tunnel = `bytes in/out: 0/0` = timeout

From os_trace analysis:
```
process: afcd:1037 SYN in/out: 1/1 bytes in/out: 0/0
...
timed out stuck process 1037 [afcd], moving to idle band
```

### Services by Trust Level

**Untrusted (WiFi accessible):**
- `com.apple.mobile.lockdown.remote.untrusted`
- `com.apple.internal.dt.coredevice.untrusted.tunnelservice`
- `com.apple.mobile.insecure_notification_proxy.remote`
- Lockdown queries (GetValue)
- syslog_relay, os_trace_relay
- notification_proxy

**Trusted (Requires tunnel):**
- `com.apple.afc.shim.remote` ← Filesystem access
- `com.apple.amfi.lockdown.shim.remote`
- `com.apple.atc.shim.remote` ← Asset transfer
- Developer/debug tools
- Screenshot capture
- Installation proxy

### The Trusted Tunnel Flow
1. USB connection creates Ethernet-over-USB network interface
2. Client queries RSD on port 58783 (QUIC)
3. Connects to `untrusted.tunnelservice`
4. SRP key exchange (password: `000000`)
5. Pair record saved on device
6. Client requests QUIC tunnel with own keypair
7. Device returns tunnel params:
   ```json
   {
     "clientParameters": {
       "address": "fd58:8c92:8961::2",
       "mtu": 1280
     },
     "serverRSDPort": 56307
   }
   ```
8. Client creates TUN device, connects to trusted RSD
9. Full service access granted

### Why Our WiFi Approach Works (Partially)
Legacy lockdown (port 62078) wasn't removed:
- Still handles device queries
- Still allows diagnostic services
- Still streams logs
- **But trusted services now check for RemoteXPC tunnel**

**What bypasses the wall:**
1. Lockdown protocol queries (full access to 89+ keys)
2. Syslog/os_trace streaming (real-time monitoring)
3. Notification subscriptions
4. Diagnostics relay (Sleep command)

**What hits the wall:**
1. AFC (filesystem) - needs tunnel
2. Installation proxy - needs tunnel
3. Developer instruments - needs tunnel

---

## Files Generated

```
the orchard/
├── activation_private.pem    # !!! PRIVATE KEY !!!
├── activation_public.der     # Public key (DER)
├── device_public.der         # Device public key
├── fm_spkeys.bin             # Find My crypto keys
├── extracted_secrets.json    # All secrets JSON
├── deep_results.json         # Full probe results
├── probe_results.json        # Initial probe
└── *.py                      # Probe scripts
```

---

## Security Implications

1. **Any WiFi-paired computer** can extract these secrets without user interaction
2. **Find My keys** enable location tracking/spoofing research
3. **Activation keys** may enable activation research
4. **Complete device fingerprint** enables device impersonation
5. **Live syslog** reveals real-time device activity

---

## Research Value

This demonstrates that iOS WiFi sync pairing grants significant access to device secrets. The pairing record (stored in `C:\ProgramData\Apple\Lockdown\`) is the key - whoever has it can:

1. Query all device properties
2. Extract crypto keys
3. Stream system logs
4. Subscribe to system events

**The pairing record IS the credential.**

---

## 🎯 Potential Attack Vectors

Based on iOS 17 architecture analysis:

### 1. USB Ethernet Spoofing
If we could make iOS believe we're connected via USB:
- Create virtual Ethernet adapter with correct identifiers
- May trigger RemoteXPC stack instead of legacy lockdown
- **Challenge**: iOS likely checks USB bus enumeration

### 2. QUIC Tunnel Hijacking
If a Mac has an active trusted tunnel to the iPhone:
- The tunnel uses TUN device (utun3, etc.) with IPv6
- Tunnel parameters visible in macOS syslog
- Could potentially route traffic through existing tunnel
- **Challenge**: Need physical access to paired Mac

### 3. Untrusted Service Exploitation
Services accessible without tunnel:
- `com.apple.internal.dt.coredevice.untrusted.tunnelservice`
- `com.apple.mobile.lockdown.remote.untrusted`
- `com.apple.mobile.insecure_notification_proxy.remote`

Possible bugs: buffer overflows, logic errors in handshake

### 4. SRP Protocol Attack
- Pairing uses SRP with known password: `000000`
- If we could initiate SRP over WiFi (need USB Ethernet layer)
- Brute force not needed since password is fixed

### 5. Legacy Lockdown Escalation
- Legacy lockdown still grants significant access
- Look for services that forgot to check tunnel requirement
- Exploit race conditions during service initialization

### 6. os_trace Intelligence Gathering
- Real-time visibility into all system activity
- Can observe:
  - When user unlocks device
  - App launches/transitions
  - Network connections
  - Bluetooth pairing attempts
  - Security decisions being made
- Use to time other attacks or gather intel

---

## 🔮 Magic Hunt Findings (21:32-21:48)

### SetValue Persistence Discovery
We can write arbitrary values to lockdownd domains - and they PERSIST:

```python
# These all returned SUCCESS and persist across sessions:
{'Domain': 'com.apple.mobile.developer', 'Key': 'DisableAMFI', 'Value': True}
{'Domain': 'com.apple.mobile.developer', 'Key': 'EnableUnsignedCode', 'Value': True}
{'Domain': 'com.apple.amfi', 'Key': 'EnforcementDisabled', 'Value': True}
{'Domain': 'com.apple.kernel', 'Key': 'AllowUnsigned', 'Value': True}
{'Domain': 'com.apple.mobile.system', 'Key': 'JailbreakMode', 'Value': True}
{'Domain': 'com.apple.mobile.system', 'Key': 'RootEnabled', 'Value': True}
```

**Reading back confirms persistence:**
```
com.apple.mobile.developer: {DisableAMFI: True, EnableUnsignedCode: True, TrustAllCode: True}
com.apple.amfi: {AllowInvalidSignatures: True, Enabled: False, EnforcementDisabled: True}
com.apple.kernel: {AllowUnsigned: True, DisableSignatureCheck: True}
com.apple.mobile.system: {JailbreakMode: True, RootEnabled: True}
```

**Limitation**: These don't affect actual security - `EffectiveSecurityModeAp` stays True.
Values are cached in lockdownd, but kernel/AMFI doesn't read them.

### ConnectionType Spoofing
Adding extra session parameters:
```python
{
    'Request': 'StartSession',
    'ConnectionType': 'USB',
    'TransportType': 'USB',
    'HostID': '...',
    'SystemBUID': '...'
}
```

**Result**: `GetValue('ConnectionType')` returned `'USB'`!
But services still blocked - they check actual transport layer, not lockdownd's cache.

### Security Lockout Detection
After aggressive spoofing attempts, device returned `InvalidHostID`.
**Finding**: iOS detects suspicious pairing behavior and can temporarily revoke trust.

### The Architecture Insight
```
┌─────────────────────────────────────────────────────────┐
│                  THE SECURITY LAYERS                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  lockdownd cache     ←  We can write here (SetValue)    │
│       ↓ NOT READ BY ↓                                   │
│  Kernel/AMFI         ←  Actual security checks here     │
│       ↓                                                  │
│  Hardware (SEP)      ←  Untouchable                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

The "jailbreak boolean" (`cs_enforcement_enabled`) lives in kernel memory, not lockdownd.

### Research Questions
- Does anything read these cached values? (Recovery? Restore? Developer tools?)
- Could these values affect behavior during special modes?
- Is there legacy code that trusts lockdownd's cache?

---

## 📚 Technical References

- [pymobiledevice3 RemoteXPC docs](https://github.com/doronz88/pymobiledevice3/blob/master/misc/RemoteXPC.md)
- [Frida iOS 17 support writeup](https://www.nowsecure.com/blog/2024/08/14/the-road-to-frida-ios-17-support-and-beyond/)
- [Apple T2 RemoteXPC research](https://duo.com/labs/research/apple-t2-xpc)
