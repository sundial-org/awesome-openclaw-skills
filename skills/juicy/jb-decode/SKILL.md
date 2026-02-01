---
name: jb-decode
description: Decode and analyze Juicebox V5 transaction calldata. Explain what a transaction does, decode function parameters, and analyze historical transactions using cast or ethers.js.
---

# Juicebox V5 Transaction Decoder

Decode and analyze Juicebox V5 transaction calldata.

## Common Function Selectors

### JBMultiTerminal
```
pay(uint256,address,uint256,address,uint256,string,bytes)
  Selector: 0x...
  - Pay into a project

cashOutTokensOf(address,uint256,uint256,address,uint256,address,bytes)
  Selector: 0x...
  - Cash out tokens for funds

sendPayoutsOf(uint256,address,uint256,uint256,uint256)
  Selector: 0x...
  - Distribute payouts to splits

useAllowanceOf(uint256,address,uint256,uint256,uint256,address,address,string)
  Selector: 0x...
  - Use surplus allowance
```

### JBController
```
launchProjectFor(address,string,(uint256,uint256,uint256,uint256,address,(uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,address,uint256),(uint256,(bool,uint256,uint256,address,uint256,address)[])[],(address,address,(uint256,uint32)[],(uint256,uint32)[])[])[],(address,(address,uint8,uint32)[])[],string)
  - Launch a new project

queueRulesetsOf(uint256,(uint256,uint256,uint256,uint256,address,(uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,address,uint256),(uint256,(bool,uint256,uint256,address,uint256,address)[])[],(address,address,(uint256,uint32)[],(uint256,uint32)[])[])[],string)
  - Queue new rulesets

mintTokensOf(uint256,uint256,address,string,bool)
  - Mint tokens

burnTokensOf(address,uint256,uint256,string)
  - Burn tokens
```

## Decoding with Cast

### Decode Calldata
```bash
# Get the function signature
cast 4byte <first-4-bytes-of-calldata>

# Decode full calldata (need ABI)
cast calldata-decode "pay(uint256,address,uint256,address,uint256,string,bytes)" <calldata>
```

### Decode Transaction
```bash
# Get transaction details
cast tx <txhash> --rpc-url $RPC_URL

# Decode the input
cast tx <txhash> --rpc-url $RPC_URL | grep input
```

### Example: Decode a Pay Transaction
```bash
# Assuming calldata starts with pay() selector
cast calldata-decode \
    "pay(uint256,address,uint256,address,uint256,string,bytes)" \
    "0x..." \
    # Returns:
    # projectId: 123
    # token: 0x0000...0000 (native)
    # amount: 1000000000000000000
    # beneficiary: 0x...
    # minReturnedTokens: 0
    # memo: "Supporting the project"
    # metadata: 0x...
```

## Decoding with ethers.js

### Setup
```typescript
import { ethers } from 'ethers';

// Terminal ABI fragment
const TERMINAL_ABI = [
    'function pay(uint256 projectId, address token, uint256 amount, address beneficiary, uint256 minReturnedTokens, string memo, bytes metadata) payable returns (uint256)',
    'function cashOutTokensOf(address holder, uint256 projectId, uint256 cashOutCount, address tokenToReclaim, uint256 minTokensReclaimed, address beneficiary, bytes metadata) returns (uint256)',
    'function sendPayoutsOf(uint256 projectId, address token, uint256 amount, uint256 currency, uint256 minTokensPaidOut) returns (uint256)',
];

const iface = new ethers.Interface(TERMINAL_ABI);
```

### Decode Calldata
```typescript
function decodeCalldata(calldata: string) {
    try {
        const decoded = iface.parseTransaction({ data: calldata });
        return {
            name: decoded.name,
            args: decoded.args,
            signature: decoded.signature,
        };
    } catch (e) {
        return null;
    }
}
```

### Decode Transaction from Hash
```typescript
async function decodeTransaction(txHash: string) {
    const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
    const tx = await provider.getTransaction(txHash);

    if (!tx) throw new Error('Transaction not found');

    const decoded = iface.parseTransaction({ data: tx.data });

    return {
        from: tx.from,
        to: tx.to,
        value: ethers.formatEther(tx.value),
        function: decoded?.name,
        args: decoded?.args,
    };
}
```

## Transaction Analysis Examples

### Pay Transaction
```
Function: pay(uint256,address,uint256,address,uint256,string,bytes)
Parameters:
  projectId: 123          → Paying into project #123
  token: 0x000...000      → Using native currency (ETH)
  amount: 1e18            → Paying 1 ETH
  beneficiary: 0xABC...   → Tokens go to this address
  minReturnedTokens: 0    → No minimum (accepts any amount)
  memo: "Great project!"  → Payment memo
  metadata: 0x...         → Optional hook metadata

Effect: Sends 1 ETH to project #123, mints tokens to 0xABC...
```

### Cash Out Transaction
```
Function: cashOutTokensOf(...)
Parameters:
  holder: 0xABC...        → Token holder cashing out
  projectId: 123          → From project #123
  cashOutCount: 1000e18   → Cashing out 1000 tokens
  tokenToReclaim: 0x0...  → Reclaiming ETH
  minTokensReclaimed: 0   → No minimum
  beneficiary: 0xABC...   → ETH goes here
  metadata: 0x...         → Optional hook metadata

Effect: Burns 1000 tokens, sends proportional ETH to 0xABC...
```

### Queue Rulesets Transaction
```
Function: queueRulesetsOf(...)
Parameters:
  projectId: 123
  rulesetConfigs: [...]   → New ruleset configurations
  memo: "Update params"

Effect: Queues new ruleset(s) that activate when current ends
```

## Decoding Hook Metadata

Hook metadata is ABI-encoded. Common patterns:

### Buyback Hook Metadata
```solidity
// Encode
bytes memory metadata = abi.encode(amountToSwapWith, minimumSwapAmountOut);

// Decode
(uint256 amountToSwapWith, uint256 minimumSwapAmountOut) = abi.decode(metadata, (uint256, uint256));
```

### 721 Hook Metadata
```solidity
// Encode tier IDs to mint
bytes memory metadata = abi.encode(tierIds);

// Decode
uint256[] memory tierIds = abi.decode(metadata, (uint256[]));
```

## Generation Guidelines

1. **Identify the contract** from the `to` address
2. **Extract function selector** (first 4 bytes)
3. **Decode parameters** using the appropriate ABI
4. **Explain the effect** in plain language
5. **Decode nested metadata** if present

## Example Prompts

- "What does this transaction do? 0x..."
- "Decode this calldata for JBMultiTerminal"
- "Explain what happened in transaction 0xabc..."
- "What parameters were used in this pay() call?"
