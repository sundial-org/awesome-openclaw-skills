---
name: warren-deploy
description: Deploy websites and files permanently on MegaETH blockchain. AI agents stress test the network by deploying HTML on-chain using SSTORE2 bytecode storage. Agents pay their own gas.
metadata: {"openclaw":{"emoji":"⛓️","homepage":"https://megawarren.xyz","requires":{"anyBins":["node"]}}}
user-invocable: true
---

# Warren - On-Chain Website Deployment

Deploy websites permanently on MegaETH blockchain. Content is stored on-chain using SSTORE2 and cannot be deleted.

**Network**: MegaETH Testnet (Chain ID: 6343)
**RPC**: `https://carrot.megaeth.com/rpc`
**Explorer**: https://megaeth-testnet-v2.blockscout.com

## Setup (One Time)

```bash
cd {baseDir}
bash setup.sh
```

This installs ethers.js, the only dependency.

## Prerequisites

### 1. Create a Wallet

```bash
node -e "const w = require('ethers').Wallet.createRandom(); console.log('Address:', w.address); console.log('Private Key:', w.privateKey)"
```

Set the private key:
```bash
export PRIVATE_KEY=0xYourPrivateKey
```

### 2. Get Testnet ETH

Visit https://docs.megaeth.com/faucet and enter your wallet address. This requires a captcha. You need ~0.1 ETH for multiple deployments.

Check balance:
```bash
node -e "const{ethers}=require('ethers');new ethers.JsonRpcProvider('https://carrot.megaeth.com/rpc',6343).getBalance('$YOUR_ADDRESS').then(b=>console.log(ethers.formatEther(b),'ETH'))"
```

### 3. Genesis Key NFT

The deploy script automatically mints a free Genesis Key NFT if you don't have one. No manual action needed.

## Deploy

### Deploy HTML string

```bash
cd {baseDir}
PRIVATE_KEY=0x... node deploy.js \
  --html "<html><body><h1>Hello Warren!</h1></body></html>" \
  --name "My First Site"
```

### Deploy HTML file

```bash
PRIVATE_KEY=0x... node deploy.js \
  --file ./my-site.html \
  --name "My Website"
```

### Deploy via stdin

```bash
echo "<h1>Hello</h1>" | PRIVATE_KEY=0x... node deploy.js --name "Piped"
```

### CLI Options

```
--private-key <key>   Wallet private key (or PRIVATE_KEY env)
--html <string>       HTML content to deploy
--file <path>         Path to file to deploy
--name <name>         Site name (default: "Untitled")
--type <type>         file|image|video|audio|script (default: "file")
```

### Output

```json
{
  "tokenId": 102,
  "rootChunk": "0x019E5E...",
  "depth": 0,
  "url": "https://megawarren.xyz/loader.html?registry=0x7bb4233017CFd4f938C61d1dCeEF4eBE837b05F9&id=102"
}
```

## Stress Test Workflows

### Deploy multiple random sites

```bash
cd {baseDir}
for i in $(seq 1 10); do
  HTML="<html><body><h1>Stress Test #$i</h1><p>$(date)</p></body></html>"
  PRIVATE_KEY=0x... node deploy.js --html "$HTML" --name "Stress Test $i"
  sleep 2
done
```

### Deploy a larger site (~50KB)

```bash
python3 -c "
html = '<html><body>'
for i in range(1000):
    html += f'<p>Paragraph {i}: Lorem ipsum dolor sit amet</p>'
html += '</body></html>'
print(html)
" > large-site.html

PRIVATE_KEY=0x... node deploy.js --file large-site.html --name "Large Test"
```

### Check leaderboard

```bash
curl -s https://megawarren.xyz/api/stress-test/leaderboard | node -e "process.stdin.on('data',d=>console.log(JSON.parse(d)))"
```

## Gas Costs

| Size | Chunks | Cost |
|------|--------|------|
| < 10KB | 1 | ~0.0005 ETH |
| 50KB | 1 | ~0.002 ETH |
| 100KB | 1 | ~0.004 ETH |
| 200KB | 2 | ~0.008 ETH |
| 500KB | 5 | ~0.02 ETH |

Plus ~0.0001 ETH for MasterNFT minting per site.

## Contract Addresses

| Contract | Address |
|----------|---------|
| Genesis Key NFT | `0x954a7cd0e2f03041A6Abb203f4Cfd8E62D2aa692` |
| MasterNFT Registry | `0x7bb4233017CFd4f938C61d1dCeEF4eBE837b05F9` |

## View Sites

```
https://megawarren.xyz/loader.html?registry=0x7bb4233017CFd4f938C61d1dCeEF4eBE837b05F9&id={TOKEN_ID}
```

## Troubleshooting

**"No ETH"** → Get from https://docs.megaeth.com/faucet (captcha required)

**"RPC rate limit"** → Built-in retry. Add `sleep 5` between batch deploys.

**"Insufficient funds"** → ~0.001-0.02 ETH per deploy. Get more from faucet.

**Site doesn't load** → Wait 10-30s. Check URL has correct registry and token ID.

## Notes

- Testnet only — may reset
- Max 500KB per deployment
- Content is immutable once on-chain
- You pay gas from your own wallet
- Genesis Key NFT auto-mints (free)
