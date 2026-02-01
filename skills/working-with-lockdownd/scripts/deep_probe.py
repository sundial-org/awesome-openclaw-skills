#!/usr/bin/env python3
# Deep Device Probe - Comprehensive Enumeration
# This script exhaustively queries every known Lockdown domain and attempts to handshake with every known service.
# It builds a complete JSON snapshot of the device's exposed attack surface, including persistent NVRAM values
# and service availability. It is strictly read-only but produces very large output files.
"""
Deep iOS Probe - Extract everything possible
READ ONLY - No writes
"""

import socket
import ssl
import struct
import plistlib
import os
import sys
import tempfile
import json
import base64
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCKDOWN_PORT = 62078

from wifi_lockdown import get_pairing_record

def get_pairing(udid: str | None = None):
    # Back-compat: original Orchard scripts used a hardcoded glob.
    return get_pairing_record(udid)

def send_recv(sock, data):
    payload = plistlib.dumps(data)
    sock.sendall(struct.pack('>I', len(payload)) + payload)
    header = b''
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return None
        header += chunk
    length = struct.unpack('>I', header)[0]
    body = b''
    while len(body) < length:
        chunk = sock.recv(length - len(body))
        if not chunk:
            return None
        body += chunk
    return plistlib.loads(body)

def upgrade_ssl(sock, pairing):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as f:
        f.write(pairing['HostCertificate'])
        cert = f.name
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as f:
        f.write(pairing['HostPrivateKey'])
        key = f.name
    ctx.load_cert_chain(cert, key)
    ssl_sock = ctx.wrap_socket(sock)
    os.unlink(cert)
    os.unlink(key)
    return ssl_sock

def connect_service(host, port, pairing):
    """Connect to a service port with SSL"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))
    return upgrade_ssl(sock, pairing)

def safe_bytes(v, max_len=200):
    """Convert bytes to readable format"""
    if isinstance(v, bytes):
        if len(v) <= max_len:
            # Try to decode as plist
            try:
                decoded = plistlib.loads(v)
                return {'_plist': decoded}
            except:
                pass
            # Try UTF-8
            try:
                return v.decode('utf-8')
            except:
                return {'_hex': v.hex(), '_len': len(v)}
        return {'_hex_truncated': v[:100].hex() + '...', '_len': len(v)}
    elif isinstance(v, dict):
        return {k: safe_bytes(val) for k, val in v.items()}
    elif isinstance(v, list):
        return [safe_bytes(item) for item in v]
    return v

# ALL known lockdown keys to query
INTERESTING_KEYS = [
    # Crypto/Security
    'ActivationPublicKey',
    'ActivationPrivateKey', 
    'ActivationState',
    'ActivationStateAcknowledged',
    'BasebandKeyHashInformation',
    'BasebandMasterKeyHash',
    'DevicePublicKey',
    'DeviceCertificate',
    'EscrowBag',
    'PkHash',
    
    # Device Identity
    'UniqueDeviceID',
    'UniqueChipID',
    'DieID',
    'SerialNumber',
    'MLBSerialNumber',
    'ChipSerialNo',
    'WirelessBoardSerialNumber',
    'HardwareModel',
    'HardwarePlatform',
    'ModelNumber',
    'RegionInfo',
    'ProductType',
    'ProductVersion',
    'BuildVersion',
    'FirmwareVersion',
    
    # Network
    'WiFiAddress',
    'BluetoothAddress', 
    'EthernetAddress',
    'PhoneNumber',
    
    # Cellular
    'IMEI',
    'MEID',
    'InternationalMobileEquipmentIdentity',
    'InternationalMobileEquipmentIdentity2',
    'InternationalMobileSubscriberIdentity',
    'IntegratedCircuitCardIdentity',
    'MobileEquipmentIdentifier',
    'MobileSubscriberCountryCode',
    'MobileSubscriberNetworkCode',
    'CarrierBundleInfoArray',
    
    # SIM
    'SIMStatus',
    'SIMTrayStatus',
    'SIMGID1',
    'SIMGID2',
    'GID1',
    'GID2',
    
    # Baseband
    'BasebandVersion',
    'BasebandStatus',
    'BasebandSerialNumber',
    'BasebandCertId',
    'BasebandChipID',
    'BasebandRegionSKU',
    
    # State
    'PasswordProtected',
    'BrickState',
    'HostAttached',
    'TrustedHostAttached',
    'USBConnected',
    
    # NVRAM (contains secrets!)
    'NonVolatileRAM',
    
    # Calibration/Sensors
    'ProximitySensorCalibration',
    'CompassCalibration',
    
    # Time
    'TimeIntervalSince1970',
    'TimeZone',
    'TimeZoneOffsetFromUTC',
    
    # Misc
    'DeviceColor',
    'DeviceClass',
    'DeviceName',
    'SyncFromHost',
    'BootSessionID',
    'PairRecordProtectionClass',
]

# All known domains
DOMAINS = [
    None,  # Default
    'com.apple.disk_usage',
    'com.apple.disk_usage.factory',
    'com.apple.mobile.battery',
    'com.apple.mobile.iTunes',
    'com.apple.mobile.backup',
    'com.apple.mobile.data_sync',
    'com.apple.mobile.debug',
    'com.apple.mobile.internal',
    'com.apple.mobile.lockdown_cache',
    'com.apple.mobile.mobile_application_usage',
    'com.apple.mobile.restriction',
    'com.apple.mobile.software_behavior',
    'com.apple.mobile.sync_data_class',
    'com.apple.mobile.user_preferences',
    'com.apple.mobile.wireless_lockdown',
    'com.apple.fairplay',
    'com.apple.international',
    'com.apple.purplebuddy',
    'com.apple.xcode.developerdomain',
    'com.apple.mobile.chaperone',
    'com.apple.mobile.third_party_termination',
    'com.apple.mobile.tethered_sync',
    'com.apple.mobile.iTunes.SQLMusicLibraryPostProcessCommands',
    'com.apple.mobile.iTunes.accessories',
    'com.apple.mobile.iTunes.store',
]

# All services to probe
SERVICES = [
    # Diagnostic/Debug
    'com.apple.syslog_relay',
    'com.apple.os_trace_relay',
    'com.apple.mobile.diagnostics_relay',
    'com.apple.iosdiagnostics.relay',
    'com.apple.mobile.file_relay',
    'com.apple.pcapd',
    
    # Notification/Events
    'com.apple.mobile.notification_proxy',
    'com.apple.mobile.insecure_notification_proxy',
    
    # File Access
    'com.apple.afc',
    'com.apple.afc2',
    'com.apple.mobile.house_arrest',
    
    # Backup/Sync
    'com.apple.mobilebackup',
    'com.apple.mobilebackup2',
    'com.apple.mobilesync',
    
    # Install/Apps
    'com.apple.mobile.installation_proxy',
    'com.apple.misagent',
    
    # Dev Tools
    'com.apple.debugserver',
    'com.apple.instruments.remoteserver',
    'com.apple.instruments.remoteserver.DVTSecureSocketProxy',
    'com.apple.testmanagerd.lockdown',
    'com.apple.testmanagerd.lockdown.secure',
    
    # Web/Safari
    'com.apple.webinspector',
    'com.apple.webkit.remote-web-inspector',
    
    # Screenshot/Screen
    'com.apple.screenshot',
    'com.apple.streaming_zip_conduit',
    
    # Location
    'com.apple.dt.simulatelocation',
    
    # Pairing/Auth
    'com.apple.coredevice.remotepairing',
    'com.apple.mobile.heartbeat',
    
    # System
    'com.apple.springboardservices',
    'com.apple.syslog_relay',
    'com.apple.mobile.MCInstall',
    'com.apple.mobile.mobile_image_mounter',
    
    # Companion/Watch
    'com.apple.companion_proxy',
    
    # Media
    'com.apple.atc',
    'com.apple.atc2',
    
    # Security
    'com.apple.amfi.lockdown',
    'com.apple.preboardservice',
    'com.apple.preboardservice_v2',
    
    # Unknown/Experimental
    'com.apple.ait.aitd',
    'com.apple.accessibility.axAuditDaemon.remoteserver',
    'com.apple.coredevice.appservice',
    'com.apple.coredevice.deviceinfo',
    'com.apple.coredevice.diagnosticsservice',
    'com.apple.coredevice.fileservice.control',
    'com.apple.coredevice.openstdiosocket',
    'com.apple.dt.ViewHierarchyAgent',
    'com.apple.idamd',
    'com.apple.instruments.deviceinfo',
    'com.apple.mobile.assertion_agent',
    'com.apple.mobile.storage_mounter_proxy',
    'com.apple.os.update',
    'com.apple.RestoreRemoteServices.restoreserviced',
    'com.apple.security.cryptexd',
    'com.apple.sysdiagnose.remote',
]

def main():
    import argparse

    ap = argparse.ArgumentParser(description="Deep iOS lockdownd probe (Orchard) — READ ONLY")
    ap.add_argument("--host", required=True, help="iOS device IP")
    ap.add_argument("--udid", help="pairing record UDID (optional)")
    ap.add_argument("--out", default="deep_results.json", help="output JSON path")
    args = ap.parse_args()

    pairing = get_pairing(args.udid)
    results = {
        'timestamp': datetime.now().isoformat(),
        'host': args.host,
        'device': {},
        'domains': {},
        'services': {},
        'nvram_secrets': {},
        'crypto': {},
    }

    print("=" * 70)
    print("DEEP iOS PROBE - Extracting Everything")
    print("=" * 70)

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((args.host, LOCKDOWN_PORT))
    print(f"[+] Connected to {args.host}")
    
    # QueryType
    send_recv(sock, {'Request': 'QueryType', 'Label': 'deepprobe'})
    
    # Start session
    resp = send_recv(sock, {
        'Request': 'StartSession',
        'Label': 'deepprobe',
        'HostID': pairing['HostID'],
        'SystemBUID': pairing['SystemBUID'],
    })
    
    if resp.get('EnableSessionSSL'):
        sock = upgrade_ssl(sock, pairing)
        print("[+] SSL session established")
    
    print(f"[+] Session: {resp.get('SessionID')}")
    
    # === PHASE 1: Extract all interesting keys ===
    print("\n" + "=" * 70)
    print("PHASE 1: Extracting Individual Keys")
    print("=" * 70)
    
    for key in INTERESTING_KEYS:
        try:
            resp = send_recv(sock, {
                'Request': 'GetValue',
                'Label': 'deepprobe',
                'Key': key
            })
            if resp and resp.get('Value') is not None:
                val = resp['Value']
                results['device'][key] = safe_bytes(val)
                
                # Special handling for sensitive data
                if key == 'NonVolatileRAM' and isinstance(val, dict):
                    print(f"\n[!] NVRAM SECRETS:")
                    for nk, nv in val.items():
                        if isinstance(nv, bytes):
                            results['nvram_secrets'][nk] = safe_bytes(nv)
                            if b'fm-' in nk.encode() or 'fm-' in nk:
                                print(f"    {nk}: <{len(nv)} bytes> [FIND MY KEY]")
                            elif 'key' in nk.lower() or 'secret' in nk.lower():
                                print(f"    {nk}: <{len(nv)} bytes> [CRYPTO]")
                            else:
                                print(f"    {nk}: {nv[:50]}..." if len(nv) > 50 else f"    {nk}: {nv}")
                        else:
                            print(f"    {nk}: {nv}")
                            
                elif key in ['ActivationPublicKey', 'ActivationPrivateKey', 'DevicePublicKey', 'EscrowBag', 'PkHash']:
                    if isinstance(val, bytes):
                        results['crypto'][key] = {'hex': val.hex(), 'len': len(val)}
                        print(f"[CRYPTO] {key}: {len(val)} bytes")
                        
                elif key in ['WiFiAddress', 'BluetoothAddress', 'EthernetAddress']:
                    print(f"[NET] {key}: {val}")
                    
                elif key == 'PhoneNumber':
                    print(f"[ID] {key}: {val}")
                    
                elif key in ['SerialNumber', 'UniqueDeviceID', 'IMEI']:
                    print(f"[ID] {key}: {val}")
                    
        except Exception as e:
            pass
    
    # === PHASE 2: Query all domains ===
    print("\n" + "=" * 70)
    print("PHASE 2: Querying All Domains")
    print("=" * 70)
    
    for domain in DOMAINS:
        try:
            req = {'Request': 'GetValue', 'Label': 'deepprobe'}
            if domain:
                req['Domain'] = domain
            resp = send_recv(sock, req)
            if resp and resp.get('Value'):
                val = resp['Value']
                domain_name = domain or 'default'
                results['domains'][domain_name] = safe_bytes(val)
                if isinstance(val, dict) and val:
                    print(f"[{domain_name}]: {len(val)} keys")
                    # Show interesting keys
                    for k, v in val.items():
                        if 'key' in k.lower() or 'secret' in k.lower() or 'password' in k.lower():
                            print(f"  [!] {k}: {safe_bytes(v)}")
        except Exception as e:
            pass
    
    # === PHASE 3: Probe all services ===
    print("\n" + "=" * 70)
    print("PHASE 3: Probing Services")
    print("=" * 70)
    
    available_services = []
    
    for service in SERVICES:
        try:
            resp = send_recv(sock, {
                'Request': 'StartService',
                'Label': 'deepprobe',
                'Service': service
            })
            results['services'][service] = safe_bytes(resp)
            
            if resp and resp.get('Port'):
                port = resp['Port']
                ssl_required = resp.get('EnableServiceSSL', False)
                print(f"[+] {service}: port {port} (SSL: {ssl_required})")
                available_services.append({
                    'name': service,
                    'port': port,
                    'ssl': ssl_required
                })
            elif resp and resp.get('Error'):
                err = resp['Error']
                if err != 'InvalidService':
                    print(f"[-] {service}: {err}")
        except Exception as e:
            pass
    
    # === PHASE 4: Try to interact with available services ===
    print("\n" + "=" * 70)
    print("PHASE 4: Deep Service Interaction")
    print("=" * 70)
    
    for svc in available_services:
        name = svc['name']
        port = svc['port']
        
        if name == 'com.apple.mobile.diagnostics_relay':
            print(f"\n[*] Probing diagnostics_relay on port {port}...")
            try:
                diag_sock = connect_service(args.host, port, pairing)
                
                # Try various diagnostic commands
                commands = [
                    {'Request': 'QueryAll'},
                    {'Request': 'IORegistry'},
                    {'Request': 'GasGauge'},
                    {'Request': 'WiFi'},
                    {'Request': 'All'},
                    {'Request': 'NAND'},
                    {'Request': 'Baseband'},
                ]
                
                for cmd in commands:
                    try:
                        resp = send_recv(diag_sock, cmd)
                        if resp and 'Diagnostics' in str(resp):
                            print(f"  [+] {cmd['Request']}: Got response")
                            results[f'diag_{cmd["Request"]}'] = safe_bytes(resp)
                    except:
                        pass
                        
                diag_sock.close()
            except Exception as e:
                print(f"  [-] Error: {e}")
                
        elif name == 'com.apple.mobile.notification_proxy':
            print(f"\n[*] Probing notification_proxy on port {port}...")
            try:
                notif_sock = connect_service(args.host, port, pairing)
                
                # Subscribe to notifications
                notifications = [
                    'com.apple.mobile.application_installed',
                    'com.apple.mobile.application_uninstalled',
                    'com.apple.springboard.screenlocked',
                    'com.apple.springboard.screenunlocked',
                    'com.apple.springboard.hasBlankedScreen',
                    'com.apple.mobile.lockdown.activation_state',
                    'com.apple.mobile.data_sync.domain_changed',
                    'com.apple.itunes-client.syncCancelRequest',
                    'com.apple.mobile.lockdown.trusted_host_attached',
                    'com.apple.mobile.lockdown.host_attached',
                    'com.apple.mobile.lockdown.phone_number_changed',
                ]
                
                for notif in notifications:
                    try:
                        send_recv(notif_sock, {
                            'Command': 'ObserveNotification',
                            'Name': notif
                        })
                        print(f"  [+] Subscribed: {notif}")
                    except:
                        pass
                
                results['notification_subscriptions'] = notifications
                notif_sock.close()
            except Exception as e:
                print(f"  [-] Error: {e}")
                
        elif name == 'com.apple.springboardservices':
            print(f"\n[*] Probing SpringBoard on port {port}...")
            try:
                sb_sock = connect_service(args.host, port, pairing)
                
                commands = [
                    {'command': 'queryState'},
                    {'command': 'getIconState'},
                    {'command': 'getHomeScreenWallpaper'},
                    {'command': 'getLockScreenWallpaper'},
                    {'command': 'getInterfaceOrientation'},
                ]
                
                for cmd in commands:
                    try:
                        resp = send_recv(sb_sock, cmd)
                        if resp:
                            print(f"  [+] {cmd['command']}: Got response")
                            results[f'springboard_{cmd["command"]}'] = safe_bytes(resp)
                    except:
                        pass
                        
                sb_sock.close()
            except Exception as e:
                print(f"  [-] Error: {e}")
    
    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"[+] Results saved to {args.out}")
    print(f"[+] Found {len(results['device'])} device properties")
    print(f"[+] Found {len(results['nvram_secrets'])} NVRAM entries")
    print(f"[+] Found {len(results['crypto'])} crypto artifacts")
    print(f"[+] Found {len(available_services)} available services")
    
    sock.close()

if __name__ == '__main__':
    main()
