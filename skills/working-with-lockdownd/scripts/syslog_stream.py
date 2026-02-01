#!/usr/bin/env python3
# Syslog Relay Streamer - Live Text Logs
# This script connects to the 'com.apple.syslog_relay' service to stream the device's standard syslog buffer.
# It mirrors the functionality of 'idevicesyslog' but works purely over WiFi using the existing pairing record.
# Useful for debugging crashes, checking system state, or monitoring app behavior in real-time.
"""
iOS Syslog Relay Stream - Real-time OS logs over WiFi
"""

import socket
import ssl
import struct
import plistlib
import os
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCKDOWN_PORT = 62078

from wifi_lockdown import get_pairing_record

def get_pairing():
    # Back-compat: previous Orchard scripts used a hardcoded glob.
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

def connect_to_service(host, port, pairing):
    """Connect to a lockdown service port with SSL"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((host, port))
    return upgrade_ssl(sock, pairing)

def main():
    import argparse

    ap = argparse.ArgumentParser(description="Stream iOS syslog_relay over WiFi lockdownd")
    ap.add_argument("host", help="iOS device IP")
    ap.add_argument("--udid", help="pairing record UDID (optional)")
    args = ap.parse_args()

    pairing = get_pairing() if not args.udid else get_pairing_record(args.udid)

    # First establish lockdown session and get syslog port
    print("[*] Connecting to lockdown...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((args.host, LOCKDOWN_PORT))
    
    # QueryType
    send_recv(sock, {'Request': 'QueryType', 'Label': 'foxprobe'})
    
    # Start session
    resp = send_recv(sock, {
        'Request': 'StartSession',
        'Label': 'foxprobe',
        'HostID': pairing['HostID'],
        'SystemBUID': pairing['SystemBUID'],
    })
    
    if resp.get('EnableSessionSSL'):
        sock = upgrade_ssl(sock, pairing)
    
    print(f"[+] Session: {resp.get('SessionID')}")
    
    # Request syslog_relay service
    resp = send_recv(sock, {
        'Request': 'StartService',
        'Label': 'foxprobe',
        'Service': 'com.apple.syslog_relay'
    })
    
    syslog_port = resp.get('Port')
    if not syslog_port:
        print(f"[-] Failed to get syslog port: {resp}")
        return
    
    print(f"[+] syslog_relay on port {syslog_port}")
    sock.close()
    
    # Connect to syslog service
    print(f"[*] Connecting to syslog service...")
    syslog_sock = connect_to_service(args.host, syslog_port, pairing)
    print("[+] Connected to syslog_relay!")
    print("=" * 60)
    print("LIVE SYSLOG STREAM")
    print("=" * 60)
    
    # Read syslog stream
    buffer = b''
    try:
        while True:
            data = syslog_sock.recv(4096)
            if not data:
                print("[-] Connection closed")
                break
            
            buffer += data
            
            # Syslog entries are newline-separated
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                try:
                    text = line.decode('utf-8', errors='replace').strip()
                    if text:
                        print(text)
                except:
                    print(f"[raw] {line.hex()}")
    
    except (ConnectionResetError, BrokenPipeError):
        print("[-] Connection lost (Remote host closed connection)")
    except KeyboardInterrupt:
        print("\n[*] Stopped by user")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        syslog_sock.close()

if __name__ == '__main__':
    main()
