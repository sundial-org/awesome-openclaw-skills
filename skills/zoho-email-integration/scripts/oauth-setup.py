#!/usr/bin/env python3
"""
Zoho Mail OAuth2 Setup Script
Interactive browser-based OAuth2 authorization for Zoho Mail API
"""

import json
import os
import sys
import webbrowser
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
import time

# Default token storage path
DEFAULT_TOKEN_PATH = os.path.expanduser('~/.zoho-mail-tokens.json')

# Zoho OAuth2 endpoints
ZOHO_AUTH_URL = 'https://accounts.zoho.com/oauth/v2/auth'
ZOHO_TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token'

# Scopes required for Zoho Mail
ZOHO_SCOPES = [
    'ZohoMail.messages.READ',
    'ZohoMail.messages.CREATE',
    'ZohoMail.messages.UPDATE',
    'ZohoMail.folders.READ',
    'ZohoMail.accounts.READ'
]

class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback"""
    
    authorization_code = None
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass
    
    def do_GET(self):
        """Handle OAuth callback"""
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            CallbackHandler.authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = '''
                <html>
                <head><title>OAuth2 Success</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                    <h1 style="color: green;">&#10003; Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(function() { window.close(); }, 3000);</script>
                </body>
                </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        elif 'error' in params:
            error = params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f'''
                <html>
                <head><title>OAuth2 Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                    <h1 style="color: red;">&#10007; Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Invalid callback')

def find_free_port(start_port=8080, max_attempts=10):
    """Find a free port for the callback server"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError("Could not find a free port")

def exchange_code_for_tokens(client_id, client_secret, code, redirect_uri):
    """Exchange authorization code for access and refresh tokens"""
    try:
        import urllib.request
        import urllib.error
        
        data = urlencode({
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }).encode()
        
        req = urllib.request.Request(ZOHO_TOKEN_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Token exchange failed: {e.code} - {error_body}")
    except Exception as e:
        raise Exception(f"Failed to exchange code for tokens: {e}")

def refresh_access_token(client_id, client_secret, refresh_token):
    """Refresh access token using refresh token"""
    try:
        import urllib.request
        import urllib.error
        
        data = urlencode({
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }).encode()
        
        req = urllib.request.Request(ZOHO_TOKEN_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Token refresh failed: {e.code} - {error_body}")
    except Exception as e:
        raise Exception(f"Failed to refresh token: {e}")

def save_tokens(token_data, client_id, client_secret, token_path=DEFAULT_TOKEN_PATH):
    """Save tokens to file"""
    token_file = {
        'client_id': client_id,
        'client_secret': client_secret,
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_in': token_data['expires_in'],
        'token_type': token_data.get('token_type', 'Bearer'),
        'created_at': int(time.time())
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    
    # Save with restricted permissions
    with open(token_path, 'w') as f:
        json.dump(token_file, f, indent=2)
    
    # Set file permissions to 600 (owner read/write only)
    os.chmod(token_path, 0o600)
    
    print(f"\n✓ Tokens saved to: {token_path}")
    print(f"✓ File permissions: 600 (owner read/write only)")

def setup_oauth2():
    """Interactive OAuth2 setup"""
    print("=" * 70)
    print("Zoho Mail OAuth2 Setup")
    print("=" * 70)
    print()
    
    # Get client credentials
    print("First, you need to create OAuth2 credentials in Zoho:")
    print("1. Go to: https://api-console.zoho.com/")
    print("2. Click 'Add Client' → 'Server-based Applications'")
    print("3. Enter:")
    print("   - Client Name: Clawdbot Zoho Mail")
    print("   - Homepage URL: http://localhost")
    print("   - Redirect URI: http://localhost:8080/callback")
    print("4. Copy the Client ID and Client Secret")
    print()
    
    client_id = input("Enter your Client ID: ").strip()
    if not client_id:
        print("Error: Client ID is required")
        sys.exit(1)
    
    client_secret = input("Enter your Client Secret: ").strip()
    if not client_secret:
        print("Error: Client Secret is required")
        sys.exit(1)
    
    # Custom token path
    token_path = input(f"Token storage path [{DEFAULT_TOKEN_PATH}]: ").strip()
    if not token_path:
        token_path = DEFAULT_TOKEN_PATH
    
    token_path = os.path.expanduser(token_path)
    
    print()
    print("-" * 70)
    print("Starting OAuth2 authorization flow...")
    print("-" * 70)
    
    # Find free port
    port = find_free_port()
    redirect_uri = f'http://localhost:{port}/callback'
    
    # Build authorization URL
    auth_params = {
        'scope': ','.join(ZOHO_SCOPES),
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{ZOHO_AUTH_URL}?{urlencode(auth_params)}"
    
    print(f"\n🌐 Opening browser for authorization...")
    print(f"If browser doesn't open, visit this URL:")
    print(f"\n{auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Start callback server
    print(f"✓ Listening for callback on http://localhost:{port}")
    print("Please log in and authorize the application in your browser...")
    print()
    
    server = HTTPServer(('127.0.0.1', port), CallbackHandler)
    
    # Wait for callback (with timeout)
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while CallbackHandler.authorization_code is None:
        server.handle_request()
        if time.time() - start_time > timeout:
            print("\n✗ Timeout waiting for authorization")
            sys.exit(1)
    
    code = CallbackHandler.authorization_code
    print("✓ Authorization code received")
    
    # Exchange code for tokens
    print("Exchanging authorization code for tokens...")
    
    try:
        token_data = exchange_code_for_tokens(client_id, client_secret, code, redirect_uri)
        
        if 'access_token' not in token_data or 'refresh_token' not in token_data:
            print(f"✗ Error: Missing tokens in response: {token_data}")
            sys.exit(1)
        
        print("✓ Tokens received successfully")
        
        # Save tokens
        save_tokens(token_data, client_id, client_secret, token_path)
        
        print()
        print("=" * 70)
        print("✓ OAuth2 Setup Complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print(f"1. Your tokens are stored in: {token_path}")
        print("2. Test the connection:")
        print(f"   python3 scripts/zoho-email.py oauth-status --token-file {token_path}")
        print("3. Use OAuth2 in your scripts:")
        print(f"   python3 scripts/zoho-email.py unread --auth oauth2 --token-file {token_path}")
        print()
        print("⚠️  Security notes:")
        print("- Keep your token file secure (permissions: 600)")
        print("- Never commit tokens to version control")
        print("- Tokens will auto-refresh when expired")
        print()
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

def refresh_token_cmd():
    """Refresh token command"""
    token_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TOKEN_PATH
    token_path = os.path.expanduser(token_path)
    
    if not os.path.exists(token_path):
        print(f"✗ Error: Token file not found: {token_path}")
        print("Run 'python3 oauth-setup.py' first to set up OAuth2")
        sys.exit(1)
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        
        print(f"Refreshing tokens from: {token_path}")
        
        new_tokens = refresh_access_token(
            token_data['client_id'],
            token_data['client_secret'],
            token_data['refresh_token']
        )
        
        # Update with new access token (refresh_token may or may not be returned)
        token_data['access_token'] = new_tokens['access_token']
        if 'refresh_token' in new_tokens:
            token_data['refresh_token'] = new_tokens['refresh_token']
        token_data['expires_in'] = new_tokens['expires_in']
        token_data['created_at'] = int(time.time())
        
        # Save updated tokens
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        os.chmod(token_path, 0o600)
        
        print("✓ Tokens refreshed successfully")
        print(json.dumps({
            'status': 'refreshed',
            'token_file': token_path,
            'expires_in': new_tokens['expires_in']
        }, indent=2))
    
    except Exception as e:
        print(f"✗ Error refreshing token: {e}")
        sys.exit(1)

def check_token_status():
    """Check token status"""
    token_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TOKEN_PATH
    token_path = os.path.expanduser(token_path)
    
    if not os.path.exists(token_path):
        print(json.dumps({
            'status': 'not_configured',
            'message': 'OAuth2 not configured. Run oauth-setup.py to set up.'
        }))
        sys.exit(1)
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        
        created_at = token_data.get('created_at', 0)
        expires_in = token_data.get('expires_in', 3600)
        expires_at = created_at + expires_in
        now = int(time.time())
        
        is_expired = now >= expires_at
        time_until_expiry = expires_at - now
        
        status = {
            'status': 'expired' if is_expired else 'valid',
            'token_file': token_path,
            'created_at': created_at,
            'expires_at': expires_at,
            'expires_in_seconds': time_until_expiry,
            'has_refresh_token': 'refresh_token' in token_data
        }
        
        print(json.dumps(status, indent=2))
        
        if is_expired:
            print("\n⚠️  Token has expired. Run 'python3 oauth-setup.py refresh' to refresh.", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "refresh":
            refresh_token_cmd()
        elif command == "status":
            check_token_status()
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python3 oauth-setup.py           # Initial setup")
            print("  python3 oauth-setup.py refresh [token_file]  # Refresh tokens")
            print("  python3 oauth-setup.py status [token_file]   # Check token status")
            sys.exit(1)
    else:
        setup_oauth2()
