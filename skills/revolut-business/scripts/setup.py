#!/usr/bin/env python3
"""Interactive setup wizard for Revolut Business API skill."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

STATE_DIR = Path(os.environ.get("REVOLUT_DIR", os.path.expanduser("~/.clawdbot/revolut")))
PRIVATE_KEY = STATE_DIR / "private.pem"
CERTIFICATE = STATE_DIR / "certificate.pem"
CONFIG_FILE = STATE_DIR / "config.json"

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def step(n, title):
    print(f"\n{BOLD}{BLUE}━━━ Step {n}: {title} ━━━{RESET}\n")


def ok(msg):
    print(f"  {GREEN}✅ {msg}{RESET}")


def warn(msg):
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


def err(msg):
    print(f"  {RED}❌ {msg}{RESET}")


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val or default


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def main():
    print(f"""
{BOLD}╔══════════════════════════════════════════════════╗
║   Revolut Business API — Setup Wizard            ║
╚══════════════════════════════════════════════════╝{RESET}

This wizard will guide you through:
  1. Generate RSA key pair & X509 certificate
  2. Upload certificate to Revolut
  3. Configure OAuth redirect URI
  4. Authorize and get access token

{YELLOW}Requirements:{RESET}
  • Python 3.10+ with PyJWT & cryptography
  • A Revolut Business account
  • A domain you control (for OAuth callback)
""")

    # Check dependencies
    try:
        import jwt
        ok("PyJWT installed")
    except ImportError:
        err("PyJWT not found")
        print(f"  Run: pip install PyJWT cryptography")
        sys.exit(1)

    try:
        from cryptography import x509
        ok("cryptography installed")
    except ImportError:
        err("cryptography not found")
        print(f"  Run: pip install cryptography")
        sys.exit(1)

    input(f"\n  Press Enter to start...")

    # ─── Step 1: Generate keys ───
    step(1, "Generate RSA Key Pair & X509 Certificate")

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    if PRIVATE_KEY.exists():
        warn(f"Private key already exists: {PRIVATE_KEY}")
        reuse = ask("Reuse existing key? (y/n)", "y")
        if reuse.lower() != "y":
            PRIVATE_KEY.unlink()
            CERTIFICATE.unlink(missing_ok=True)

    if not PRIVATE_KEY.exists():
        print(f"  Generating 2048-bit RSA key...")
        r = run(f'openssl genrsa -out "{PRIVATE_KEY}" 2048')
        if r.returncode != 0:
            err(f"Failed: {r.stderr}")
            sys.exit(1)
        ok(f"Private key: {PRIVATE_KEY}")

    if not CERTIFICATE.exists():
        org = ask("Organization name (for certificate)", "OpenClaw")
        country = ask("Country code (2 letters)", "US")
        cn = ask("Common name", "openclaw")

        r = run(f'openssl req -new -x509 -key "{PRIVATE_KEY}" -out "{CERTIFICATE}" '
                f'-days 730 -subj "/CN={cn}/O={org}/C={country}"')
        if r.returncode != 0:
            err(f"Failed: {r.stderr}")
            sys.exit(1)
        ok(f"Certificate: {CERTIFICATE}")
    else:
        ok(f"Certificate exists: {CERTIFICATE}")

    # ─── Step 2: Show certificate for upload ───
    step(2, "Upload Certificate to Revolut")

    cert_content = CERTIFICATE.read_text()
    print(f"""  Now go to Revolut Business:
  {BOLD}business.revolut.com → Settings → API → Add Certificate{RESET}

  Fill in:
  • Certificate title: {BOLD}openclaw{RESET} (or any name)
  • OAuth redirect URI: (see Step 3 below first!)
  • X509 public key: Paste this 👇

{YELLOW}{'─' * 60}
{cert_content.strip()}
{'─' * 60}{RESET}
""")

    # Copy to clipboard if possible
    for cmd in ["pbcopy", "xclip -selection clipboard", "xsel --clipboard"]:
        r = run(f'echo "{cert_content.strip()}" | {cmd}')
        if r.returncode == 0:
            ok("Certificate copied to clipboard!")
            break

    # ─── Step 3: Callback URL ───
    step(3, "Configure OAuth Redirect URI")

    print(f"""  Revolut needs a real HTTPS URL to redirect to after authorization.
  Options:
    a) Cloudflare Worker (free, recommended)
    b) n8n webhook
    c) Any HTTPS endpoint that shows the ?code= parameter

  {RED}❌ localhost will NOT work{RESET}
  {RED}❌ revolut.com will NOT work{RESET}
""")

    redirect_uri = ask("Your OAuth redirect URI (full URL)", "https://revolut.yourdomain.com/callback")

    # Extract domain from redirect URI
    from urllib.parse import urlparse
    parsed = urlparse(redirect_uri)
    domain = parsed.hostname
    ok(f"Redirect URI: {redirect_uri}")
    ok(f"ISS domain: {domain}")

    print(f"""
  {BOLD}Now in Revolut, set:{RESET}
  • OAuth redirect URI: {BOLD}{redirect_uri}{RESET}
  • Production IP whitelist: """, end="")

    # Get public IP
    r = run("curl -s ifconfig.me")
    public_ip = r.stdout.strip() if r.returncode == 0 else "your.server.ip"
    print(f"{BOLD}{public_ip}{RESET}")

    print(f"""
  Click {BOLD}Add{RESET} in Revolut, then copy the {BOLD}Client ID{RESET} it shows you.
""")

    client_id = ask("Paste your Client ID")
    if not client_id:
        err("Client ID is required!")
        sys.exit(1)
    ok(f"Client ID: {client_id[:20]}...")

    # Save config
    config = {
        "client_id": client_id,
        "iss_domain": domain,
        "redirect_uri": redirect_uri,
        "public_ip": public_ip,
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    ok(f"Config saved: {CONFIG_FILE}")

    # ─── Step 4: Authorize ───
    step(4, "Authorize with Revolut")

    import urllib.parse
    consent_url = (
        f"https://business.revolut.com/app-confirm?"
        f"client_id={urllib.parse.quote(client_id)}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code"
    )

    print(f"  Open this URL in your browser:\n")
    print(f"  {BOLD}{consent_url}{RESET}\n")
    print(f"  1. Log in to Revolut Business")
    print(f"  2. Approve the access")
    print(f"  3. You'll be redirected — copy the {BOLD}code{RESET} from the page\n")

    # Try to open browser
    for cmd in ["open", "xdg-open", "start"]:
        r = run(f'{cmd} "{consent_url}" 2>/dev/null')
        if r.returncode == 0:
            ok("Opened browser")
            break

    auth_code = ask("Paste the authorization code")
    if not auth_code:
        err("Authorization code is required!")
        sys.exit(1)

    # Exchange code for token
    print(f"\n  Exchanging code for access token...")

    import jwt as pyjwt
    import uuid
    import urllib.request

    now = int(time.time())
    jwt_payload = {
        "iss": domain,
        "sub": client_id,
        "aud": "https://revolut.com",
        "iat": now,
        "exp": now + 2400,
        "jti": str(uuid.uuid4()),
    }

    private_key = PRIVATE_KEY.read_text()
    client_assertion = pyjwt.encode(jwt_payload, private_key, algorithm="RS256")

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": client_id,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": client_assertion,
    }).encode()

    req = urllib.request.Request(
        "https://b2b.revolut.com/api/1.0/auth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        resp = urllib.request.urlopen(req)
        tokens = json.loads(resp.read())
        tokens["obtained_at"] = now
        tokens["client_id"] = client_id

        tokens_file = STATE_DIR / "tokens.json"
        tokens_file.write_text(json.dumps(tokens, indent=2))

        ok("Authenticated successfully!")
        ok(f"Tokens saved: {tokens_file}")
    except Exception as e:
        body = e.read().decode() if hasattr(e, "read") else str(e)
        err(f"Authentication failed: {body}")
        print(f"""
  {YELLOW}Common causes:{RESET}
  • Auth code expired — they only last a few minutes, try again
  • Client ID mismatch — check Revolut API settings
  • Certificate mismatch — make sure you uploaded the right cert
  • ISS domain wrong — must be the domain of your redirect URI without https://
""")
        sys.exit(1)

    # ─── Step 5: Verify ───
    step(5, "Verify Connection")

    print("  Fetching accounts...")
    token = tokens["access_token"]
    req = urllib.request.Request(
        "https://b2b.revolut.com/api/1.0/accounts",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req)
        accounts = json.loads(resp.read())
        ok(f"Connected! Found {len(accounts)} account(s):\n")
        for acc in accounts:
            symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(acc["currency"], acc["currency"])
            print(f"    {acc.get('name', '?'):15} {acc['currency']}  {symbol}{acc['balance']:>10,.2f}")
    except Exception as e:
        err(f"Verification failed: {e}")
        sys.exit(1)

    # ─── Done ───
    print(f"""
{BOLD}{GREEN}━━━ Setup Complete! ━━━{RESET}

  {BOLD}Environment variables{RESET} (add to your .env):
    REVOLUT_CLIENT_ID={client_id}
    REVOLUT_ISS_DOMAIN={domain}

  {BOLD}Quick start:{RESET}
    python3 scripts/revolut.py accounts     # List accounts
    python3 scripts/revolut.py tx -n 10     # Recent transactions
    python3 scripts/revolut.py balance      # EUR balance

  Tokens auto-refresh — no manual intervention needed. 🎉
""")


if __name__ == "__main__":
    main()
