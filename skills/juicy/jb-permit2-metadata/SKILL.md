---
name: jb-permit2-metadata
description: Encode metadata for Juicebox V5 terminal payments using JBMetadataResolver. Covers Permit2 gasless ERC20 payments, 721 hook tier selection, and combining multiple metadata types. Use when seeing AllowanceExpired errors, metadata extraction returns zeros, specifying NFT tiers to mint, or Tenderly shows exists false at getDataFor call.
---

# JBMetadataResolver: Pay Metadata Encoding

## Overview

Juicebox V5 uses `JBMetadataResolver` to pass structured data through the `metadata` parameter of `pay()`, `addToBalance()`, and other terminal functions. Multiple extensions (Permit2, 721 hook, buyback hook, etc.) can read their specific data from a single metadata blob using a lookup table format.

**Key concept**: Each extension has a unique 4-byte ID. The metadata contains a lookup table mapping IDs to data offsets, allowing each extension to find its data without knowing about other extensions.

## When to Use This Skill

- Implementing gasless ERC20 payments via Permit2 (single-transaction UX)
- Specifying which NFT tiers to mint when paying a 721 hook project
- Seeing "AllowanceExpired" error from Permit2 contract
- Tenderly shows `exists: false` or all-zeros at `getDataFor` call
- Combining multiple metadata types in one payment (e.g., Permit2 + tier selection)

## Critical Rule: Use the Official Library

**ALWAYS use `juicebox-metadata-helper` for metadata construction.** Manual construction has subtle bugs:

```bash
npm install juicebox-metadata-helper
```

The library handles:
- Correct offset calculation (in words, not bytes)
- Proper padding to 32-byte boundaries
- Lookup table format matching JBMetadataResolver exactly

---

## Metadata Type 1: Permit2 (Gasless ERC20 Payments)

Permit2 allows single-transaction ERC20 payments without separate approve transactions.

### Swap Terminal Registries

Two swap terminal registries exist, deployed at the same address on all chains:

| Registry | Address | TOKEN_OUT | Purpose |
|----------|---------|-----------|---------|
| **JBSwapTerminalRegistry** | `0x60b4f5595ee509c4c22921c7b7999f1616e6a4f6` | NATIVE_TOKEN (ETH) | Swaps incoming tokens → ETH |
| **JBSwapTerminalUSDCRegistry** | `0x1ce40d201cdec791de05810d17aaf501be167422` | USDC | Swaps incoming tokens → USDC |

**Choose based on what the project should RECEIVE** after the swap, not what the user pays with.

### Step 1: Compute the Permit2 Metadata ID

**CRITICAL**: Use ethers.js for ID computation. Viem's byte handling can have subtle issues with the XOR operation.

```typescript
import { ethers } from 'ethers'
import type { Address } from 'viem'

function computePermit2MetadataId(terminalAddress: Address): string {
  // Use ethers to match Solidity's bytes20 XOR exactly
  const purposeHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes('permit2'))

  // Get first 20 bytes of hash (40 hex chars after 0x)
  const purposeBytes20 = purposeHash.slice(0, 42)

  // Terminal address is already 20 bytes
  const terminalBytes20 = terminalAddress.toLowerCase()

  // XOR as BigNumbers - matches Solidity's bytes20 ^ bytes20
  const purposeBN = ethers.BigNumber.from(purposeBytes20)
  const terminalBN = ethers.BigNumber.from(terminalBytes20)
  const xorResult = purposeBN.xor(terminalBN)

  // Get first 4 bytes (8 hex chars) - matches Solidity's bytes4(...)
  return xorResult.toHexString().slice(0, 10)
}
```

### Step 2: Encode JBSingleAllowance Struct

**CRITICAL: Must encode as a TUPLE, not individual parameters!**

```typescript
import { encodeAbiParameters, type Hex } from 'viem'

function encodeJBSingleAllowance(
  sigDeadline: bigint,
  amount: bigint,
  expiration: number,
  nonce: number,
  signature: Hex
): Hex {
  // MUST use tuple encoding to match abi.encode(struct) in Solidity
  return encodeAbiParameters(
    [{
      type: 'tuple',
      components: [
        { name: 'sigDeadline', type: 'uint256' },
        { name: 'amount', type: 'uint160' },
        { name: 'expiration', type: 'uint48' },
        { name: 'nonce', type: 'uint48' },
        { name: 'signature', type: 'bytes' },
      ]
    }],
    [{
      sigDeadline,
      amount,
      expiration: BigInt(expiration),
      nonce: BigInt(nonce),
      signature,
    }]
  )
}
```

### Step 3: Build Permit2 Metadata

```typescript
import createMetadata from 'juicebox-metadata-helper'
import type { Hex, Address } from 'viem'

function buildPermit2Metadata(allowanceData: Hex, terminalAddress: Address): Hex {
  const permit2Id = computePermit2MetadataId(terminalAddress)

  // Pad allowance data to 32-byte boundary (required by the library)
  const dataLen = (allowanceData.length - 2) / 2
  const paddedLen = Math.ceil(dataLen / 32) * 32
  const paddedData = ('0x' + allowanceData.slice(2).padEnd(paddedLen * 2, '0')) as Hex

  // Use the official library
  return createMetadata([permit2Id], [paddedData]) as Hex
}
```

### Step 4: Sign the Permit2 Message

```typescript
const PERMIT2_ADDRESS = '0x000000000022D473030F116dDEE9F6B43aC78BA3'

const PERMIT2_TYPES = {
  PermitSingle: [
    { name: 'details', type: 'PermitDetails' },
    { name: 'spender', type: 'address' },
    { name: 'sigDeadline', type: 'uint256' },
  ],
  PermitDetails: [
    { name: 'token', type: 'address' },
    { name: 'amount', type: 'uint160' },
    { name: 'expiration', type: 'uint48' },
    { name: 'nonce', type: 'uint48' },
  ],
}

// Get current nonce from Permit2
const [, , currentNonce] = await publicClient.readContract({
  address: PERMIT2_ADDRESS,
  abi: permit2AllowanceAbi,
  functionName: 'allowance',
  args: [userAddress, tokenAddress, terminalAddress],
})

const nowSeconds = Math.floor(Date.now() / 1000)
const expiration = nowSeconds + 30 * 24 * 60 * 60  // 30 days
const sigDeadline = BigInt(nowSeconds + 30 * 60)   // 30 minutes

const signature = await walletClient.signTypedData({
  domain: {
    name: 'Permit2',
    chainId: chainId,
    verifyingContract: PERMIT2_ADDRESS,
  },
  types: PERMIT2_TYPES,
  primaryType: 'PermitSingle',
  message: {
    details: {
      token: tokenAddress,
      amount: paymentAmount,
      expiration: expiration,
      nonce: Number(currentNonce),
    },
    spender: terminalAddress,  // The terminal that will call permit2
    sigDeadline: sigDeadline,
  },
})
```

### Complete Permit2 Payment Flow

```typescript
// 1. Ensure token is approved to Permit2 (one-time)
const tokenToPermit2Allowance = await publicClient.readContract({
  address: tokenAddress,
  abi: erc20Abi,
  functionName: 'allowance',
  args: [userAddress, PERMIT2_ADDRESS],
})

if (tokenToPermit2Allowance < amount) {
  // Approve max to Permit2 (one-time unlimited approval)
  await walletClient.writeContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'approve',
    args: [PERMIT2_ADDRESS, maxUint256],
  })
}

// 2. Get terminal address
const terminalAddress = await publicClient.readContract({
  address: JB_DIRECTORY,
  abi: directoryAbi,
  functionName: 'primaryTerminalOf',
  args: [projectId, tokenAddress],
})

// 3. Sign permit and build metadata
const signature = await walletClient.signTypedData(...)
const allowanceData = encodeJBSingleAllowance(sigDeadline, amount, expiration, nonce, signature)
const metadata = buildPermit2Metadata(allowanceData, terminalAddress)

// 4. Call pay with metadata - single transaction!
await walletClient.writeContract({
  address: terminalAddress,
  abi: terminalAbi,
  functionName: 'pay',
  args: [projectId, tokenAddress, amount, beneficiary, 0n, memo, metadata],
})
```

---

## Metadata Type 2: 721 Hook (NFT Tier Selection)

When paying a project with a 721 hook, you can specify which NFT tiers to mint.

### The 721 Hook Metadata ID

Unlike Permit2, the 721 hook ID is NOT XOR'd with the contract address. It's a static ID:

```typescript
import { ethers } from 'ethers'

// Static ID - same for all 721 hooks
const JB721_HOOK_ID = '0x' + ethers.utils.keccak256(
  ethers.utils.toUtf8Bytes('JB721TiersHook')
).slice(2, 10) // First 4 bytes
```

### 721 Hook Data Format

The data payload is:
1. `allowOverspending` (bool) - If true, excess payment beyond tier prices goes to token minting
2. `tierIds` (uint16[]) - Array of tier IDs to mint

```typescript
import { encodeAbiParameters, type Hex } from 'viem'

function encode721HookData(
  allowOverspending: boolean,
  tierIds: number[]
): Hex {
  return encodeAbiParameters(
    [
      { type: 'bool' },
      { type: 'uint16[]' }
    ],
    [
      allowOverspending,
      tierIds.map(id => id)  // uint16[] of tier IDs
    ]
  )
}
```

### Build 721 Hook Metadata

```typescript
import createMetadata from 'juicebox-metadata-helper'
import { ethers } from 'ethers'

function build721HookMetadata(allowOverspending: boolean, tierIds: number[]): Hex {
  // Compute the static 721 hook ID
  const hookId = '0x' + ethers.utils.keccak256(
    ethers.utils.toUtf8Bytes('JB721TiersHook')
  ).slice(2, 10)

  // Encode the data
  const data = encode721HookData(allowOverspending, tierIds)

  // Pad to 32-byte boundary
  const dataLen = (data.length - 2) / 2
  const paddedLen = Math.ceil(dataLen / 32) * 32
  const paddedData = ('0x' + data.slice(2).padEnd(paddedLen * 2, '0')) as Hex

  return createMetadata([hookId], [paddedData]) as Hex
}
```

### Example: Mint Specific NFT Tiers

```typescript
import { parseEther } from 'viem'

// Mint tier 1 and tier 3, allow overspending
const metadata = build721HookMetadata(true, [1, 3])

await walletClient.writeContract({
  address: terminalAddress,
  abi: terminalAbi,
  functionName: 'pay',
  args: [
    projectId,
    '0x0000000000000000000000000000000000000000',  // ETH (native token)
    parseEther('0.5'),              // Amount
    beneficiary,
    0n,                             // minReturnedTokens
    'Minting tiers 1 and 3',
    metadata
  ],
  value: parseEther('0.5'),
})
```

### allowOverspending Explained

| `allowOverspending` | Behavior |
|---------------------|----------|
| `true` | Payment exceeding tier prices mints project tokens |
| `false` | Reverts if payment doesn't exactly match tier prices |

Example: If tier 1 costs 0.1 ETH and you pay 0.5 ETH with `allowOverspending: true`:
- You receive 1 NFT from tier 1
- Remaining 0.4 ETH mints project tokens

---

## Combining Multiple Metadata Types

You can include both Permit2 AND 721 hook data in a single payment!

```typescript
import createMetadata from 'juicebox-metadata-helper'

function buildCombinedMetadata(
  terminalAddress: Address,
  permit2AllowanceData: Hex,
  tierIds: number[],
  allowOverspending: boolean
): Hex {
  // Permit2 ID (XOR'd with terminal)
  const permit2Id = computePermit2MetadataId(terminalAddress)

  // 721 Hook ID (static)
  const hookId = '0x' + ethers.utils.keccak256(
    ethers.utils.toUtf8Bytes('JB721TiersHook')
  ).slice(2, 10)

  // Encode both data payloads
  const permit2Data = padTo32Bytes(permit2AllowanceData)
  const hookData = padTo32Bytes(encode721HookData(allowOverspending, tierIds))

  // Combine with library - handles lookup table automatically
  return createMetadata(
    [permit2Id, hookId],
    [permit2Data, hookData]
  ) as Hex
}

// Helper
function padTo32Bytes(data: Hex): Hex {
  const dataLen = (data.length - 2) / 2
  const paddedLen = Math.ceil(dataLen / 32) * 32
  return ('0x' + data.slice(2).padEnd(paddedLen * 2, '0')) as Hex
}
```

### Example: Pay with USDC + Mint NFT Tier

```typescript
// Pay with USDC via Permit2 AND mint tier 2
const permit2Data = encodeJBSingleAllowance(sigDeadline, amount, expiration, nonce, signature)
const metadata = buildCombinedMetadata(
  terminalAddress,
  permit2Data,
  [2],      // Mint tier 2
  true      // Allow overspending
)

await walletClient.writeContract({
  address: terminalAddress,
  abi: terminalAbi,
  functionName: 'pay',
  args: [projectId, usdcAddress, amount, beneficiary, 0n, memo, metadata],
})
```

---

## Debugging Guide

### `exists: false` in Tenderly trace

**Problem**: The metadata ID is not being found in the lookup table.

**For Permit2**:
1. Verify you're using ethers.js for ID computation (not viem byte arrays)
2. Verify the terminal address matches what `primaryTerminalOf` returns
3. Log both the computed ID and compare with what the contract expects

**For 721 Hook**:
1. Verify you're using `keccak256("JB721TiersHook")` not something else
2. Check that the hook is actually deployed for this project

### `exists: true` but decoded values are zeros or shifted

**Problem**: The metadata format is incorrect - data is in the wrong position.

**Solution**:
1. Use `juicebox-metadata-helper` library instead of manual construction
2. Ensure data is padded to 32-byte boundaries before passing to library
3. Check that offset is in WORDS (not bytes)

### Decoded sigDeadline shows wrong value (e.g., 288)

**Problem**: The contract is reading the data length instead of the actual data.

**Solution**: This indicates the offset or format is wrong. Use the library.

### Error: "Called function does not exist in the contract" on abi.decode

**Problem**: JBSingleAllowance is encoded as individual parameters instead of as a tuple.

**Solution**: Use explicit tuple encoding:
```typescript
encodeAbiParameters(
  [{ type: 'tuple', components: [...] }],  // NOT individual types
  [{ sigDeadline, amount, ... }]           // Pass as object
)
```

### 721 Hook: No NFTs minted despite correct metadata

**Check**:
1. Payment amount covers tier price(s)
2. Tier has remaining supply (`remainingSupply > 0`)
3. Tier is not paused
4. Project has 721 hook configured as data hook

---

## Common Mistakes

### Permit2
1. **Individual parameters instead of tuple**: MUST encode JBSingleAllowance as a tuple type
2. **Manual metadata construction**: Has subtle bugs. ALWAYS use `juicebox-metadata-helper`
3. **Viem for ID computation**: Use ethers.js BigNumber.xor() instead
4. **Wrong terminal address**: Must use the terminal from `primaryTerminalOf`
5. **Offset in bytes instead of words**: The offset is in 32-byte words
6. **Missing padding**: Data must be padded to 32-byte boundaries
7. **Wrong spender**: Permit2 spender must be the terminal address

### 721 Hook
1. **Using XOR for hook ID**: 721 hook uses a static ID, not XOR'd with address
2. **Wrong tier ID type**: Must be uint16[], not uint256[]
3. **Missing allowOverspending field**: Both fields are required
4. **Insufficient payment**: Must cover total tier prices unless allowOverspending is true

---

## Verification

### Check metadata ID matches

**Permit2**: Terminal uses `JBMetadataResolver.getId("permit2")` which XORs with `address(this)`

**721 Hook**: Uses `bytes4(keccak256("JB721TiersHook"))` - static, no XOR

### In Tenderly trace

- `getDataFor()` should return `(true, <non-zero-data>)`
- If `exists: false`, ID computation is wrong
- If `exists: true` but data is wrong, format is wrong (use the library!)

---

## References

- [JBMetadataResolver.sol](https://github.com/Bananapus/nana-core-v5/blob/main/src/libraries/JBMetadataResolver.sol)
- [JBSingleAllowance.sol](https://github.com/Bananapus/nana-core-v5/blob/main/src/structs/JBSingleAllowance.sol)
- [JB721TiersHook.sol](https://github.com/Bananapus/nana-721-hook/blob/main/src/JB721TiersHook.sol)
- [TestPermit2Terminal5_1.sol](https://github.com/Bananapus/nana-core-v5/blob/main/test/TestPermit2Terminal5_1.sol)
- [Permit2 AllowanceTransfer](https://github.com/Uniswap/permit2)
- [juicebox-metadata-helper](https://www.npmjs.com/package/juicebox-metadata-helper)
