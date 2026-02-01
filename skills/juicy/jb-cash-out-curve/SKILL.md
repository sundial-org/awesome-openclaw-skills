---
name: jb-cash-out-curve
description: |
  Juicebox V5 cash out redemption calculations using the bonding curve formula.
  Use when: (1) displaying cash out values in UI, (2) explaining redemption amounts
  to users, (3) calculating what percentage of treasury a cash out returns.
  The simple "X% of proportional share" is WRONG - must use bonding curve formula.
---

# Juicebox V5 Cash Out Bonding Curve

## Problem

When displaying cash out / redemption values in Juicebox V5 UIs, it's tempting to show
a simple message like "Cashing out returns 90% of proportional treasury share" (for a
10% tax rate). This is **incorrect** and misleading to users.

The actual redemption amount depends on a bonding curve formula where the percentage
of supply being cashed out affects the return.

## Context / Trigger Conditions

- Building UI that shows cash out / redemption values
- Explaining to users what they'll receive when cashing out
- Any display of `cashOutTaxRate` impact on redemptions
- When you see code like `retainedPercent = 100 - cashOutTax` - this is WRONG

## Solution

### The Bonding Curve Formula

```
reclaimAmount = (x * s / y) * ((1 - r) + (r * x / y))
```

Where:
- `x` = number of tokens being cashed out
- `s` = surplus (treasury overflow available for redemption)
- `y` = total token supply
- `r` = cash out tax rate as decimal (0 to 1, where 0.1 = 10%)

### Normalized Form

When working with fractions (what % of supply is being cashed out):

```
Let f = x/y (fraction of supply being cashed out)
reclaimFraction = f * ((1 - r) + (r * f))
```

Where `reclaimFraction` is the fraction of surplus received.

### Key Insight

The return depends on HOW MUCH of the supply is being cashed out, not just the tax rate.
Cashing out a larger percentage of supply returns proportionally less per token.

### Example Calculation

With 10% cash out tax rate (`r = 0.1`), cashing out 10% of supply (`f = 0.1`):

```javascript
reclaimFraction = 0.1 * ((1 - 0.1) + (0.1 * 0.1))
reclaimFraction = 0.1 * (0.9 + 0.01)
reclaimFraction = 0.1 * 0.91
reclaimFraction = 0.091  // 9.1% of surplus
```

So cashing out 10% of the supply gets ~9.1% of the surplus (not 9% as simple math would suggest).

### Code Implementation

```typescript
// WRONG - Don't do this:
const retainedPercent = 100 - (cashOutTaxRate / 100)
message = `Cashing out returns ${retainedPercent}% of proportional treasury share`

// CORRECT - Use bonding curve:
function calculateCashOutReturn(
  tokensToRedeem: number,
  totalSupply: number,
  surplus: number,
  cashOutTaxRate: number // 0-10000 basis points
): number {
  const r = cashOutTaxRate / 10000  // Convert basis points to 0-1
  const x = tokensToRedeem
  const y = totalSupply
  const s = surplus

  // Bonding curve formula
  return (x * s / y) * ((1 - r) + (r * x / y))
}

// For UI display with example percentage:
const r = cashOutTaxRate / 10000
const exampleFraction = 0.1  // 10% of supply
const returnFraction = exampleFraction * ((1 - r) + (r * exampleFraction))
const returnPercent = (returnFraction * 100).toFixed(1)
message = `Cashing out 10% of ${tokenSymbol} gets ~${returnPercent}% of treasury`
```

## Verification

Test with known values:
- `r = 0` (no tax): `reclaimFraction = f` (linear, full proportional return)
- `r = 1` (100% tax): `reclaimFraction = f * f` (quadratic, harsh penalty)
- `r = 0.1, f = 0.1`: `reclaimFraction = 0.091` (9.1%)
- `r = 0.1, f = 0.5`: `reclaimFraction = 0.5 * (0.9 + 0.05) = 0.475` (47.5%)

## Example

In the RulesetSchedule component's Juicy Summary:

```typescript
// Cash out - redemption value using bonding curve formula
const cashOutTaxRate = ruleset.cashOutTaxRate / 10000
if (cashOutTaxRate >= 1) {
  actionItems.push({ action: 'caution', message: 'Cash outs disabled' })
} else if (cashOutTaxRate > 0) {
  const x = 0.1 // 10% of supply
  const y = x * ((1 - cashOutTaxRate) + (cashOutTaxRate * x))
  const returnPercent = (y * 100).toFixed(1)
  actionItems.push({
    action: 'cash-out',
    message: `Cashing out 10% of ${tokenSymbol} gets ~${returnPercent}% of treasury`,
  })
}
```

## Notes

- The `cashOutTaxRate` in Juicebox V5 is stored in basis points (0-10000)
- A rate of 10000 (100%) means cash outs are effectively disabled
- The formula assumes the treasury "overflow" is the redeemable amount
- This bonding curve incentivizes holding - early/small cash outs get better rates
- The CashOutCurve visualization component can show this graphically

## References

- Juicebox V5 JBRulesets contract
- Cash out bonding curve formula: `y = (o * x / s) * ((1 - r) + (r * x / s))`
  - Normalized to: `y = x * ((1 - r) + (r * x))` where x is fraction of supply
