---
name: botcoin-miner
description: Mine Botcoin (BOT) - a Bitcoin fork for AI agents using RandomX CPU mining. Use when the user wants to mine Botcoin, set up a Botcoin node, or earn BOT cryptocurrency.
license: MIT
metadata:
  author: happybigmtn
  version: "1.0.0"
compatibility: Requires Ubuntu 22.04+ or Debian 12+, build-essential, cmake, and network access to seed nodes.
---

# Botcoin Miner

Mine Botcoin - a Bitcoin fork designed for the AI agent economy. Uses RandomX proof-of-work, optimized for CPU mining without special hardware.

## Quick Start

```bash
# 1. Clone repository with submodules
git clone --recursive https://github.com/happybigmtn/botcoin.git
cd botcoin

# 2. Install dependencies
sudo apt-get update && sudo apt-get install -y \
    build-essential cmake pkg-config git \
    libboost-all-dev libssl-dev libzmq3-dev \
    libunbound-dev libsodium-dev libevent-dev \
    liblzma-dev libsqlite3-dev libminiupnpc-dev

# 3. Initialize submodules (required for RandomX)
git submodule update --init --recursive

# 4. Build
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DBUILD_BENCH=OFF -DENABLE_IPC=OFF ..
make -j$(nproc)

# 5. Start daemon
./src/botcoind -daemon

# 6. Create wallet and get address
./src/botcoin-cli createwallet "miner"
ADDRESS=$(./src/botcoin-cli -rpcwallet=miner getnewaddress)
echo "Mining address: $ADDRESS"

# 7. Start mining
while true; do
    ./src/botcoin-cli -rpcwallet=miner generatetoaddress 1 $ADDRESS
    sleep 0.1
done
```

## Network Information

| Property | Value |
|----------|-------|
| Algorithm | RandomX (CPU-optimized) |
| Block Time | ~60 seconds |
| P2P Port | 8433 |
| RPC Port | 8434 |
| Address Prefix | bot1 |
| Data Directory | ~/.botcoin |

## Seed Nodes

Connect to the live network:

```
95.111.227.14:8433
95.111.229.108:8433
```

## Commands

### Start Daemon

```bash
botcoind -daemon
```

### Create Wallet

```bash
botcoin-cli createwallet "miner"
botcoin-cli -rpcwallet=miner getnewaddress
```

### Start Mining

```bash
ADDRESS=$(botcoin-cli -rpcwallet=miner getnewaddress)
while true; do
    botcoin-cli -rpcwallet=miner generatetoaddress 1 $ADDRESS
    sleep 0.1
done
```

### Check Status

```bash
botcoin-cli getblockchaininfo
botcoin-cli getmininginfo
botcoin-cli -rpcwallet=miner getbalance
```

### Stop Mining

```bash
botcoin-cli stop
```

## Mining Script

```bash
#!/bin/bash
# botcoin-miner.sh - Background mining script

WALLET="miner"
botcoin-cli createwallet "$WALLET" 2>/dev/null || true
ADDRESS=$(botcoin-cli -rpcwallet=$WALLET getnewaddress)

echo "Mining to: $ADDRESS"
screen -dmS miner bash -c "while true; do \
    nice -n 19 botcoin-cli -rpcwallet=$WALLET generatetoaddress 1 $ADDRESS >/dev/null 2>&1; \
    sleep 0.1; \
done"
echo "Mining started in background (screen -r miner to attach)"
```

## Common Issues

| Problem | Solution |
|---------|----------|
| RandomX/submodule errors | Run `git submodule update --init --recursive` |
| Cap'n Proto required | Add `-DENABLE_IPC=OFF` to cmake |
| Could not find Boost | `apt-get install libboost-all-dev` |
| Cannot connect to peers | Verify seed nodes reachable on port 8433 |
| Wallet not found | Create wallet first: `botcoin-cli createwallet "miner"` |

## Differences from Bitcoin

| Aspect | Bitcoin | Botcoin |
|--------|---------|---------|
| Algorithm | SHA-256d | RandomX |
| Block Time | 10 min | 60 sec |
| P2P Port | 8333 | 8433 |
| RPC Port | 8332 | 8434 |
| Address | bc1... | bot1... |

## Resources

- [Botcoin Repository](https://github.com/happybigmtn/botcoin)
- [Full Documentation](https://github.com/happybigmtn/botcoin/blob/master/README.md)
