---
name: finance-tracker
description: Track personal expenses with natural language. Log spending, view reports, search transactions. Works with any AI model.
---

# Finance Tracker

Track personal expenses with natural language. Simple, accurate, works with any model.

## Installation

```bash
clawdhub install finance-tracker
```

Or manually add to your system PATH:
```bash
export PATH="$PATH:/path/to/finance-tracker/bin"
```

## Quick Start

Add an expense:
```bash
finance add 50000 "lunch at cafe"
```

View this month's spending:
```bash
finance report month
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `finance add <amount> "<desc>"` | Log an expense | `finance add 50000 "lunch"` |
| `finance report [period]` | View spending report | `finance report week` |
| `finance recent [n]` | List recent transactions | `finance recent 10` |
| `finance search "<query>"` | Search transactions | `finance search "food"` |
| `finance categories` | List all categories | `finance categories` |
| `finance export [format]` | Export data (csv/json) | `finance export csv` |
| `finance currency [code]` | Get/set currency | `finance currency USD` |

## Periods

For reports, use these period options:
- `today` — Today only
- `week` — Last 7 days
- `month` — Last 30 days (default)
- `year` — Last 365 days
- `all` — All time

## Amount Formats

These all work:
- `50000` — Plain number
- `50k` or `50K` — With k suffix (= 50,000)
- `"50 000"` — With spaces (will be parsed)

## Auto-Categorization

Categories are detected automatically from your description:

| Category | Detected Keywords |
|----------|-------------------|
| 🍔 Food | lunch, dinner, breakfast, cafe, restaurant, grocery |
| 🚗 Transport | taxi, uber, bus, metro, fuel, gas |
| 🛍️ Shopping | clothes, shoes, shirt, shopping |
| 📱 Tech | phone, laptop, headphones, charger |
| 🎮 Entertainment | movie, game, netflix, spotify |
| 📚 Education | book, course, school, university |
| 💊 Health | medicine, pharmacy, doctor, gym |
| 🏠 Home | rent, utility, furniture, internet |
| 💇 Personal | haircut, barber, salon |
| 🎁 Gifts | gift, present, birthday |
| ✈️ Travel | travel, flight, hotel |

No keyword match? Defaults to ❓ Other.

## Output Format

All commands return consistent, parseable output:

**Success:**
```
✅ Logged: 🍔 50,000 UZS — lunch at cafe (food)
```

**Report:**
```
📊 This Month's Spending
━━━━━━━━━━━━━━━━━━━━━
💵 Total: 250,000 UZS

🍔 Food: 120,000 UZS (48.0%)
🚗 Transport: 80,000 UZS (32.0%)
📱 Tech: 50,000 UZS (20.0%)

📝 15 transactions
📈 Average: 16,666 UZS
```

**Error:**
```
❌ Invalid amount. Use a positive number.
💡 Usage: finance add 50000 "lunch"
```

## Data Storage

All data is stored locally in `~/.finance-tracker/`:
- `transactions.json` — Machine-readable data
- `FINANCE_LOG.md` — Human-readable log

Data is automatically synced to both files.

## Examples for Agents

When your human says "I spent 50k on lunch", run:
```bash
finance add 50000 "lunch"
```

When they ask "how much did I spend this week?", run:
```bash
finance report week
```

When they ask "what did I spend on food?", run:
```bash
finance search "food"
```

## Tips

1. Always quote descriptions with spaces: `"lunch at cafe"`
2. Use `k` for thousands to save typing: `50k` instead of `50000`
3. Check `finance recent` to verify transactions were logged
4. Categories are case-insensitive
5. Data persists across sessions in `~/.finance-tracker/`

---

Made with 🦞 by Salen
