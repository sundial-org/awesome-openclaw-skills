---
name: jb-terminal-selection
description: |
  Dynamic terminal selection for Juicebox V5 payments. Use when: (1) building payment UIs that support
  multiple tokens (ETH/USDC), (2) encountering JBMultiTerminal_TokenNotAccepted error, (3) paying a
  project that uses ETH-only accounting with non-ETH tokens, (4) implementing cross-token payments
  where the project may not directly accept the user's payment token. Covers JBDirectory.primaryTerminalOf()
  querying, JBSwapTerminal fallback logic, and permit2 integration with correct terminal addresses.
---

# Dynamic Terminal Selection for Juicebox V5 Payments

## Problem

When paying a Juicebox V5 project, users may want to pay with tokens (e.g., USDC) that the project
doesn't directly accept in its accounting context. Sending such payments to `JBMultiTerminal` results
in a `JBMultiTerminal_TokenNotAccepted(token)` revert.

Common symptom: Transaction simulation shows "likely to fail" after permit2 signing, with the
`TokenNotAccepted` error in Tenderly or other simulation tools.

## Context / Trigger Conditions

Apply this pattern when:
- Building a payment UI that supports multiple tokens (ETH, USDC, etc.)
- A project uses ETH accounting context but users want to pay with USDC
- You see `JBMultiTerminal_TokenNotAccepted` errors in transaction simulations
- MetaMask shows "This transaction is likely to fail" after permit2 signing
- You need to determine which terminal to use at runtime

## Solution

### Core Concept

Query `JBDirectory.primaryTerminalOf(projectId, tokenAddress)` to discover which terminal
accepts payments for a given token. If no terminal is registered (returns zero address),
use `JBSwapTerminal` which automatically swaps the payment token to what the project accepts.

### Implementation

```typescript
import { type PublicClient, type Address, zeroAddress } from 'viem'

// JBSwapTerminal addresses (same via CREATE2 across chains)
const JB_SWAP_TERMINAL: Record<number, Address> = {
  1: '0x259385b97dfbd5576bd717dc7b25967ec8b145dd',      // Ethereum
  10: '0x73d04584bde126242c36c2c7b219cbdec7aad774',     // Optimism
  8453: '0x4fd73d8b285e82471f08a4ef9861d6248b832edd',   // Base
  42161: '0x483c9b12c5bd2da73133aae30642ce0008c752ad',  // Arbitrum
}

// JBDirectory address (same on all chains via CREATE2)
const JB_DIRECTORY = '0x0061e516886a0540f63157f112c0588ee0651dcf'

const JB_DIRECTORY_ABI = [
  {
    name: 'primaryTerminalOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'projectId', type: 'uint256' },
      { name: 'token', type: 'address' },
    ],
    outputs: [{ name: '', type: 'address' }],
  },
] as const

type TerminalType = 'multi' | 'swap'

interface PaymentTerminal {
  address: Address
  type: TerminalType
}

/**
 * Determines which terminal to use for a payment.
 *
 * 1. Query JBDirectory.primaryTerminalOf(projectId, tokenAddress)
 * 2. If zero address → project doesn't accept this token directly → use SwapTerminal
 * 3. If non-zero → use the returned terminal (could be Multi or Swap)
 */
async function getPaymentTerminal(
  client: PublicClient,
  chainId: number,
  projectId: bigint,
  paymentToken: Address
): Promise<PaymentTerminal> {
  // Query directory for the primary terminal that accepts this token
  const terminal = await client.readContract({
    address: JB_DIRECTORY,
    abi: JB_DIRECTORY_ABI,
    functionName: 'primaryTerminalOf',
    args: [projectId, paymentToken],
  })

  const swapTerminal = JB_SWAP_TERMINAL[chainId]

  // No terminal registered for this token → use swap terminal
  if (terminal === zeroAddress) {
    return { address: swapTerminal, type: 'swap' }
  }

  // Check if the returned terminal IS the swap terminal
  const isSwapTerminal = terminal.toLowerCase() === swapTerminal?.toLowerCase()

  return {
    address: terminal,
    type: isSwapTerminal ? 'swap' : 'multi'
  }
}
```

### Permit2 Integration

When using permit2 for token approvals, the metadata ID computation must use the correct
terminal address as the spender:

```typescript
// Permit2 metadata ID = bytes4(bytes20(terminal) ^ bytes20(keccak256("permit2")))
function computePermit2MetadataId(terminalAddress: Address): `0x${string}` {
  const permit2Hash = keccak256(toBytes('permit2'))
  const terminalBytes = terminalAddress.slice(0, 42) // 0x + 40 hex chars
  const hashBytes = permit2Hash.slice(0, 42)

  // XOR the first 20 bytes
  const xorResult = BigInt(terminalBytes) ^ BigInt(hashBytes)
  const bytes4 = (xorResult >> 128n) & 0xffffffffn

  return `0x${bytes4.toString(16).padStart(8, '0')}`
}
```

### Usage in Payment Flow

```typescript
async function pay(projectId: string, amount: string, token: 'ETH' | 'USDC') {
  const tokenAddress = token === 'ETH'
    ? '0x000000000000000000000000000000000000EEEe'  // Native token
    : USDC_ADDRESSES[chainId]

  // 1. Detect correct terminal
  const terminal = await getPaymentTerminal(
    publicClient,
    chainId,
    BigInt(projectId),
    tokenAddress
  )

  // 2. For ERC20, sign permit2 with terminal as spender
  if (token !== 'ETH') {
    const permit = await signPermit2({
      spender: terminal.address,  // CRITICAL: use detected terminal
      token: tokenAddress,
      amount,
      // ...
    })
  }

  // 3. Call pay on the correct terminal
  await walletClient.writeContract({
    address: terminal.address,
    abi: terminal.type === 'swap' ? JB_SWAP_TERMINAL_ABI : JB_MULTI_TERMINAL_ABI,
    functionName: 'pay',
    args: [projectId, tokenAddress, amount, beneficiary, minTokens, memo, metadata],
  })
}
```

## Verification

1. Query `primaryTerminalOf` for ETH → should return JBMultiTerminal address
2. Query `primaryTerminalOf` for USDC on ETH-only project → should return zero address
3. Use SwapTerminal when zero address returned
4. Transaction simulation should no longer show `TokenNotAccepted` error

## Example

**Scenario**: User wants to pay NANA (Project ID 1) with USDC on Base. NANA only uses ETH accounting.

```typescript
// Query: What terminal accepts USDC for NANA?
const terminal = await getPaymentTerminal(
  publicClient,
  8453,  // Base
  1n,    // NANA project ID
  '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'  // USDC on Base
)

// Result: { address: '0x4fd73d8b285e82471f08a4ef9861d6248b832edd', type: 'swap' }
// The SwapTerminal will swap USDC → ETH before paying NANA
```

## Notes

- JBSwapTerminal swaps tokens via Uniswap before crediting the project
- The swap uses TWAP pricing with slippage protection
- Projects can explicitly register JBSwapTerminal for tokens they want to accept via swaps
- Some projects register JBMultiTerminal for multiple tokens (e.g., both ETH and USDC)
- Always query at runtime; terminal registrations can change

## Related Skills

- `/jb-v5-impl` - Deep dive into terminal mechanics and payment flow internals
- `/jb-terminal-wrapper` - Pattern for wrapping terminals with custom logic
- `/jb-v5-api` - Core terminal interface signatures
- `/jb-query` - Querying project state from blockchain

## References

- [revnet-app terminal detection](https://github.com/rev-net/revnet-app/blob/main/src/lib/paymentTerminal.ts)
- [JBSwapTerminal implementation](https://github.com/Bananapus/nana-swap-terminal)
- [JBDirectory contract](https://github.com/Bananapus/nana-core-v5/blob/main/src/JBDirectory.sol)
