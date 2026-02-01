# LLM Wallet Usage Examples

## Complete Workflows

### Workflow 1: First Time User

```bash
# Step 1: Create wallet
llm-wallet create --label "my-first-wallet"
# Output: address: 0x742d35Cc6635C0532925a3b8D2A0a7e3E4b1b4e4

# Step 2: Set conservative spending limits
llm-wallet set-limit --per-tx 0.10 --daily 5.00

# Step 3: Fund wallet with testnet USDC
# Visit: https://faucet.polygon.technology/
# Request USDC on Polygon Amoy network

# Step 4: Verify balance
llm-wallet balance
# Output: usdc: "10.000000", network: "polygon-amoy"

# Step 5: Ready to make payments!
```

### Workflow 2: Making a Payment

```bash
# Step 1: Pre-check payment
llm-wallet check-payment "https://api.example.com/weather?location=London"
# Output: canAfford: true, estimatedCost: "0.001"

# Step 2: Ask user for approval
# "I need to pay $0.001 USDC to https://api.example.com/weather. Approve?"

# Step 3: Execute payment
llm-wallet pay "https://api.example.com/weather?location=London"
# Output: success, data: {...}, transactionHash: "0xabc..."

# Step 4: Verify in history
llm-wallet history
# Shows: timestamp, recipient, amount, status, txHash
```

### Workflow 3: Registering a Paid API

```bash
# Step 1: Register API as reusable tool
llm-wallet register-api "https://api.example.com/translate" --name translate_api

# Step 2: Confirm registration
llm-wallet list-apis
# Output: translate_api, weather_api, ...

# Step 3: Use registered API
llm-wallet call-api translate_api --params '{"text": "hello", "to": "es"}'
# Output: translation result + payment confirmation

# Step 4: Check payment in history
llm-wallet history
# Shows: payment to translate_api endpoint
```

### Workflow 4: Monitoring Usage

```bash
# Check current limits and usage
llm-wallet get-limits
# Output:
#   perTransaction: "0.10"
#   dailyLimit: "5.00"
#   dailySpent: "0.015"
#   remainingDaily: "4.985"

# View all transactions
llm-wallet history
# Output: List of all payments with details

# Check balance
llm-wallet balance
# Output: Current USDC and native token balance
```

## Real API Examples

### Example 1: Weather API

```bash
# Make payment to weather API
llm-wallet pay "https://api.weatherapi.com/v1/current.json?q=London" \
  --method GET

# Response:
# {
#   "location": {"name": "London", "country": "UK"},
#   "current": {"temp_c": 15, "condition": {"text": "Cloudy"}},
#   "payment": {"amount": "0.001", "status": "completed"}
# }
```

### Example 2: Translation API

```bash
# Register translation API
llm-wallet register-api "https://api.translate.com/v1/translate" \
  --name translate_api

# Call with parameters
llm-wallet call-api translate_api \
  --params '{"text": "Hello, world!", "source": "en", "target": "es"}'

# Response:
# {
#   "translation": "¡Hola, mundo!",
#   "payment": {"amount": "0.002", "status": "completed"}
# }
```

### Example 3: Image Generation API

```bash
# Make POST request with JSON body
llm-wallet pay "https://api.image-gen.com/v1/generate" \
  --method POST \
  --body '{"prompt": "sunset over ocean", "size": "1024x1024"}'

# Response:
# {
#   "image_url": "https://cdn.image-gen.com/abc123.png",
#   "payment": {"amount": "0.050", "status": "completed"}
# }
```

## Agent Conversation Examples

### Example 1: Weather Query

**User:** "What's the weather in London?"

**Agent:** "I'll check the weather for you using a paid API."

```bash
# Agent checks cost first
llm-wallet check-payment "https://api.weather.com/current?location=London"
# canAfford: true, estimatedCost: "0.001"
```

**Agent:** "I need to make a payment of $0.001 USDC to access the weather API. Your current limits are: $0.10 per transaction, $5.00 daily ($4.99 remaining). Approve?"

**User:** "Yes, approved."

```bash
# Agent executes payment
llm-wallet pay "https://api.weather.com/current?location=London"
# success: true, temperature: 15°C, condition: "Cloudy"
```

**Agent:** "The weather in London is currently 15°C and cloudy. Payment of $0.001 USDC completed. Transaction ID: 0xabc..."

### Example 2: Multiple API Calls

**User:** "Translate 'hello' to Spanish, French, and German"

**Agent:** "I'll use the translation API for each language. This will cost approximately $0.006 USDC total. Approve?"

**User:** "Approved"

```bash
# First translation
llm-wallet pay "https://api.translate.com/v1/translate?text=hello&to=es"
# Result: "hola"

# Second translation
llm-wallet pay "https://api.translate.com/v1/translate?text=hello&to=fr"
# Result: "bonjour"

# Third translation
llm-wallet pay "https://api.translate.com/v1/translate?text=hello&to=de"
# Result: "hallo"
```

**Agent:** "Translations complete:
- Spanish: hola
- French: bonjour
- German: hallo
Total cost: $0.006 USDC. Remaining daily limit: $4.994"

### Example 3: Registered API Usage

**User:** "Set up the translation API for easy reuse"

```bash
# Agent registers API
llm-wallet register-api "https://api.translate.com/v1/translate" --name translate_api
# success: true
```

**Agent:** "Translation API registered as 'translate_api'. You can now use it without specifying the full URL."

**User:** "Translate 'goodbye' to Japanese"

```bash
# Agent uses registered API
llm-wallet call-api translate_api --params '{"text": "goodbye", "to": "ja"}'
# Result: "さようなら" (sayōnara)
```

**Agent:** "In Japanese, 'goodbye' is 'さようなら' (sayōnara). Payment of $0.002 USDC completed."

## Error Handling Examples

### Insufficient Balance

```bash
llm-wallet pay "https://api.example.com/expensive?cost=100"
# Error: Insufficient USDC balance. Have: 0.5, Need: 100.0
#        Fund your wallet at: https://faucet.polygon.technology/
```

### Spending Limit Exceeded

```bash
llm-wallet pay "https://api.example.com/premium?cost=0.50"
# Error: Payment exceeds per-transaction limit
#        Requested: 0.50, Limit: 0.10
#        Increase limit with: llm-wallet set-limit --per-tx 1.00
```

### Daily Limit Reached

```bash
llm-wallet pay "https://api.example.com/standard?cost=0.05"
# Error: Daily spending limit reached
#        Spent today: 5.00/5.00
#        Resets at: 2026-02-01 00:00:00 UTC
#        Or increase limit: llm-wallet set-limit --daily 10.00
```

### API Not Responding

```bash
llm-wallet pay "https://api.down-service.com/endpoint"
# Error: Network timeout after 3 retry attempts
#        Service may be temporarily unavailable
#        Try again later or check: https://status.down-service.com
```

## Advanced Examples

### Custom Network Configuration

```bash
# Use mainnet (⚠️ real money!)
export WALLET_NETWORK="polygon"
export FACILITATOR_URL="https://x402.polygon.technology"

llm-wallet balance
# Shows mainnet balance

# Make mainnet payment
llm-wallet pay "https://api.mainnet-service.com/endpoint"
```

### Multiple Wallets

```bash
# Create production wallet
llm-wallet create --label "production"
# address: 0x111...

# Create development wallet
llm-wallet create --label "development"
# address: 0x222...

# List all wallets
llm-wallet list-wallets
# production: 0x111..., development: 0x222...

# Switch to production
llm-wallet set-active --label "production"

# Verify active wallet
llm-wallet balance
# Shows production wallet balance
```

### Batch Operations

```bash
# Register multiple APIs
llm-wallet register-api "https://api.weather.com/v1" --name weather
llm-wallet register-api "https://api.translate.com/v1" --name translate
llm-wallet register-api "https://api.image.com/v1" --name image_gen

# List all registered
llm-wallet list-apis
# weather, translate, image_gen

# Call each in sequence
llm-wallet call-api weather --params '{"location": "NYC"}'
llm-wallet call-api translate --params '{"text": "hi", "to": "es"}'
llm-wallet call-api image_gen --params '{"prompt": "sunset"}'

# Check total spent
llm-wallet get-limits
# dailySpent: "0.153"
```

## Integration Tips

### In OpenClaw Agents

When an agent needs to use a paid API:

1. **Check cost first**: Always run `check-payment` to verify affordability
2. **Ask user**: Present cost and current limits, request approval
3. **Execute**: Run `pay` command after approval
4. **Confirm**: Show transaction ID and update limits
5. **Log**: Record in conversation for transparency

### Approval Templates

**Standard approval request:**
```
I need to access [SERVICE_NAME] at [URL].
Cost: $[AMOUNT] USDC
Current limits: $[PER_TX] per transaction, $[DAILY_REMAINING] remaining today
Approve payment?
```

**Batch approval request:**
```
I need to make [N] API calls to [SERVICE_NAME].
Estimated total cost: $[TOTAL] USDC
Individual costs: $[COST1], $[COST2], ...
Current remaining daily limit: $[REMAINING]
Approve all payments?
```

### Best Practices

1. **Always verify cost** before requesting approval
2. **Be transparent** about what payment enables
3. **Show remaining limits** to help user decide
4. **Log all transactions** for audit trail
5. **Handle errors gracefully** with clear instructions
6. **Test on testnet first** before mainnet usage
7. **Start with low limits** and increase as needed
8. **Monitor daily usage** to avoid limit exhaustion
