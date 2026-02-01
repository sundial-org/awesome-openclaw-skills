---
name: revnet-economics
description: |
  Academic findings and economic thresholds for revnets from CryptoEconLab research.
  Use when: (1) explaining cash-out vs loan decision thresholds, (2) discussing loan
  solvency guarantees, (3) recommending revnet archetypes, (4) explaining price corridor
  dynamics, (5) citing academic sources for revnet mechanics. Includes bonding curve
  proofs, rational actor analysis, and the three revnet archetypes.
---

# Revnet Economics: Academic Findings

## Problem

Explaining revnet mechanics to sophisticated users requires citing academic sources and
understanding the mathematical foundations: why loans are always solvent, when rational
actors should choose loans vs cash-outs, and which revnet configurations suit different
use cases.

## Context / Trigger Conditions

- User asks "why are revnet loans safe?"
- Explaining when to take a loan vs cash out
- Recommending revnet configurations for specific use cases
- Discussing price floor/ceiling dynamics
- Citing academic research on revnet economics

## Solution

### Source Papers

All findings from CryptoEconLab (cryptoeconlab.com):

1. **"Cryptoeconomics of Revnets"** (34 pages) - Main whitepaper
2. **"Revnet Value Flows as a Continuous-Time Dynamical System"** (6 pages) - ODE formalization
3. **"Revnet Parameters Analysis"** (15 pages) - Archetype recommendations

---

### Bonding Curve Formula

The redemption (cash-out) curve is NOT linear. It's a convex bonding curve:

```
C_k(q; S, B) = (q/S) × B × [(1 - r_k) + r_k × (q/S)]
```

Where:
- `q` = tokens being cashed out
- `S` = total supply
- `B` = treasury backing (surplus)
- `r_k` = cash-out tax rate (0 to 1)

**Key insight:** Cashing out a larger fraction of supply returns proportionally less per token.

```
Example: r_k = 0.5 (50% tax)
- Cash out 1% of supply → get 0.505% of treasury (per-token: 50.5%)
- Cash out 50% of supply → get 37.5% of treasury (per-token: 75%)
- Cash out 100% of supply → get 50% of treasury (per-token: 50%)
```

---

### Price Corridor

Revnet tokens trade within a bounded price corridor:

```
P_floor ≤ P_AMM ≤ P_ceil
```

**Floor Price (P_floor):** Cash-out value per token
- Enforced by arbitrage: if AMM price < floor, buy from AMM → cash out for profit
- Increases monotonically as treasury grows and supply decreases

**Ceiling Price (P_ceil):** Issuance price (mint cost)
- Enforced by arbitrage: if AMM price > ceiling, pay revnet → sell tokens on AMM
- Increases over time via issuance cuts

> "These arbitrage mechanisms establish a self-enforcing price corridor that persists
> regardless of market conditions." - Cryptoeconomics of Revnets

---

### Loan Solvency Guarantee

**Theorem:** The revnet remains solvent for any sequence of loans, regardless of their
number, sizes, or whether they default.

**Proof sketch:**
1. Loan amount L ≤ cash-out value of collateral C
2. Collateral is burned at origination (reduces supply S)
3. Burning C tokens increases floor price for remaining holders
4. If loan defaults: treasury keeps L, collateral already burned
5. If loan repaid: treasury receives L back, collateral reminted

> "Since collateral tokens are burned upon loan origination, the effective supply decreases,
> which mechanically increases the floor price for all remaining token holders."

---

### Rational Actor Thresholds

#### Cash-Out vs Loan Decision

A rational actor should take a **loan instead of cashing out** when the cash-out tax
rate exceeds approximately **39.16%**.

```
r_k ≈ 0.3916 is the crossover point
```

- If `r_k < 39.16%`: Cash out is more efficient (lower tax)
- If `r_k ≥ 39.16%`: Loan is more efficient (avoid tax, keep upside)

**Mathematical basis:** At high tax rates, the bonding curve penalty on cash-outs exceeds
the loan fees. Loans preserve upside exposure while providing liquidity.

#### Loan vs Hold Decision

A rational actor should take a **loan instead of holding** when expected returns exceed
the fee cost:

```
R > (1 - a) / a
```

Where:
- `R` = expected return on borrowed capital
- `a` = loan-to-value ratio (typically 80-90%)

If you can deploy borrowed capital at returns exceeding this threshold, borrowing is rational.

---

### Three Revnet Archetypes

The papers identify three canonical configurations:

#### 1. Token Launchpad (Speculative)

**Characteristics:**
- High initial issuance rate
- Steep issuance cuts (5-10% per period)
- Low/no cash-out tax initially
- Time-limited reserved allocation

**Use case:** New token launches seeking price appreciation through supply scarcity.

**Example params:**
```
initialIssuance: 1_000_000 tokens/$
issuanceCutPercent: 10%
issuanceCutFrequency: 7 days
cashOutTaxRate: 0%
splitPercent: 20% (to team, decreasing)
```

#### 2. Stable-Commerce (Loyalty/Stablecoin)

**Characteristics:**
- Moderate, stable issuance rate
- Minimal or no issuance cuts
- High cash-out tax (70-90%)
- Focus on utility over speculation

**Use case:** Loyalty programs, stablecoins, commerce applications where price stability matters.

**Example params:**
```
initialIssuance: 100 tokens/$
issuanceCutPercent: 0%
cashOutTaxRate: 80%
splitPercent: 10% (to treasury operations)
```

#### 3. Periodic Fundraising

**Characteristics:**
- Multiple stages with different parameters
- Stage transitions at specific dates
- Varying split percentages per round
- Often mirrors traditional funding rounds

**Use case:** Projects wanting structured fundraising rounds (seed, series A, etc.)

**Example params:**
```
Stage 1 (Seed):
  duration: 90 days
  issuance: 500_000 tokens/$
  splitPercent: 30%

Stage 2 (Series A):
  duration: 180 days
  issuance: 250_000 tokens/$
  splitPercent: 20%

Stage 3 (Public):
  duration: unlimited
  issuance: 100_000 tokens/$
  issuanceCutPercent: 5%
  splitPercent: 10%
```

---

### Fee Structure Economic Impact

From the whitepaper analysis:

| Fee Type | Rate | Recipient | Economic Effect |
|----------|------|-----------|-----------------|
| NANA Network | 2.5% | NANA project | Protocol sustainability |
| REV | 1% | REV project | Cross-network value |
| Prepaid Interest | 2.5-50% | Treasury | Loan time-value compensation |
| Liquidation | N/A | Protocol | Bad debt prevention |

> "The fee structure is designed to align incentives: internal fees return value to the
> revnet, while external fees support the broader infrastructure."

---

### Dynamical System Behavior

The floor price follows an ODE:

```
dP_floor/dt = f(inflows, outflows, supply_changes)
```

**Key properties:**
- Floor price is monotonically non-decreasing if no cash-outs occur
- Each payment increases floor (adds backing, may add supply)
- Each cash-out can decrease floor (removes backing and supply)
- Loan defaults increase floor (backing kept, supply reduced)

---

## Verification

Test thresholds with modeler:
1. Set cash-out tax to 39% → verify loan vs cash-out break-even
2. Model loan defaults → verify floor price increases
3. Compare archetype configurations → verify expected dynamics

## Example

Citing findings in user explanation:

> "Based on the CryptoEconLab research, with your current 50% cash-out tax rate,
> taking a loan is more economically efficient than cashing out. The crossover
> point is approximately 39% - above that, loans preserve your upside exposure
> while still providing liquidity."

> "Revnet loans are mathematically proven to be solvent regardless of defaults.
> When you take a loan, your collateral is burned (not locked), which actually
> increases the floor price for all remaining holders. If you default, the
> treasury keeps your borrowed funds and the burned tokens stay burned."

## Notes

- The 39.16% threshold assumes standard fee parameters
- Archetype recommendations are guidelines, not requirements
- Price corridor bounds are theoretical; AMM liquidity affects practical trading
- Loan solvency proof assumes honest price oracle for collateral valuation

## References

- "Cryptoeconomics of Revnets" - CryptoEconLab (2024)
- "Revnet Value Flows as a Continuous-Time Dynamical System" - CryptoEconLab (2024)
- "Revnet Parameters Analysis" - CryptoEconLab (2024)
- Available at: cryptoeconlab.com/paper/pub-0
