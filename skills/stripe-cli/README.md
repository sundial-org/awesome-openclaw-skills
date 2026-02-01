# Stripe CLI for Moltbot 🧾

A universal Moltbot skill wrapping Stripe CLI for payment processing, webhook testing, and API operations. Includes optional ShapeScale-specific extensions.

[![ClawdHub](https://img.shields.io/badge/ClawdHub-stripe--cli-blue)](https://clawdhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 💳 **Payment Operations** - Create payment intents, process refunds
- 👤 **Customer Management** - Create and list customers
- 🔄 **Subscriptions** - Recurring payments (ShapeScale extension)
- 🏥 **Clinic Presets** - Pre-configured templates (ShapeScale extension)
- 📡 **Webhook Testing** - Listen and trigger webhooks locally
- 🔧 **Generic API** - Full Stripe API access

## Quick Start

### Install Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
wget https://github.com/stripe/stripe-cli/releases/download/v1.34.0/stripe_1.34.0_linux_amd64.deb
sudo dpkg -i stripe_1.34.0_linux_amd64.deb

# Login
stripe login
```

### Install Skill

```bash
cd ~/.moltbot/skills/
git clone https://github.com/mkessler/stripe-cli-moltbot-skill.git stripe
```

### Configure

```bash
export STRIPE_SECRET_KEY=sk_test_your_key_here
```

## Usage

### Universal Commands

| Command | Description |
|---------|-------------|
| `stripe customer create "Name"` | Create a customer |
| `stripe payment create 5000` | Create $50 payment intent |
| `stripe payment refund pi_xxx` | Refund payment |
| `stripe webhook trigger payment_intent.succeeded` | Test webhook |
| `stripe webhook listen 30` | Listen for webhooks (30s) |

### ShapeScale Commands (Optional)

| Command | Description |
|---------|-------------|
| `shapescale clinic create "Clinic Name"` | Create clinic with preset |
| `shapescale subscription create cus_xxx annual` | Create subscription |
| `shapescale invoice generate cus_xxx ORDER-001` | Generate invoice |
| `shapescale order status ORDER-001` | Check order payment |

See [SKILL.md](SKILL.md) for full documentation.

## File Structure

```
stripe-cli-moltbot-skill/
├── SKILL.md                    # Full skill documentation
├── README.md                   # This file
├── LICENSE                     # MIT License
├── package.json                # ClawdHub metadata
├── .gitignore
├── scripts/
│   ├── stripe.sh               # Universal CLI wrapper
│   └── shapescale-ext.sh       # ShapeScale extensions
├── config/
│   └── shapescale-presets.json # Clinic/subscription templates
└── patterns/
    └── examples.md             # Usage examples
```

## Configuration

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
  "tax_rate": 0.0875
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key |
| `STRIPE_WEBHOOK_ENDPOINT` | No | Webhook forwarding URL |
| `SHAPESCALE_PRESETS_PATH` | No | Path to presets JSON |

## Publishing

This skill is available on:
- **GitHub**: https://github.com/mkessler/stripe-cli-moltbot-skill
- **ClawdHub**: stripe-cli

## License

MIT License - see [LICENSE](LICENSE) file.

## Author

Martin Kessler [@mkessler](https://github.com/mkessler)
