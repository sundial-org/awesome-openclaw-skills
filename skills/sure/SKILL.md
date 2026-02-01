---
name: sure
description: Get report from Sure personal financial board
homepage: https://sure.am
metadata: {"clawdbot":{"emoji":"📈","requires":{"bin": ["curl"],"env":["SURE_API_KEY", "SURE_BASE_URL"]}}}
---
# Sure Skill

## Setup
1. Go to your Sure app, example : https://localhost:3000 
2. Go to settings and get an API key, example : https://localhost:3000/settings/api_key
3. Export your API KEY and BASE URL as environment variables :
 ```bash
export SURE_API_KEY="YOUR_API_KEY"
export SURE_BASE_URL="YOUR_BASE_URL"
```

## Get accounts
List all accounts amounts
```bash
curl -H "X-Api-Key: $SURE_API_KEY" "$SURE_BASE_URL/api/v1/accounts"
```
