# @skillzmarket/openclaw-skill

OpenClaw skill for calling monetized AI skills from the Skillz Market with automatic cryptocurrency payments.

## Installation

### Via ClawHub (recommended)
```bash
clawhub install skillzmarket
```

### Via npx add-skill
```bash
npx add-skill github:skillzmarket/skill
```

### Via openskills
```bash
npx openskills install skillzmarket/skill
```

### Manual installation
```bash
git clone https://github.com/skillzmarket/skill
cp -r skill ~/.openclaw/skills/skillzmarket
cd ~/.openclaw/skills/skillzmarket && npm install
```

## Configuration

Set your wallet private key for payments. Either:

**Option 1: Environment variable**
```bash
export SKILLZ_PRIVATE_KEY=0x...
```

**Option 2: OpenClaw config** (`~/.openclaw/openclaw.json`)
```json
{
  "skills": {
    "entries": {
      "skillzmarket": {
        "enabled": true,
        "apiKey": "0xYOUR_PRIVATE_KEY"
      }
    }
  }
}
```

## Usage

### Search for skills
```
/skillzmarket search translate
```

### Get skill details
```
/skillzmarket info echo
```

### Call a skill (with automatic payment)
```
/skillzmarket call echo {"message": "hello"}
```

### Call an endpoint directly
```
/skillzmarket direct https://skills.example.com/echo {"message": "hello"}
```

## How it works

1. Skills are registered on the Skillz Market API
2. When you call a skill, the CLI looks up the skill's endpoint and price
3. The x402 payment protocol automatically handles USDC payments on Base
4. You receive the skill's response

## Environment Variables

- `SKILLZ_PRIVATE_KEY` - Your wallet private key for payments (required for `call` and `direct`)
- `SKILLZ_API_URL` - Override the API URL (default: `https://api.skillz.market`)

## Links

- [Skillz Market](https://skillz.market)
- [ClawHub](https://clawhub.com)
- [x402 Protocol](https://x402.org)
