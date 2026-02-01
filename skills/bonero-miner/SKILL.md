---
name: bonero-miner
description: Mine Bonero (BON) - a privacy-focused cryptocurrency for AI agents using RandomX CPU mining. Use when the user wants to mine Bonero, set up a Bonero node, or earn BON cryptocurrency.
license: MIT
metadata:
  author: happybigmtn
  version: "1.0.0"
compatibility: Requires Ubuntu 22.04+ or Debian 12+, build-essential, cmake, and network access to seed nodes.
---

# Bonero Miner

Mine Bonero - a privacy-focused cryptocurrency designed for AI agents. Based on Monero, uses RandomX proof-of-work optimized for CPU mining.

## Quick Start

```bash
# 1. Clone repository
git clone --recursive https://github.com/happybigmtn/bonero.git
cd bonero

# 2. Install dependencies
sudo apt-get update && sudo apt-get install -y \
    build-essential cmake pkg-config git \
    libboost-all-dev libssl-dev libzmq3-dev \
    libunbound-dev libsodium-dev libhidapi-dev \
    liblzma-dev libreadline-dev libexpat1-dev \
    libusb-1.0-0-dev libudev-dev

# 3. Initialize submodules (required)
git submodule update --init --recursive

# 4. Build
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# 5. Create wallet
./bin/bonero-wallet-cli --generate-new-wallet=mywallet
# Save your seed phrase! Note the address starting with 'C'

# 6. Start mining (replace with your address)
./bin/bonerod --detach \
    --start-mining YOUR_WALLET_ADDRESS \
    --mining-threads 2 \
    --add-exclusive-node 185.218.126.23:18080 \
    --add-exclusive-node 185.239.209.227:18080
```

## Network Information

| Property | Value |
|----------|-------|
| Algorithm | RandomX (CPU-optimized) |
| Block Time | ~120 seconds |
| P2P Port | 18080 |
| RPC Port | 18881 |
| Address Prefix | C |
| Data Directory | ~/.bonero |

## Seed Nodes

```
185.218.126.23:18080
185.239.209.227:18080
```

## Commands

### Start Mining

```bash
./build/bin/bonerod --detach \
    --start-mining YOUR_WALLET_ADDRESS \
    --mining-threads 2 \
    --add-exclusive-node 185.218.126.23:18080 \
    --add-exclusive-node 185.239.209.227:18080
```

### Check Status

```bash
curl -s http://127.0.0.1:18881/json_rpc \
    -d '{"jsonrpc":"2.0","id":"0","method":"get_info"}' | \
    grep -E 'height|difficulty'
```

### Stop Mining

```bash
pkill bonerod
```

## Runtime Dependencies

If using pre-built binaries (not building from source):

```bash
sudo apt-get install -y libzmq5 libhidapi-libusb0 libunbound8
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Submodule errors | Run `git submodule update --init --recursive` |
| Missing libzmq.so.5 | `apt-get install libzmq5` |
| Missing libhidapi | `apt-get install libhidapi-libusb0` |
| Cannot connect | Verify seed nodes reachable on port 18080 |
| RPC not responding | Daemon may still be syncing |

## Resources

- [Bonero Repository](https://github.com/happybigmtn/bonero)
- [Full Documentation](https://github.com/happybigmtn/bonero/blob/master/README.md)
