# Cryptographic Secret Extractor - HIGH SENSITIVITY
# This script performs a deep extraction of all available cryptographic material from the device's lockdown cache.
# It retrieves: Activation Private Keys (RSA), Find My network decryption keys (fm-spkeys), and Escrow keybags.
# WARNING: This data allows cloning device identity and decrypting location beacons. Use with extreme caution.
### SAFETY WARNING: THIS SCRIPT EXTRACTS PRIVATE KEY MATERIAL ###
#
# This script retrieves:
# 1. Activation Identity Keys (RSA Private Key)
# 2. Find My Network Decryption Keys (fm-spkeys)
# 3. Escrow Keybags
#
# HANDLE OUTPUT WITH EXTREME CARE.
# DO NOT EXFILTRATE without explicit authorization.
#
"""
Extract and decode all cryptographic secrets from the device.
Requires --yes flag to acknowledge risks.
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

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCKDOWN_PORT = 62078

from wifi_lockdown import get_pairing_record

def get_pairing(udid: str | None = None):
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

def decode_findmy_keys(data):
    """Decode Find My Service Provider keys (fm-spkeys)"""
    try:
        # It's a plist inside NVRAM
        keys = plistlib.loads(data)
        return {
            'p': base64.b64encode(keys.get('p', b'')).decode() if keys.get('p') else None,  # Public key
            's': base64.b64encode(keys.get('s', b'')).decode() if keys.get('s') else None,  # Secret key
            'v': keys.get('v'),  # Version
            'i': keys.get('i'),  # Index
            'l': keys.get('l'),  # Level
            'b': base64.b64encode(keys.get('b', b'')).decode() if keys.get('b') else None,  # Beacon key?
            '1': keys.get('1', {}),  # Slot 1
            '2': keys.get('2', {}),  # Slot 2
        }
    except Exception as e:
        return {'raw_hex': data.hex(), 'error': str(e)}

def main():
    import argparse

    ap = argparse.ArgumentParser(description="Extract crypto/identity material via WiFi lockdownd (Orchard)")
    ap.add_argument("--host", required=True, help="iOS device IP")
    ap.add_argument("--udid", help="pairing record UDID (optional)")
    ap.add_argument("--out", default="extracted_secrets.json", help="output JSON path")
    ap.add_argument("--outdir", default=".", help="directory for key files")
    ap.add_argument("--write-files", action="store_true", help="write key files to --outdir")
    ap.add_argument(
        "--yes",
        action="store_true",
        help="required: acknowledge this will extract sensitive device secrets",
    )
    args = ap.parse_args()

    if not args.yes:
        print("ERROR: Safety interlock active.")
        print("You must provide the --yes flag to confirm you understand this script extracts PRIVATE KEYS.")
        sys.exit(1)

    pairing = get_pairing(args.udid)
    secrets = {"host": args.host}

    print("=" * 70)
    print("CRYPTOGRAPHIC SECRET EXTRACTION")
    print("=" * 70)

    from pathlib import Path as _Path
    outdir = _Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((args.host, LOCKDOWN_PORT))
    
    send_recv(sock, {'Request': 'QueryType', 'Label': 'secrets'})
    
    resp = send_recv(sock, {
        'Request': 'StartSession',
        'Label': 'secrets',
        'HostID': pairing['HostID'],
        'SystemBUID': pairing['SystemBUID'],
    })
    
    if resp.get('EnableSessionSSL'):
        sock = upgrade_ssl(sock, pairing)
    
    print(f"[+] Session established")
    
    # === Extract activation keys ===
    print("\n[ACTIVATION KEYS]")
    
    # Public key (DER format)
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'ActivationPublicKey'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['ActivationPublicKey'] = {
            'format': 'DER',
            'length': len(data),
            'hex': data.hex(),
            'b64': base64.b64encode(data).decode()
        }
        print(f"  ActivationPublicKey: {len(data)} bytes (DER)")
        if args.write_files:
            with open(outdir / 'activation_public.der', 'wb') as f:
                f.write(data)
            print("    Saved to activation_public.der")
    
    # Private key (PEM format!)
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'ActivationPrivateKey'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['ActivationPrivateKey'] = {
            'format': 'PEM',
            'length': len(data),
            'preview': data[:100].decode('utf-8', errors='replace') if data else None
        }
        print(f"  ActivationPrivateKey: {len(data)} bytes (PEM)")
        print(f"    !!! THIS IS A PRIVATE KEY !!!")
        if args.write_files:
            with open(outdir / 'activation_private.pem', 'wb') as f:
                f.write(data)
            print("    Saved to activation_private.pem")
    
    # Device public key
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'DevicePublicKey'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['DevicePublicKey'] = {
            'format': 'DER',
            'length': len(data),
            'b64': base64.b64encode(data).decode()
        }
        print(f"  DevicePublicKey: {len(data)} bytes")
        if args.write_files:
            with open(outdir / 'device_public.der', 'wb') as f:
                f.write(data)
    
    # Escrow bag
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'EscrowBag'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['EscrowBag'] = {
            'length': len(data),
            'hex': data.hex()
        }
        print(f"  EscrowBag: {len(data)} bytes")
        print(f"    {data.hex()}")
    
    # PkHash
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'PkHash'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['PkHash'] = data.hex()
        print(f"  PkHash: {data.hex()}")
    
    # === Extract NVRAM secrets ===
    print("\n[NVRAM SECRETS]")
    
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'NonVolatileRAM'})
    if resp and resp.get('Value'):
        nvram = resp['Value']
        secrets['NVRAM'] = {}
        
        for key, val in nvram.items():
            if isinstance(val, bytes):
                if 'fm-' in key:
                    # Find My related
                    print(f"\n  [{key}] - FIND MY DATA")
                    
                    if key == 'fm-spkeys':
                        decoded = decode_findmy_keys(val)
                        secrets['NVRAM'][key] = decoded
                        print(f"    Decoded Find My Keys:")
                        for k, v in decoded.items():
                            if v:
                                print(f"      {k}: {v[:50]}..." if isinstance(v, str) and len(v) > 50 else f"      {k}: {v}")
                        if args.write_files:
                            with open(outdir / 'fm_spkeys.bin', 'wb') as f:
                                f.write(val)
                            print("    Raw saved to fm_spkeys.bin")
                        
                    elif key == 'fm-account-masked':
                        try:
                            account = val.decode('utf-8')
                            secrets['NVRAM'][key] = account
                            print(f"    Account: {account}")
                        except:
                            secrets['NVRAM'][key] = val.hex()
                            print(f"    Raw: {val.hex()}")
                            
                    else:
                        secrets['NVRAM'][key] = val.hex() if len(val) > 50 else val.decode('utf-8', errors='replace')
                        print(f"    {val.decode('utf-8', errors='replace') if len(val) < 50 else f'{len(val)} bytes'}")
                        
                elif 'key' in key.lower() or 'secret' in key.lower() or 'password' in key.lower():
                    secrets['NVRAM'][key] = val.hex()
                    print(f"  [{key}]: {val.hex()[:64]}...")
                else:
                    secrets['NVRAM'][key] = val.decode('utf-8', errors='replace') if len(val) < 100 else f"<{len(val)} bytes>"
            else:
                secrets['NVRAM'][key] = str(val)
    
    # === Extract baseband keys ===
    print("\n[BASEBAND CRYPTO]")
    
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'BasebandKeyHashInformation'})
    if resp and resp.get('Value'):
        data = resp['Value']
        secrets['BasebandKeyHash'] = {}
        for k, v in data.items():
            if isinstance(v, bytes):
                secrets['BasebandKeyHash'][k] = v.hex()
                print(f"  {k}: {v.hex()}")
            else:
                secrets['BasebandKeyHash'][k] = v
                print(f"  {k}: {v}")
    
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Key': 'BasebandMasterKeyHash'})
    if resp and resp.get('Value'):
        secrets['BasebandMasterKeyHash'] = resp['Value']
        print(f"  MasterKeyHash: {resp['Value']}")
    
    # === Extract FairPlay info ===
    print("\n[FAIRPLAY / DRM]")
    
    resp = send_recv(sock, {'Request': 'GetValue', 'Label': 'secrets', 'Domain': 'com.apple.fairplay'})
    if resp and resp.get('Value'):
        secrets['FairPlay'] = resp['Value']
        print(f"  FairPlay domain: {resp['Value']}")
    
    # === Save all secrets ===
    print("\n" + "=" * 70)
    print("SAVING SECRETS")
    print("=" * 70)
    
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(secrets, f, indent=2, default=str)

    print(f"[+] All secrets saved to {args.out}")
    if args.write_files:
        print("[+] Key files saved to:", str(outdir))
        print("    - activation_public.der")
        print("    - activation_private.pem  [!!!]")
        print("    - device_public.der")
        print("    - fm_spkeys.bin  [Find My crypto]")
    else:
        print("[i] Key files were NOT written (use --write-files to save them).")
    
    sock.close()

if __name__ == '__main__':
    main()
