# Stripe CLI Skill 🧾

A universal Moltbot skill wrapping Stripe CLI for payment processing, webhook testing, and API operations. Includes optional ShapeScale-specific extensions for clinic management.

## What It Does

- Process payments, refunds, and subscriptions
- Manage customers and invoices
- Test webhooks locally
- Execute generic API calls to Stripe
- **ShapeScale extensions** (optional): Clinic presets, subscription plans, order integration

## Installation

### 1. Install Stripe CLI

**macOS:**
```bash
brew install stripe/stripe-cli/stripe
```

**Linux:**
```bash
# Download from https://github.com/stripe/stripe-cli/releases
wget https://github.com/stripe/stripe-cli/releases/download/v1.34.0/stripe_1.34.0_linux_amd64.deb
sudo dpkg -i stripe_1.34.0_linux_amd64.deb
```

**Authenticate:**
```bash
stripe login
```

### 2. Set Environment Variable

```bash
export STRIPE_SECRET_KEY=sk_test_your_key_here
```

Or use 1Password:
```bash
op read "op://Stripe/Secret Key" --vault Personal
```

### 3. Clone to Skills

```bash
cd ~/.moltbot/skills/
git clone https://github.com/mkessler/stripe-cli-moltbot-skill.git stripe
```

## Usage

### Universal Commands

| Invocation | Description |
|------------|-------------|
| `Create a test customer for $50` | Creates customer + $50 payment intent |
| `List my recent payments` | Lists last 10 payment intents |
| `Check payment status for pi_xxx` | Retrieves payment intent details |
| `Refund payment pi_xxx` | Refunds the full amount |
| `Trigger payment_intent.succeeded webhook` | Simulates webhook event |
| `Listen for webhooks for 30s` | Forwards webhooks to localhost |
| `Get customer details for cus_xxx` | Retrieves customer record |

### ShapeScale Extensions (Optional)

Requires `config/shapescale-presets.json`:

| Invocation | Description |
|------------|-------------|
| `Create clinic deposit for PracticeXYZ` | Creates customer + deposit template |
| `Create monthly subscription for clinic` | Creates recurring payment from presets |
| `Generate invoice for order #1234` | Creates invoice from template |
| `Check order status 1234` | Cross-references with shapescale-db |

## Configuration

### Universal

No config required. Uses `STRIPE_SECRET_KEY` environment variable.

### ShapeScale Presets (Optional)

Create `config/shapescale-presets.json`:

```json
{
  "clinic_templates": {
    "standard": { "deposit": 5000, "terms": "net30" },
    "premium": { "deposit": 10000, "terms": "net30" }
  },
  "subscription_plans": {
    "monthly": { "amount": 39900, "interval": "month" },
    "annual": { "amount": 399000, "interval": "year" }
  },
  "tax_rate": 0.0875,
  "default_currency": "usd"
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key (test or live) |
| `STRIPE_WEBHOOK_ENDPOINT` | No | Webhook forwarding URL (default: http://localhost:4242) |
| `SHAPESCALE_PRESETS_PATH` | No | Path to shapescale-presets.json |

## File Structure

```
stripe/
├── SKILL.md                    # This file
├── scripts/
│   ├── stripe.sh               # Universal CLI wrapper
│   └── shapescale-ext.sh       # ShapeScale extensions (optional)
├── config/
│   └── shapescale-presets.json # Clinic/subscription templates
├── patterns/
│   └── examples.md             # Usage examples
└── README.md                   # Installation guide (auto-generated)
```

## State

**Stateless** — Pure function of inputs. All state lives in Stripe.

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `shapescale-crm` | Link Stripe customer ID to CRM records |
| `shapescale-sales` | Orders → Payment intent creation |
| `campaign-orchestrator` | Failed payment → Follow-up campaign |
| `shapescale-db` | Match payments to database orders |

## Publishing

This skill is published to ClawdHub and available at:
https://github.com/mkessler/stripe-cli-moltbot-skill

## License

MIT License - see LICENSE file for details.
