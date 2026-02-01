#!/usr/bin/env python3
"""
Zoho Email Tool for Clawdbot
Handles: Read, Search, Monitor, Send emails
Supports: App passwords and OAuth2 authentication
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
import json
import sys
import os
import socket
import base64
import time
from datetime import datetime, timedelta

# Load credentials from environment variables
EMAIL = os.environ.get('ZOHO_EMAIL')
PASSWORD = os.environ.get('ZOHO_PASSWORD')
IMAP_SERVER = os.environ.get('ZOHO_IMAP', 'imap.zoho.com')
SMTP_SERVER = os.environ.get('ZOHO_SMTP', 'smtp.zoho.com')
IMAP_PORT = int(os.environ.get('ZOHO_IMAP_PORT', '993'))
SMTP_PORT = int(os.environ.get('ZOHO_SMTP_PORT', '465'))



# OAuth2 settings
DEFAULT_TOKEN_PATH = os.path.expanduser('~/.zoho-mail-tokens.json')
ZOHO_TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token'
# Timeouts
IMAP_TIMEOUT = int(os.environ.get('ZOHO_TIMEOUT', '30'))
DEFAULT_SEARCH_DAYS = int(os.environ.get('ZOHO_SEARCH_DAYS', '30'))


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
    auth_string = f"user={user}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()

def is_token_expired(token_data):
    """Check if access token is expired"""
    created_at = token_data.get('created_at', 0)
    expires_in = token_data.get('expires_in', 3600)
    expires_at = created_at + expires_in
    now = int(time.time())
    
    # Refresh if expired or expiring within 5 minutes
    return now >= (expires_at - 300)

def has_requests_library():
    """Check if requests library is available"""
    try:
        import requests
        return True
    except ImportError:
        return False

class ZohoRestAPIClient:
    """Zoho Mail REST API Client with OAuth2 authentication"""
    
    def __init__(self, token_file=DEFAULT_TOKEN_PATH, verbose=False):
        """
        Initialize REST API client
        
        Args:
            token_file: Path to OAuth2 token file
            verbose: Enable debug logging
        """
        self.verbose = verbose
        self.token_file = token_file
        self.base_url = os.environ.get('ZOHO_API_BASE_URL', 'https://mail.zoho.com/api')
        self.account_id = None
        self.session = None
        
        # Load tokens
        self.tokens = load_oauth_tokens(token_file)
        
        # Create session for connection pooling
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'ZohoEmailClient/2.0'
            })
        except ImportError:
            raise Exception("requests library required for REST API mode. Install: pip install requests")
        
        self.log("REST API client initialized")
    
    def log(self, message):
        """Print debug messages if verbose mode is on"""
        if self.verbose:
            print(f"[REST API] {message}", file=sys.stderr)
    
    def _refresh_token_if_needed(self):
        """Check and refresh access token if expired"""
        if is_token_expired(self.tokens):
            self.log("Access token expired, refreshing...")
            
            new_tokens = refresh_oauth_token(
                self.tokens['client_id'],
                self.tokens['client_secret'],
                self.tokens['refresh_token']
            )
            
            # Update tokens
            self.tokens['access_token'] = new_tokens['access_token']
            if 'refresh_token' in new_tokens:
                self.tokens['refresh_token'] = new_tokens['refresh_token']
            self.tokens['expires_in'] = new_tokens['expires_in']
            self.tokens['created_at'] = int(time.time())
            
            # Save updated tokens
            save_oauth_tokens(self.tokens, self.token_file)
            self.log("Token refreshed successfully")
    
    def _make_request(self, method, endpoint, **kwargs):
        """
        Make HTTP request with OAuth2 authentication and retries
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/messages')
            **kwargs: Additional arguments for requests (params, json, etc.)
        
        Returns:
            Response JSON data
        """
        # Ensure token is valid
        self._refresh_token_if_needed()
        
        # Build URL
        if not endpoint.startswith('http'):
            url = f"{self.base_url}{endpoint}"
        else:
            url = endpoint
        
        # Add OAuth2 bearer token
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {self.tokens['access_token']}"
        
        max_retries = int(os.environ.get('ZOHO_MAX_RETRIES', '3'))
        retry_delay = float(os.environ.get('ZOHO_API_RATE_DELAY', '0.5'))
        
        for attempt in range(max_retries):
            try:
                self.log(f"{method} {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=int(os.environ.get('ZOHO_API_TIMEOUT', '30')),
                    **kwargs
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', retry_delay * (attempt + 1)))
                    self.log(f"Rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                # Handle token expiration
                if response.status_code == 401:
                    self.log("Token invalid, refreshing...")
                    self._refresh_token_if_needed()
                    headers['Authorization'] = f"Bearer {self.tokens['access_token']}"
                    continue
                
                # Raise for other HTTP errors
                response.raise_for_status()
                
                # Rate limiting delay
                time.sleep(retry_delay)
                
                # Return JSON response
                if response.content:
                    return response.json()
                else:
                    return {}
            
            except Exception as e:
                self.log(f"Request failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"API request failed after {max_retries} attempts: {e}")
                time.sleep(retry_delay * (attempt + 1))
        
        raise Exception("Max retries exceeded")
    
    def get_account_id(self):
        """Get Zoho Mail account ID"""
        if self.account_id:
            return self.account_id
        
        self.log("Fetching account ID...")
        response = self._make_request('GET', '/accounts')
        
        if response.get('status', {}).get('code') == 200:
            accounts = response.get('data', [])
            if accounts:
                self.account_id = accounts[0]['accountId']
                self.log(f"Account ID: {self.account_id}")
                return self.account_id
        
        raise Exception("Failed to get account ID")
    
    def list_messages(self, folder='Inbox', limit=100, search_query=None, status=None):
        """
        List messages in a folder with optional filtering or searching
        
        Args:
            folder: Folder name (default: 'Inbox')
            limit: Maximum messages to return
            search_query: Zoho Mail search syntax (e.g., 'entire:keyword', 'subject:test')
                         If provided, uses /messages/search endpoint
            status: Filter by read status: 'read', 'unread', or 'all' (default: 'all')
                   Only applies to /messages/view endpoint
        
        Returns:
            List of message dictionaries
        """
        account_id = self.get_account_id()
        
        # If search_query is provided, use the /messages/search endpoint
        if search_query:
            params = {
                'searchKey': search_query,
                'limit': limit,
                'start': 1
            }
            
            self.log(f"Searching messages with query: {search_query} (limit={limit})")
            response = self._make_request(
                'GET',
                f'/accounts/{account_id}/messages/search',
                params=params
            )
        else:
            # Otherwise use the /messages/view endpoint with status filter
            params = {
                'limit': limit,
                'sortBy': 'date',  # Valid values: date, messageId, size
                'sortorder': False  # False = descending, True = ascending
            }
            
            if status:
                params['status'] = status
            
            self.log(f"Listing messages in {folder} (limit={limit}, status={status or 'all'})")
            response = self._make_request(
                'GET',
                f'/accounts/{account_id}/messages/view',
                params=params
            )
        
        if response.get('status', {}).get('code') == 200:
            return response.get('data', [])
        
        return []
    
    def get_message(self, message_id):
        """Get specific message by ID"""
        account_id = self.get_account_id()
        
        self.log(f"Getting message {message_id}")
        response = self._make_request(
            'GET',
            f'/accounts/{account_id}/messages/{message_id}'
        )
        
        if response.get('status', {}).get('code') == 200:
            return response.get('data', {})
        
        raise Exception(f"Failed to get message {message_id}")
    
    def send_message(self, to, subject, body, html_body=None, cc=None, bcc=None):
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
        
        Returns:
            Send status dictionary
        """
        account_id = self.get_account_id()
        
        # Build message payload
        payload = {
            'fromAddress': self.tokens.get('email', EMAIL),
            'toAddress': to,
            'subject': subject,
            'content': html_body if html_body else body,
            'mailFormat': 'html' if html_body else 'plaintext'
        }
        
        if cc:
            payload['ccAddress'] = cc
        if bcc:
            payload['bccAddress'] = bcc
        
        self.log(f"Sending email to {to}")
        response = self._make_request(
            'POST',
            f'/accounts/{account_id}/messages',
            json=payload
        )
        
        if response.get('status', {}).get('code') == 200:
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "message_id": response.get('data', {}).get('messageId')
            }
        
        raise Exception("Failed to send email")
    
    def mark_as_read(self, message_ids):
        """Mark messages as read"""
        if not message_ids:
            return {"success": [], "failed": []}
        
        account_id = self.get_account_id()
        
        # Convert to list of ints if they're strings
        message_id_list = [int(mid) if isinstance(mid, str) else mid for mid in message_ids]
        
        try:
            self.log(f"Marking {len(message_id_list)} message(s) as read")
            response = self._make_request(
                'PUT',
                f'/accounts/{account_id}/updatemessage',
                json={
                    'mode': 'markAsRead',
                    'messageId': message_id_list
                }
            )
            
            if response.get('status', {}).get('code') == 200:
                return {"success": message_ids, "failed": []}
            else:
                return {"success": [], "failed": message_ids}
        except Exception as e:
            self.log(f"Failed to mark messages as read: {e}")
            return {"success": [], "failed": message_ids}
    
    def mark_as_unread(self, message_ids):
        """Mark messages as unread"""
        if not message_ids:
            return {"success": [], "failed": []}
        
        account_id = self.get_account_id()
        
        # Convert to list of ints if they're strings
        message_id_list = [int(mid) if isinstance(mid, str) else mid for mid in message_ids]
        
        try:
            self.log(f"Marking {len(message_id_list)} message(s) as unread")
            response = self._make_request(
                'PUT',
                f'/accounts/{account_id}/updatemessage',
                json={
                    'mode': 'markAsUnread',
                    'messageId': message_id_list
                }
            )
            
            if response.get('status', {}).get('code') == 200:
                return {"success": message_ids, "failed": []}
            else:
                return {"success": [], "failed": message_ids}
        except Exception as e:
            self.log(f"Failed to mark messages as unread: {e}")
            return {"success": [], "failed": message_ids}
    
    def delete_messages(self, message_ids, folder_name='INBOX'):
        """Delete messages (move to trash)"""
        if not message_ids:
            return {"success": [], "failed": []}
        
        account_id = self.get_account_id()
        
        # Get folder ID from folder name
        folders = self.list_folders()
        folder_id = None
        for folder in folders:
            if folder.get('folderName', '').upper() == folder_name.upper():
                folder_id = folder.get('folderId')
                break
        
        if not folder_id:
            self.log(f"Error: Folder '{folder_name}' not found")
            return {"success": [], "failed": message_ids}
        
        results = {"success": [], "failed": []}
        
        for message_id in message_ids:
            try:
                self.log(f"Deleting message {message_id} from folder {folder_name}")
                response = self._make_request(
                    'DELETE',
                    f'/accounts/{account_id}/folders/{folder_id}/messages/{message_id}'
                )
                
                if response.get('status', {}).get('code') == 200:
                    results["success"].append(message_id)
                else:
                    results["failed"].append(message_id)
            except Exception as e:
                self.log(f"Failed to delete {message_id}: {e}")
                results["failed"].append(message_id)
        
        return results
    
    def move_messages(self, message_ids, folder_name):
        """Move messages to another folder"""
        if not message_ids:
            return {"success": [], "failed": []}
        
        account_id = self.get_account_id()
        
        # Get folder ID from folder name
        folders = self.list_folders()
        folder_id = None
        for folder in folders:
            if folder.get('folderName', '').upper() == folder_name.upper():
                folder_id = folder.get('folderId')
                break
        
        if not folder_id:
            self.log(f"Error: Folder '{folder_name}' not found")
            return {"success": [], "failed": message_ids}
        
        # Convert to list of ints if they're strings
        message_id_list = [int(mid) if isinstance(mid, str) else mid for mid in message_ids]
        
        try:
            self.log(f"Moving {len(message_id_list)} message(s) to folder {folder_name}")
            response = self._make_request(
                'PUT',
                f'/accounts/{account_id}/updatemessage',
                json={
                    'mode': 'moveMessage',
                    'messageId': message_id_list,
                    'destfolderId': int(folder_id)
                }
            )
            
            if response.get('status', {}).get('code') == 200:
                return {"success": message_ids, "failed": []}
            else:
                return {"success": [], "failed": message_ids}
        except Exception as e:
            self.log(f"Failed to move messages: {e}")
            return {"success": [], "failed": message_ids}
    
    def list_folders(self):
        """List all folders"""
        account_id = self.get_account_id()
        
        self.log("Listing folders")
        response = self._make_request(
            'GET',
            f'/accounts/{account_id}/folders'
        )
        
        if response.get('status', {}).get('code') == 200:
            return response.get('data', [])
        
        return []

class ZohoEmail:
    def __init__(self, verbose=False, auth_method='auto', token_file=None, api_mode='auto'):
        """
        Initialize Zoho Email client
        
        Args:
            verbose: Enable debug logging
            auth_method: 'auto', 'password', or 'oauth2'
            token_file: Path to OAuth2 token file (for oauth2 auth)
            api_mode: 'auto', 'rest', or 'imap' - API mode to use
        """
        self.verbose = verbose
        self.imap_server = IMAP_SERVER
        self.smtp_server = SMTP_SERVER
        self.imap = None
        self.rest_client = None
        self.api_mode = None
        
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
        
        # Determine API mode (REST vs IMAP/SMTP)
        if api_mode == 'auto':
            # Auto-detect: prefer REST if OAuth2 is available and requests library installed
            if self.auth_method == 'oauth2' and has_requests_library():
                self.api_mode = 'rest'
                try:
                    self.rest_client = ZohoRestAPIClient(self.token_file, verbose=verbose)
                    self.log("Using REST API mode")
                except Exception as e:
                    self.log(f"REST API initialization failed: {e}, falling back to IMAP")
                    self.api_mode = 'imap'
            else:
                self.api_mode = 'imap'
                self.log("Using IMAP/SMTP mode")
        elif api_mode == 'rest':
            # Force REST mode
            if self.auth_method != 'oauth2':
                raise ValueError("REST API mode requires OAuth2 authentication")
            if not has_requests_library():
                raise ValueError("REST API mode requires 'requests' library. Install: pip install requests")
            self.api_mode = 'rest'
            self.rest_client = ZohoRestAPIClient(self.token_file, verbose=verbose)
            self.log("Forced REST API mode")
        elif api_mode == 'imap':
            # Force IMAP mode
            self.api_mode = 'imap'
            self.log("Forced IMAP/SMTP mode")
        else:
            raise ValueError(f"Unknown api_mode: {api_mode}. Use 'auto', 'rest', or 'imap'")
    
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
                f"OAuth2 token file not found: {self.token_file}\n"
                "Run 'python3 scripts/oauth-setup.py' to configure OAuth2"
            )
        except Exception as e:
            raise ValueError(f"Failed to setup OAuth2: {e}")
    
    def log(self, message):
        """Print debug messages if verbose mode is on"""
        if self.verbose:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
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
        }
    
    def connect_imap(self):
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
                    f"IMAP OAuth2 authentication failed: {e}\n"
                    "Token may be invalid. Try: python3 scripts/zoho-email.py oauth-login"
                )
            raise ConnectionError(f"IMAP authentication failed: {e}")
        except socket.timeout:
            raise ConnectionError(f"Connection timeout after {IMAP_TIMEOUT}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IMAP: {e}")
    
    def disconnect_imap(self):
        """Safely disconnect from IMAP"""
        if self.imap:
            try:
                self.imap.close()
            except:
                pass
            try:
                self.imap.logout()
            except:
                pass
            self.imap = None
    
    def decode_subject(self, subject):
        """Decode email subject"""
        if not subject:
            return ""
        
        try:
            decoded = decode_header(subject)
            subject_parts = []
            for part, encoding in decoded:
                if isinstance(part, bytes):
                    subject_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
                else:
                    subject_parts.append(str(part))
            return ''.join(subject_parts)
        except Exception as e:
            self.log(f"Failed to decode subject: {e}")
            return str(subject)
    
    def get_email_body(self, msg):
        """Extract email body from message"""
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                        except:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = str(msg.get_payload())
        except Exception as e:
            self.log(f"Failed to extract body: {e}")
            body = "[Error extracting body]"
        
        return body
    
    def search_emails(self, folder="INBOX", query="ALL", limit=10, search_days=None):
        """Search emails in a folder"""
        search_days = search_days or DEFAULT_SEARCH_DAYS
        
        if self.api_mode == 'rest':
            try:
                # Convert IMAP query to Zoho Mail REST API search syntax
                search_query = None
                if query != "ALL":
                    # Convert common IMAP queries to Zoho Mail search syntax
                    # Examples: 
                    #   IMAP: SUBJECT "test" -> Zoho: subject:test
                    #   IMAP: FROM "user@example.com" -> Zoho: sender:user@example.com
                    if query.startswith('SUBJECT "') and query.endswith('"'):
                        keyword = query[9:-1]  # Extract keyword from SUBJECT "keyword"
                        search_query = f'subject:{keyword}'
                    elif query.startswith('FROM "') and query.endswith('"'):
                        sender = query[6:-1]  # Extract sender from FROM "sender"
                        search_query = f'sender:{sender}'
                    else:
                        # Default: search entire email for the keyword
                        search_query = f'entire:{query}'
                
                messages = self.rest_client.list_messages(folder=folder, limit=limit, search_query=search_query)
                
                # Convert REST API response to match IMAP format
                results = []
                for msg in messages:
                    results.append({
                        "id": msg.get('messageId', ''),
                        "subject": msg.get('subject', ''),
                        "from": msg.get('fromAddress', ''),
                        "to": msg.get('toAddress', ''),
                        "date": msg.get('receivedTime', ''),
                        "body": (msg.get('summary', '') or '')[:500] + "..." if len(msg.get('summary', '') or '') > 500 else (msg.get('summary', '') or '')
                    })
                
                self.log(f"Found {len(results)} emails via REST API")
                return results
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=True)
            
            # Add date filter for performance
            if search_days > 0 and query != "ALL":
                since_date = (datetime.now() - timedelta(days=search_days)).strftime("%d-%b-%Y")
                query = f'({query} SINCE {since_date})'
                self.log(f"Search query: {query}")
            
            status, messages = self.imap.search(None, query)
            
            if status != 'OK':
                raise Exception(f"Search failed: {status}")
            
            email_ids = messages[0].split()
            self.log(f"Found {len(email_ids)} emails, returning last {limit}")
            
            results = []
            for email_id in email_ids[-limit:]:  # Get last N emails
                try:
                    status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            subject = self.decode_subject(msg.get("Subject", ""))
                            from_addr = msg.get("From", "")
                            to_addr = msg.get("To", "")
                            date = msg.get("Date", "")
                            body = self.get_email_body(msg)
                            
                            results.append({
                                "id": email_id.decode(),
                                "subject": subject,
                                "from": from_addr,
                                "to": to_addr,
                                "date": date,
                                "body": body[:500] + "..." if len(body) > 500 else body
                            })
                except Exception as e:
                    self.log(f"Error fetching email {email_id}: {e}")
                    continue
            
            return results
        
        finally:
            self.disconnect_imap()
    
    def get_email(self, folder="INBOX", email_id=None):
        """Get a specific email by ID"""
        if not email_id:
            raise ValueError("email_id is required")
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=True)
            
            status, msg_data = self.imap.fetch(str(email_id).encode(), '(RFC822)')
            
            if status != 'OK':
                raise Exception(f"Fetch failed: {status}")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = self.decode_subject(msg.get("Subject", ""))
                    from_addr = msg.get("From", "")
                    to_addr = msg.get("To", "")
                    date = msg.get("Date", "")
                    body = self.get_email_body(msg)
                    
                    return {
                        "subject": subject,
                        "from": from_addr,
                        "to": to_addr,
                        "date": date,
                        "body": body
                    }
            
            raise Exception("Email not found")
        
        finally:
            self.disconnect_imap()
    
    def get_attachments(self, folder="INBOX", email_id=None):
        """List attachments for a specific email"""
        if not email_id:
            raise ValueError("email_id is required")
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=True)
            
            status, msg_data = self.imap.fetch(str(email_id).encode(), '(RFC822)')
            
            if status != 'OK':
                raise Exception(f"Fetch failed: {status}")
            
            attachments = []
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    attachment_index = 0
                    for part in msg.walk():
                        # Skip multipart containers
                        if part.get_content_maintype() == 'multipart':
                            continue
                        
                        # Skip text/plain and text/html parts (body)
                        if part.get_content_type() in ['text/plain', 'text/html']:
                            continue
                        
                        # Check if this is an attachment
                        filename = part.get_filename()
                        if filename:
                            # Decode filename if needed
                            decoded = decode_header(filename)
                            filename_parts = []
                            for part_data, encoding in decoded:
                                if isinstance(part_data, bytes):
                                    filename_parts.append(part_data.decode(encoding or 'utf-8', errors='ignore'))
                                else:
                                    filename_parts.append(str(part_data))
                            filename = ''.join(filename_parts)
                            
                            attachments.append({
                                "index": attachment_index,
                                "filename": filename,
                                "content_type": part.get_content_type(),
                                "size": len(part.get_payload(decode=True) or b'')
                            })
                            attachment_index += 1
            
            return attachments
        
        finally:
            self.disconnect_imap()
    
    def download_attachment(self, folder="INBOX", email_id=None, attachment_index=0, output_path=None):
        """Download a specific attachment from an email by index"""
        if not email_id:
            raise ValueError("email_id is required")
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=True)
            
            status, msg_data = self.imap.fetch(str(email_id).encode(), '(RFC822)')
            
            if status != 'OK':
                raise Exception(f"Fetch failed: {status}")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    current_index = 0
                    for part in msg.walk():
                        # Skip multipart containers
                        if part.get_content_maintype() == 'multipart':
                            continue
                        
                        # Skip text/plain and text/html parts (body)
                        if part.get_content_type() in ['text/plain', 'text/html']:
                            continue
                        
                        # Check if this is an attachment
                        filename = part.get_filename()
                        if filename:
                            if current_index == attachment_index:
                                # Decode filename
                                decoded = decode_header(filename)
                                filename_parts = []
                                for part_data, encoding in decoded:
                                    if isinstance(part_data, bytes):
                                        filename_parts.append(part_data.decode(encoding or 'utf-8', errors='ignore'))
                                    else:
                                        filename_parts.append(str(part_data))
                                filename = ''.join(filename_parts)
                                
                                # Get attachment data
                                payload = part.get_payload(decode=True)
                                
                                # Determine output path
                                if not output_path:
                                    output_path = filename
                                
                                # Write to file
                                self.log(f"Saving attachment to {output_path}")
                                with open(output_path, 'wb') as f:
                                    f.write(payload)
                                
                                return {
                                    "filename": filename,
                                    "output_path": output_path,
                                    "size": len(payload),
                                    "content_type": part.get_content_type()
                                }
                            
                            current_index += 1
            
            raise Exception(f"Attachment index {attachment_index} not found")
        
        finally:
            self.disconnect_imap()
    
    
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
    
    def send_email_with_attachment(self, to, subject, body, attachments=None, cc=None, bcc=None, html_body=None):
        """Send an email with one or more attachments via SMTP
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
        
        Returns:
            dict: Status information
        """
        try:
            msg = MIMEMultipart('mixed')
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc
            
            # Create alternative part for text/html if html_body is provided
            if html_body:
                msg_alternative = MIMEMultipart('alternative')
                msg_alternative.attach(MIMEText(body, 'plain'))
                msg_alternative.attach(MIMEText(html_body, 'html'))
                msg.attach(msg_alternative)
            else:
                # Attach plain text body
                msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Attachment not found: {file_path}")
                    
                    self.log(f"Attaching file: {file_path}")
                    
                    # Read file
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Create MIME part
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    
                    # Add header
                    filename = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    
                    msg.attach(part)
            
            self.log(f"Sending email with {len(attachments or [])} attachment(s) to {to}...")
            socket.setdefaulttimeout(IMAP_TIMEOUT)
            
            with smtplib.SMTP_SSL(self.smtp_server, SMTP_PORT) as server:
                self._smtp_login(server)
                server.send_message(msg)
            
            self.log("Email with attachments sent successfully")
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "attachments": len(attachments or [])
            }
        
        except Exception as e:
            raise Exception(f"Failed to send email with attachments: {e}")
    
    def send_email(self, to, subject, body, cc=None, bcc=None, html_body=None):
        """Send an email via SMTP or REST API
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body (required)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional). When provided, sends as multipart/alternative
        
        Returns:
            dict: Status information
        """
        if self.api_mode == 'rest':
            try:
                return self.rest_client.send_message(to, subject, body, html_body, cc, bcc)
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to SMTP")
                # Fall through to SMTP mode
        
        try:
            msg = MIMEMultipart('alternative') if html_body else MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc
            
            # Attach plain text version (always include)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
                self.log("Sending multipart email (plain + HTML)")
            else:
                self.log("Sending plain text email")
            
            self.log(f"Sending email to {to}...")
            socket.setdefaulttimeout(IMAP_TIMEOUT)
            
            with smtplib.SMTP_SSL(self.smtp_server, SMTP_PORT) as server:
                self._smtp_login(server)
                server.send_message(msg)
            
            self.log("Email sent successfully")
            return {"status": "sent", "to": to, "subject": subject, "html": bool(html_body), "auth_method": self.auth_method}
        
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")
    
    def send_html_email(self, to, subject, html_body, text_body=None, cc=None, bcc=None):
        """Convenience method to send HTML email with auto-generated plain text fallback
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML body content
            text_body: Plain text body (optional, auto-generated if not provided)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
        
        Returns:
            dict: Status information
        """
        import re
        
        # Auto-generate plain text version if not provided
        if text_body is None:
            # Strip HTML tags for a basic plain text version
            text_body = re.sub('<[^<]+?>', '', html_body)
            # Clean up extra whitespace
            text_body = re.sub(r'\n\s*\n', '\n\n', text_body)
            text_body = text_body.strip()
            self.log("Auto-generated plain text fallback from HTML")
        
        return self.send_email(to, subject, text_body, cc=cc, bcc=bcc, html_body=html_body)
    
    def get_unread_count(self, folder="INBOX"):
        """Get count of unread emails"""
        if self.api_mode == 'rest':
            try:
                # Use status='unread' parameter, not searchKey
                messages = self.rest_client.list_messages(folder=folder, limit=1000, status='unread')
                unread_count = len(messages)
                self.log(f"Found {unread_count} unread emails (REST API)")
                return unread_count
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Checking unread in {folder}...")
            self.imap.select(folder, readonly=True)
            
            status, messages = self.imap.search(None, 'UNSEEN')
            
            if status != 'OK':
                raise Exception(f"Unread check failed: {status}")
            
            unread_count = len(messages[0].split())
            self.log(f"Found {unread_count} unread emails")
            
            return unread_count
        
        finally:
            self.disconnect_imap()
    
    def mark_as_read(self, email_ids, folder="INBOX"):
        """Mark multiple emails as read"""
        if not email_ids:
            raise ValueError("email_ids list cannot be empty")
        
        if self.api_mode == 'rest':
            try:
                return self.rest_client.mark_as_read(email_ids)
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=False)
            
            results = {"success": [], "failed": []}
            
            for email_id in email_ids:
                try:
                    status, _ = self.imap.store(str(email_id).encode(), '+FLAGS', '\\Seen')
                    if status == 'OK':
                        self.log(f"Marked {email_id} as read")
                        results["success"].append(email_id)
                    else:
                        self.log(f"Failed to mark {email_id} as read")
                        results["failed"].append(email_id)
                except Exception as e:
                    self.log(f"Error marking {email_id} as read: {e}")
                    results["failed"].append(email_id)
            
            return results
        
        finally:
            self.disconnect_imap()
    
    def mark_as_unread(self, email_ids, folder="INBOX"):
        """Mark multiple emails as unread"""
        if not email_ids:
            raise ValueError("email_ids list cannot be empty")
        
        if self.api_mode == 'rest':
            try:
                return self.rest_client.mark_as_unread(email_ids)
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=False)
            
            results = {"success": [], "failed": []}
            
            for email_id in email_ids:
                try:
                    status, _ = self.imap.store(str(email_id).encode(), '-FLAGS', '\\Seen')
                    if status == 'OK':
                        self.log(f"Marked {email_id} as unread")
                        results["success"].append(email_id)
                    else:
                        self.log(f"Failed to mark {email_id} as unread")
                        results["failed"].append(email_id)
                except Exception as e:
                    self.log(f"Error marking {email_id} as unread: {e}")
                    results["failed"].append(email_id)
            
            return results
        
        finally:
            self.disconnect_imap()
    
    def delete_emails(self, email_ids, folder="INBOX"):
        """Move multiple emails to Trash (mark as Deleted)"""
        if not email_ids:
            raise ValueError("email_ids list cannot be empty")
        
        if self.api_mode == 'rest':
            try:
                return self.rest_client.delete_messages(email_ids, folder_name=folder)
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Selecting folder: {folder}")
            self.imap.select(folder, readonly=False)
            
            results = {"success": [], "failed": []}
            
            for email_id in email_ids:
                try:
                    status, _ = self.imap.store(str(email_id).encode(), '+FLAGS', '\\Deleted')
                    if status == 'OK':
                        self.log(f"Marked {email_id} for deletion")
                        results["success"].append(email_id)
                    else:
                        self.log(f"Failed to delete {email_id}")
                        results["failed"].append(email_id)
                except Exception as e:
                    self.log(f"Error deleting {email_id}: {e}")
                    results["failed"].append(email_id)
            
            # Expunge to permanently delete
            self.imap.expunge()
            self.log("Expunged deleted emails")
            
            return results
        
        finally:
            self.disconnect_imap()
    
    def move_emails(self, email_ids, target_folder, source_folder="INBOX"):
        """Move multiple emails to another folder"""
        if not email_ids:
            raise ValueError("email_ids list cannot be empty")
        if not target_folder:
            raise ValueError("target_folder is required")
        
        if self.api_mode == 'rest':
            try:
                return self.rest_client.move_messages(email_ids, target_folder)
            except Exception as e:
                self.log(f"REST API failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        try:
            self.connect_imap()
            self.log(f"Selecting source folder: {source_folder}")
            self.imap.select(source_folder, readonly=False)
            
            results = {"success": [], "failed": []}
            
            for email_id in email_ids:
                try:
                    # Copy to target folder
                    status, _ = self.imap.copy(str(email_id).encode(), target_folder)
                    if status == 'OK':
                        # Mark original as deleted
                        self.imap.store(str(email_id).encode(), '+FLAGS', '\\Deleted')
                        self.log(f"Moved {email_id} to {target_folder}")
                        results["success"].append(email_id)
                    else:
                        self.log(f"Failed to move {email_id}")
                        results["failed"].append(email_id)
                except Exception as e:
                    self.log(f"Error moving {email_id}: {e}")
                    results["failed"].append(email_id)
            
            # Expunge to complete the move
            self.imap.expunge()
            self.log("Completed move operation")
            
            return results
        
        finally:
            self.disconnect_imap()
    
    def _convert_imap_search_to_rest(self, imap_query):
        """Convert IMAP search query to Zoho REST API search syntax
        
        Args:
            imap_query: IMAP search query (e.g., 'SUBJECT "test"', 'FROM user@example.com')
        
        Returns:
            Zoho REST API search query (e.g., 'subject:test', 'from:user@example.com')
        """
        # Remove parentheses and extra whitespace
        query = imap_query.strip('() ')
        
        # Handle common IMAP search patterns
        conversions = {
            r'SUBJECT\s+"([^"]+)"': r'subject:\1',
            r'SUBJECT\s+(\S+)': r'subject:\1',
            r'FROM\s+"([^"]+)"': r'from:\1',
            r'FROM\s+(\S+)': r'from:\1',
            r'TO\s+"([^"]+)"': r'to:\1',
            r'TO\s+(\S+)': r'to:\1',
            r'BODY\s+"([^"]+)"': r'entire:\1',
            r'BODY\s+(\S+)': r'entire:\1',
            r'TEXT\s+"([^"]+)"': r'entire:\1',
            r'TEXT\s+(\S+)': r'entire:\1',
        }
        
        import re
        for pattern, replacement in conversions.items():
            query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
        
        # Remove SINCE date filters (handled separately)
        query = re.sub(r'\s*SINCE\s+\S+', '', query, flags=re.IGNORECASE)
        
        return query.strip()
    
    def bulk_action(self, query, action, folder="INBOX", limit=100, search_days=None, dry_run=False):
        """Perform bulk action on emails matching a search query
        
        Args:
            query: IMAP search query
            action: 'mark-read', 'mark-unread', 'delete', or 'move'
            folder: Source folder to search
            limit: Maximum emails to process
            search_days: Limit search to recent N days
            dry_run: If True, only show what would be done
        
        Returns:
            Dict with matched emails and action results
        """
        search_days = search_days or DEFAULT_SEARCH_DAYS
        
        # Try REST API first if available
        if self.api_mode == 'rest':
            try:
                self.log("Using REST API for bulk action")
                
                # Convert IMAP query to REST API search syntax
                rest_query = self._convert_imap_search_to_rest(query)
                self.log(f"Converted search query: '{query}' -> '{rest_query}'")
                
                # Search messages using REST API
                messages = self.rest_client.list_messages(
                    folder=folder,
                    limit=limit,
                    search_query=rest_query
                )
                
                total_found = len(messages)
                self.log(f"Found {total_found} emails via REST API")
                
                if dry_run:
                    # Return preview of what would be affected
                    previews = []
                    for msg in messages[:10]:  # Show first 10 as preview
                        previews.append({
                            "id": msg.get("messageId", ""),
                            "subject": msg.get("subject", ""),
                            "from": msg.get("fromAddress", ""),
                            "date": msg.get("receivedTime", "")
                        })
                    
                    return {
                        "dry_run": True,
                        "total_found": total_found,
                        "to_process": len(messages),
                        "action": action,
                        "preview": previews,
                        "api_used": "REST"
                    }
                
                # Extract message IDs
                email_ids = [msg.get("messageId") for msg in messages if msg.get("messageId")]
                self.log(f"Processing {len(email_ids)} message IDs via REST API")
                
                # Perform action based on type
                if action == 'mark-read':
                    return self.mark_as_read(email_ids, folder)
                elif action == 'mark-unread':
                    return self.mark_as_unread(email_ids, folder)
                elif action == 'delete':
                    return self.delete_emails(email_ids, folder)
                else:
                    raise ValueError(f"Unknown action: {action}. Use 'mark-read', 'mark-unread', or 'delete'")
                    
            except Exception as e:
                self.log(f"REST API bulk action failed: {e}, falling back to IMAP")
                # Fall through to IMAP mode
        
        # IMAP fallback
        try:
            self.connect_imap()
            self.log(f"Using IMAP for bulk action - Selecting folder: {folder}")
            self.imap.select(folder, readonly=True if dry_run else False)
            
            # Add date filter for performance
            if search_days > 0:
                since_date = (datetime.now() - timedelta(days=search_days)).strftime("%d-%b-%Y")
                query = f'({query} SINCE {since_date})'
                self.log(f"Search query: {query}")
            
            status, messages = self.imap.search(None, query)
            
            if status != 'OK':
                raise Exception(f"Search failed: {status}")
            
            email_ids = messages[0].split()
            total_found = len(email_ids)
            email_ids = email_ids[-limit:]  # Apply limit
            
            self.log(f"Found {total_found} emails, processing {len(email_ids)}")
            
            if dry_run:
                # Just return what would be affected
                previews = []
                for email_id in email_ids[:10]:  # Show first 10 as preview
                    try:
                        status, msg_data = self.imap.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
                        if status == 'OK' and msg_data[0]:
                            msg = email.message_from_bytes(msg_data[0][1])
                            previews.append({
                                "id": email_id.decode(),
                                "subject": self.decode_subject(msg.get("Subject", "")),
                                "from": msg.get("From", ""),
                                "date": msg.get("Date", "")
                            })
                    except:
                        continue
                
                return {
                    "dry_run": True,
                    "total_found": total_found,
                    "to_process": len(email_ids),
                    "action": action,
                    "preview": previews,
                    "api_used": "IMAP"
                }
            
            # Convert email_ids bytes to strings
            email_ids_str = [eid.decode() for eid in email_ids]
            
            # Disconnect to avoid readonly issues
            self.disconnect_imap()
            
            # Perform action based on type
            if action == 'mark-read':
                return self.mark_as_read(email_ids_str, folder)
            elif action == 'mark-unread':
                return self.mark_as_unread(email_ids_str, folder)
            elif action == 'delete':
                return self.delete_emails(email_ids_str, folder)
            else:
                raise ValueError(f"Unknown action: {action}. Use 'mark-read', 'mark-unread', or 'delete'")
        
        finally:
            if self.imap:
                self.disconnect_imap()

# CLI Interface
if __name__ == "__main__":
    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    if verbose:
        sys.argv = [arg for arg in sys.argv if arg not in ('--verbose', '-v')]
    
    # Parse OAuth2 flags
    auth_method = 'auto'
    token_file = None
    api_mode = 'auto'
    
    if '--auth' in sys.argv:
        idx = sys.argv.index('--auth')
        if idx + 1 < len(sys.argv):
            auth_method = sys.argv[idx + 1]
            sys.argv = sys.argv[:idx] + sys.argv[idx+2:]
    
    if '--token-file' in sys.argv:
        idx = sys.argv.index('--token-file')
        if idx + 1 < len(sys.argv):
            token_file = sys.argv[idx + 1]
            sys.argv = sys.argv[:idx] + sys.argv[idx+2:]
    
    if '--api-mode' in sys.argv:
        idx = sys.argv.index('--api-mode')
        if idx + 1 < len(sys.argv):
            api_mode = sys.argv[idx + 1]
            if api_mode not in ('auto', 'rest', 'imap'):
                print(f"Error: Invalid --api-mode value: {api_mode}. Use 'auto', 'rest', or 'imap'", file=sys.stderr)
                sys.exit(1)
            sys.argv = sys.argv[:idx] + sys.argv[idx+2:]
    
    if len(sys.argv) < 2:
        print("Zoho Email CLI")
        print("\nBasic Usage:")
        print("  Search sent:     python3 zoho-email.py search-sent 'keyword'")
        print("  Search inbox:    python3 zoho-email.py search 'keyword'")
        print("  Get unread:      python3 zoho-email.py unread")
        print("  Get email:       python3 zoho-email.py get <folder> <id>")
        print("  Send:            python3 zoho-email.py send <to> <subject> <body> [--attach file1] [--attach file2]")
        print("  Send HTML:       python3 zoho-email.py send-html <to> <subject> <html_file_or_text>")
        print("  Preview HTML:    python3 zoho-email.py preview-html <html_file_or_text>")
        print("\nAttachments:")
        print("  List attachments: python3 zoho-email.py list-attachments <folder> <email_id>")
        print("  Download:        python3 zoho-email.py download-attachment <folder> <email_id> <index> [output_path]")
        print("\nBatch Operations:")
        print("  Mark as read:    python3 zoho-email.py mark-read <folder> <id1> <id2> ...")
        print("  Mark as unread:  python3 zoho-email.py mark-unread <folder> <id1> <id2> ...")
        print("  Delete emails:   python3 zoho-email.py delete <folder> <id1> <id2> ...")
        print("  Move emails:     python3 zoho-email.py move <source_folder> <target_folder> <id1> <id2> ...")
        print("  Bulk action:     python3 zoho-email.py bulk-action --folder INBOX --search 'SUBJECT \"spam\"' --action mark-read [--dry-run]")
        print("\nOAuth2 Commands:")
        print("  Setup OAuth2:    python3 scripts/oauth-setup.py")
        print("  Refresh tokens:  python3 zoho-email.py oauth-login [--token-file path]")
        print("  Check status:    python3 zoho-email.py oauth-status [--token-file path]")
        print("  Revoke tokens:   python3 zoho-email.py oauth-revoke [--token-file path]")
        print("\nAuthentication:")
        print("  --auth <method>      Authentication method: 'auto' (default), 'password', or 'oauth2'")
        print("  --token-file <path>  OAuth2 token file path (default: ~/.zoho-mail-tokens.json)")
        print("\nAPI Mode:")
        print("  --api-mode <mode>    API mode: 'auto' (default), 'rest', or 'imap'")
        print("                       'auto': Use REST API if available, fallback to IMAP")
        print("                       'rest': Force REST API (requires OAuth2)")
        print("                       'imap': Force IMAP/SMTP mode")
        print("\nOptions:")
        print("  --verbose, -v    Enable debug output")
        print("  --dry-run        Preview bulk action without executing (bulk-action only)")
        print("\nEnvironment:")
        print("  ZOHO_EMAIL       Your Zoho email address (required for all auth methods)")
        print("  ZOHO_PASSWORD    App-specific password (for password auth)")
        print("  ZOHO_TIMEOUT     Connection timeout (default: 30s)")
        print("  ZOHO_SEARCH_DAYS Limit search to recent N days (default: 30)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Handle preview-html command without requiring credentials
    if command == "preview-html":
        html_input = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not html_input:
            print("Error: html_file_or_text required", file=sys.stderr)
            sys.exit(1)
        
        # Check if input is a file or raw HTML
        if os.path.isfile(html_input):
            with open(html_input, 'r') as f:
                html_body = f.read()
            print(f"Preview of: {html_input}\n", file=sys.stderr)
        else:
            html_body = html_input
            print("Preview of HTML:\n", file=sys.stderr)
        
        # Generate plain text preview
        import re
        text_preview = re.sub('<[^<]+?>', '', html_body)
        text_preview = re.sub(r'\n\s*\n', '\n\n', text_preview).strip()
        
        print("=== HTML CONTENT ===")
        print(html_body)
        print("\n=== PLAIN TEXT FALLBACK ===")
        print(text_preview)
        print("\n=== STATS ===")
        print(f"HTML length: {len(html_body)} chars")
        print(f"Plain text length: {len(text_preview)} chars")
        sys.exit(0)
        
    # Handle OAuth2-specific commands
    if command == "oauth-status":
        try:
            zoho = ZohoEmail(verbose=verbose, auth_method='oauth2', token_file=token_file)
            status = zoho.get_token_status()
            print(json.dumps(status, indent=2))
            
            if status['status'] == 'expired':
                print("\n⚠️  Token has expired. Run 'python3 zoho-email.py oauth-login' to refresh.", file=sys.stderr)
                sys.exit(1)
            elif status['status'] == 'valid':
                print(f"\n✓ Token is valid (expires in {status['expires_in_seconds']}s)", file=sys.stderr)
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
            sys.exit(1)
        sys.exit(0)
    
    elif command == "oauth-login":
        try:
            zoho = ZohoEmail(verbose=verbose, auth_method='oauth2', token_file=token_file)
            print(f"Refreshing OAuth2 tokens from: {zoho.token_file}", file=sys.stderr)
            zoho.refresh_token()
            status = zoho.get_token_status()
            print(json.dumps(status, indent=2))
            print(f"\n✓ Tokens refreshed successfully (expires in {status['expires_in_seconds']}s)", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            print("\nIf tokens are invalid, run 'python3 scripts/oauth-setup.py' to set up OAuth2 again.", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    
    elif command == "oauth-revoke":
        try:
            zoho = ZohoEmail(verbose=verbose, auth_method='oauth2', token_file=token_file)
            print(f"Revoking OAuth2 tokens: {zoho.token_file}", file=sys.stderr)
            zoho.revoke_token()
            print(json.dumps({"status": "revoked", "token_file": zoho.token_file}))
            print(f"\n✓ Token file deleted. Run 'python3 scripts/oauth-setup.py' to set up OAuth2 again.", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    
# For all other commands, initialize ZohoEmail (requires credentials)
    try:
        zoho = ZohoEmail(verbose=verbose, auth_method=auth_method, token_file=token_file, api_mode=api_mode)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nAuthentication options:", file=sys.stderr)
        print("  1. OAuth2 (recommended): Run 'python3 scripts/oauth-setup.py' to configure", file=sys.stderr)
        print("  2. App Password: Set ZOHO_EMAIL and ZOHO_PASSWORD environment variables:", file=sys.stderr)
        print("     export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("     export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)
        sys.exit(1)
    
    try:
        if command == "search-sent":
            query = sys.argv[2] if len(sys.argv) > 2 else "ALL"
            # Convert to IMAP search format
            imap_query = f'SUBJECT "{query}"' if query != "ALL" else "ALL"
            results = zoho.search_emails(folder="Sent", query=imap_query, limit=5)
            print(json.dumps(results, indent=2))
        
        elif command == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "ALL"
            imap_query = f'SUBJECT "{query}"' if query != "ALL" else "ALL"
            results = zoho.search_emails(folder="INBOX", query=imap_query, limit=10)
            print(json.dumps(results, indent=2))
        
        elif command == "unread":
            count = zoho.get_unread_count()
            print(json.dumps({"unread_count": count}))
        
        elif command == "get":
            folder = sys.argv[2] if len(sys.argv) > 2 else "INBOX"
            email_id = sys.argv[3] if len(sys.argv) > 3 else None
            if not email_id:
                print("Error: email_id required", file=sys.stderr)
                sys.exit(1)
            result = zoho.get_email(folder=folder, email_id=email_id)
            print(json.dumps(result, indent=2))
        
        elif command == "send":
            # Parse --attach flags
            attachments = []
            filtered_args = []
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == '--attach' and i + 1 < len(sys.argv):
                    attachments.append(sys.argv[i + 1])
                    i += 2
                else:
                    filtered_args.append(sys.argv[i])
                    i += 1
            
            to = filtered_args[0] if len(filtered_args) > 0 else None
            subject = filtered_args[1] if len(filtered_args) > 1 else None
            body = filtered_args[2] if len(filtered_args) > 2 else None
            
            if not all([to, subject, body]):
                print("Error: to, subject, and body required", file=sys.stderr)
                sys.exit(1)
            
            # Send with or without attachments
            if attachments:
                result = zoho.send_email_with_attachment(to, subject, body, attachments=attachments)
            else:
                result = zoho.send_email(to, subject, body)
            print(json.dumps(result, indent=2))
        
        elif command == "send-html":
            to = sys.argv[2] if len(sys.argv) > 2 else None
            subject = sys.argv[3] if len(sys.argv) > 3 else None
            html_input = sys.argv[4] if len(sys.argv) > 4 else None
            
            if not all([to, subject, html_input]):
                print("Error: to, subject, and html_file_or_text required", file=sys.stderr)
                sys.exit(1)
            
            # Check if input is a file or raw HTML
            if os.path.isfile(html_input):
                with open(html_input, 'r') as f:
                    html_body = f.read()
                print(f"Loaded HTML from: {html_input}", file=sys.stderr)
            else:
                html_body = html_input
            
            result = zoho.send_html_email(to, subject, html_body)
            print(json.dumps(result, indent=2))
        
        elif command == "download-attachment":
            folder = sys.argv[2] if len(sys.argv) > 2 else "INBOX"
            email_id = sys.argv[3] if len(sys.argv) > 3 else None
            attachment_index = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            output_path = sys.argv[5] if len(sys.argv) > 5 else None
            
            if not email_id:
                print("Error: email_id required", file=sys.stderr)
                sys.exit(1)
            
            result = zoho.download_attachment(
                folder=folder,
                email_id=email_id,
                attachment_index=attachment_index,
                output_path=output_path
            )
            print(json.dumps(result, indent=2))
        
        
        elif command == "mark-read":
            if len(sys.argv) < 4:
                print("Error: folder and at least one email_id required", file=sys.stderr)
                print("Usage: python3 zoho-email.py mark-read <folder> <id1> <id2> ...", file=sys.stderr)
                sys.exit(1)
            
            folder = sys.argv[2]
            email_ids = sys.argv[3:]
            
            print(f"Marking {len(email_ids)} emails as read in folder '{folder}'...", file=sys.stderr)
            result = zoho.mark_as_read(email_ids, folder)
            print(json.dumps(result, indent=2))
            
            if result["failed"]:
                print(f"\nWarning: {len(result['failed'])} emails failed to update", file=sys.stderr)
        
        elif command == "mark-unread":
            if len(sys.argv) < 4:
                print("Error: folder and at least one email_id required", file=sys.stderr)
                print("Usage: python3 zoho-email.py mark-unread <folder> <id1> <id2> ...", file=sys.stderr)
                sys.exit(1)
            
            folder = sys.argv[2]
            email_ids = sys.argv[3:]
            
            print(f"Marking {len(email_ids)} emails as unread in folder '{folder}'...", file=sys.stderr)
            result = zoho.mark_as_unread(email_ids, folder)
            print(json.dumps(result, indent=2))
            
            if result["failed"]:
                print(f"\nWarning: {len(result['failed'])} emails failed to update", file=sys.stderr)
        
        elif command == "delete":
            if len(sys.argv) < 4:
                print("Error: folder and at least one email_id required", file=sys.stderr)
                print("Usage: python3 zoho-email.py delete <folder> <id1> <id2> ...", file=sys.stderr)
                sys.exit(1)
            
            folder = sys.argv[2]
            email_ids = sys.argv[3:]
            
            # Safety confirmation for deletions
            print(f"⚠️  WARNING: About to delete {len(email_ids)} emails from '{folder}'", file=sys.stderr)
            print("Emails will be moved to Trash. Continue? (y/N): ", file=sys.stderr, end='')
            confirmation = input().strip().lower()
            
            if confirmation != 'y':
                print("Deletion cancelled.", file=sys.stderr)
                sys.exit(0)
            
            print(f"Deleting {len(email_ids)} emails...", file=sys.stderr)
            result = zoho.delete_emails(email_ids, folder)
            print(json.dumps(result, indent=2))
            
            if result["failed"]:
                print(f"\nWarning: {len(result['failed'])} emails failed to delete", file=sys.stderr)
        
        elif command == "move":
            if len(sys.argv) < 5:
                print("Error: source_folder, target_folder, and at least one email_id required", file=sys.stderr)
                print("Usage: python3 zoho-email.py move <source_folder> <target_folder> <id1> <id2> ...", file=sys.stderr)
                sys.exit(1)
            
            source_folder = sys.argv[2]
            target_folder = sys.argv[3]
            email_ids = sys.argv[4:]
            
            print(f"Moving {len(email_ids)} emails from '{source_folder}' to '{target_folder}'...", file=sys.stderr)
            result = zoho.move_emails(email_ids, target_folder, source_folder)
            print(json.dumps(result, indent=2))
            
            if result["failed"]:
                print(f"\nWarning: {len(result['failed'])} emails failed to move", file=sys.stderr)
        
        elif command == "bulk-action":
            # Parse flags
            dry_run = '--dry-run' in sys.argv
            
            # Extract parameters
            folder = None
            search_query = None
            action = None
            
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == '--folder' and i + 1 < len(sys.argv):
                    folder = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--search' and i + 1 < len(sys.argv):
                    search_query = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--action' and i + 1 < len(sys.argv):
                    action = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--dry-run':
                    i += 1
                else:
                    i += 1
            
            if not all([folder, search_query, action]):
                print("Error: --folder, --search, and --action are required", file=sys.stderr)
                print("Usage: python3 zoho-email.py bulk-action --folder INBOX --search 'SUBJECT \"test\"' --action mark-read [--dry-run]", file=sys.stderr)
                print("Actions: mark-read, mark-unread, delete", file=sys.stderr)
                sys.exit(1)
            
            if dry_run:
                print(f"🔍 DRY RUN: Searching '{folder}' for emails matching: {search_query}", file=sys.stderr)
            else:
                print(f"Executing bulk action '{action}' on '{folder}' for query: {search_query}", file=sys.stderr)
            
            result = zoho.bulk_action(search_query, action, folder=folder, dry_run=dry_run)
            print(json.dumps(result, indent=2))
            
            if dry_run and result.get("to_process", 0) > 0:
                print(f"\n💡 To execute, remove --dry-run flag", file=sys.stderr)
            elif not dry_run and result.get("failed"):
                print(f"\nWarning: {len(result['failed'])} emails failed to process", file=sys.stderr)

        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            print("Run without arguments for usage help", file=sys.stderr)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
