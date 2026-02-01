---
name: jb-multi-currency
description: |
  Handle Juicebox V5 multi-currency projects (ETH vs USDC accounting).
  Use when: (1) building UI that displays currency labels (ETH vs USDC),
  (2) sending transactions that require currency parameter,
  (3) configuring fund access limits or accounting contexts for new rulesets,
  (4) querying project balance/surplus with correct token,
  (5) debugging "wrong currency" issues in payout or allowance transactions,
  (6) need currency code constants (NATIVE_CURRENCY=61166, USDC varies by chain),
  (7) cash out modal shows wrong return currency (ETH instead of USDC),
  (8) need shared chain constants (names, explorers) across multiple modals.
  Currency in JBAccountingContext is uint32(uint160(tokenAddress)), NOT 1 or 2.
  Covers baseCurrency detection, decimal handling, terminal accounting, currency codes,
  dynamic labels, cash out return display, and shared chain constants patterns.
---

# Juicebox V5 Multi-Currency Support

## Problem

Juicebox V5 projects can be denominated in either ETH (baseCurrency=1) or USD (baseCurrency=2).
UI components and transactions must use the correct currency value, token address, and display
labels. Hardcoding "ETH" or currency=1 causes failures for USDC-based projects.

## Context / Trigger Conditions

- UI shows "ETH" when project is USDC-based
- Payout or allowance transaction fails silently
- Fund access limits set with wrong currency
- Currency mismatch between ruleset config and terminal accounting
- Need to display correct currency symbol in forms

## Solution

### 1. Detect Project Currency from Ruleset

```typescript
// baseCurrency is in ruleset metadata
// 1 = ETH, 2 = USD (USDC)
const baseCurrency = ruleset?.metadata?.baseCurrency || 1
const currencyLabel = baseCurrency === 2 ? 'USDC' : 'ETH'
```

### 2. Use Dynamic Currency in Transactions

When calling terminal functions (sendPayoutsOf, useAllowanceOf), use the project's baseCurrency:

```typescript
// WRONG - hardcoded
args: [projectId, token, amount, 1n, minTokensPaidOut, beneficiary]

// CORRECT - dynamic
args: [projectId, token, amount, BigInt(baseCurrency), minTokensPaidOut, beneficiary]
```

### 3. Fund Access Limits Currency

When queuing new rulesets or displaying limits, match the existing project currency.
**Use correct decimals**: Query from `ERC20.decimals()` or use 18 for native tokens.

```typescript
import { parseUnits } from 'viem'

// Get currency from existing config
const currency = existingConfig?.baseCurrency || 1

// Get decimals from the token contract (or 18 for native token)
// For USDC: 6 decimals. For native token (ETH): 18 decimals.
const decimals = await getTokenDecimals(tokenAddress, publicClient)

// Use in fund access limit configuration
const payoutLimits = [{
  amount: parseUnits(limitAmount, decimals).toString(),
  currency, // Match project's base currency (1 or 2)
}]
```

### 4. Two Different "currency" Concepts (CRITICAL)

Juicebox V5 has TWO different concepts called "currency" that are often confused:

| Field | Location | Values | Purpose |
|-------|----------|--------|---------|
| `baseCurrency` | Ruleset metadata | 1 = ETH, 2 = USD | Issuance rate calculation |
| `JBCurrencyAmount.currency` | Fund access limits | 1 = ETH, 2 = USD | Payout/allowance limits |
| `JBAccountingContext.currency` | Terminal config | `uint32(uint160(token))` | Terminal accounting |

**The `currency` value in JBAccountingContext is NOT 1 or 2. It's `uint32(uint160(tokenAddress))`.**

```typescript
// NATIVE_TOKEN (ETH) - same on all chains - from JBConstants.NATIVE_TOKEN
const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe'
const NATIVE_CURRENCY = 61166 // uint32(uint160(NATIVE_TOKEN)) = 0x0000EEEe

// USDC addresses and currency codes per chain
const USDC_CONFIG: Record<number, { address: string; currency: number }> = {
  1: {      // Ethereum
    address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    currency: 909516616,
  },
  10: {     // Optimism
    address: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    currency: 3530704773,
  },
  8453: {   // Base
    address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    currency: 3169378579,
  },
  42161: {  // Arbitrum
    address: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    currency: 1156540465,
  },
}
```

**How to calculate currency from any token address:**
```typescript
const calculateCurrency = (tokenAddress: string): number => {
  // Take last 4 bytes of address as uint32
  return Number(BigInt(tokenAddress) & BigInt(0xFFFFFFFF))
}
```

### 5. Decimal Handling

**General rule:** Get decimals from `ERC20.decimals()` for any token. Native tokens (ETH, MATIC, etc.) always use 18 decimals.

Common cases:
- Native token (ETH): 18 decimals
- USDC: 6 decimals
- Most ERC-20s: varies - always query `decimals()`

```typescript
import { erc20Abi } from 'viem'

// For native token
const NATIVE_DECIMALS = 18

// For ERC-20 tokens - query the contract
const getTokenDecimals = async (tokenAddress: string, publicClient: PublicClient) => {
  if (tokenAddress === NATIVE_TOKEN) return NATIVE_DECIMALS
  return await publicClient.readContract({
    address: tokenAddress as `0x${string}`,
    abi: erc20Abi,
    functionName: 'decimals',
  })
}

// Shortcut for known tokens (use with caution)
const KNOWN_DECIMALS: Record<string, number> = {
  [NATIVE_TOKEN]: 18,
  // USDC on all chains uses 6 decimals
}
```

### 6. Terminal Accounting Contexts

When configuring terminals, set accounting context to match. **The currency MUST be derived from the token address.**

```typescript
// ETH-based project
{
  terminal: JB_MULTI_TERMINAL,
  accountingContextsToAccept: [{
    token: NATIVE_TOKEN,        // 0x000000000000000000000000000000000000EEEe
    decimals: 18,
    currency: 61166,            // uint32(uint160(NATIVE_TOKEN)) = 0x0000EEEe
  }]
}

// USDC-based project (example: Ethereum)
{
  terminal: JB_MULTI_TERMINAL,
  accountingContextsToAccept: [{
    token: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    decimals: 6,
    currency: 909516616,        // uint32(uint160(USDC_ADDRESS))
  }]
}
```

**WRONG:** Using currency: 1 for ETH or currency: 2 for USD
**RIGHT:** Using the calculated uint32 value from the token address

## Component Pattern

For React components that handle multiple currencies:

```typescript
interface ChainData {
  chainId: number
  projectId: number
  baseCurrency: number // 1 = ETH, 2 = USD
  // ... other fields
}

function MyComponent({ chainData }: { chainData: ChainData }) {
  const baseCurrency = chainData?.baseCurrency || 1
  const currencyLabel = baseCurrency === 2 ? 'USDC' : 'ETH'

  return (
    <div>
      <span>Amount: {amount} {currencyLabel}</span>
      {/* Use currencyLabel throughout, never hardcode "ETH" */}
    </div>
  )
}
```

### 7. Cash Out Modal Currency Display

When cashing out, users burn project tokens and receive funds **in the project's base currency**.
The modal must show the correct currency for the return amount:

```typescript
interface CashOutModalProps {
  projectId: string
  tokenAmount: string      // Tokens being burned
  tokenSymbol: string      // e.g., "NANA", "REV"
  estimatedReturn: number  // Amount user will receive
  currencySymbol: 'ETH' | 'USDC'  // CRITICAL: matches project's base currency
}

function CashOutModal({
  tokenAmount,
  tokenSymbol,
  estimatedReturn,
  currencySymbol = 'ETH',  // Default to ETH for backwards compatibility
}: CashOutModalProps) {
  // Format decimals based on currency
  const decimals = currencySymbol === 'USDC' ? 2 : 4

  return (
    <div>
      <div>Burning: {tokenAmount} {tokenSymbol}</div>
      <div>You receive: ~{estimatedReturn.toFixed(decimals)} {currencySymbol}</div>
    </div>
  )
}
```

**Key insight**: The component receiving cash out data must pass `currencySymbol` based on the
project's `baseCurrency`, not hardcode "ETH". For USDC-based projects, show "~5.00 USDC" not "~0.002 ETH".

### 8. Shared Chain Constants Pattern

Avoid duplicating chain info across modals. Create a shared constants file:

```typescript
// constants/index.ts
export const CHAINS: Record<number, {
  name: string
  shortName: string
  explorerTx: string
  explorerAddress: string
}> = {
  1: {
    name: 'Ethereum',
    shortName: 'ETH',
    explorerTx: 'https://etherscan.io/tx/',
    explorerAddress: 'https://etherscan.io/address/',
  },
  10: {
    name: 'Optimism',
    shortName: 'OP',
    explorerTx: 'https://optimistic.etherscan.io/tx/',
    explorerAddress: 'https://optimistic.etherscan.io/address/',
  },
  8453: {
    name: 'Base',
    shortName: 'BASE',
    explorerTx: 'https://basescan.org/tx/',
    explorerAddress: 'https://basescan.org/address/',
  },
  42161: {
    name: 'Arbitrum',
    shortName: 'ARB',
    explorerTx: 'https://arbiscan.io/tx/',
    explorerAddress: 'https://arbiscan.io/address/',
  },
}

export const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe' as const
```

Then import in modals:
```typescript
import { CHAINS, NATIVE_TOKEN } from '../constants'

const chainInfo = CHAINS[chainId] || CHAINS[1]
const explorerLink = `${chainInfo.explorerTx}${txHash}`
```

## Verification

- USDC-based projects display "USDC" labels (not "ETH")
- Cash out modals show return in correct currency (ETH or USDC)
- Transactions use correct currency parameter
- Fund access limits store correct currency
- Balance queries use correct token address

## Example

For Artizen (project 6 on Base):
- baseCurrency = 2 (USD)
- Display "USDC" in all labels
- Use USDC token address for balance queries: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Fund access limits use currency: 2

## Common Mistakes

1. **Hardcoded labels**: Using "ETH" string instead of `currencyLabel`
2. **Hardcoded currency**: Using `1n` instead of `BigInt(baseCurrency)`
3. **Wrong decimals**: Using 18 decimals for USDC (should be 6)
4. **Token mismatch**: Querying with NATIVE_TOKEN for USDC project

## Notes

- Default to ETH (baseCurrency=1) if not specified
- JBSwapTerminal accepts any token and swaps to project's base currency
- Cash out returns funds in the project's base currency
- Price feeds convert between currencies when needed

## References

- JBMultiTerminal5_1: `0x52869db3d61dde1e391967f2ce5039ad0ecd371c`
- JBSwapTerminal: `0x0c02e48e55f4451a499e48a53595de55c40f3574`
- JBPrices: `0x6e92e3b5ce1e7a4344c6d27c0c54efd00df92fb6`
