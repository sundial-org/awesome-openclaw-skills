#!/usr/bin/env python3
# WiFi Lockdown Library - Core Protocol Implementation
# This module implements the raw TCP/SSL communication logic for talking to iOS devices on port 62078 (lockdownd).
# It handles: 1) Parsing Windows pairing records, 2) SSL certificate upgrades, 3) Plist message serialization.
# It is the foundational dependency for all other scripts in this skill.
"""
WiFi Lockdown Client - Pure Python iOS device communication
Uses only stdlib: socket, ssl, plistlib, struct
"""

import socket
import ssl
import struct
import plistlib
import os
from pathlib import Path

# iOS lockdown port
LOCKDOWN_PORT = 62078

def list_pairing_records() -> list[dict]:
    """List pairing records found on this machine.

    Returns items like:
      {"udid": "0000...", "path": "C:/ProgramData/Apple/Lockdown/<udid>.plist"}
    """
    lockdown_dir = Path(os.environ.get('ALLUSERSPROFILE', 'C:/ProgramData')) / 'Apple' / 'Lockdown'
    out: list[dict] = []
    for f in sorted(lockdown_dir.glob('*.plist')):
        if f.name == 'SystemConfiguration.plist':
            continue
        out.append({"udid": f.stem, "path": str(f)})
    return out


def get_pairing_record(udid: str | None = None, pairing_path: str | None = None) -> dict:
    """Load pairing record from Windows Lockdown folder."""
    lockdown_dir = Path(os.environ.get('ALLUSERSPROFILE', 'C:/ProgramData')) / 'Apple' / 'Lockdown'

    if pairing_path:
        plist_path = Path(pairing_path)
    elif udid:
        plist_path = lockdown_dir / f"{udid}.plist"
    else:
        # Find first device plist (not SystemConfiguration)
        recs = list_pairing_records()
        if not recs:
            raise FileNotFoundError("No pairing records found")
        plist_path = Path(recs[0]["path"])

    with open(plist_path, 'rb') as f:
        return plistlib.load(f)

def create_ssl_context(pairing: dict) -> ssl.SSLContext:
    """Create SSL context using pairing certificates"""
    import tempfile
    
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Write certs to temp files (ssl module needs files)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as cert_file:
        cert_file.write(pairing['HostCertificate'])
        cert_path = cert_file.name
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as key_file:
        key_file.write(pairing['HostPrivateKey'])
        key_path = key_file.name
    
    ctx.load_cert_chain(cert_path, key_path)
    
    # Clean up temp files
    os.unlink(cert_path)
    os.unlink(key_path)
    
    return ctx

class LockdownClient:
    """WiFi Lockdown protocol client"""
    
    def __init__(self, host: str, pairing: dict = None):
        self.host = host
        self.port = LOCKDOWN_PORT
        self.pairing = pairing or get_pairing_record()
        self.sock = None
        self.ssl_sock = None
        
    def connect(self):
        """Establish TCP connection"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.host, self.port))
        print(f"[+] Connected to {self.host}:{self.port}")
        
    def start_ssl(self):
        """Upgrade to SSL using pairing certs"""
        ctx = create_ssl_context(self.pairing)
        self.ssl_sock = ctx.wrap_socket(self.sock)
        print(f"[+] SSL handshake complete")
        
    def send_plist(self, data: dict) -> dict:
        """Send plist request and receive response"""
        sock = self.ssl_sock or self.sock
        
        # Encode request
        payload = plistlib.dumps(data)
        header = struct.pack('>I', len(payload))
        sock.sendall(header + payload)
        
        # Read response header
        header = self._recv_exact(4)
        if not header:
            return None
        length = struct.unpack('>I', header)[0]
        
        # Read response body
        body = self._recv_exact(length)
        if not body:
            return None
            
        return plistlib.loads(body)
    
    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly n bytes"""
        sock = self.ssl_sock or self.sock
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def query(self, domain: str = None, key: str = None) -> dict:
        """Query lockdown value"""
        req = {'Request': 'GetValue', 'Label': 'foxprobe'}
        if domain:
            req['Domain'] = domain
        if key:
            req['Key'] = key
        return self.send_plist(req)
    
    def start_session(self) -> dict:
        """Start authenticated session using pairing"""
        req = {
            'Request': 'StartSession',
            'Label': 'foxprobe',
            'HostID': self.pairing['HostID'],
            'SystemBUID': self.pairing['SystemBUID'],
        }
        return self.send_plist(req)
    
    def start_service(self, service: str) -> dict:
        """Request to start a service"""
        req = {
            'Request': 'StartService',
            'Label': 'foxprobe',
            'Service': service,
        }
        return self.send_plist(req)
    
    def close(self):
        """Close connection"""
        if self.ssl_sock:
            self.ssl_sock.close()
        if self.sock:
            self.sock.close()


def discover_device() -> str:
    """Find iOS device on local network via mDNS/scanning"""
    # Quick scan common IPs
    for last_octet in range(2, 255):
        ip = f"10.0.0.{last_octet}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, LOCKDOWN_PORT))
            sock.close()
            if result == 0:
                return ip
        except:
            pass
    return None


if __name__ == '__main__':
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else '10.0.0.33'
    
    print(f"[*] Connecting to {host}...")
    client = LockdownClient(host)
    
    try:
        client.connect()
        
        # Query device info (no SSL needed for basic queries)
        info = client.query(key='DeviceName')
        print(f"[+] Device: {info}")
        
        # Try to start session
        print("[*] Starting session...")
        session = client.start_session()
        print(f"[+] Session: {session}")
        
        if session and session.get('EnableSessionSSL'):
            print("[*] Upgrading to SSL...")
            client.start_ssl()
            
            # Now try syslog service
            print("[*] Requesting syslog_relay service...")
            svc = client.start_service('com.apple.syslog_relay')
            print(f"[+] Service response: {svc}")
            
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client.close()
