# Revolut Business API — OpenClaw Skill

Full CLI for **Revolut Business** — accounts, balances, transactions, counterparties, payments, FX exchange, CSV export.

> ⚠️ **Business only** — Revolut Personal API requires PSD2 Open Banking (AISP) registration and is not supported.

## Features

- 💰 **Accounts & Balances** — list all accounts, total EUR balance
- 📋 **Transactions** — filter by date, type, account; JSON output
- 👥 **Counterparties** — list, search by name
- 💸 **Payments** — send payments (with confirmation) or create drafts
- 💱 **FX Exchange** — exchange currencies between accounts
- 🔄 **Internal Transfers** — move funds between own accounts
- 📊 **CSV Export** — export transactions for bookkeeping
- 🔑 **Auto Token Refresh** — OAuth tokens refresh automatically via JWT

## Setup (Step by Step)

### Prerequisites
- Python 3.10+
- `pip install PyJWT cryptography`
- A **Revolut Business** account (not personal!)
- A domain you control (for OAuth redirect URI)

---

### Step 1: Generate RSA Key Pair & X509 Certificate

```bash
mkdir -p ~/.clawdbot/revolut
cd ~/.clawdbot/revolut

# Generate private key
openssl genrsa -out private.pem 2048

# Generate X509 certificate (Revolut requires this format, NOT just a public key!)
openssl req -new -x509 -key private.pem -out certificate.pem -days 730 -subj "/CN=openclaw/O=YourCompany/C=AT"
```

> ⚠️ Revolut **rejects** a plain public key — you must upload an **X509 certificate**.

---

### Step 2: Set Up OAuth Callback URL

Revolut needs a real HTTPS URL to redirect to after authorization. You have two options:

#### Option A: Cloudflare Worker (recommended, free)

If you have a domain on Cloudflare, create a simple worker that displays the auth code:

```javascript
addEventListener("fetch", event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const code = url.searchParams.get("code")
  if (code) {
    return new Response(`<html><body style="font-family:sans-serif;padding:40px">
      <h1>✅ Revolut Authorization Code</h1>
      <pre style="background:#f0f0f0;padding:20px;font-size:18px">${code}</pre>
      <p>Copy this code and paste it into the CLI.</p>
    </body></html>`, { headers: { "content-type": "text/html" } })
  }
  return new Response("Waiting for redirect...", { headers: { "content-type": "text/html" } })
}
```

Deploy it to e.g. `https://revolut.yourdomain.com/callback`

You'll also need a DNS record pointing to the worker:
- Type: `AAAA`, Name: `revolut`, Content: `100::`, Proxy: ON (orange cloud)

#### Option B: n8n Webhook

If you run n8n, create a webhook workflow that returns the `code` query parameter.

#### Option C: Any HTTPS endpoint

Any URL that captures the `?code=` parameter and shows it to you works.

> ❌ `localhost` will **not** work as a redirect URI.
> ❌ `revolut.com` will **not** work (Revolut blocks their own domain).

---

### Step 3: Register API Certificate in Revolut

1. Go to **business.revolut.com** → **Settings** → **API**
2. Click **Add Certificate**
3. Fill in:
   - **Certificate title:** `openclaw` (or any name)
   - **OAuth redirect URI:** Your callback URL from Step 2 (e.g. `https://revolut.yourdomain.com/callback`)
   - **X509 public key:** Paste the **entire** content of `certificate.pem` (including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`)
4. **Production IP whitelist:** Add your server's public IP (`curl ifconfig.me`)
5. Click **Add** → Copy the **Client ID** that Revolut shows you

---

### Step 4: Configure Environment Variables

Add to your `.env`:

```bash
REVOLUT_CLIENT_ID=your_client_id_here
REVOLUT_ISS_DOMAIN=revolut.yourdomain.com   # your redirect URI domain WITHOUT https://
```

> ⚠️ **Important:** `REVOLUT_ISS_DOMAIN` must be the domain part of your redirect URI (without `https://`). This is used as the `iss` (issuer) claim in the JWT. Revolut will reject any other value with: *"The 'iss' (issuer) claim must be your domain"*

---

### Step 5: Authorize (OAuth Flow)

```bash
# Shows the consent URL
python3 scripts/revolut.py auth
```

This prints a URL like:
```
https://business.revolut.com/app-confirm?client_id=YOUR_ID&redirect_uri=https://revolut.yourdomain.com/callback&response_type=code
```

1. Open this URL in your browser
2. Log in to Revolut Business and approve the access
3. You'll be redirected to your callback URL with a `?code=` parameter
4. Copy the code and exchange it immediately (codes expire in minutes!):

```bash
python3 scripts/revolut.py auth --code oa_prod_xxxxx
```

If successful, you'll see: `✅ Authenticated successfully!`

Tokens are saved to `~/.clawdbot/revolut/tokens.json` and auto-refresh from now on.

---

### Step 6: Verify It Works

```bash
python3 scripts/revolut.py accounts      # Should show your accounts + balances
python3 scripts/revolut.py tx -n 5       # Last 5 transactions
python3 scripts/revolut.py token-info    # Token status
```

## Usage

```bash
# Accounts & Balances
revolut accounts                 # All accounts with balances
revolut balance                  # Total EUR balance

# Transactions
revolut tx                       # Last 20 transactions
revolut tx -n 50                 # Last 50
revolut tx --since 2026-01-01    # Since date
revolut tx --since 2026-01-01 --to 2026-01-31
revolut tx -a Main               # Filter by account name
revolut tx --type card_payment   # Filter by type
revolut tx --json                # JSON output

# Counterparties
revolut cp                       # List all
revolut cp --name "Lisa"         # Search

# Payments
revolut pay -c "Lisa Dreischer" --amount 50.00 -r "Lunch"
revolut pay -c "Lisa Dreischer" --amount 50.00 --draft    # Draft (approve in app)
revolut pay -c "Lisa Dreischer" --amount 50.00 --yes      # Skip confirmation

# Currency Exchange
revolut fx --amount 100 --sell EUR --buy USD

# Internal Transfers
revolut transfer --from-account <ID> --to-account <ID> --amount 100

# Export
revolut export -o transactions.csv
revolut export --since 2026-01-01 -n 200 -o jan.csv

# Token Status
revolut token-info
```

Transaction types: `card_payment`, `transfer`, `exchange`, `topup`, `atm`, `fee`, `refund`

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Invalid public key` | Uploaded plain RSA public key | Use X509 certificate (`openssl req -new -x509 ...`) |
| `Bad Request: redirect URL` | Redirect URI mismatch | Must match exactly what's in Revolut API settings |
| `unauthorized_client: Failed to authorise client` | Wrong Client ID or expired auth code | Check Client ID in Revolut settings; get a fresh code |
| `The 'iss' claim must be your domain` | JWT issuer doesn't match | Set `REVOLUT_ISS_DOMAIN` to your redirect URI domain (without https://) |
| Auth code doesn't work | Codes expire in minutes | Get a new code and exchange immediately |

## Security

- Private key and tokens stored in `~/.clawdbot/revolut/` — treat as sensitive
- Payments require explicit confirmation (use `--yes` to skip, `--draft` for approval in app)
- Never share your private key, tokens, or client assertion JWT
- Access tokens expire after ~40 minutes and auto-refresh

## License

MIT
