#!/usr/bin/env python3
"""Revolut Business API CLI — accounts, balances, transactions, counterparties, payments."""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

try:
    import jwt
except ImportError:
    print("ERROR: PyJWT required. Install: pip install PyJWT cryptography", file=sys.stderr)
    sys.exit(1)

import urllib.request
import urllib.parse
import urllib.error

# --- Config ---
STATE_DIR = Path(os.environ.get("REVOLUT_DIR", os.path.expanduser("~/.clawdbot/revolut")))
TOKENS_FILE = STATE_DIR / "tokens.json"
PRIVATE_KEY_FILE = STATE_DIR / "private.pem"
API_BASE = "https://b2b.revolut.com/api/1.0"

CLIENT_ID = os.environ.get("REVOLUT_CLIENT_ID", "")
ISS_DOMAIN = os.environ.get("REVOLUT_ISS_DOMAIN", "")


def load_env():
    """Load .env from clawd workspace if vars not set."""
    global CLIENT_ID, ISS_DOMAIN
    if CLIENT_ID and ISS_DOMAIN:
        return
    env_paths = [
        Path.home() / "clawd" / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip("'\"")
                if k == "REVOLUT_CLIENT_ID" and not CLIENT_ID:
                    CLIENT_ID = v
                elif k == "REVOLUT_ISS_DOMAIN" and not ISS_DOMAIN:
                    ISS_DOMAIN = v
            break


def generate_jwt():
    """Generate client assertion JWT for Revolut API."""
    private_key = PRIVATE_KEY_FILE.read_text()
    now = int(time.time())
    payload = {
        "iss": ISS_DOMAIN,
        "sub": CLIENT_ID,
        "aud": "https://revolut.com",
        "iat": now,
        "exp": now + 2400,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def load_tokens():
    """Load tokens from file."""
    if not TOKENS_FILE.exists():
        return None
    return json.loads(TOKENS_FILE.read_text())


def save_tokens(tokens):
    """Save tokens to file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    TOKENS_FILE.write_text(json.dumps(tokens, indent=2))


def refresh_access_token():
    """Refresh the access token using refresh_token."""
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("ERROR: No refresh token. Run 'revolut auth' first.", file=sys.stderr)
        sys.exit(1)

    client_assertion = generate_jwt()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": CLIENT_ID,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": client_assertion,
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/auth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        result["obtained_at"] = int(time.time())
        result["client_id"] = CLIENT_ID
        # Keep refresh_token if not returned
        if "refresh_token" not in result and "refresh_token" in tokens:
            result["refresh_token"] = tokens["refresh_token"]
        save_tokens(result)
        return result["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR refreshing token: {body}", file=sys.stderr)
        sys.exit(1)


def get_access_token():
    """Get a valid access token, refreshing if needed."""
    tokens = load_tokens()
    if not tokens:
        print("ERROR: Not authenticated. Run 'revolut auth' first.", file=sys.stderr)
        sys.exit(1)

    obtained = tokens.get("obtained_at", 0)
    expires_in = tokens.get("expires_in", 2399)
    if time.time() > obtained + expires_in - 120:
        return refresh_access_token()
    return tokens["access_token"]


def api_call(method, endpoint, data=None, params=None):
    """Make an authenticated API call."""
    token = get_access_token()
    url = f"{API_BASE}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")

    try:
        resp = urllib.request.urlopen(req)
        content = resp.read()
        return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        # Try refresh on 401
        if e.code == 401:
            token = refresh_access_token()
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {token}")
            try:
                resp = urllib.request.urlopen(req)
                content = resp.read()
                return json.loads(content) if content else {}
            except urllib.error.HTTPError as e2:
                body = e2.read().decode()
        print(f"API Error ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)


# --- Commands ---

def cmd_auth(args):
    """Exchange authorization code for tokens."""
    if not args.code:
        print(f"Open this URL to authorize:")
        print(f"https://business.revolut.com/app-confirm?client_id={CLIENT_ID}&redirect_uri=https://{ISS_DOMAIN}/callback&response_type=code")
        print(f"\nThen run: revolut auth --code <CODE>")
        return

    client_assertion = generate_jwt()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": args.code,
        "client_id": CLIENT_ID,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": client_assertion,
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/auth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        result["obtained_at"] = int(time.time())
        result["client_id"] = CLIENT_ID
        save_tokens(result)
        print("✅ Authenticated successfully!")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ Auth failed: {body}", file=sys.stderr)
        sys.exit(1)


def cmd_accounts(args):
    """List accounts with balances."""
    accounts = api_call("GET", "/accounts")
    if args.json:
        print(json.dumps(accounts, indent=2))
        return

    print(f"{'Account':<20} {'Currency':<8} {'Balance':>12}  {'State':<8}")
    print("-" * 55)
    for acc in accounts:
        name = acc.get("name", "?")
        currency = acc["currency"]
        balance = acc["balance"]
        state = acc["state"]
        symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(currency, currency)
        print(f"{name:<20} {currency:<8} {symbol}{balance:>10,.2f}  {state:<8}")


def cmd_balance(args):
    """Show total balance in EUR."""
    accounts = api_call("GET", "/accounts")
    total_eur = 0
    for acc in accounts:
        if acc["currency"] == "EUR" and acc.get("state") == "active":
            total_eur += acc["balance"]
    if args.json:
        print(json.dumps({"total_eur": total_eur}))
    else:
        print(f"€{total_eur:,.2f}")


def cmd_transactions(args):
    """List recent transactions."""
    params = {"count": args.count or 20}
    if args.account:
        # Resolve account name to ID
        accounts = api_call("GET", "/accounts")
        for acc in accounts:
            if acc.get("name", "").lower() == args.account.lower() or acc["id"] == args.account:
                params["account_id"] = acc["id"]
                break
    if args.since:
        params["from"] = args.since
    if args.to:
        params["to"] = args.to
    if args.type:
        params["type"] = args.type

    txns = api_call("GET", "/transactions", params=params)

    if args.json:
        print(json.dumps(txns, indent=2))
        return

    print(f"{'Date':<12} {'Type':<15} {'Description':<30} {'Amount':>10} {'Cur':<5} {'State':<10}")
    print("-" * 90)
    for tx in txns:
        date = tx.get("created_at", "")[:10]
        tx_type = tx.get("type", "?")
        state = tx.get("state", "?")
        legs = tx.get("legs", [{}])
        leg = legs[0] if legs else {}
        amount = leg.get("amount", 0)
        currency = leg.get("currency", "?")
        desc = leg.get("description", tx.get("reference", ""))[:29]
        if not desc and tx.get("merchant"):
            desc = tx["merchant"].get("name", "")[:29]
        symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(currency, "")
        print(f"{date:<12} {tx_type:<15} {desc:<30} {symbol}{amount:>9,.2f} {currency:<5} {state:<10}")


def cmd_counterparties(args):
    """List counterparties."""
    params = {}
    if args.name:
        params["name"] = args.name
    cps = api_call("GET", "/counterparties", params=params)

    if args.json:
        print(json.dumps(cps, indent=2))
        return

    print(f"{'Name':<35} {'Type':<15} {'Currency':<8} {'Account':<25}")
    print("-" * 85)
    for cp in cps:
        name = cp.get("name", "?")[:34]
        cp_type = cp.get("type", "?")
        accs = cp.get("accounts", [])
        if accs:
            for a in accs:
                currency = a.get("currency", "?")
                iban = a.get("iban", a.get("account_no", "?"))
                print(f"{name:<35} {cp_type:<15} {currency:<8} {iban:<25}")
        else:
            print(f"{name:<35} {cp_type:<15}")


def cmd_pay(args):
    """Create a payment (draft or direct)."""
    # Find counterparty account
    if args.counterparty:
        cps = api_call("GET", "/counterparties", params={"name": args.counterparty})
        if not cps:
            print(f"❌ Counterparty '{args.counterparty}' not found", file=sys.stderr)
            sys.exit(1)
        cp = cps[0]
        cp_accs = cp.get("accounts", [])
        if not cp_accs:
            print(f"❌ No accounts for counterparty '{cp['name']}'", file=sys.stderr)
            sys.exit(1)
        # Pick matching currency account
        target_acc = None
        for a in cp_accs:
            if a.get("currency") == args.currency:
                target_acc = a
                break
        if not target_acc:
            target_acc = cp_accs[0]

        account_id = target_acc["id"]
    elif args.account_id:
        account_id = args.account_id
    else:
        print("❌ Specify --counterparty or --account-id", file=sys.stderr)
        sys.exit(1)

    payload = {
        "request_id": str(uuid.uuid4()),
        "account_id": account_id,
        "receiver": {"counterparty_id": cp["id"], "account_id": account_id},
        "amount": args.amount,
        "currency": args.currency or "EUR",
        "reference": args.reference or "",
    }

    if args.draft:
        result = api_call("POST", "/payment-drafts", data={"title": args.reference or "Payment", "payments": [payload]})
        print(f"✅ Payment draft created: {result.get('id', '?')}")
    else:
        print(f"⚠️  About to send {args.currency or 'EUR'} {args.amount:.2f} to {args.counterparty or args.account_id}")
        if not args.yes:
            confirm = input("Confirm? (yes/no): ")
            if confirm.lower() != "yes":
                print("Aborted.")
                return
        result = api_call("POST", "/pay", data=payload)
        print(f"✅ Payment sent! ID: {result.get('id', '?')}, State: {result.get('state', '?')}")

    if args.json:
        print(json.dumps(result, indent=2))


def cmd_exchange(args):
    """Exchange currencies."""
    payload = {
        "request_id": str(uuid.uuid4()),
        "from": {"amount": args.amount, "currency": args.sell},
        "to": {"currency": args.buy},
        "reference": args.reference or "Currency exchange",
    }
    result = api_call("POST", "/exchange", data=payload)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ Exchanged {args.sell} {args.amount:.2f} → {args.buy}")
        print(f"   State: {result.get('state', '?')}, ID: {result.get('id', '?')}")


def cmd_transfer(args):
    """Transfer between own accounts."""
    payload = {
        "request_id": str(uuid.uuid4()),
        "source_account_id": args.from_account,
        "target_account_id": args.to_account,
        "amount": args.amount,
        "currency": args.currency or "EUR",
        "reference": args.reference or "Internal transfer",
    }
    result = api_call("POST", "/transfer", data=payload)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ Transferred {args.currency or 'EUR'} {args.amount:.2f}")
        print(f"   State: {result.get('state', '?')}")


def cmd_export(args):
    """Export transactions as CSV."""
    params = {"count": args.count or 100}
    if args.since:
        params["from"] = args.since
    if args.to:
        params["to"] = args.to

    txns = api_call("GET", "/transactions", params=params)

    import csv
    import io
    output = io.StringIO() if not args.output else open(args.output, "w", newline="")
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Description", "Amount", "Currency", "Balance", "State", "Merchant", "Card"])

    for tx in txns:
        date = tx.get("created_at", "")[:19]
        tx_type = tx.get("type", "")
        state = tx.get("state", "")
        merchant = tx.get("merchant", {}).get("name", "")
        card = tx.get("card", {}).get("card_number", "")
        for leg in tx.get("legs", []):
            desc = leg.get("description", "")
            amount = leg.get("amount", 0)
            currency = leg.get("currency", "")
            balance = leg.get("balance", "")
            writer.writerow([date, tx_type, desc, amount, currency, balance, state, merchant, card])

    if args.output:
        output.close()
        print(f"✅ Exported {len(txns)} transactions to {args.output}")
    else:
        print(output.getvalue())


def cmd_token_info(args):
    """Show token status."""
    tokens = load_tokens()
    if not tokens:
        print("Not authenticated.")
        return
    obtained = tokens.get("obtained_at", 0)
    expires_in = tokens.get("expires_in", 0)
    expires_at = obtained + expires_in
    remaining = expires_at - time.time()
    print(f"Client ID:     {tokens.get('client_id', '?')}")
    print(f"Token Type:    {tokens.get('token_type', '?')}")
    print(f"Obtained:      {datetime.fromtimestamp(obtained).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expires in:    {max(0, int(remaining))}s ({max(0, int(remaining/60))}min)")
    print(f"Refresh Token: {'✅ present' if tokens.get('refresh_token') else '❌ missing'}")


def main():
    load_env()

    parser = argparse.ArgumentParser(description="Revolut Business API CLI")
    sub = parser.add_subparsers(dest="command", help="Command")

    # auth
    p_auth = sub.add_parser("auth", help="Authenticate with Revolut")
    p_auth.add_argument("--code", help="Authorization code from OAuth redirect")

    # accounts
    p_acc = sub.add_parser("accounts", help="List accounts with balances")
    p_acc.add_argument("--json", action="store_true")

    # balance
    p_bal = sub.add_parser("balance", help="Show total EUR balance")
    p_bal.add_argument("--json", action="store_true")

    # transactions
    p_tx = sub.add_parser("transactions", aliases=["tx"], help="List transactions")
    p_tx.add_argument("--count", "-n", type=int, default=20)
    p_tx.add_argument("--account", "-a", help="Account name or ID")
    p_tx.add_argument("--since", help="From date (ISO)")
    p_tx.add_argument("--to", help="To date (ISO)")
    p_tx.add_argument("--type", help="Transaction type filter")
    p_tx.add_argument("--json", action="store_true")

    # counterparties
    p_cp = sub.add_parser("counterparties", aliases=["cp"], help="List counterparties")
    p_cp.add_argument("--name", help="Filter by name")
    p_cp.add_argument("--json", action="store_true")

    # pay
    p_pay = sub.add_parser("pay", help="Send payment")
    p_pay.add_argument("--counterparty", "-c", help="Counterparty name")
    p_pay.add_argument("--account-id", help="Target account ID")
    p_pay.add_argument("--amount", type=float, required=True)
    p_pay.add_argument("--currency", default="EUR")
    p_pay.add_argument("--reference", "-r", help="Payment reference")
    p_pay.add_argument("--draft", action="store_true", help="Create draft instead of sending")
    p_pay.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    p_pay.add_argument("--json", action="store_true")

    # exchange
    p_ex = sub.add_parser("exchange", aliases=["fx"], help="Exchange currencies")
    p_ex.add_argument("--amount", type=float, required=True)
    p_ex.add_argument("--sell", required=True, help="Sell currency (e.g. EUR)")
    p_ex.add_argument("--buy", required=True, help="Buy currency (e.g. USD)")
    p_ex.add_argument("--reference", "-r")
    p_ex.add_argument("--json", action="store_true")

    # transfer
    p_tr = sub.add_parser("transfer", help="Transfer between own accounts")
    p_tr.add_argument("--from-account", required=True, help="Source account ID")
    p_tr.add_argument("--to-account", required=True, help="Target account ID")
    p_tr.add_argument("--amount", type=float, required=True)
    p_tr.add_argument("--currency", default="EUR")
    p_tr.add_argument("--reference", "-r")
    p_tr.add_argument("--json", action="store_true")

    # export
    p_exp = sub.add_parser("export", help="Export transactions as CSV")
    p_exp.add_argument("--count", "-n", type=int, default=100)
    p_exp.add_argument("--since", help="From date (ISO)")
    p_exp.add_argument("--to", help="To date (ISO)")
    p_exp.add_argument("--output", "-o", help="Output file path")

    # token-info
    sub.add_parser("token-info", help="Show token status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "auth": cmd_auth,
        "accounts": cmd_accounts,
        "balance": cmd_balance,
        "transactions": cmd_transactions,
        "tx": cmd_transactions,
        "counterparties": cmd_counterparties,
        "cp": cmd_counterparties,
        "pay": cmd_pay,
        "exchange": cmd_exchange,
        "fx": cmd_exchange,
        "transfer": cmd_transfer,
        "export": cmd_export,
        "token-info": cmd_token_info,
    }

    func = cmd_map.get(args.command)
    if func:
        func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
