#!/usr/bin/env python3
# OS Trace Relay - High-Frequency System Tracing
# This script connects to 'com.apple.os_trace_relay' to consume the binary log stream (Unified Logging).
# Unlike standard syslog, this stream is incredibly verbose (~2MB/s), showing internal kernel, XPC, and daemon activity.
# It decodes the binary plist stream to reveal process execution, network connections, and security checks.
"""
os_trace_relay v2 - Based on working session_probe code
"""

import socket
import ssl
import struct
import plistlib
import os
import sys
import tempfile
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCKDOWN_PORT = 62078

from wifi_lockdown import get_pairing_record

def get_pairing():
    return get_pairing_record()

def send_recv(sock, data):
    payload = plistlib.dumps(data)
    sock.sendall(struct.pack('>I', len(payload)) + payload)
    
    header = b''
    while len(header) < 4:
        header += sock.recv(4 - len(header))
    length = struct.unpack('>I', header)[0]
    
    body = b''
    while len(body) < length:
        body += sock.recv(length - len(body))
    
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

def main():
    import argparse

    ap = argparse.ArgumentParser(description="Stream iOS os_trace_relay over WiFi lockdownd")
    ap.add_argument("host", help="iOS device IP")
    ap.add_argument("--seconds", type=int, default=10, help="how long to stream")
    ap.add_argument("--udid", help="pairing record UDID (optional)")
    args = ap.parse_args()

    pairing = get_pairing() if not args.udid else get_pairing_record(args.udid)

    print("=" * 70)
    print("os_trace_relay v2")
    print("=" * 70)

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((args.host, LOCKDOWN_PORT))
    print(f"[+] Connected to {args.host}")
    
    # QueryType
    send_recv(sock, {'Request': 'QueryType', 'Label': 'ostrace'})
    
    # Start session
    resp = send_recv(sock, {
        'Request': 'StartSession',
        'Label': 'ostrace',
        'HostID': pairing['HostID'],
        'SystemBUID': pairing['SystemBUID'],
    })
    
    if resp.get('EnableSessionSSL'):
        sock = upgrade_ssl(sock, pairing)
        print("[+] SSL established")
    
    print(f"[+] Session: {resp.get('SessionID')}")
    
    # Start os_trace_relay
    resp = send_recv(sock, {
        'Request': 'StartService',
        'Label': 'ostrace',
        'Service': 'com.apple.os_trace_relay'
    })
    
    if not resp.get('Port'):
        print(f"[-] No port: {resp}")
        return
    
    port = resp['Port']
    print(f"[+] os_trace_relay on port {port}")

    # Connect to service
    trace_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trace_sock.settimeout(10)
    trace_sock.connect((args.host, port))
    trace_sock = upgrade_ssl(trace_sock, pairing)
    print("[+] Connected to os_trace_relay!")
    
    # Try various commands
    commands = [
        # From screenshot - StartActivity
        {'Request': 'StartActivity', 'MessageFilter': 65535, 'Pid': -1, 'StreamFlags': 60},
        # Process list
        {'Request': 'ProcessList'},
        # Other possibilities
        {'Request': 'Ping'},
        {'Request': 'CreateArchive'},
    ]
    
    for cmd in commands:
        print(f"\n[*] Trying: {cmd.get('Request', cmd)}")
        try:
            payload = plistlib.dumps(cmd)
            trace_sock.sendall(struct.pack('>I', len(payload)) + payload)
            
            trace_sock.settimeout(3)
            header = trace_sock.recv(4)
            if header and len(header) == 4:
                length = struct.unpack('>I', header)[0]
                if 0 < length < 1000000:
                    body = b''
                    while len(body) < length:
                        chunk = trace_sock.recv(min(4096, length - len(body)))
                        if not chunk:
                            break
                        body += chunk
                    
                    try:
                        resp = plistlib.loads(body)
                        print(f"    Response: {list(resp.keys())}")
                        
                        if 'ProcessList' in resp:
                            procs = resp['ProcessList']
                            print(f"\n🔥 PROCESS LIST - {len(procs)} processes!")
                            
                            for p in procs[:30]:
                                name = p.get('ProcessName', p.get('Name', '?'))
                                pid = p.get('Pid', p.get('PID', '?'))
                                print(f"    [{pid}] {name}")
                            
                            if len(procs) > 30:
                                print(f"    ... and {len(procs) - 30} more")
                            
                            # Intentionally do not write to disk by default.
                            # (This skill is for reliable interaction, not dumping secrets/PII into files.)
                            
                        elif 'Status' in resp:
                            print(f"    Status: {resp['Status']}")
                            
                        # Show full response for debugging
                        for k, v in resp.items():
                            if k not in ['ProcessList']:
                                print(f"    {k}: {str(v)[:100]}")
                                
                    except:
                        print(f"    Binary response: {len(body)} bytes")
            else:
                print(f"    No/bad header: {header}")
                
        except socket.timeout:
            print(f"    Timeout")
        except Exception as e:
            print(f"    Error: {e}")
    
    # Now stream for a bit
    print(f"\n[*] Streaming trace data ({args.seconds} seconds)...")

    trace_sock.settimeout(0.5)
    entries = []
    end_time = time.time() + args.seconds
    
    while time.time() < end_time:
        try:
            header = trace_sock.recv(4)
            if header and len(header) == 4:
                length = struct.unpack('>I', header)[0]
                if 0 < length < 100000:
                    body = trace_sock.recv(length)
                    entries.append(body)
        except socket.timeout:
            continue
        except:
            break
    
    print(f"[+] Captured {len(entries)} trace entries")
    # Tip: if you want to persist data, pipe stdout to a file or extend this script with an explicit --out.
    
    trace_sock.close()
    sock.close()

if __name__ == '__main__':
    main()
