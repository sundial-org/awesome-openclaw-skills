---
name: jbx-fee-flows
description: |
  JBX ecosystem fee flows and revenue streams for investor understanding.
  Use when: (1) explaining how JBX captures ecosystem value, (2) describing protocol
  fee flows, (3) showing revenue streams to JBX holders, (4) explaining NANA and REV
  relationships, (5) explaining layered fees on revnet cash outs and loans. Covers
  V5 protocol fees, revnet external protocol fees, the NANA-REV feedback loop, and
  JBX ownership stakes across ecosystem tokens.
---

# JBX Fee Flows: How Fees Generate Value for JBX Holders

## Problem

JBX investors need to understand how fees throughout the Juicebox ecosystem flow back
to JBX token holders through the layered ownership structure of NANA and REV.

## Context / Trigger Conditions

- User asks "how does JBX make money?"
- Explaining JBX as a fund-of-funds
- Describing ecosystem fee flows
- Questions about NANA or REV relationship to JBX
- Investor due diligence on JBX value capture
- Explaining layered fees on revnet operations

## Solution

### The Protocol Stack

Understanding the fee structure requires knowing how the layers relate:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PROTOCOL STACK                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   LAYER 3: Individual Revnets                                   │
│   ─────────────────────────────                                 │
│   Any project using the Revnet framework                        │
│   (including NANA and REV themselves!)                          │
│                    │                                             │
│                    │ built on                                    │
│                    ▼                                             │
│   LAYER 2: Revnet Framework                                     │
│   ─────────────────────────                                     │
│   Adds loans, bonding curves, external protocol fees            │
│   REV collects fees from all revnet cash outs & loans           │
│   (REV is itself a Revnet!)                                     │
│                    │                                             │
│                    │ built on                                    │
│                    ▼                                             │
│   LAYER 1: Juicebox V5 Protocol                                 │
│   ─────────────────────────────                                 │
│   Base protocol for all projects                                │
│   NANA (Project #1) collects 2.5% on all outbound funds         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

KEY INSIGHT: Both NANA and REV are themselves Revnets!
This creates a powerful compounding feedback loop.
```

### Layered Fees on Revnet Operations

When a revnet performs a cash out or loan, **BOTH** fee layers apply:

```
┌─────────────────────────────────────────────────────────────────┐
│           LAYERED FEES ON REVNET CASH OUT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User cashes out $1000 from a Revnet                           │
│                    │                                             │
│                    ▼                                             │
│   ┌────────────────────────────────────────┐                    │
│   │  LAYER 2 FEE: REV External Protocol    │                    │
│   │  2.5% = $25 ──▶ Goes to REV            │                    │
│   └────────────────────────────────────────┘                    │
│                    │                                             │
│                    │ $975 remaining                              │
│                    ▼                                             │
│   ┌────────────────────────────────────────┐                    │
│   │  LAYER 1 FEE: V5 Protocol Fee (2.5%)   │                    │
│   │  ~$24 ──▶ Goes to NANA                 │                    │
│   └────────────────────────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│   User receives ~$951 (5% total)                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           LAYERED FEES ON REVNET LOAN                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User takes $1000 loan from a Revnet                           │
│                    │                                             │
│                    ▼                                             │
│   ┌────────────────────────────────────────┐                    │
│   │  INTERNAL FEE: 2.5% = $25              │                    │
│   │  (Stays in revnet treasury)            │                    │
│   └────────────────────────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│   ┌────────────────────────────────────────┐                    │
│   │  LAYER 2 FEE: REV External Protocol    │                    │
│   │  1% = $10 ──▶ Goes to REV              │                    │
│   └────────────────────────────────────────┘                    │
│                    │                                             │
│                    │ $965 remaining                              │
│                    ▼                                             │
│   ┌────────────────────────────────────────┐                    │
│   │  LAYER 1 FEE: V5 Protocol Fee (2.5%)   │                    │
│   │  ~$24 ──▶ Goes to NANA                 │                    │
│   └────────────────────────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│   User receives ~$941 (3.5% external + 2.5% internal)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The NANA-REV Feedback Loop

Both NANA and REV are themselves Revnets, creating a powerful compounding feedback loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE FEEDBACK LOOP                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐                      ┌─────────────┐          │
│   │             │   V5 fees (2.5%)     │             │          │
│   │  ALL V5     │ ─────────────────▶   │    NANA     │          │
│   │  PROJECTS   │                      │  (Revnet)   │          │
│   │             │                      │      │      │          │
│   └─────────────┘                      └──────┼──────┘          │
│                                               │      ▲          │
│                                               │      │          │
│                                               │      │ 2.5%     │
│                                               │      │ V5 fee   │
│                                               ▼      │          │
│   ┌─────────────┐                      ┌──────┴──────┐          │
│   │             │   2.5% cash outs     │             │          │
│   │  ALL        │   1% loans           │    REV      │          │
│   │  REVNETS    │ ─────────────────▶   │  (Revnet)   │          │
│   │ (inc NANA   │   (+ 2.5% NANA fee)  │             │          │
│   │  and REV!)  │                      └─────────────┘          │
│   └─────────────┘                                               │
│                                                                  │
│   REV is also a Revnet! When REV does cash outs or loans,       │
│   it pays 2.5% V5 fee back to NANA, completing the loop.        │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   NANA ──── 62% issuance ────▶ JBX                     │   │
│   │                                  ▲                      │   │
│   │   REV ───── >30% ownership ──────┘                     │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   JBX captures value from BOTH layers!                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Complete Fee Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     JBX ECOSYSTEM FEE FLOWS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │          JUICEBOX V5                │
                    │        All Projects                 │
                    │   (Payouts, Surplus Allowance,      │
                    │         Cash Outs)                  │
                    └─────────────────┬───────────────────┘
                                      │
                                      │ 2.5% Protocol Fee
                                      │ (on ALL outbound funds)
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                              NANA                                        │
    │                     (Project ID 1 - A REVNET)                           │
    │                                                                          │
    │   Receives: 2.5% of all V5 outbound funds                               │
    │                                                                          │
    │   Issuance split:  ┌───────────┬───────────────┐                        │
    │                    │    62%    │      38%      │                        │
    │                    │   ──▶     │     ──▶       │                        │
    │                    │   JBX     │   Fee Payer   │                        │
    │                    └───────────┴───────────────┘                        │
    │                                                                          │
    │   As a Revnet, NANA also pays REV fees on its own cash outs & loans!   │
    └─────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      │ REV fees when NANA
                                      │ does cash outs/loans
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                               REV                                        │
    │                      (Revnet Protocol Layer)                            │
    │                                                                          │
    │   Receives: External protocol fees from ALL revnets (including NANA)   │
    │   • 2.5% on cash outs (+ 2.5% NANA = 5% total to user)                 │
    │   • 1% on loans (+ 2.5% NANA = 3.5% total external to user)            │
    │                                                                          │
    │   NEW ISSUANCE    ┌───────────┬───────────────┐                         │
    │   (when fees      │    32%    │      68%      │                         │
    │    are paid):     │   ──▶     │     ──▶       │                         │
    │                   │ team.rev  │   Fee Payer   │                         │
    │                   │   .eth    │               │                         │
    │                   └───────────┴───────────────┘                         │
    │                                                                          │
    │   EXISTING OWNERSHIP: JBX CURRENTLY owns >30% of all REV tokens        │
    └─────────────────────────────────────────────────────────────────────────┘
```

### Revenue Stream #1: Juicebox V5 Protocol Fees

**Source:** All Juicebox V5 projects
**Fee Rate:** 2.5% on outbound funds
**Recipient:** NANA revnet (project ID 1)
**JBX Capture:** 62% of NANA token issuance

**When fees apply:**
- Payouts to non-project addresses
- Surplus allowance usage
- Cash outs (when cash out tax rate < 100%)

**Fee-exempt:**
- Project-to-project payments
- Feeless terminal addresses
- Internal transfers

**Fee calculation:**
```
feeAmount = amount × 25 / (1000 + 25)
         ≈ 2.44% of gross amount
```

### Revenue Stream #2: Revnet External Protocol Fees

**Source:** All Revnets (projects using revnet framework)
**Recipient:** REV revnet
**JBX Capture:** >30% ownership of all REV

**Fee breakdown:**

| Action | Internal Fee | REV Fee | NANA Fee (V5) | Total |
|--------|-------------|---------|---------------|-------|
| Cash out | N/A | **2.5%** | **2.5%** | 5% |
| Loan origination | 2.5% (to treasury) | **1%** | **2.5%** | 6% |
| Loan repayment | Interest (to treasury) | N/A | N/A | varies |

**How the layered fees work:**
- REV fee: 2.5% on cash outs, 1% on loans → goes to REV
- NANA fee: 2.5% V5 protocol fee on all outbound funds → goes to NANA
- These fees stack: user pays REV fee + NANA fee

**JBX and REV ownership:**
- JBX **currently** owns **>30% of existing REV supply** (from early participation)
- New REV issuance (when fees are paid): 32% → team.rev.eth, 68% → fee payer

### Revenue Stream #3: JBX Investment Holdings

JBX treasury holds tokens from ecosystem investments:
- **NANA:** 62% of issuance from V5 protocol fees
- **REV:** >30% of total supply
- **Other tokens:** Strategic ecosystem investments

This creates a "fund of funds" structure where JBX captures value from multiple layers.

---

## Revnet Fee Details (from Revnet Planner)

### Loan System Fees

1. **2.5% Upfront Internal Fee**
   - Goes to revnet treasury as revenue
   - Creates new tokens at current issuance price
   - Distributed according to stage splits

2. **1% External Protocol Fee on Loan Origination (to REV)**
   - Goes to REV (external entity)
   - Does NOT create tokens in the revnet
   - Leaves the revnet system entirely

3. **2.5% V5 Protocol Fee on Loan Disbursement (to NANA)**
   - Applied to outbound loan funds
   - Goes to NANA, 62% of issuance to JBX

4. **5% Annual Compounding Interest**
   - Begins after 6-month grace period
   - Applied to repayments
   - Goes to treasury as revenue (creates tokens)

### Cash Out System Fees

1. **2.5% External Protocol Fee on Cash Outs (to REV)**
   - Applied to the cash out amount
   - Goes to REV (external entity)
   - Does NOT create tokens in the revnet

2. **2.5% V5 Protocol Fee on Cash Out Disbursement (to NANA)**
   - Applied to outbound cash out funds
   - Goes to NANA, 62% of issuance to JBX

**Key distinction:**
- Internal fees = Revenue to revnet treasury = Token creation
- External protocol fees = Leave the system = No token creation

**Total fees paid by users:**
- Cash outs: 2.5% REV + 2.5% NANA = **5% total**
- Loans: 2.5% internal + 1% REV + 2.5% NANA = **6% total** (3.5% external)

---

## Value Flow Summary

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   ANY V5 PROJECT  ───2.5%──▶  NANA  ───62%──▶  JBX            │
│         │                       │               ▲              │
│         │                       │               │              │
│         ▼                       ▼               │              │
│   (if Revnet)     ───fees──▶  REV   ──>30%────┘              │
│                                 │                              │
│                                 │ 2.5% V5 fee                  │
│                                 │ (REV is a Revnet!)           │
│                                 └────────▶ NANA                │
│                                                                │
│   The loop: V5 → NANA → REV → NANA → ... → JBX               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

JBX captures ecosystem value through:
1. Direct ownership of NANA (62% of issuance)
2. Significant ownership of REV (>30%)
3. The feedback loop where REV activity pays back to NANA
4. Additional ecosystem token holdings

---

## Verification

- Check NANA ownership: JBX split allocation in NANA ruleset
- Check REV ownership: JBX token balance in REV project
- Fee rates: Defined in protocol contracts (JBFees, REVLoans)

## Example

Explaining the layered fees to an investor:

> "The Juicebox ecosystem has a layered fee structure that benefits JBX holders.
> At the base layer, Juicebox V5 charges 2.5% on all outbound funds - this goes
> to NANA, and JBX receives 62% of all NANA tokens minted from those fees.
>
> On top of that, the Revnet framework adds its own external protocol fees on
> cash outs and loans - these go to REV, and JBX owns over 30% of REV.
>
> Here's the key insight: NANA itself is a Revnet! So when someone cashes out
> of NANA or takes a loan against NANA tokens, both fee layers apply - REV
> gets its fee, and that payment also generates NANA issuance. This creates a
> feedback loop where ecosystem activity compounds value back to JBX at multiple
> levels."

Explaining revnet cash out fees:

> "When you cash out from any revnet, there are two fees that apply in sequence:
> first the REV external protocol fee on your cash out amount, then the V5
> protocol fee (2.5%) on what's being sent out. Both of these ultimately benefit
> JBX holders through their ownership stakes in NANA and REV."

## Notes

- Fee percentages may be subject to governance changes
- JBX ownership percentages are based on current split configurations
- External protocol fees are configurable per revnet deployment
- The 2.5% V5 protocol fee is a protocol constant (FEE = 25 out of 1000)
- Both NANA and REV are Revnets - this creates a compounding feedback loop:
  - NANA pays REV fees when NANA holders cash out or take loans
  - REV pays NANA fees (V5 protocol fee) when REV holders cash out or take loans
  - This circular flow compounds value capture for JBX at multiple levels
- The layered structure means revnet users pay BOTH V5 fees (to NANA) AND revnet fees (to REV)
