---
name: jb-suckers
description: |
  Juicebox V5 sucker contracts for cross-chain token bridging. Use when: (1) implementing bridge
  functionality, (2) understanding prepare/toRemote/claim flow, (3) working with merkle proofs for
  cross-chain claims, (4) querying sucker pairs from registry, (5) handling emergency exits,
  (6) debugging "claimable" vs "pending" states, (7) encoding sucker transaction calldata.
  Covers JBSucker, JBOptimismSucker, JBArbitrumSucker, JBCCIPSucker, and JBSuckerRegistry.
---

# Juicebox V5 Suckers - Cross-Chain Token Bridging

## Problem

Bridging project tokens between chains while maintaining their proportional treasury backing requires understanding a complex three-phase protocol with merkle proofs, chain-specific AMBs, and careful state management.

## Context / Trigger Conditions

Apply this knowledge when:
- Building cross-chain bridging UIs
- Encoding `prepare()`, `toRemote()`, or `claim()` transactions
- Querying pending/claimable bridge transactions
- Fetching merkle proofs from Juicerkle
- Understanding why a bridge is "stuck" in pending state
- Implementing emergency exit flows
- Working with JBSuckerRegistry to find bridge routes

## Solution

### What Are Suckers?

Suckers are specialized bridge contracts that **link Juicebox projects across chains** and move project tokens AND their proportional treasury backing between them.

**Why Suckers are necessary:** Project IDs cannot be coordinated across chains—each chain assigns the next available ID independently. If you deploy to Ethereum you might get project #42, and deploying to Optimism might give you project #17. Suckers connect these separate projects so they function as a single "omnichain project" with unified token bridging.

Unlike standard token bridges:

- Tokens are burned on source chain via cash-out
- Proportional ETH/USDC moves with the tokens
- Recipient receives newly minted tokens on destination
- Treasury value follows the tokens

### The Three-Phase Bridge Flow

```
PHASE 1: PREPARE (Source Chain)
┌─────────────────────────────────────────────────────────────┐
│ User calls: sucker.prepare(                                  │
│   projectTokenCount,  // Amount to bridge                   │
│   beneficiary,        // Recipient on remote chain          │
│   minTokensReclaimed, // Slippage protection                │
│   token               // Terminal token (ETH/USDC address)  │
│ )                                                           │
│                                                             │
│ What happens:                                               │
│ 1. Project tokens transferred from user to sucker           │
│ 2. Sucker calls terminal.cashOutTokensOf()                  │
│ 3. Receives proportional ETH/USDC from treasury             │
│ 4. Creates leaf in outbox merkle tree                       │
│ 5. Emits InsertToOutboxTree event                          │
│                                                             │
│ Status: PENDING                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 2: EXECUTE (Cross-Chain Message)
┌─────────────────────────────────────────────────────────────┐
│ User/Relayer calls: sucker.toRemote(token)                  │
│                                                             │
│ What happens:                                               │
│ 1. Computes merkle root of all pending outbox leaves        │
│ 2. Increments nonce                                         │
│ 3. Sends JBMessageRoot via AMB:                             │
│    - OP Stack: IOPMessenger.sendMessage()                   │
│    - Arbitrum: IInbox.unsafeCreateRetryableTicket()         │
│    - CCIP: ICCIPRouter.ccipSend()                          │
│ 4. Transfers ETH/tokens to peer sucker                      │
│ 5. Emits RootToRemote event                                │
│                                                             │
│ Status: CLAIMABLE (on destination)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
PHASE 3: CLAIM (Destination Chain)
┌─────────────────────────────────────────────────────────────┐
│ User calls: peerSucker.claim(claimData)                     │
│                                                             │
│ claimData = {                                               │
│   token: address,                                           │
│   leaf: { index, beneficiary, projectTokenCount,            │
│           terminalTokenAmount },                            │
│   proof: bytes32[32]  // Merkle proof from Juicerkle        │
│ }                                                           │
│                                                             │
│ What happens:                                               │
│ 1. Validates merkle proof against inbox root                │
│ 2. Checks leaf not already executed (prevents double-spend) │
│ 3. Marks leaf as executed in bitmap                         │
│ 4. Mints project tokens to beneficiary                      │
│ 5. Adds terminal tokens to project balance                  │
│ 6. Emits Claimed event                                      │
│                                                             │
│ Status: CLAIMED                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Contracts

| Contract | Purpose |
|----------|---------|
| `JBSucker` | Abstract base with core bridging logic |
| `JBOptimismSucker` | OP Stack bridges (Optimism, Base) |
| `JBArbitrumSucker` | Arbitrum Inbox/Outbox messaging |
| `JBCCIPSucker` | Chainlink CCIP for L2↔L2 |
| `JBSuckerRegistry` | Deploys and tracks sucker pairs |

### Querying Sucker Pairs

```javascript
// Get all bridge destinations for a project
const pairs = await publicClient.readContract({
  address: JB_SUCKER_REGISTRY,
  abi: [{
    name: 'suckerPairsOf',
    type: 'function',
    inputs: [{ name: 'projectId', type: 'uint256' }],
    outputs: [{
      name: 'pairs',
      type: 'tuple[]',
      components: [
        { name: 'local', type: 'address' },
        { name: 'remote', type: 'address' },
        { name: 'remoteChainId', type: 'uint256' }
      ]
    }],
    stateMutability: 'view'
  }],
  functionName: 'suckerPairsOf',
  args: [projectId]
});

// pairs = [
//   { local: '0x...', remote: '0x...', remoteChainId: 10n },
//   { local: '0x...', remote: '0x...', remoteChainId: 8453n }
// ]
```

### Encoding Transactions

**Prepare (Step 1):**
```javascript
import { encodeFunctionData } from 'viem';

const prepareData = encodeFunctionData({
  abi: [{
    name: 'prepare',
    type: 'function',
    inputs: [
      { name: 'projectTokenCount', type: 'uint256' },
      { name: 'beneficiary', type: 'address' },
      { name: 'minTokensReclaimed', type: 'uint256' },
      { name: 'token', type: 'address' }
    ],
    outputs: [],
    stateMutability: 'nonpayable'
  }],
  functionName: 'prepare',
  args: [
    parseUnits('100', 18),     // 100 project tokens
    beneficiaryAddress,
    parseUnits('0.9', 18),     // 10% slippage allowed
    NATIVE_TOKEN               // 0xEEEE...EEEe for ETH
  ]
});

// Send transaction
await walletClient.sendTransaction({
  to: suckerAddress,
  data: prepareData
});
```

**Execute (Step 2):**
```javascript
// Estimate fee via simulation (binary search)
async function estimateBridgeFee(sucker, token) {
  let low = 0n;
  let high = parseUnits('0.04', 18);

  for (let i = 0; i < 10; i++) {
    const mid = (low + high) / 2n;
    try {
      await publicClient.simulateContract({
        address: sucker,
        abi: SUCKER_ABI,
        functionName: 'toRemote',
        args: [token],
        value: mid
      });
      high = mid; // Success - try lower
    } catch {
      low = mid;  // Failed - try higher
    }
  }
  return (high * 110n) / 100n; // Add 10% buffer
}

const fee = await estimateBridgeFee(suckerAddress, NATIVE_TOKEN);

const toRemoteData = encodeFunctionData({
  abi: [{
    name: 'toRemote',
    type: 'function',
    inputs: [{ name: 'token', type: 'address' }],
    outputs: [],
    stateMutability: 'payable'
  }],
  functionName: 'toRemote',
  args: [NATIVE_TOKEN]
});

await walletClient.sendTransaction({
  to: suckerAddress,
  data: toRemoteData,
  value: fee
});
```

**Claim (Step 3):**
```javascript
// Fetch proof from Juicerkle
const JUICERKLE_API = 'https://juicerkle-production.up.railway.app';

// NOTE: Addresses must be lowercase for Juicerkle API
const proofResponse = await fetch(`${JUICERKLE_API}/claims`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chainId: destinationChainId,
    sucker: peerSuckerAddress.toLowerCase(),
    token: NATIVE_TOKEN.toLowerCase(),
    beneficiary: userAddress.toLowerCase()
  })
});

// Response uses PascalCase
// interface JuicerkleClaim {
//   Token: string;
//   Leaf: { Index, Beneficiary, ProjectTokenCount, TerminalTokenAmount };
//   Proof: number[][]; // Array of 32-byte arrays
// }
const proofs = await proofResponse.json();
const claim = proofs[0];

// Convert Proof from number[][] to bytes32[]
const proofBytes = claim.Proof.map(arr => {
  const hex = arr.map(b => b.toString(16).padStart(2, '0')).join('');
  return `0x${hex}`;
});

const claimData = encodeFunctionData({
  abi: [{
    name: 'claim',
    type: 'function',
    inputs: [{
      name: 'claimData',
      type: 'tuple',
      components: [
        { name: 'token', type: 'address' },
        { name: 'leaf', type: 'tuple', components: [
          { name: 'index', type: 'uint256' },
          { name: 'beneficiary', type: 'address' },
          { name: 'projectTokenCount', type: 'uint256' },
          { name: 'terminalTokenAmount', type: 'uint256' }
        ]},
        { name: 'proof', type: 'bytes32[32]' }
      ]
    }],
    outputs: [],
    stateMutability: 'nonpayable'
  }],
  functionName: 'claim',
  args: [{
    token: claim.Token,
    leaf: {
      index: BigInt(claim.Leaf.Index),
      beneficiary: claim.Leaf.Beneficiary,
      projectTokenCount: BigInt(claim.Leaf.ProjectTokenCount),
      terminalTokenAmount: BigInt(claim.Leaf.TerminalTokenAmount)
    },
    proof: proofBytes
  }]
});

await walletClient.sendTransaction({
  to: peerSuckerAddress,
  data: claimData
});
```

### Querying Bridge Status (Bendystraw)

```graphql
query SuckerTransactions($suckerGroupId: String!, $status: suckerTransactionStatus) {
  suckerTransactions(
    where: { suckerGroupId: $suckerGroupId, status: $status }
    orderBy: "createdAt"
    orderDirection: "desc"
  ) {
    items {
      id
      chainId
      peerChainId
      sucker
      peer
      beneficiary
      projectTokenCount
      terminalTokenAmount
      token
      status        # "pending" | "claimable" | "claimed"
      index
      root
      createdAt
    }
  }
}
```

### State Transitions

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `pending` | Prepared but not sent | Call `toRemote()` |
| `claimable` | Root arrived, awaiting claim | Call `claim()` with proof |
| `claimed` | Complete | None |

### Emergency Exit

If a bridge becomes non-functional:

```javascript
// 1. Project owner enables emergency hatch
await ownerClient.writeContract({
  address: suckerAddress,
  abi: SUCKER_ABI,
  functionName: 'enableEmergencyHatchFor',
  args: [token]
});

// 2. Users can exit locally (no bridging)
// Retrieves funds from outbox without crossing chains
await userClient.writeContract({
  address: suckerAddress,
  abi: SUCKER_ABI,
  functionName: 'exitThroughEmergencyHatch',
  args: [claimData] // Same structure as claim()
});
```

### Token Mapping

Projects must map which tokens can be bridged:

```javascript
const mapping = {
  localToken: USDC_MAINNET,
  remoteToken: USDC_OPTIMISM,
  minGas: 300000,        // Minimum gas for cross-chain call
  minBridgeAmount: 10e6  // Minimum 10 USDC to bridge
};

await ownerClient.writeContract({
  address: suckerAddress,
  abi: SUCKER_ABI,
  functionName: 'mapToken',
  args: [mapping]
});
```

### Chain-Specific Notes

**OP Stack (Optimism, Base):**
- Uses native OP Messenger
- Lowest fees (~0.0005-0.002 ETH)
- Fast finality

**Arbitrum:**
- Uses Retryable Tickets
- Dynamic gas pricing
- Requires calculating `maxSubmissionCost`

**CCIP (L2↔L2):**
- Highest fees but most flexible
- Works between any CCIP-supported chains
- Good for Optimism↔Arbitrum, Base↔Arbitrum

### Sucker Deprecation

```
ENABLED → DEPRECATION_PENDING → SENDING_DISABLED → DEPRECATED
```

- `DEPRECATION_PENDING`: Warning state, still functional
- `SENDING_DISABLED`: Cannot prepare new bridges, can still claim
- `DEPRECATED`: Only emergency exits allowed

## Verification

1. Check sucker state before bridging: `sucker.state()`
2. Verify token is mapped: `sucker.remoteTokenFor(localToken)`
3. Check outbox balance: `sucker.outboxOf(token).balance`
4. Verify claim proof via Juicerkle before submitting

## Example

**Complete bridge flow from React:**

```typescript
async function bridgeTokens({
  sourceChainId,
  destChainId,
  suckerAddress,
  amount,
  beneficiary
}: BridgeParams) {
  // 1. Approve project token
  await writeContract({
    address: projectToken,
    abi: erc20Abi,
    functionName: 'approve',
    args: [suckerAddress, amount]
  });

  // 2. Prepare
  await writeContract({
    address: suckerAddress,
    abi: suckerAbi,
    functionName: 'prepare',
    args: [amount, beneficiary, 0n, NATIVE_TOKEN]
  });

  // 3. Execute (can be batched with others)
  const fee = await estimateBridgeFee(suckerAddress, NATIVE_TOKEN);
  await writeContract({
    address: suckerAddress,
    abi: suckerAbi,
    functionName: 'toRemote',
    args: [NATIVE_TOKEN],
    value: fee
  });

  // 4. Wait for root to arrive (check Bendystraw)
  // 5. Claim on destination (separate transaction)
}
```

## Notes

- Merkle tree depth is 32 - proofs are always `bytes32[32]`
- Nonces are monotonically increasing - prevents replay attacks
- Each token has independent outbox/inbox trees
- `addToBalanceMode` can be `MANUAL` or `ON_CLAIM`
- Double-spend prevention via executed leaf bitmap
- Emergency hatch uses separate execution namespace

## Related Skills

- `/jb-omnichain-ui` - Building omnichain UIs with Relayr and Bendystraw
- `/jb-v5-currency-types` - Currency handling for cross-chain projects
- `/jb-bendystraw` - Querying cross-chain data
