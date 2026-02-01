# OS Trace Analysis - WiFi Entry Points

*Analysis from 2026-01-28 ~20:45*

## Stream Stats
- ~3.5MB in 8 seconds
- 34+ processes visible
- 158+ subsystems
- Real-time device activity monitoring

## WiFi-Related Discoveries

### Subsystems
- `com.apple.WiFiManager`
- `com.apple.WiFiPolicy`
- `com.apple.wifip`

### Functions/Callbacks
- `WiFiDeviceManagerGetAppState`
- `WiFiDeviceProcessRSSIEvent`
- `WiFiLQAMgrCopyCoalescedUndispatchedLQMEvent`
- `onWiFiDeviceClientRegisterLQMCallback` ← Interesting entry point

### Network Stack
- ConnectionManager
- NetworkConsumer
- NetworkEnergy
- NetworkEnvironment
- NetworkPublishActivityService
- NetworkReachability
- NetworkReachabilityGetFlagsFromPath
- NetworkTasks

### Service Discovery (mDNS/Bonjour)
- Advertisement, AdvertisementCache, AdvertisementData
- AdvertisementDetected, Advertisments
- AdvertisingChannel
- DiscoveryADVBuffersIfNeeded

## Lockdown Activity
- lockdownd uses IOKit framework
- Visible at `/usr/libexec/lockdownd`
- Interacts with system frameworks

## New Finding (2026-01-30): Selected text can leak into os_trace (app-dependent)
While streaming `com.apple.os_trace_relay` over WiFi and watching for screenshot triggers, we observed that **selected text inside Telegram** can appear verbatim in trace logs via Accessibility text processing.

Observed pattern (Telegram):
- Selecting/highlighting text in the message composer triggers logs like:
  - `AccessibilityUtilitiesRunning language detection on chunk: '<TEXT>'`
  - subsystem: `com.apple.AccessibilityAXSpokenContentTextProcessing`
- This occurred for both a unique token (`TOKEN_XYZ`) and a normal word (`hello`).
- By contrast, the same select/copy tests did **not** surface the literal text in our capture windows for:
  - Notes (MobileNotes)
  - Safari address bar (MobileSafari)
  - iMessage (MobileSMS)
  - Discord

Implication:
- os_trace can act as a side-channel for **selected text content**, but behavior appears **app/component-specific** (likely tied to how a text view integrates with Accessibility).

Also confirmed in traces during screenshot events:
- `SpringBoard` logs `QUEUEING Screenshot presses:1` (hardware combo)
- FrontBoard/RunningBoard manages `com.apple.ScreenshotServicesService`

## MagicPairing (RemotePairing Protocol)
- WPPairing (Wireless Pairing)
- Used for Bluetooth/proximity pairing
- Has device time, advertising channel, RSSI, device address fields

## Security Patterns Found
- lockdown: 4 matches
- wifi: 1377 matches!
- pair: 164 matches
- session: 329 matches
- trust: 104 matches
- sandbox: 14 matches (extensions being attached)
- codesign: 35 matches

## XPC Endpoints
- aonsensed.xpc (always-on sensors)
- apple.xpc

## Entry Point Functions
- BTDeviceMsgHandler
- processEventHandler
- onWiFiDeviceClientRegisterLQMCallback
- dataCallback
- generateCallback
- PerfPowerServicesEventListen

## Potential Research Angles

1. **WiFiManager** - Can we observe connection state changes?
2. **MagicPairing** - RemotePairing protocol (iOS 17+)
3. **XPC endpoints** - Internal service communication
4. **mDNS/Bonjour** - Device discovery patterns

## Key Insight
The os_trace stream gives us visibility into:
- Every system daemon's activity
- Network stack operations
- Service discovery
- Security checks (sandbox, codesign)
- Internal XPC communication

This is a monitoring backdoor into the entire iOS system.

## AFC Wall Investigation (20:48)

When triggering AFC while tracing:

### What We See
1. **afcd** daemon is active at `/usr/libexec/afcd`
2. XPC connection: `com.apple.afcd` with listener/peer
3. TCP shows: `process: afcd:1037 SYN in/out: 1/1 bytes in/out: 0/0`
4. Security.framework interaction visible
5. Eventually: `timed out stuck process 1037 [afcd], moving to idle band`

### The Wall Mechanism
- Connection is ESTABLISHED at TCP level
- SSL handshake succeeds
- afcd receives connection but **won't process data**
- Connection times out (no bytes flow)
- afcd demoted to idle band

### Implications
The block is NOT at:
- Network layer (TCP connects)
- TLS layer (SSL succeeds)
- lockdownd (gives us port)

The block IS at:
- afcd's own connection handler
- Possibly in Security.framework check
- Before any AFC protocol messages are processed

### XPC Patterns Seen
- `mach=true/false listener=false peer=true/false`
- Connection activations and cancellations
- Various com.apple.* XPC services

---

## iOS 17 Architecture Discovery (21:06)

### The New Stack: RemoteXPC
From pymobiledevice3 documentation:

1. **USB Ethernet** - iOS 17 creates a network device via Ethernet-over-USB
2. **QUIC Protocol** - Uses HTTP/2 over QUIC, not raw TCP
3. **RSD Port 58783** - RemoteServiceDiscovery, QUIC-only
4. **`remoted` daemon** - Handles all RemoteXPC connections
5. **`remotepairingd`** - Manages pairing and trusted tunnels

### The Pairing Flow
1. Connect to `com.apple.internal.dt.coredevice.untrusted.tunnelservice`
2. **SRP key exchange with password "000000"**
3. Save pair record on device
4. Request trusted tunnel (creates TUN device like utun3)
5. Over tunnel, connect to trusted RSD for full service access

### Key Ports
- **58783** - RSD (RemoteServiceDiscovery) - QUIC only!
- **49152** - Likely tunnel service
- **62078** - Legacy lockdown (still works for some services)

### Why AFC Fails Over WiFi
AFC (`com.apple.afc.shim.remote`) requires:
- `Entitlement: com.apple.mobile.lockdown.remote.trusted`
- Only accessible **over the trusted tunnel**
- The trusted tunnel requires USB pairing first

### Services Available WITHOUT Tunnel (Untrusted)
- `com.apple.internal.dt.coredevice.untrusted.tunnelservice`
- `com.apple.mobile.lockdown.remote.untrusted`
- `com.apple.mobile.insecure_notification_proxy.remote`

### Services Requiring Tunnel (Trusted)
- **com.apple.afc.shim.remote** ← This is why AFC fails!
- com.apple.amfi.lockdown.shim.remote
- com.apple.atc.shim.remote
- Many developer tools

### The Wall Explained
The legacy lockdown (port 62078) still works for WiFi pairing but:
- iOS 17 added a new layer: **RemoteXPC trusted tunnel**
- Services like AFC now check for this tunnel
- Without the tunnel, connections are accepted but data blocked
- This is why we see `bytes in/out: 0/0` in traces

### Possible Attack Vectors
1. **Spoof USB Ethernet** - Make iOS think we're USB connected?
2. **QUIC tunnel hijacking** - If macOS has active tunnel, reuse it?
3. **Exploit untrusted services** - Find vulnerabilities in accessible services
4. **SRP attack** - Password "000000" is known, but need USB for initial handshake
