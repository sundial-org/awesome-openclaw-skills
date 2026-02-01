---
name: gas-tracker
description: Monitor Ethereum gas prices in real-time - get current gwei rates, estimate transaction costs, find optimal times to transact, and track gas trends.
metadata: {"openclaw":{"requires":{"bins":["cast"]},"install":[{"id":"foundry","kind":"shell","command":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["cast"],"label":"Install Foundry (cast)"}]}}
---

# Ethereum Gas Tracker

## Quick Gas Check

Current gas price:
```bash
cast gas-price --rpc-url https://eth.llamarpc.com | xargs -I {} cast --to-unit {} gwei
```

With priority fee (EIP-1559):
```bash
cast base-fee --rpc-url https://eth.llamarpc.com | xargs -I {} cast --to-unit {} gwei
```

## Detailed Gas Info

```bash
python3 << 'EOF'
import requests

resp = requests.post('https://eth.llamarpc.com', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'eth_gasPrice',
    'params': []
}).json()

gas_wei = int(resp['result'], 16)
gas_gwei = gas_wei / 1e9

print(f"Gas Price: {gas_gwei:.2f} Gwei")
print(f"Gas Price: {gas_wei} Wei")

# Estimate costs
gas_limits = {
    'ETH Transfer': 21000,
    'ERC-20 Transfer': 65000,
    'Uniswap Swap': 150000,
    'NFT Mint': 200000,
    'Contract Deploy': 500000
}

eth_price = 3000  # Update with current price

print(f"\n=== Estimated Costs (ETH @ ${eth_price}) ===")
for name, limit in gas_limits.items():
    cost_eth = (gas_wei * limit) / 1e18
    cost_usd = cost_eth * eth_price
    print(f"{name}: {cost_eth:.6f} ETH (${cost_usd:.2f})")
EOF
```

## EIP-1559 Gas Estimation

```bash
python3 << 'EOF'
import requests

# Get fee history
resp = requests.post('https://eth.llamarpc.com', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'eth_feeHistory',
    'params': ['0x5', 'latest', [25, 50, 75]]
}).json()

result = resp['result']
base_fees = [int(x, 16) / 1e9 for x in result['baseFeePerGas']]

print("=== Recent Base Fees (Gwei) ===")
for i, fee in enumerate(base_fees):
    print(f"Block -{len(base_fees)-i-1}: {fee:.2f}")

print(f"\nCurrent Base Fee: {base_fees[-1]:.2f} Gwei")
print(f"Average: {sum(base_fees)/len(base_fees):.2f} Gwei")

# Priority fee recommendations
print("\n=== Recommended Priority Fees ===")
print("🐢 Low (slow): 0.5-1 Gwei")
print("🚶 Medium: 1-2 Gwei")
print("🚀 Fast: 2-5 Gwei")
print("⚡ Urgent: 5-10+ Gwei")
EOF
```

## Gas Price APIs

### Etherscan Gas Oracle

```bash
curl -s "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=YourKey" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)['result']
print('=== Etherscan Gas Oracle ===')
print(f\"🐢 Safe Low: {data['SafeGasPrice']} Gwei\")
print(f\"🚶 Average: {data['ProposeGasPrice']} Gwei\")
print(f\"🚀 Fast: {data['FastGasPrice']} Gwei\")
print(f\"📦 Base Fee: {data.get('suggestBaseFee', 'N/A')} Gwei\")"
```

### Blocknative Gas Estimator

```bash
curl -s "https://api.blocknative.com/gasprices/blockprices" \
  -H "Authorization: YOUR_API_KEY" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
prices = data['blockPrices'][0]['estimatedPrices']
print('=== Blocknative Estimates ===')
for p in prices:
    print(f\"{p['confidence']}% confidence: {p['price']} Gwei | Priority: {p['maxPriorityFeePerGas']} Gwei\")"
```

## Real-Time Monitor

```bash
python3 << 'EOF'
import requests
import time
from datetime import datetime

print("=== Gas Price Monitor (Ctrl+C to stop) ===\n")

history = []

while True:
    try:
        resp = requests.post('https://eth.llamarpc.com', json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_gasPrice',
            'params': []
        }).json()

        gas_gwei = int(resp['result'], 16) / 1e9
        history.append(gas_gwei)

        if len(history) > 60:
            history.pop(0)

        avg = sum(history) / len(history)
        trend = "📈" if gas_gwei > avg else "📉" if gas_gwei < avg else "➡️"

        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {gas_gwei:.2f} Gwei {trend} (avg: {avg:.2f})")

        time.sleep(10)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
EOF
```

## Gas Cost Calculator

```bash
python3 << 'EOF'
import requests

# Get current gas price
resp = requests.post('https://eth.llamarpc.com', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'eth_gasPrice',
    'params': []
}).json()

gas_wei = int(resp['result'], 16)
gas_gwei = gas_wei / 1e9

# Get ETH price (using CoinGecko)
try:
    eth_resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd').json()
    eth_price = eth_resp['ethereum']['usd']
except:
    eth_price = 3000

print(f"Current Gas: {gas_gwei:.2f} Gwei")
print(f"ETH Price: ${eth_price:,.2f}\n")

operations = [
    ("ETH Transfer", 21000),
    ("ERC-20 Approve", 46000),
    ("ERC-20 Transfer", 65000),
    ("Uniswap V2 Swap", 150000),
    ("Uniswap V3 Swap", 185000),
    ("OpenSea NFT Buy", 200000),
    ("NFT Mint (single)", 150000),
    ("NFT Mint (batch 5)", 400000),
    ("Bridge Deposit", 100000),
    ("Contract Deploy (small)", 300000),
    ("Contract Deploy (large)", 1000000),
]

print("=== Transaction Cost Estimates ===")
print(f"{'Operation':<25} {'Gas':>10} {'ETH':>12} {'USD':>10}")
print("-" * 60)

for name, gas_limit in operations:
    cost_eth = (gas_wei * gas_limit) / 1e18
    cost_usd = cost_eth * eth_price
    print(f"{name:<25} {gas_limit:>10,} {cost_eth:>12.6f} ${cost_usd:>9.2f}")
EOF
```

## Historical Gas Analysis

```bash
python3 << 'EOF'
import requests

# Get last 100 blocks fee history
resp = requests.post('https://eth.llamarpc.com', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'eth_feeHistory',
    'params': ['0x64', 'latest', [10, 50, 90]]
}).json()

result = resp['result']
base_fees = [int(x, 16) / 1e9 for x in result['baseFeePerGas']]

print("=== Last 100 Blocks Gas Analysis ===")
print(f"Minimum: {min(base_fees):.2f} Gwei")
print(f"Maximum: {max(base_fees):.2f} Gwei")
print(f"Average: {sum(base_fees)/len(base_fees):.2f} Gwei")
print(f"Current: {base_fees[-1]:.2f} Gwei")

# Find optimal times (lowest gas)
sorted_fees = sorted(enumerate(base_fees), key=lambda x: x[1])
print("\n=== Lowest Gas Periods ===")
for idx, fee in sorted_fees[:5]:
    blocks_ago = len(base_fees) - idx - 1
    print(f"{blocks_ago} blocks ago: {fee:.2f} Gwei")
EOF
```

## Gas Price Alerts

```bash
python3 << 'EOF'
import requests
import time

TARGET_GWEI = 20  # Alert when gas drops below this
CHECK_INTERVAL = 30

print(f"Waiting for gas to drop below {TARGET_GWEI} Gwei...")

while True:
    try:
        resp = requests.post('https://eth.llamarpc.com', json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_gasPrice',
            'params': []
        }).json()

        gas_gwei = int(resp['result'], 16) / 1e9

        if gas_gwei < TARGET_GWEI:
            print(f"\n🔔 ALERT! Gas is now {gas_gwei:.2f} Gwei!")
            print("Good time to transact!")
            # Add notification here (telegram, discord, etc.)
            break
        else:
            print(f"Current: {gas_gwei:.2f} Gwei (waiting for < {TARGET_GWEI})")

        time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        break
EOF
```

## L2 Gas Comparison

```bash
python3 << 'EOF'
import requests

chains = {
    'Ethereum': 'https://eth.llamarpc.com',
    'Arbitrum': 'https://arb1.arbitrum.io/rpc',
    'Optimism': 'https://mainnet.optimism.io',
    'Polygon': 'https://polygon-rpc.com',
    'Base': 'https://mainnet.base.org',
}

print("=== Gas Prices Across Chains ===\n")

for name, rpc in chains.items():
    try:
        resp = requests.post(rpc, json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_gasPrice',
            'params': []
        }, timeout=5).json()

        gas_gwei = int(resp['result'], 16) / 1e9
        print(f"{name:<12}: {gas_gwei:>10.4f} Gwei")
    except Exception as e:
        print(f"{name:<12}: Error")
EOF
```

## Best Times to Transact

| Time (UTC) | Gas Level | Reason |
|------------|-----------|--------|
| 00:00-06:00 | Low | US sleeping, Asia waking |
| 06:00-12:00 | Medium | Europe active |
| 12:00-18:00 | High | US + Europe overlap |
| 18:00-00:00 | Medium | US peak, Europe sleeping |
| Weekends | Low | Less trading activity |

## Gas Tokens

| Option | Description |
|--------|-------------|
| Flashbots | MEV protection, often lower gas |
| Gas tokens (deprecated) | CHI, GST2 no longer work post-London |
| Batch transactions | Combine multiple ops |
| L2 solutions | Arbitrum, Optimism for lower fees |

## Notes

- Gas prices fluctuate with network demand
- Base fee burns, priority fee goes to validators
- EIP-1559: maxFeePerGas = baseFee + priorityFee
- Use Flashbots for MEV protection
- L2s are 10-100x cheaper for most operations
- Weekend transactions typically cheaper
