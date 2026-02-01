# SafeSkills - Secure Secret Management for AI Agents

SafeSkills is a secure secret management service. It stores secrets (like wallet private keys) and executes actions using them so that **you (the agent) never see the raw secret values**. The first supported skill is an EVM wallet -- you can create wallets, transfer tokens, send transactions, check balances, and more.

**CRITICAL: Never attempt to access or request raw secret values. All operations are performed server-side through the API.**

## Configuration

- **Base API URL:** Use the `SAFESKILLS_API_URL` environment variable if set, otherwise default to `https://safeskill-production.up.railway.app`
- **Frontend URL:** Use the `SAFESKILLS_FRONTEND_URL` environment variable if set, otherwise default to `https://safeskill-production.up.railway.app`

All API requests require a Bearer token (the API key returned when creating a secret).

```
Authorization: Bearer <API_KEY>
```

## Workflow

### 1. Create a Wallet

Create an EVM wallet secret. Store the returned API key for all subsequent calls. Share the claim URL with the user so they can manage policies for the wallet.

```bash
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/secrets" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "EVM_WALLET",
    "memo": "My agent wallet",
    "chainId": 11155111
  }'
```

Response includes:
- `apiKey` -- store this securely; use it as the Bearer token for all future requests
- `claimUrl` -- share this with the user so they can view and manage policies for this wallet
- `address` -- the smart account address of the created wallet

After creating, tell the user: "Here is your wallet claim URL: <claimUrl>. You can use this to manage spending policies and monitor the wallet."

### 2. Get Secret Info

Retrieve metadata about the secret associated with the current API key.

```bash
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/secrets/info" \
  -H "Authorization: Bearer <API_KEY>"
```

### 3. Get Wallet Address

```bash
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/address" \
  -H "Authorization: Bearer <API_KEY>"
```

### 4. Check Balances

Check native token balance and optionally ERC-20 token balances by passing token contract addresses as a comma-separated query parameter.

```bash
# Native balance only
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/balance" \
  -H "Authorization: Bearer <API_KEY>"

# With ERC-20 tokens
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/balance?tokens=0xTokenAddr1,0xTokenAddr2" \
  -H "Authorization: Bearer <API_KEY>"
```

### 5. Transfer ETH or Tokens

Transfer native ETH or an ERC-20 token to a recipient address.

```bash
# Transfer native ETH
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "0.01"
  }'

# Transfer ERC-20 token
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "100",
    "token": "0xTokenContractAddress"
  }'
```

### 6. Send Arbitrary Transaction

Send a raw transaction with custom calldata. Useful for interacting with smart contracts.

```bash
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/send-transaction" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xContractAddress",
    "data": "0xCalldata",
    "value": "0"
  }'
```

## Important Notes

- **Never try to access raw secret values.** The whole point of SafeSkills is that secrets stay server-side.
- Always store the API key returned from wallet creation -- it is the only way to authenticate subsequent requests.
- Always share the claim URL with the user after creating a wallet.
- The default chain ID `11155111` is Ethereum Sepolia testnet. Adjust as needed.
- If a transfer or transaction fails, check that the wallet has sufficient balance and that any required policies have been approved by the user via the claim URL.
