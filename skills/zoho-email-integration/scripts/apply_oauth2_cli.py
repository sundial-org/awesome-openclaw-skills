#!/usr/bin/env python3
"""Add OAuth2 CLI support to zoho-email.py"""

# Read the file
with open('zoho-email.py', 'r') as f:
    content = f.read()

print("Adding OAuth2 CLI support...")

# 1. Update help text - add OAuth2 commands before Options section
old_help_options = '''        print("\\nOptions:")
        print("  --verbose, -v    Enable debug output")
        print("  --dry-run        Preview bulk action without executing (bulk-action only)")
        print("\\nEnvironment:")
        print("  ZOHO_EMAIL       Your Zoho email address")
        print("  ZOHO_PASSWORD    App-specific password")'''

new_help_options = '''        print("\\nOAuth2 Commands:")
        print("  Setup OAuth2:    python3 scripts/oauth-setup.py")
        print("  Refresh tokens:  python3 zoho-email.py oauth-login [--token-file path]")
        print("  Check status:    python3 zoho-email.py oauth-status [--token-file path]")
        print("  Revoke tokens:   python3 zoho-email.py oauth-revoke [--token-file path]")
        print("\\nAuthentication:")
        print("  --auth <method>      Authentication method: 'auto' (default), 'password', or 'oauth2'")
        print("  --token-file <path>  OAuth2 token file path (default: ~/.zoho-mail-tokens.json)")
        print("\\nOptions:")
        print("  --verbose, -v    Enable debug output")
        print("  --dry-run        Preview bulk action without executing (bulk-action only)")
        print("\\nEnvironment:")
        print("  ZOHO_EMAIL       Your Zoho email address (required for all auth methods)")
        print("  ZOHO_PASSWORD    App-specific password (for password auth)'''

content = content.replace(old_help_options, new_help_options)

# 2. Add OAuth2 flag parsing after verbose flag parsing
old_flag_parse = '''    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    if verbose:
        sys.argv = [arg for arg in sys.argv if arg not in ('--verbose', '-v')]'''

new_flag_parse = '''    # Check for verbose flag
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

content = content.replace(old_flag_parse, new_flag_parse)

# 3. Add OAuth2 command handlers after preview-html command
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
    
'''

# Find the marker to insert commands (after preview-html, before "For all other commands")
marker = '        sys.exit(0)\n    \n    # For all other commands, initialize ZohoEmail (requires credentials)'
if marker in content:
    content = content.replace(marker, '        sys.exit(0)\n    ' + oauth_commands + '# For all other commands, initialize ZohoEmail (requires credentials)')
else:
    # Alternative marker
    marker2 = '        sys.exit(0)\n    \n    # For all other commands, initialize ZohoEmail'
    if marker2 in content:
        content = content.replace(marker2, '        sys.exit(0)\n    ' + oauth_commands + '# For all other commands, initialize ZohoEmail')
    else:
        print("⚠️  Warning: Could not find insertion point for OAuth2 commands")

# 4. Update ZohoEmail initialization to pass auth_method and token_file
content = content.replace(
    '        zoho = ZohoEmail(verbose=verbose)',
    '        zoho = ZohoEmail(verbose=verbose, auth_method=auth_method, token_file=token_file)'
)

# 5. Update error message for missing credentials
old_error = '''        print("\\nPlease set your Zoho credentials:", file=sys.stderr)
        print("  export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("  export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)'''

new_error = '''        print("\\nAuthentication options:", file=sys.stderr)
        print("  1. OAuth2 (recommended): Run 'python3 scripts/oauth-setup.py' to configure", file=sys.stderr)
        print("  2. App Password: Set ZOHO_EMAIL and ZOHO_PASSWORD environment variables:", file=sys.stderr)
        print("     export ZOHO_EMAIL='your-email@domain.com'", file=sys.stderr)
        print("     export ZOHO_PASSWORD='your-app-specific-password'", file=sys.stderr)'''

content = content.replace(old_error, new_error)

# Write the modified content
with open('zoho-email.py', 'w') as f:
    f.write(content)

print("✓ OAuth2 CLI support added successfully!")
print("✓ File updated: zoho-email.py")
print("\\nOAuth2 implementation complete!")
