---
name: revnet-modeler
description: |
  Revnet simulation and planning tool for modeling token dynamics. Use when: (1) planning
  revnet parameters before deployment, (2) visualizing treasury/token dynamics over time,
  (3) comparing different scenarios (loans, cash-outs, investments), (4) understanding
  chart outputs, (5) explaining simulation results. Covers stage configuration, event
  sequences, and all chart types.
---

# Revnet Modeler: Simulation Tool

## Problem

Planning revnet parameters requires understanding how different configurations affect
treasury dynamics, token distribution, and participant outcomes over time. The modeler
simulates these dynamics before deployment.

## Context / Trigger Conditions

- Planning a new revnet deployment
- Comparing different parameter configurations
- Understanding how events (investments, loans, cash-outs) affect the system
- Visualizing treasury and token dynamics
- Explaining chart outputs to users

## Solution

### Tool Location

```
https://github.com/mejango/rev-sim/index.html
```

Open in browser to use the interactive modeler.

### Seven Economic Levers (Per Stage)

Each stage can configure:

| Lever | Description | Effect |
|-------|-------------|--------|
| **Stage Start Day** | When this stage begins | Defines stage transitions |
| **Initial Issuance Rate** | Tokens minted per $ | Higher = more tokens per payment |
| **Issuance Cut %** | % reduction per period | Creates supply scarcity over time |
| **Issuance Cut Frequency** | Days between cuts | Controls cut rate (7, 14, 28 days) |
| **Split %** | % of minted tokens to splits | Team/reserved allocation |
| **Cash-Out Tax Rate** | Bonding curve tax (0-100%) | Higher = more treasury retention |
| **Auto-Issuances** | Automatic token mints | Pre-scheduled distributions |

### Event Types

The modeler supports these event types:

| Event | Description | Treasury Effect |
|-------|-------------|-----------------|
| `investment` | External payment | + backing, + supply |
| `revenue` | Operating revenue | + backing, + supply |
| `loan` | Take loan against tokens | - backing (net of fees) |
| `payback-loan` | Repay loan | + backing |
| `cashout` | Redeem tokens | - backing, - supply |

Events are labeled by participant (e.g., "Team", "Investor A", "Customer").

### Available Charts

#### Treasury & Value Charts

| Chart | Shows | Key Insight |
|-------|-------|-------------|
| **Treasury Backing** | Total backing over time | Overall treasury health |
| **Cash Out Value** | Per-token redemption value | Floor price dynamics |
| **Issuance Price** | Token mint cost | Ceiling price with cuts |
| **Cash Flows** | Inflows/outflows by day | Event impact on treasury |

#### Token Charts

| Chart | Shows | Key Insight |
|-------|-------|-------------|
| **Token Distribution** | Tokens by holder (liquid + locked) | Who holds what |
| **Ownership %** | Percentage ownership over time | Dilution visualization |
| **Token Valuations** | Dollar value of holdings | Participant wealth |
| **Token Performance** | ROI % by participant | Investment returns |

#### Loan Charts

| Chart | Shows | Key Insight |
|-------|-------|-------------|
| **Loan Potential** | Max borrowable by holder | Available liquidity |
| **Loan Status** | Outstanding loan amounts | Current debt |
| **Outstanding Loans** | Loan values over time | Debt trajectory |
| **Tokens Backing Loans %** | % of tokens as collateral | Leverage exposure |

#### Fee Charts

| Chart | Shows | Key Insight |
|-------|-------|-------------|
| **Fee Flows** | Internal vs external fees | Fee destination breakdown |

### State Machine Calculations

The modeler uses a state machine (`StateMachine.getStateAtDay(day)`) that tracks:

```javascript
{
  day: number,
  revnetBacking: number,      // Treasury balance
  totalSupply: number,        // Total token supply
  tokensByLabel: {            // Tokens held by each participant
    "Team": 1000,
    "Investor A": 500,
    ...
  },
  dayLabeledInvestorLoans: {  // Outstanding loan amounts by participant
    "Team": 50000,
    ...
  },
  loanHistory: {              // Detailed loan records
    "Team": [
      { amount: 50000, remainingTokens: 100, ... }
    ]
  }
}
```

### Key Formulas

#### Cash-Out Value (Bonding Curve)

```javascript
calculateCashOutValueForEvent(tokensToCash, totalSupply, backing, cashOutTax) {
  const proportionalShare = backing * tokensToCash / totalSupply
  const taxMultiplier = (1 - cashOutTax) + (tokensToCash * cashOutTax / totalSupply)
  return proportionalShare * taxMultiplier
}
```

#### Loan Fees

```javascript
// Internal fee (to treasury)
const internalFee = loanAmount * 0.025  // 2.5%

// External fee (to protocol)
const externalFee = loanAmount * 0.035  // 3.5%

// Interest (after grace period)
const annualInterest = 0.05  // 5% after 6-month grace period
```

### Pre-Built Scenarios

The modeler includes pre-configured scenarios:

| Scenario | Description |
|----------|-------------|
| `conservative-growth` | Steady investment, gradual expansion |
| `hypergrowth` | Rapid investment, high volatility |
| `bootstrap-scale` | Small start, then scale-up |
| `vc-fueled` | Large early investment, then revenue |
| `community-driven` | Many small investments |
| `boom-bust` | Growth followed by cash-outs |

Each has variants: `-with-loans`, `-with-exits`

### Interpreting Results

#### Treasury Health
- **Healthy:** Backing grows over time, floor price increases
- **Warning:** Backing flat or declining, many cash-outs
- **Critical:** Large loan defaults, negative treasury trajectory

#### Token Distribution
- **Balanced:** No single holder > 50%
- **Concentrated:** Few holders control majority
- **Diluted:** Early holders significantly diluted

#### Loan Exposure
- **Safe:** < 20% of tokens backing loans
- **Moderate:** 20-50% collateralized
- **High:** > 50% collateralized (systemic risk)

### Using for Planning

1. **Set stages** matching your fundraising/growth plan
2. **Add events** representing expected investments, revenue, exits
3. **Run simulation** and review charts
4. **Iterate** on parameters until dynamics match goals
5. **Compare** multiple scenarios to stress-test

## Verification

1. Verify cash-out calculations match bonding curve formula
2. Check loan fees sum to expected percentages
3. Confirm token distribution adds to total supply
4. Validate treasury balance equals sum of inflows - outflows

## Example

Planning a revnet with team allocation and investor entry:

```
Stage 1 (Days 0-90):
  - Issuance: 1,000,000 tokens/$
  - Split: 30% to Team
  - Cash-out tax: 10%

Events:
  Day 1: Team invests $10,000
  Day 30: Investor A invests $50,000
  Day 60: Revenue $20,000
  Day 90: Team takes loan (50% of tokens)

Run simulation → Review:
  - Token Distribution: Team 30%, Investor A 50%, Revenue recipients 20%
  - Team's loan potential and actual loan
  - Treasury backing trajectory
  - Cash-out value for each participant
```

## Notes

- Modeler uses simplified fee model (may differ from exact contract implementation)
- Simulations are deterministic given same inputs
- Charts update automatically when parameters change
- Export scenarios for comparison and documentation
- The modeler runs entirely client-side (no data sent externally)

## References

- Tool: `https://github.com/mejango/rev-sim/index.html`
- State machine: `https://github.com/mejango/rev-sim/js/state.js`
- Charts: `https://github.com/mejango/rev-sim/js/chartManager.js`
- Academic validation: `/revnet-economics` skill
