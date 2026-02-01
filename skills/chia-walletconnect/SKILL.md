---
name: chia-walletconnect
description: Telegram Web App for Chia wallet verification via WalletConnect and Sage. Enables cryptographic proof of wallet ownership through signature verification using MintGarden API.
metadata: {"clawdbot":{"requires":{"bins":["node"]},"install":[]}}
---

# Chia WalletConnect Skill

Verify Chia wallet ownership via Telegram using WalletConnect integration with Sage Wallet.

## What It Does

This skill provides a **Telegram Mini App** (Web App) that enables users to:
1. Connect their Sage Wallet via WalletConnect v2
2. Sign a challenge message cryptographically
3. Verify wallet ownership via MintGarden's signature verification API
4. Return verification status to your Telegram bot

**Use Cases:**
- NFT-gated Telegram groups
- Airdrop eligibility verification
- Web3-style authentication
- DAO voting authentication
- Proof of token holdings

## Architecture

```
/verify command → Web App button → WalletConnect → Sage signs → Verification
```

The user never leaves Telegram. The entire flow happens in-app via the Telegram Web App API.

## Installation

```bash
# Install via ClawdHub
clawdhub install chia-walletconnect

# Install dependencies
cd skills/chia-walletconnect
npm install

# Make CLI executable
chmod +x cli.js
```

## Deployment

### Step 1: Deploy Web App

Deploy the `webapp/` folder to a public HTTPS URL:

**Vercel (Recommended):**
```bash
cd skills/chia-walletconnect/webapp
vercel
# Copy the URL (e.g., https://chia-verify.vercel.app)
```

**Netlify:**
```bash
cd skills/chia-walletconnect/webapp
netlify deploy --prod
```

**Your Server:**
```bash
# Start Express server
npm start
# Expose via ngrok or reverse proxy
```

### Step 2: Register with BotFather

1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newapp` or `/editapp`
3. Select your bot
4. **Web App URL:** Enter deployed URL
5. **Short Name:** `verify`

### Step 3: Add to Bot

#### Using Clawdbot Message Tool

```javascript
// Send /verify command handler
message({
  action: 'send',
  target: chatId,
  message: 'Click below to verify your Chia wallet:',
  buttons: [[{
    text: '🌱 Verify Wallet',
    web_app: { url: 'https://your-app.vercel.app' }
  }]]
});
```

#### Handling Verification Response

```javascript
// In your bot's web_app_data handler
bot.on('web_app_data', async (msg) => {
  const data = JSON.parse(msg.web_app_data.data);
  const { address, message, signature, publicKey, userId } = data;
  
  // Verify signature
  const { verifySignature } = require('./skills/chia-walletconnect/lib/verify');
  const result = await verifySignature(address, message, signature, publicKey);
  
  if (result.verified) {
    // Wallet verified! Grant access, record verification, etc.
    message({
      action: 'send',
      target: msg.chat.id,
      message: `✅ Wallet verified!\n\nAddress: ${address}`
    });
    
    // Store verification
    // await db.saveVerification(userId, address);
  } else {
    message({
      action: 'send',
      target: msg.chat.id,
      message: `❌ Verification failed: ${result.error}`
    });
  }
});
```

## CLI Usage

The skill includes a CLI for testing:

```bash
# Generate challenge message
node cli.js challenge xch1abc... telegram_user_123

# Verify signature manually
node cli.js verify xch1abc... "message" "signature" "pubkey"

# Validate address format
node cli.js validate xch1abc...

# Start development server
node cli.js server
```

## API Reference

### MintGarden Signature Verification

**Endpoint:** `POST https://api.mintgarden.io/address/verify_signature`

```json
{
  "address": "xch1abc...",
  "message": "Verify ownership of Chia wallet:...",
  "signature": "hex_signature",
  "pubkey": "hex_public_key"
}
```

**Response:**
```json
{
  "verified": true
}
```

### CHIP-0002 Methods (WalletConnect)

| Method | Purpose |
|--------|---------|
| `chip0002_getPublicKeys` | Fetch public keys from wallet |
| `chip0002_signMessage` | Request message signature |
| `chia_getCurrentAddress` | Get current receive address |

## Verification Flow

```
1. User sends /verify to bot
2. Bot responds with Web App button
3. User taps button → Mini App opens in Telegram
4. Mini App initializes WalletConnect
5. User connects Sage Wallet
6. Challenge message generated (includes nonce + timestamp)
7. User signs message in Sage Wallet
8. Signature sent back to bot via Telegram.WebApp.sendData()
9. Bot verifies signature with MintGarden API
10. Bot confirms verification success/failure
```

**Time:** ~5-10 seconds for full flow (user-dependent)

## Configuration

### Environment Variables

Create `.env` in skill folder:

```env
PORT=3000
WALLETCONNECT_PROJECT_ID=your-project-id
MINTGARDEN_API_URL=https://api.mintgarden.io
```

### Get WalletConnect Project ID

1. Visit [WalletConnect Cloud](https://cloud.walletconnect.com)
2. Create a new project
3. Copy your Project ID
4. Update in `webapp/app.js`

**Default Project ID:**  
The skill includes `6d377259062295c0f6312b4f3e7a5d9b` (Dracattus reference). For production, use your own.

## Security

### What's Protected

- ✅ Challenge nonces prevent replay attacks
- ✅ Timestamps expire after 5 minutes
- ✅ MintGarden cryptographic verification
- ✅ No private keys ever requested
- ✅ HTTPS enforced by Telegram

### Best Practices

1. **Store verifications securely** — Use encrypted database
2. **Rate limit** — Prevent spam verification attempts
3. **Link to Telegram user ID** — Prevent address spoofing
4. **Implement cooldown** — 1 verification per user per day
5. **Log attempts** — Audit trail for security

### Production Checklist

- [ ] Deploy to HTTPS URL (required by Telegram)
- [ ] Use your own WalletConnect Project ID
- [ ] Enable CORS only for your domain
- [ ] Add rate limiting on webhook endpoints
- [ ] Store verifications in persistent database
- [ ] Implement retry logic for network errors
- [ ] Set up monitoring/alerts

## Files

```
chia-walletconnect/
├── webapp/
│   ├── index.html        # Telegram Web App UI
│   ├── app.js            # WalletConnect logic
│   └── styles.css        # Styling
├── lib/
│   ├── challenge.js      # Challenge generation
│   └── verify.js         # MintGarden API client
├── server/
│   └── index.js          # Express webhook server
├── cli.js                # CLI interface
├── package.json          # Dependencies
├── SKILL.md              # This file
└── README.md             # Full documentation
```

## Troubleshooting

### Web App Doesn't Load

- Verify HTTPS deployment (Telegram requires SSL)
- Check URL is publicly accessible
- Test URL directly in browser
- Review browser console for errors

### WalletConnect Connection Fails

- Ensure Sage Wallet is latest version
- Try manual URI paste instead of QR
- Check WalletConnect Project ID is valid
- Verify Sage supports WalletConnect v2

### Signature Verification Fails

- Ensure message format matches exactly
- Confirm public key corresponds to address
- Check MintGarden API is operational
- Verify signature encoding (hex)

### "No Public Key" Error

- Some wallets don't expose pubkey via WalletConnect
- Public key is optional for verification
- Signature verification works without it

## Examples

### Simple Verification Bot

```javascript
// Clawdbot skill handler

const { verifySignature } = require('./lib/verify');

// /verify command
if (message.text === '/verify') {
  await message({
    action: 'send',
    target: message.chat.id,
    message: 'Verify your Chia wallet:',
    buttons: [[{
      text: '🌱 Connect Wallet',
      web_app: { url: process.env.WEB_APP_URL }
    }]]
  });
}

// Handle web app data
bot.on('web_app_data', async (msg) => {
  const { address, message: challengeMsg, signature, publicKey } = 
    JSON.parse(msg.web_app_data.data);
  
  const result = await verifySignature(address, challengeMsg, signature, publicKey);
  
  if (result.verified) {
    // Grant access
    await grantAccess(msg.from.id, address);
    await message({
      action: 'send',
      target: msg.chat.id,
      message: `✅ Verified! Welcome, ${address.substring(0, 12)}...`
    });
  } else {
    await message({
      action: 'send',
      target: msg.chat.id,
      message: `❌ Verification failed`
    });
  }
});
```

### NFT Gating

```javascript
// Check if user owns specific NFT collection

const { verifySignature } = require('./skills/chia-walletconnect/lib/verify');
const mintGarden = require('./skills/mintgarden'); // Assume mintgarden skill exists

bot.on('web_app_data', async (msg) => {
  const { address, message, signature, publicKey } = 
    JSON.parse(msg.web_app_data.data);
  
  // Verify signature first
  const verifyResult = await verifySignature(address, message, signature, publicKey);
  
  if (!verifyResult.verified) {
    return bot.sendMessage(msg.chat.id, '❌ Invalid signature');
  }
  
  // Check NFT ownership
  const nfts = await mintGarden.getNFTsByAddress(address);
  const hasRequiredNFT = nfts.some(nft => 
    nft.collection_id === 'col1required...'
  );
  
  if (hasRequiredNFT) {
    // Grant access to private group
    await inviteToGroup(msg.from.id);
    bot.sendMessage(msg.chat.id, '✅ Access granted! Check your invites.');
  } else {
    bot.sendMessage(msg.chat.id, '❌ You need a Wojak NFT to join!');
  }
});
```

## Performance

| Stage | Time |
|-------|------|
| WalletConnect Init | ~1-2s |
| Connection Approval | User action |
| Sign Request | ~2-5s |
| MintGarden Verify | ~0.5-1s |
| **Total** | **~5-10s** |

## Dependencies

- `@walletconnect/sign-client` — WalletConnect v2
- `@walletconnect/utils` — WalletConnect helpers
- `@walletconnect/types` — TypeScript types
- `express` — Web server
- `node-fetch` — HTTP client
- `cors` — CORS middleware
- `dotenv` — Environment config

## Version

1.0.0

## License

MIT — Koba42 Corp

## Links

- **MintGarden API:** https://api.mintgarden.io/docs
- **WalletConnect:** https://docs.walletconnect.com/
- **Telegram Web Apps:** https://core.telegram.org/bots/webapps
- **Sage Wallet:** https://www.sagewallet.io/
- **CHIP-0002:** https://github.com/Chia-Network/chips/blob/main/CHIPs/chip-0002.md

---

**Built with 🌱 by Koba42 Corp**
