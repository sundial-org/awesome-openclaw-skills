#!/usr/bin/env python3
"""Add OAuth2 CLI support to zoho-email.py"""

with open('zoho-email.py', 'r') as f:
    content = f.read()

# Find where to insert the OAuth2 command handlers
marker = '    # For all other commands, initialize ZohoEmail (requires credentials)'

if marker in content:
    # Split at the marker
    parts = content.split(marker, 1)
    
    oauth_commands = '''    
    # Handle OAuth2-specific commands
    if command == "oauth-status":
        try:
            zoho = ZohoEmail(verbose=verbose, auth_method='oauth2', token_file=token_file)
            status = zoho.get_token_status()
            print(json.dumps(status, indent=2))
            
            if status['status'] == 'expired':
                print("\\n⚠️  Token has expired. Run 'python3 zoho-email.py oauth-login' to refresh.", file=sys.stderr)
                sys.exit(1)
            elif status['status'] == 'valid':
                print(f"\\n✓ Token is valid (expires in {status['expires_in_seconds']}s)", file=sys.stderr)
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
            print(f"\\n✓ Tokens refreshed successfully (expires in {status['expires_in_seconds']}s)", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            print("\\nIf tokens are invalid, run 'python3 scripts/oauth-setup.py' to set up OAuth2 again.", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    
    elif command == "oauth-revoke":
        try:
            zoho = ZohoEmail(verbose=verbose, auth_method='oauth2', token_file=token_file)
            print(f"Revoking OAuth2 tokens: {zoho.token_file}", file=sys.stderr)
            zoho.revoke_token()
            print(json.dumps({"status": "revoked", "token_file": zoho.token_file}))
            print(f"\\n✓ Token file deleted. Run 'python3 scripts/oauth-setup.py' to set up OAuth2 again.", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    
    ''' + marker
    
    # Reconstruct the file
    new_content = parts[0] + oauth_commands + parts[1]
    
    # Update initialization to use auth_method and token_file
    new_content = new_content.replace(
        '        zoho = ZohoEmail(verbose=verbose)',
        '        zoho = ZohoEmail(verbose=verbose, auth_method=auth_method, token_file=token_file)'
    )
    
    # Update help text
    new_content = new_content.replace(
        '        print("\\nOptions:")',
        '''        print("\\nOAuth2 Commands:")
        print("  Setup OAuth2:    python3 scripts/oauth-setup.py")
        print("  Refresh tokens:  python3 zoho-email.py oauth-login [--token-file path]")
        print("  Check status:    python3 zoho-email.py oauth-status [--token-file path]")
        print("  Revoke tokens:   python3 zoho-email.py oauth-revoke [--token-file path]")
        print("\\nAuthentication:")
        print("  --auth <method>      Authentication method: 'auto' (default), 'password', or 'oauth2'")
        print("  --token-file <path>  OAuth2 token file path (default: ~/.zoho-mail-tokens.json)")
        print("\\nOptions:")'''
    )
    
    # Add OAuth2 flag parsing
    new_content = new_content.replace(
        '''    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    if verbose:
        sys.argv = [arg for arg in sys.argv if arg not in ('--verbose', '-v')]''',
        '''    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    if verbose:
        sys.argv = [arg for arg in sys.argv if arg not in ('--verbose', '-v')]
    
    # Parse OAuth2 flags
    auth_method = 'auto'
    token_file = None
    
    if '--auth' in sys.argv:
        idx = sys.argv.index('--auth')
        if idx + 1 < len(sys.argv):
            auth_method = sys.argv[idx + 1]
            sys.argv = sys.argv[:idx] + sys.argv[idx+2:]
    
    if '--token-file' in sys.argv:
        idx = sys.argv.index('--token-file')
        if idx + 1 < len(sys.argv):
            token_file = sys.argv[idx + 1]
            sys.argv = sys.argv[:idx] + sys.argv[idx+2:]'''
    )
    
    # Update error message
    new_content = new_content.replace(
        '''        print("\\nPlease set your Zoho credentials:", file=sys.stderr)
        print("  export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("  export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)''',
        '''        print("\\nAuthentication options:", file=sys.stderr)
        print("  1. OAuth2: Run 'python3 scripts/oauth-setup.py' to configure OAuth2", file=sys.stderr)
        print("  2. App Password: Set ZOHO_EMAIL and ZOHO_PASSWORD environment variables:", file=sys.stderr)
        print("     export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("     export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)'''
    )
    
    with open('zoho-email.py', 'w') as f:
        f.write(new_content)
    
    print("✓ OAuth2 CLI support added successfully")
else:
    print("✗ Error: Could not find marker in file")
    exit(1)
