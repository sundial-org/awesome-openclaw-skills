# Magic Hunt - Session Notes

*2026-01-28 21:32-21:48*

## What We Tried

### 1. SetValue Persistence (INTERESTING!)
We can set arbitrary domain/key values:
```python
{'Domain': 'com.apple.mobile.developer', 'Key': 'DisableAMFI', 'Value': True}  # SUCCESS
{'Domain': 'com.apple.kernel', 'Key': 'AllowUnsigned', 'Value': True}  # SUCCESS
{'Domain': 'com.apple.mobile.system', 'Key': 'JailbreakMode', 'Value': True}  # SUCCESS
```

**Values PERSIST** - they survive across sessions and can be read back:
```
com.apple.mobile.developer: {DisableAMFI: True, EnableUnsignedCode: True, TrustAllCode: True}
com.apple.amfi: {AllowInvalidSignatures: True, Enabled: False, EnforcementDisabled: True}
com.apple.kernel: {AllowUnsigned: True, DisableSignatureCheck: True}
com.apple.mobile.system: {JailbreakMode: True, RootEnabled: True}
```

**BUT**: These don't affect actual kernel security - `EffectiveSecurityModeAp` stays True.
The values are stored in lockdownd's cache, not read by kernel/AMFI.

### 2. ConnectionType Spoofing (PARTIALLY WORKED!)
Sending extra session parameters:
```python
{
    'Request': 'StartSession',
    'ConnectionType': 'USB',
    'TransportType': 'USB',
    ...
}
```

**Result**: `GetValue('ConnectionType')` returned `'USB'` after spoofing!
But AFC still didn't work - the actual transport check happens at a lower level.

### 3. AMFI Service Probing
- AMFI service gives us a port (connects!)
- But commands return nothing (WiFi wall)
- Traced amfid: `/usr/libexec/amfid`
- Uses Security.framework for signature checks
- Connection pattern: `bytes in/out: 0/0` (blocked)

### 4. Heartbeat Commands
Heartbeat service responds to:
- `Marco` → `{Interval: 10, SupportsSleepyTime: True}`
- `GetInfo` → same response
- `Eval` → same response (not actual eval!)

### 5. Security Lockout Triggered
After aggressive probing, got `InvalidHostID` - device may have temporarily revoked our pairing trust.

## Key Insights

### The Security Architecture
1. **lockdownd** accepts arbitrary SetValue (just caches them)
2. **Services** check connection type at XPC/kernel level
3. **AMFI/kernel** doesn't read lockdownd's cache
4. **Transport check** happens below SSL layer

### What ACTUALLY Reads These Values?
The question: Is there ANY component that reads lockdownd's cached domains and acts on them?
- Maybe legacy code?
- Maybe during restore/recovery?
- Maybe during pairing flow?

### The Wall
```
WiFi TCP → SSL → Lockdownd (fooled) → Service Port → Service (blocked)
                     ↑                                    ↑
              We can spoof here              But check happens here
```

## Potential Vectors Not Yet Explored

1. **Recovery mode behavior** - Do our SetValue changes affect recovery mode?
2. **DFU mode** - Does lockdown cache persist through DFU?
3. **Restore flow** - iTunes reads lockdown values during restore
4. **Developer disk mounting** - Might read some of these flags
5. **Activation flow** - mobileactivationd might check lockdown cache
