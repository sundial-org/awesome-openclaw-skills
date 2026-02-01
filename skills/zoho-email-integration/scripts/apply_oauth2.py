#!/usr/bin/env python3
"""Apply OAuth2 functionality to zoho-email.py"""

import re

# Read the original file
with open('zoho-email-pre-oauth.py.backup', 'r') as f:
    content = f.read()

print("Applying OAuth2 modifications...")

# 1. Update the docstring
content = content.replace(
    '''"""
Zoho Email Tool for Clawdbot
Handles: Read, Search, Monitor, Send emails
"""''',
    '''"""
Zoho Email Tool for Clawdbot
Handles: Read, Search, Monitor, Send emails
Supports: App passwords and OAuth2 authentication
"""'''
)

# 2. Add time import
content = content.replace(
    'import base64\nfrom datetime import datetime, timedelta',
    'import base64\nimport time\nfrom datetime import datetime, timedelta'
)

# 3. Add OAuth2 settings after the port definitions
oauth_settings = '''

# OAuth2 settings
DEFAULT_TOKEN_PATH = os.path.expanduser('~/.zoho-mail-tokens.json')
ZOHO_TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token'
'''

content = content.replace(
    "# Timeouts\n",
    oauth_settings + "# Timeouts\n"
)

# 4. Add OAuth2 helper functions before the class definition
oauth_functions = '''
# OAuth2 Helper Functions
def load_oauth_tokens(token_path=DEFAULT_TOKEN_PATH):
    """Load OAuth2 tokens from file"""
    token_path = os.path.expanduser(token_path)
    
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}")
    
    try:
        with open(token_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load tokens: {e}")

def save_oauth_tokens(token_data, token_path=DEFAULT_TOKEN_PATH):
    """Save OAuth2 tokens to file"""
    token_path = os.path.expanduser(token_path)
    
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        # Set secure permissions
        os.chmod(token_path, 0o600)
    except Exception as e:
        raise Exception(f"Failed to save tokens: {e}")

def refresh_oauth_token(client_id, client_secret, refresh_token):
    """Refresh OAuth2 access token"""
    try:
        import urllib.request
        import urllib.error
        from urllib.parse import urlencode
        
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
    
    except Exception as e:
        raise Exception(f"Token refresh failed: {e}")

def generate_oauth2_string(user, access_token):
    """Generate OAuth2 authentication string for IMAP/SMTP"""
    auth_string = f"user={user}\\x01auth=Bearer {access_token}\\x01\\x01"
    return base64.b64encode(auth_string.encode()).decode()

def is_token_expired(token_data):
    """Check if access token is expired"""
    created_at = token_data.get('created_at', 0)
    expires_in = token_data.get('expires_in', 3600)
    expires_at = created_at + expires_in
    now = int(time.time())
    
    # Refresh if expired or expiring within 5 minutes
    return now >= (expires_at - 300)

'''

content = content.replace(
    '\nclass ZohoEmail:',
    '\n' + oauth_functions + 'class ZohoEmail:'
)

# 5. Replace the __init__ method
old_init = '''    def __init__(self, verbose=False):
        if not EMAIL or not PASSWORD:
            raise ValueError("ZOHO_EMAIL and ZOHO_PASSWORD environment variables must be set")
        
        self.email = EMAIL
        self.password = PASSWORD
        self.imap_server = IMAP_SERVER
        self.smtp_server = SMTP_SERVER
        self.imap = None
        self.verbose = verbose'''

new_init = '''    def __init__(self, verbose=False, auth_method='auto', token_file=None):
        """
        Initialize Zoho Email client
        
        Args:
            verbose: Enable debug logging
            auth_method: 'auto', 'password', or 'oauth2'
            token_file: Path to OAuth2 token file (for oauth2 auth)
        """
        self.verbose = verbose
        self.imap_server = IMAP_SERVER
        self.smtp_server = SMTP_SERVER
        self.imap = None
        
        # Determine authentication method
        self.auth_method = auth_method
        self.token_file = token_file or DEFAULT_TOKEN_PATH
        self.oauth_tokens = None
        
        if auth_method == 'auto':
            # Auto-detect: prefer OAuth2 if token file exists
            if os.path.exists(self.token_file):
                self.auth_method = 'oauth2'
                self.log(f"Auto-detected OAuth2 (token file: {self.token_file})")
            elif EMAIL and PASSWORD:
                self.auth_method = 'password'
                self.log("Auto-detected app password authentication")
            else:
                raise ValueError(
                    "No authentication method available. Set ZOHO_EMAIL/ZOHO_PASSWORD "
                    f"or configure OAuth2 (token file: {self.token_file})"
                )
        
        # Setup authentication
        if self.auth_method == 'oauth2':
            self._setup_oauth2()
        elif self.auth_method == 'password':
            self._setup_password()
        else:
            raise ValueError(f"Unknown auth method: {auth_method}")
    
    def _setup_password(self):
        """Setup app password authentication"""
        if not EMAIL or not PASSWORD:
            raise ValueError("ZOHO_EMAIL and ZOHO_PASSWORD environment variables must be set")
        
        self.email = EMAIL
        self.password = PASSWORD
        self.log("Using app password authentication")
    
    def _setup_oauth2(self):
        """Setup OAuth2 authentication"""
        try:
            self.oauth_tokens = load_oauth_tokens(self.token_file)
            
            # Validate token structure
            required_fields = ['access_token', 'refresh_token', 'client_id', 'client_secret']
            missing = [f for f in required_fields if f not in self.oauth_tokens]
            if missing:
                raise ValueError(f"Token file missing fields: {missing}")
            
            # Auto-refresh if needed
            if is_token_expired(self.oauth_tokens):
                self.log("Access token expired, refreshing...")
                self.refresh_token()
            
            # Extract email from token file or environment
            self.email = self.oauth_tokens.get('email') or EMAIL
            if not self.email:
                raise ValueError("Email address not found in token file or ZOHO_EMAIL env var")
            
            self.password = None  # Not used with OAuth2
            self.log(f"Using OAuth2 authentication for {self.email}")
        
        except FileNotFoundError:
            raise ValueError(
                f"OAuth2 token file not found: {self.token_file}\\n"
                "Run 'python3 scripts/oauth-setup.py' to configure OAuth2"
            )
        except Exception as e:
            raise ValueError(f"Failed to setup OAuth2: {e}")'''

content = content.replace(old_init, new_init)

# 6. Add OAuth2 methods after log method
oauth_methods = '''
    
    def refresh_token(self):
        """Refresh OAuth2 access token"""
        if self.auth_method != 'oauth2':
            raise ValueError("Token refresh only available with OAuth2 authentication")
        
        try:
            self.log("Refreshing OAuth2 token...")
            
            new_tokens = refresh_oauth_token(
                self.oauth_tokens['client_id'],
                self.oauth_tokens['client_secret'],
                self.oauth_tokens['refresh_token']
            )
            
            # Update tokens
            self.oauth_tokens['access_token'] = new_tokens['access_token']
            if 'refresh_token' in new_tokens:
                self.oauth_tokens['refresh_token'] = new_tokens['refresh_token']
            self.oauth_tokens['expires_in'] = new_tokens['expires_in']
            self.oauth_tokens['created_at'] = int(time.time())
            
            # Save updated tokens
            save_oauth_tokens(self.oauth_tokens, self.token_file)
            
            self.log("Token refreshed successfully")
            return True
        
        except Exception as e:
            raise Exception(f"Failed to refresh token: {e}")
    
    def revoke_token(self):
        """Revoke OAuth2 token (delete local token file)"""
        if self.auth_method != 'oauth2':
            raise ValueError("Token revocation only available with OAuth2 authentication")
        
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                self.log(f"Token file deleted: {self.token_file}")
                return True
            else:
                self.log("Token file does not exist")
                return False
        except Exception as e:
            raise Exception(f"Failed to revoke token: {e}")
    
    def get_token_status(self):
        """Get OAuth2 token status"""
        if self.auth_method != 'oauth2':
            return {
                'auth_method': self.auth_method,
                'status': 'not_using_oauth2'
            }
        
        created_at = self.oauth_tokens.get('created_at', 0)
        expires_in = self.oauth_tokens.get('expires_in', 3600)
        expires_at = created_at + expires_in
        now = int(time.time())
        
        return {
            'auth_method': 'oauth2',
            'status': 'expired' if is_token_expired(self.oauth_tokens) else 'valid',
            'token_file': self.token_file,
            'email': self.email,
            'created_at': created_at,
            'expires_at': expires_at,
            'expires_in_seconds': max(0, expires_at - now)
        }'''

content = content.replace(
    '    def log(self, message):\n        """Print debug messages if verbose mode is on"""\n        if self.verbose:\n            print(f"[DEBUG] {message}", file=sys.stderr)',
    '    def log(self, message):\n        """Print debug messages if verbose mode is on"""\n        if self.verbose:\n            print(f"[DEBUG] {message}", file=sys.stderr)' + oauth_methods
)

print("✓ Step 1-6: Added OAuth2 core functionality")

# 7. Update connect_imap to support OAuth2
old_connect = '''    def connect_imap(self):
        """Connect to IMAP server with timeout"""
        try:
            self.log(f"Connecting to {self.imap_server}:{IMAP_PORT}...")
            # Set socket timeout
            socket.setdefaulttimeout(IMAP_TIMEOUT)
            self.imap = imaplib.IMAP4_SSL(self.imap_server, IMAP_PORT)
            self.log("Logging in...")
            self.imap.login(self.email, self.password)
            self.log("Connected successfully")
            return self.imap
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"IMAP authentication failed: {e}")
        except socket.timeout:
            raise ConnectionError(f"Connection timeout after {IMAP_TIMEOUT}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IMAP: {e}")'''

new_connect = '''    def connect_imap(self):
        """Connect to IMAP server with timeout"""
        try:
            self.log(f"Connecting to {self.imap_server}:{IMAP_PORT}...")
            # Set socket timeout
            socket.setdefaulttimeout(IMAP_TIMEOUT)
            self.imap = imaplib.IMAP4_SSL(self.imap_server, IMAP_PORT)
            self.log("Logging in...")
            
            if self.auth_method == 'oauth2':
                # OAuth2 authentication
                # Check if token needs refresh
                if is_token_expired(self.oauth_tokens):
                    self.log("Token expired, refreshing before login...")
                    self.refresh_token()
                
                auth_string = generate_oauth2_string(self.email, self.oauth_tokens['access_token'])
                self.imap.authenticate('XOAUTH2', lambda x: auth_string)
                self.log("OAuth2 authentication successful")
            else:
                # App password authentication
                self.imap.login(self.email, self.password)
                self.log("Password authentication successful")
            
            self.log("Connected successfully")
            return self.imap
        except imaplib.IMAP4.error as e:
            error_msg = str(e)
            if self.auth_method == 'oauth2' and 'AUTHENTICATE failed' in error_msg:
                raise ConnectionError(
                    f"IMAP OAuth2 authentication failed: {e}\\n"
                    "Token may be invalid. Try: python3 scripts/zoho-email.py oauth-login"
                )
            raise ConnectionError(f"IMAP authentication failed: {e}")
        except socket.timeout:
            raise ConnectionError(f"Connection timeout after {IMAP_TIMEOUT}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IMAP: {e}")'''

content = content.replace(old_connect, new_connect)

print("✓ Step 7: Updated connect_imap")

# 8. Add _smtp_login method and update SMTP functions
smtp_login = '''    
    def _smtp_login(self, server):
        """Login to SMTP server (handles OAuth2 and password)"""
        if self.auth_method == 'oauth2':
            # Check if token needs refresh
            if is_token_expired(self.oauth_tokens):
                self.log("Token expired, refreshing before SMTP login...")
                self.refresh_token()
            
            auth_string = generate_oauth2_string(self.email, self.oauth_tokens['access_token'])
            server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
            self.log("SMTP OAuth2 authentication successful")
        else:
            server.login(self.email, self.password)
            self.log("SMTP password authentication successful")
    '''

# Insert before send_email_with_attachment
content = content.replace(
    '    def send_email_with_attachment(',
    smtp_login + 'def send_email_with_attachment('
)

# Fix indentation
content = content.replace(
    smtp_login + 'def send_email_with_attachment(',
    smtp_login + '    def send_email_with_attachment('
)

# Update send_email_with_attachment to use _smtp_login
content = content.replace(
    '            with smtplib.SMTP_SSL(self.smtp_server, SMTP_PORT) as server:\n                server.login(self.email, self.password)\n                server.send_message(msg)',
    '            with smtplib.SMTP_SSL(self.smtp_server, SMTP_PORT) as server:\n                self._smtp_login(server)\n                server.send_message(msg)'
)

# Update send_email to use _smtp_login and add auth_method to return
content = content.replace(
    '            return {"status": "sent", "to": to, "subject": subject, "html": bool(html_body)}',
    '            return {"status": "sent", "to": to, "subject": subject, "html": bool(html_body), "auth_method": self.auth_method}'
)

print("✓ Step 8: Updated SMTP authentication")

# Write the modified content
with open('zoho-email.py', 'w') as f:
    f.write(content)

print("✓ OAuth2 core functionality applied successfully!")
print("✓ File written to: zoho-email.py")
print("\\nNext: Run apply_oauth2_cli.py to add CLI support")
