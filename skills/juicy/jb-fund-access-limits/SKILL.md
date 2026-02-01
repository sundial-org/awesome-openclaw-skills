---
name: jb-fund-access-limits
description: |
  Query and display Juicebox V5 fund access limits (payout limits, surplus allowances).
  Use when: (1) surplusAllowancesOf or payoutLimitsOf returns empty but values exist,
  (2) need to detect "unlimited" values which can be various max integers not just uint256,
  (3) fund access limits show as zero for USDC-based projects when querying with ETH token,
  (4) REVDeployer stageOf or configurationOf reverts, (5) CONFIGURING project deployment
  and need unlimited payouts - CRITICAL: empty fundAccessLimitGroups means ZERO payouts
  not unlimited, must use uint224.max for unlimited. Covers JBFundAccessLimits querying,
  multi-token support (ETH/USDC), ruleset chain walking, unlimited value detection, and
  proper configuration for project deployment.
---

# Juicebox V5 Fund Access Limits

## Problem

Two distinct issues with fund access limits:

1. **Configuration**: When deploying projects, `fundAccessLimitGroups: []` (empty array) means
   **ZERO payouts allowed**, NOT unlimited. This is a common mistake - to allow unlimited
   payouts, you must explicitly set `payoutLimits` with `uint224.max`.

2. **Querying**: When querying JBFundAccessLimits for payout limits or surplus allowances,
   the queries may return empty results even when values are set in the contract. Additionally,
   detecting "unlimited" values is tricky because the protocol uses various max integers.

## Context / Trigger Conditions

**Configuration (when deploying):**
- User selects "I'll manage it" or "unlimited payouts" but can't withdraw funds
- `fundAccessLimitGroups: []` was generated (WRONG - means zero payouts)
- Project owner needs ability to withdraw funds but config blocks it

**Querying (when reading):**
- `surplusAllowancesOf` or `payoutLimitsOf` returns empty array
- Fund access shows "None" when it should show "Unlimited"
- Project uses USDC instead of ETH as base currency
- REVDeployer's `stageOf` or `configurationOf` functions revert
- Large numbers displayed instead of "Unlimited" label

## Solution

### 0. CRITICAL: Configuring Unlimited Payouts (Deployment)

**Empty `fundAccessLimitGroups: []` = NO payouts allowed (not unlimited!)**

To allow unlimited payouts, you MUST specify a payout limit with `uint224.max`:

```typescript
// uint224.max - the maximum value the JBFundAccessLimits registry accepts
const UINT224_MAX = '26959946667150639794667015087019630673637144422540572481103610249215'

// WRONG - this means ZERO payouts allowed
const wrongConfig = {
  fundAccessLimitGroups: []
}

// CORRECT - unlimited payouts for ETH
const correctConfigETH = {
  fundAccessLimitGroups: [{
    terminal: '0x3f75f7e52ed15c2850b0a6a49c234d5221576dbe', // JBMultiTerminal (ETH)
    token: '0x000000000000000000000000000000000000EEEe',    // Native token
    payoutLimits: [{
      amount: UINT224_MAX,
      currency: 1  // ETH currency
    }],
    surplusAllowances: []
  }]
}

// CORRECT - unlimited payouts for USDC (Ethereum mainnet)
const correctConfigUSDC = {
  fundAccessLimitGroups: [{
    terminal: '0x52869db3d61dde1e391967f2ce5039ad0ecd371c', // JBMultiTerminal5_1
    token: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',    // USDC on Ethereum
    payoutLimits: [{
      amount: UINT224_MAX,
      currency: 909516616  // USDC currency (from accounting context)
    }],
    surplusAllowances: []
  }]
}
```

**When to use payout limits:**
- User wants to withdraw funds that are RESERVED (not available for cash outs)
- Donation/fundraising projects where owner needs guaranteed access
- Payout limits reset each ruleset cycle - good for recurring distributions

**When to use surplus allowance (owner access + cash outs both available):**
- Funds should be accessible to owner BUT ALSO available for cash outs
- Surplus allowance taps into the SAME pool supporters can cash out from
- Until owner actually uses the allowance, supporters can still cash out the full balance
- One-time per ruleset (doesn't reset each cycle)

**Key difference:**
- Payout limits REDUCE cash out value (reserved funds aren't surplus)
- Surplus allowance PRESERVES cash out value until owner uses it
- **Both owner and supporters share access to surplus** - first come, first served

**When to use zero payouts + zero allowance:**
- Revnets (use surplus allowance for loans instead)
- Projects where funds should be locked for supporter redemption only

### 1. Query with Multiple Tokens

Fund access limits are keyed by (projectId, rulesetId, terminal, token). USDC-based
projects won't have results when querying with ETH token:

```typescript
const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe'

// USDC addresses per chain
const USDC_ADDRESSES: Record<number, string> = {
  1: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',    // Ethereum
  10: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',   // Optimism
  8453: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', // Base
  42161: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', // Arbitrum
}

// Try ETH first, then USDC
let limits = await fetchLimitsForToken(rulesetId, NATIVE_TOKEN)
if (!limits) {
  const usdcToken = USDC_ADDRESSES[chainId]
  if (usdcToken) {
    limits = await fetchLimitsForToken(rulesetId, usdcToken)
  }
}
```

### 2. Walk Back Ruleset Chain

If no limits found for current rulesetId, walk back through `basedOnId`:

```typescript
let currentRsId = BigInt(rulesetId)
while (attempts < maxAttempts) {
  const ruleset = await publicClient.readContract({
    address: JB_CONTRACTS.JBRulesets,
    abi: JB_RULESETS_ABI,
    functionName: 'getRulesetOf',
    args: [BigInt(projectId), currentRsId],
  })

  const basedOnId = BigInt(ruleset.basedOnId)
  if (basedOnId === 0n || basedOnId === currentRsId) break

  const limits = await fetchLimitsForRuleset(basedOnId)
  if (limits) return limits

  currentRsId = basedOnId
}
```

### 3. Detect "Unlimited" with Threshold

The protocol uses various max values (uint256, uint224, uint128, etc.). Use threshold:

```typescript
const isUnlimited = (amount: string | undefined): boolean => {
  if (!amount) return false
  try {
    // Any value > 10^30 is effectively unlimited
    return amount.length > 30 || BigInt(amount) > BigInt('1000000000000000000000000000000')
  } catch {
    return false
  }
}
```

### 4. Handle REVDeployer Version Differences

`stageOf` doesn't exist on all REVDeployer versions. Calculate current stage from timestamps:

```typescript
// Instead of calling stageOf (may not exist)
try {
  const config = await publicClient.readContract({
    address: REV_DEPLOYER,
    abi: REV_DEPLOYER_ABI,
    functionName: 'configurationOf',
    args: [BigInt(projectId)],
  })

  // Calculate current stage from timestamps
  const now = Math.floor(Date.now() / 1000)
  let currentStage = 1
  for (let i = 0; i < stageConfigs.length; i++) {
    if (Number(stageConfigs[i].startsAtOrAfter) <= now) {
      currentStage = i + 1
    }
  }
} catch {
  // configurationOf may revert on older deployments - handle gracefully
}
```

## Verification

- Surplus allowance displays "Unlimited" for Revnets instead of raw large number
- USDC-based projects show correct fund access values
- No console errors for REVDeployer function calls on older projects

## Example

For Artizen (project 6 on Base chain 8453):
- Uses USDC, not ETH - must query with USDC token address
- Surplus allowance returns `26959946667150640000000000000000000000000` which is "unlimited"
- REVDeployer configurationOf may revert - handle gracefully

## Notes

- **CRITICAL**: Empty `fundAccessLimitGroups` = ZERO payouts, not unlimited. This is the
  most common configuration mistake. Always use `uint224.max` for unlimited payouts.
- `uint224.max` = `26959946667150639794667015087019630673637144422540572481103610249215`
- USDC addresses are chain-specific (see table above)
- JBMultiTerminal5_1 address (`0x52869db3d61dde1e391967f2ce5039ad0ecd371c`) is same on all chains
- Currency field in results may be non-standard - don't rely on it for display
- For Revnets: payout limit is always 0, surplus allowance is always unlimited (for loans)
- The terminal address in `fundAccessLimitGroups` must match the terminal that will receive payments

## Contract Functions

```solidity
// JBFundAccessLimits
function payoutLimitsOf(
  uint256 projectId,
  uint256 rulesetId,
  address terminal,
  address token
) external view returns (JBCurrencyAmount[] memory);

function surplusAllowancesOf(
  uint256 projectId,
  uint256 rulesetId,
  address terminal,
  address token
) external view returns (JBCurrencyAmount[] memory);
```

## References

- JBFundAccessLimits contract
- JBMultiTerminal5_1: `0x52869db3d61dde1e391967f2ce5039ad0ecd371c`
