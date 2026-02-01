# Mayar Payment Integration - Clawdbot Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ahsanatha/mayar-payment-skill)

Complete Mayar.id payment integration for Clawdbot. Enable your AI agent to generate invoices, payment links, and track transactions via Indonesian payment platform.

## 🎯 Features

- ✅ Create payment invoices with itemized billing
- ✅ Generate payment links for customers  
- ✅ Track transactions & payment status
- ✅ Support ALL Indonesian payment methods (bank transfer, e-wallet, QRIS)
- ✅ WhatsApp/Telegram/Discord payment workflows
- ✅ Membership/subscription management
- ✅ Complete MCP (Model Context Protocol) integration
- ✅ 15 ready-to-use MCP tools

## 🚀 Quick Start

### Prerequisites

- Clawdbot instance with mcporter installed
- Mayar.id account (free signup at [mayar.id](https://mayar.id))
- Node.js (for mcporter)

### Installation

**1. Clone this repository**

```bash
cd ~/.clawdbot/skills  # or your Clawdbot skills directory
git clone https://github.com/ahsanatha/mayar-payment-skill.git mayar-payment
```

**2. Get Mayar API Key**

- Sign up at https://mayar.id
- Go to https://web.mayar.id/api-keys
- Generate new API key (JWT token)

**For testing, use sandbox:**
- Dashboard: https://web.mayar.club
- API Keys: https://web.mayar.club/api-keys

**3. Configure Credentials**

```bash
mkdir -p ~/.config/mayar
cat > ~/.config/mayar/credentials << EOF
MAYAR_API_TOKEN="your-jwt-token-here"
EOF
chmod 600 ~/.config/mayar/credentials
```

**4. Configure MCP Server**

Add to your `config/mcporter.json`:

```json
{
  "mcpServers": {
    "mayar": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.mayar.id/sse",
        "--header",
        "Authorization:YOUR_API_TOKEN_HERE"
      ]
    }
  }
}
```

Replace `YOUR_API_TOKEN_HERE` with your actual JWT token.

**5. Test Installation**

```bash
# List available tools
mcporter list mayar

# Test balance check
mcporter call mayar.get_balance
```

If you see 15 available tools → Installation successful! ✅

## 💡 Usage Examples

### Create Payment Invoice

```bash
mcporter call mayar.create_invoice \
  name="Customer Name" \
  email="customer@email.com" \
  mobile="\"628xxxxxxxxxx\"" \
  description="Order description" \
  redirectURL="https://yoursite.com/success" \
  expiredAt="2026-12-31T23:59:59+07:00" \
  items='[
    {"quantity":1,"rate":500000,"description":"Product A"},
    {"quantity":2,"rate":100000,"description":"Product B"}
  ]'
```

Returns payment link: `https://subdomain.myr.id/invoices/xxxxx`

### WhatsApp Integration

```javascript
// Create invoice
const invoice = /* mcporter call mayar.create_invoice ... */;

// Format message
const message = `
✅ *Order Confirmed!*

*Total: Rp ${total.toLocaleString('id-ID')}*

💳 Pembayaran:
${invoice.data.link}

⏰ Berlaku sampai: ${expiryDate}
`.trim();

// Send via WhatsApp
message({
  action: 'send',
  channel: 'whatsapp',
  target: customerPhone,
  message: message
});
```

### Check Transactions

```bash
# Latest transactions
mcporter call mayar.get_latest_transactions page:1 pageSize:10

# Unpaid invoices
mcporter call mayar.get_latest_unpaid_transactions page:1 pageSize:10

# Today's revenue
mcporter call mayar.get_transactions_by_time_period \
  page:1 pageSize:100 \
  period:"today" \
  sortField:"amount" \
  sortOrder:"DESC"
```

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Main skill guide with setup & workflows
- **[MCP Tools Reference](references/mcp-tools.md)** - Complete list of 15 MCP tools
- **[Integration Examples](references/integration-examples.md)** - Real-world patterns (WhatsApp bots, subscriptions, events, etc.)
- **[API Reference](references/api-reference.md)** - REST API documentation (alternative to MCP)

## 🎯 Use Cases

- **E-commerce bots** - Automated order processing via WhatsApp/Telegram
- **Service marketplace** - Sell services with instant payment links
- **Course platforms** - Sell courses with auto-access after payment
- **Membership sites** - Subscription & tier management
- **Event ticketing** - Generate tickets after payment
- **Donation platforms** - Accept donations with tracking
- **Wedding services** - Sell templates/packages
- **Freelance payments** - Professional invoicing

## 🔧 Available MCP Tools

### Payment Generation
- `create_invoice` - Create itemized invoice with payment link
- `send_portal_link` - Send customer portal access
- `get_balance` - Check account balance

### Transaction Queries
- `get_latest_transactions` - Recent paid transactions
- `get_latest_unpaid_transactions` - Pending payments
- `get_customer_detail` - Customer transaction history
- `get_transactions_by_time_period` - Filter by period
- `get_transactions_by_time_range` - Custom date range
- Plus 7 more filtering/query tools...

### Membership Management
- `get_membership_customer_by_specific_product`
- `get_membership_customer_by_specific_product_and_tier`

[See full tool reference →](references/mcp-tools.md)

## 🌍 Payment Methods Supported

Mayar.id supports all major Indonesian payment methods:

**Bank Transfer:** BCA, Mandiri, BNI, BRI, Permata, CIMB Niaga  
**E-Wallet:** GoPay, OVO, DANA, LinkAja, ShopeePay  
**Others:** QRIS, Virtual Account, Credit/Debit Card

## 🛠️ Troubleshooting

### "MCP server not found"
```bash
mcporter config list
mcporter list mayar
```

### "Invalid mobile number"
Phone must be:
- String format: `"\"628xxx\""`
- No + symbol, no spaces
- Country code 62 (Indonesia)

### "404 on payment link"
Check your Mayar subdomain in dashboard settings.  
Link format: `https://subdomain.myr.id/invoices/slug`

### "Webhook not working"
1. Register webhook URL:
```bash
curl -X POST https://api.mayar.id/hl/v1/webhook/register \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"urlHook":"https://yoursite.com/webhook"}'
```
2. Ensure URL is publicly accessible
3. Must respond with 200 status

## 📊 Skill Architecture

```
mayar-payment/
├── SKILL.md                      # Main skill documentation
├── README.md                     # This file (GitHub)
└── references/
    ├── api-reference.md          # REST API docs (8KB)
    ├── mcp-tools.md              # MCP tools reference (6.6KB)
    └── integration-examples.md   # Real-world patterns (12KB)
```

Following Clawdbot skill best practices:
- Progressive disclosure (main guide → detailed references)
- Concise core documentation
- Real-world examples
- Production-ready patterns

## 🌐 Environments

**Production:**
- Dashboard: https://web.mayar.id
- API: `https://api.mayar.id/hl/v1/`

**Sandbox (Testing):**
- Dashboard: https://web.mayar.club  
- API: `https://api.mayar.club/hl/v1/`

Always test in sandbox first before using production!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

MIT License - Free to use, modify, and distribute.

See [LICENSE](LICENSE) file for details.

## 🙏 Credits

Created by [Samara](https://github.com/ahsanatha) / TSR Labs for the Clawdbot community.

Based on [Mayar.id](https://mayar.id) API and MCP server.

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/ahsanatha/mayar-payment-skill/issues)
- **Mayar Community:** https://t.me/mcngroup
- **Mayar Docs:** https://docs.mayar.id

## ⭐ Star History

If this skill helps you, please star the repo! ⭐

---

**Made with ❤️ for the Clawdbot community**
