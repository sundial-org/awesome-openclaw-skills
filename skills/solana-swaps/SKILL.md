---
name: solana-swaps
description: Swap tokens on Solana via Jupiter aggregator and check wallet balances. Use when user wants to swap tokens, check SOL/token balance, or get swap quotes.
metadata: {"clawdbot":{"emoji":"💰","requires":{"bins":["solana","spl-token","curl","jq","node"],"env":["SOLANA_KEYPAIR_PATH"]}}}
---

# Solana Swaps

Manage your Solana wallet: check balances and swap tokens using the Jupiter aggregator.

## Environment Variables

These environment variables are pre-configured and available for use:

| Variable | Description |
|----------|-------------|
| `SOLANA_KEYPAIR_PATH` | Path to wallet keypair JSON file |
| `JUPITER_API_KEY` | Jupiter API key for authenticated requests (avoids platform fees, required for Token2022/pump.fun tokens) |

**Note:** These are already set in the skill config. Just use `$SOLANA_KEYPAIR_PATH` and `$JUPITER_API_KEY` directly in commands.

### Verify Setup

```bash
# Check wallet address
solana address --keypair "$SOLANA_KEYPAIR_PATH"

# Check Solana CLI config
solana config get
```

## Balance Checking

### Check SOL Balance

```bash
solana balance --keypair "$SOLANA_KEYPAIR_PATH"
```

### List All Token Accounts

```bash
spl-token accounts --owner $(solana address --keypair "$SOLANA_KEYPAIR_PATH")
```

### Check Specific Token Balance

```bash
spl-token balance <TOKEN_MINT_ADDRESS> --owner $(solana address --keypair "$SOLANA_KEYPAIR_PATH")
```

## Common Token Mint Addresses

| Token | Symbol | Mint Address | Decimals |
|-------|--------|-------------|----------|
| Wrapped SOL | SOL | So11111111111111111111111111111111111111112 | 9 |
| USD Coin | USDC | EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v | 6 |
| Tether | USDT | Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB | 6 |
| Bonk | BONK | DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 | 5 |
| Jupiter | JUP | JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN | 6 |
| Raydium | RAY | 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R | 6 |

## Token Swaps via Jupiter

**CRITICAL: Always display swap details and wait for explicit user confirmation before executing any swap.**

### Step 1: Get Quote

Convert human-readable amounts to raw units:
- SOL: multiply by 1,000,000,000 (10^9)
- USDC/USDT: multiply by 1,000,000 (10^6)
- BONK: multiply by 100,000 (10^5)

```bash
# Example: Get quote for swapping 1 SOL to USDC
INPUT_MINT="So11111111111111111111111111111111111111112"
OUTPUT_MINT="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
AMOUNT="1000000000"  # 1 SOL in lamports
SLIPPAGE_BPS="50"    # 0.5% slippage

# Get quote with API key authentication
curl -s -H "x-api-key: $JUPITER_API_KEY" \
  "https://api.jup.ag/swap/v1/quote?inputMint=${INPUT_MINT}&outputMint=${OUTPUT_MINT}&amount=${AMOUNT}&slippageBps=${SLIPPAGE_BPS}" | jq .
```

### Step 2: Display Quote and Request Confirmation

Parse the quote response and display to user:
- Input: amount and token name
- Output: expected amount and token name
- Price impact percentage
- Slippage tolerance
- Minimum received (otherAmountThreshold)

**IMPORTANT**: Ask user "Do you want to proceed with this swap?" and wait for explicit confirmation ("yes", "proceed", "confirm") before continuing.

### Step 3: Build Swap Transaction

After user confirms, request the swap transaction:

```bash
USER_PUBKEY=$(solana address --keypair "$SOLANA_KEYPAIR_PATH")

# Save quote response to file
QUOTE_FILE="/tmp/jupiter_quote.json"
curl -s -H "x-api-key: $JUPITER_API_KEY" \
  "https://api.jup.ag/swap/v1/quote?inputMint=${INPUT_MINT}&outputMint=${OUTPUT_MINT}&amount=${AMOUNT}&slippageBps=${SLIPPAGE_BPS}" > "$QUOTE_FILE"

# Request swap transaction
curl -s -X POST \
  -H "x-api-key: $JUPITER_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.jup.ag/swap/v1/swap" \
  -d "{
    \"quoteResponse\": $(cat $QUOTE_FILE),
    \"userPublicKey\": \"${USER_PUBKEY}\",
    \"dynamicComputeUnitLimit\": true,
    \"prioritizationFeeLamports\": {
      \"priorityLevelWithMaxLamports\": {
        \"maxLamports\": 5000000,
        \"priorityLevel\": \"high\"
      }
    }
  }" > /tmp/jupiter_swap.json

# Extract the swap transaction
SWAP_TX=$(cat /tmp/jupiter_swap.json | jq -r '.swapTransaction')
```

### Step 4: Sign and Submit Transaction

Use the jupiter-swap.mjs script to sign and submit:

```bash
node "$(dirname "$0")/scripts/jupiter-swap.mjs" \
  --keypair "$SOLANA_KEYPAIR_PATH" \
  --transaction "$SWAP_TX"
```

The script will output the transaction signature and a Solscan link.

## Safety Rules

1. **ALWAYS** display swap details and wait for user confirmation before executing
2. **NEVER** execute swaps automatically without explicit approval
3. **ALWAYS** check balance before attempting swaps to ensure sufficient funds
4. **WARN** users if price impact exceeds 1%
5. **WARN** users if slippage is set above 1% (100 bps)
6. **NEVER** log, display, or transmit private key contents

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Insufficient balance" | Not enough input tokens | Check balance, reduce swap amount |
| "Slippage tolerance exceeded" | Price moved during swap | Get fresh quote, consider higher slippage |
| "Transaction expired" | Blockhash too old | Get fresh quote and retry immediately |
| "Account not found" | Missing token account | Token account will be created automatically |
| "Route not found" | No liquidity for pair | Try smaller amount or different token |
| "Platform fee not supported" | Token2022 tokens block platform fees | Use authenticated API with $JUPITER_API_KEY header |

### Retry Logic

If a swap fails due to network issues:
1. Wait 2-3 seconds
2. Get a fresh quote (prices may have changed)
3. Re-confirm with user showing new quote
4. Retry the swap

## Example Interactions

### Check Balance
User: "What's my SOL balance?"
1. Run: `solana balance --keypair "$SOLANA_KEYPAIR_PATH"`
2. Report: "Your wallet has X.XXX SOL"

### Swap Tokens
User: "Swap 0.5 SOL for USDC"
1. Get wallet address
2. Fetch Jupiter quote for 0.5 SOL (500000000 lamports) -> USDC
3. Display quote details:
   - From: 0.5 SOL
   - To: ~XX.XX USDC (estimated)
   - Price Impact: X.XX%
   - Minimum Received: XX.XX USDC
4. Ask: "Do you want to proceed with this swap?"
5. Wait for confirmation
6. On "yes": Execute swap, report transaction link
7. On "no": Acknowledge cancellation

### List All Tokens
User: "Show me all my tokens"
1. Run: `spl-token accounts --owner $(solana address --keypair "$SOLANA_KEYPAIR_PATH")`
2. Format and display token list with balances
