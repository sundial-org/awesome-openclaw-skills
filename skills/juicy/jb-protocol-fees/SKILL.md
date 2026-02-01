---
name: jb-protocol-fees
description: |
  Juicebox V5 and Revnet protocol fee structures and UI integration patterns.
  Use when: (1) implementing payout limits with fee calculations, (2) building cash out/redeem UIs,
  (3) building loan interfaces for revnets, (4) displaying fee breakdowns to users,
  (5) calculating net amounts after fees, (6) adding custom UI fees on top of protocol fees.
  Covers the 2.5% NANA fee, 2.5% Revnet cash out fee, 1% REV loan fee, and variable loan fees.
---

# Juicebox V5 & Revnet Protocol Fees

Complete guide to protocol fees and how UIs should handle them.

## Problem

Juicebox V5 and Revnet have multiple fee layers that UIs must correctly calculate and display:
- NANA 2.5% fee on payouts
- Revnet 2.5% fee on cash outs
- Revnet 1% + 2.5% fees on loans
- Variable loan fees over time

UIs need to show users accurate net amounts and provide transparent fee breakdowns.

## Fee Structure Overview

| Fee | Rate | Source Contract | Recipient |
|-----|------|-----------------|-----------|
| NANA payout fee | 2.5% | `JBMultiTerminal.sol:86` | Project #1 (JBX) |
| Revnet cash out fee | 2.5% | `REVDeployer.sol:95` | REV revnet |
| REV loan fee | 1% | `REVLoans.sol:89` | REV revnet |
| Source loan fee | 2.5%-50% | `REVLoans.sol:92` | Source revnet |
| Variable loan fee | 0-100% | `REVLoans.sol:377-403` | Source revnet |

---

## 1. NANA Fee (2.5%)

### Contract Definition

**File:** `nana-core-v5/src/JBMultiTerminal.sol:86`
```solidity
uint256 public constant override FEE = 25; // 2.5% (out of MAX_FEE = 1000)
```

### When Applied

- Payouts to wallet addresses (not Juicebox projects)
- Payouts to split hooks
- Surplus allowance usage
- Cash outs when `cashOutTaxRate > 0`

### When NOT Applied

- Payouts to other Juicebox projects (inter-project transfers are fee-free)
- Feeless addresses (managed by `JBFeelessAddresses` contract)
- Cash outs with 100% redemption rate (`cashOutTaxRate == 0`)

### Fee Calculation Library

**File:** `nana-core-v5/src/libraries/JBFees.sol`

```solidity
// Calculate fee from gross amount: fee = amount * 25 / 1000
function feeAmountFrom(uint256 amountBeforeFee, uint256 feePercent) internal pure returns (uint256) {
    return mulDiv(amountBeforeFee, feePercent, JBConstants.MAX_FEE);
}

// Calculate fee needed to achieve specific net amount
function feeAmountResultingIn(uint256 amountAfterFee, uint256 feePercent) internal pure returns (uint256) {
    return mulDiv(amountAfterFee, JBConstants.MAX_FEE, JBConstants.MAX_FEE - feePercent) - amountAfterFee;
}
```

### UI Implementation (juice-interface)

**File:** `juice-interface/src/packages/v4/utils/distributions.ts`

```typescript
export const JB_FEE = 0.025

// Subtract fee from gross amount
export function deriveAmountAfterFee(amount: number) {
  return amount - amount * JB_FEE  // amount * 0.975
}

// Calculate gross amount needed to achieve net
export function deriveAmountBeforeFee(amount: number) {
  return amount / (1 - JB_FEE)  // amount / 0.975
}

// Apply fee conditionally based on split type
export function derivePayoutAmount({ payoutSplit, distributionLimit, dontApplyFee }) {
  const amountBeforeFee = payoutSplit.percent.toFloat() * distributionLimit
  if (isJuiceboxProjectSplit(payoutSplit) || dontApplyFee)
    return amountBeforeFee  // No fee for project splits
  return deriveAmountAfterFee(amountBeforeFee)
}
```

### UI Display Pattern

Show fee tooltip on payout amounts:
```
Amount: 100 ETH
→ "97.5 ETH after 2.5% JBX membership fee"
```

Tooltip explanation:
> "Payouts to Ethereum addresses incur a 2.5% fee. Your project will receive JBX in return."

---

## 2. Revnet Cash Out Fee (2.5%)

### Contract Definition

**File:** `revnet-core-v5/src/REVDeployer.sol:95`
```solidity
uint256 public constant override FEE = 25; // 2.5%
```

### How It Works

1. User initiates cash out of X tokens
2. 2.5% of tokens (X * 0.025) are redirected to pay the REV revnet
3. User receives REV tokens in return for the fee portion
4. Remaining 97.5% of tokens are cashed out for the underlying asset

### Exemptions

- **Suckers** (cross-chain bridge contracts) do NOT pay cash out fees
- Check at `REVDeployer.sol:282-283`

### UI Implementation (revnet-app)

**File:** `revnet-app/src/lib/feeHelpers.ts`

```typescript
import { REVNET_CASHOUT_FEE_PERCENT } from "@/app/constants"; // 0.025

export function applyRevFee(tokenAmount: bigint) {
  return (tokenAmount * BigInt((1 - REVNET_CASHOUT_FEE_PERCENT) * 1000)) / 1000n;
}

export function applyNanaFee(reclaimableAmount: bigint) {
  return (reclaimableAmount * BigInt((1 - JBDAO_CASHOUT_FEE_PERCENT) * 1000)) / 1000n;
}
```

### Layered Fee Application

For cash outs, apply BOTH fees:
```typescript
// In reclaimableSurplus.ts
const afterRevFee = applyRevFee(tokenAmountWei)    // 2.5% Revnet fee
const afterAllFees = applyNanaFee(afterRevFee)     // 2.5% NANA fee on remainder
```

### UI Display Pattern

Show net amount directly:
```
Cash out: 1000 tokens
→ "You'll get ~X ETH"
```

The displayed amount should have both fees pre-applied.

---

## 3. Revnet Loan Fees

### Contract Definitions

**File:** `revnet-core-v5/src/REVLoans.sol:83-92`

```solidity
uint256 public constant override LOAN_LIQUIDATION_DURATION = 3650 days;  // 10 years
uint256 public constant override MAX_PREPAID_FEE_PERCENT = 500;          // 50% max
uint256 public constant override REV_PREPAID_FEE_PERCENT = 10;           // 1% REV fee
uint256 public constant override MIN_PREPAID_FEE_PERCENT = 25;           // 2.5% min source fee
```

### Fee Components

| Fee | Rate | When Charged | Recipient |
|-----|------|--------------|-----------|
| REV fee | 1% | At borrow time | REV revnet |
| Source fee | 2.5%-50% | At borrow time (prepaid) | Source revnet |
| Variable fee | 0-100% | After prepaid period expires | Source revnet |

### Prepaid Fee Mechanics

- User chooses prepaid percentage (2.5% to 50%)
- Higher prepaid = longer fee-free period
- Prepaid period = `(prepaidPercent / 50%) * 10 years`

Examples:
- 2.5% prepaid → 6 months fee-free
- 25% prepaid → 5 years fee-free
- 50% prepaid → 10 years fee-free (no variable fees ever)

### Variable Fee Calculation

**File:** `revnet-core-v5/src/REVLoans.sol:377-403`

After prepaid period expires:
```
variableFee = (elapsedAfterPrepaid / remainingTime) * amountAfterFixedFees
```

The fee increases linearly from 0% to 100% over the remaining time until 10 years.

### UI Implementation (revnet-app)

**File:** `revnet-app/src/lib/feeHelpers.ts`

```typescript
export function generateFeeData({
  grossBorrowedEth,
  prepaidPercent,
  fixedLoanFee = 0.035,  // 3.5% = 1% REV + 2.5% source
}: {
  grossBorrowedEth: number;
  prepaidPercent: string;
  fixedLoanFee?: number;
}) {
  const MAX_YEARS = 10;
  const monthsToPrepay = (parseFloat(prepaidPercent) / 50) * 120;
  const prepaidDuration = monthsToPrepay / 12;

  // Fixed fees come off immediately
  const fixedFee = grossBorrowedEth * fixedLoanFee;

  // Prepaid fee calculation
  const feeBpsBigInt = calcPrepaidFee(Math.round(monthsToPrepay));
  const prepaidFee = (grossBorrowedEth * Number(feeBpsBigInt)) / 10000;

  // Amount user actually receives
  const amountUserReceives = grossBorrowedEth - fixedFee - prepaidFee;

  // Generate fee curve data points
  const data = [];
  for (let year = 0; year <= MAX_YEARS; year += 0.25) {
    let variableFee = 0;
    if (year > prepaidDuration) {
      const elapsedAfterPrepaid = year - prepaidDuration;
      const remainingTime = MAX_YEARS - prepaidDuration;
      variableFee = amountUserReceives * (elapsedAfterPrepaid / remainingTime);
    }
    const totalCostToUnlock = grossBorrowedEth + variableFee;
    data.push({ year, totalCost: totalCostToUnlock });
  }
  return data;
}
```

### UI Display Pattern

**SimulatedLoanCard** shows inline breakdown:
```
Amount borrowed: 1.0 ETH
To beneficiary after fees: 0.945 ETH

[Tooltip]
- Collateral used: 1000 REVNET
- Protocol & project fees: 0.055 ETH (5.5%)
- Max cost to unlock before 10 years: 1.945 ETH
```

**LoanFeeChart** visualizes the fee curve:
- X-axis: Years (0-10)
- Y-axis: Total cost to unlock collateral
- Slider: Prepaid percentage (2.5%-50%)

---

## 4. Adding Custom UI Fees

UIs are welcome to add fees on top of protocol fees. Pattern:

```typescript
const UI_FEE = 0.005 // 0.5% UI operator fee

function applyAllFees(amount: bigint, includeUIFee = true) {
  // Apply protocol fees first
  let result = applyNanaFee(amount)  // 2.5%

  // Optionally apply UI fee
  if (includeUIFee) {
    result = result - (result * BigInt(UI_FEE * 10000)) / 10000n
  }

  return result
}
```

**Best practices:**
1. Be transparent - show users the full breakdown
2. Apply UI fee after protocol fees (on the remainder)
3. Route UI fee to your operator address
4. Display separately: "Protocol fee: 2.5% | Platform fee: 0.5%"

---

## 5. Fee Display Best Practices

### Payout Tables (juice-interface pattern)

```
Sub-total:           100.00 ETH
Owner remainder:      10.00 ETH
Fees (2.5%):           2.75 ETH
─────────────────────────────
Total:               112.75 ETH
```

### Cash Out Preview

```
Cashing out: 1,000 tokens
You'll receive: ~0.95 ETH
  └─ After 2.5% Revnet fee + 2.5% JBX fee
```

### Loan Summary

```
Borrowing: 1.0 ETH
You'll receive: 0.945 ETH
Fees paid now:
  - REV fee (1%): 0.01 ETH
  - Prepaid fee (4.5%): 0.045 ETH
To unlock collateral: 1.0 ETH (+ variable fees after 1 year)
```

---

## Key Source Files

### Contracts
| File | Purpose |
|------|---------|
| `nana-core-v5/src/JBMultiTerminal.sol` | NANA fee logic (lines 86, 555, 587, 1129, 2028) |
| `nana-core-v5/src/libraries/JBFees.sol` | Fee calculation library |
| `nana-core-v5/src/JBFeelessAddresses.sol` | Feeless address management |
| `revnet-core-v5/src/REVDeployer.sol` | Cash out fee (lines 95, 270-333, 567-624) |
| `revnet-core-v5/src/REVLoans.sol` | Loan fees (lines 83-92, 377-403, 821-851) |

### UI Implementations
| File | Purpose |
|------|---------|
| `juice-interface/src/packages/v4/utils/distributions.ts` | Payout fee calculations |
| `juice-interface/src/packages/v4/components/FeeTooltipLabel.tsx` | Fee display component |
| `revnet-app/src/lib/feeHelpers.ts` | Revnet fee helpers |
| `revnet-app/src/app/[slug]/components/Value/SimulatedLoanCard.tsx` | Loan fee display |
| `revnet-app/src/app/[slug]/components/Value/LoanFeeChart.tsx` | Fee curve visualization |

---

## Common Mistakes to Avoid

1. **Forgetting project splits are fee-free**: Always check `isJuiceboxProjectSplit()` before applying fees
2. **Double-applying fees**: Protocol fees are applied on-chain; UI should only display, not re-apply
3. **Ignoring the NANA fee on cash outs**: Cash outs have BOTH Revnet (2.5%) and NANA (2.5%) fees
4. **Showing gross instead of net**: Users care about what they receive, not what they send
5. **Missing the variable loan fee**: Loan costs increase over time after prepaid period

## Verification

To verify fee calculations match on-chain behavior:
1. Compare UI-calculated amounts with actual transaction results
2. Test with feeless addresses to confirm exemptions work
3. Verify loan fee curves match contract's `_determineSourceFeeAmount()` logic
