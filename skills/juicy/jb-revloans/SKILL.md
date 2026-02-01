---
name: jb-revloans
description: |
  REVLoans contract mechanics for Juicebox V5 revnets. Use when: (1) implementing loan
  borrow/repay/refinance flows, (2) calculating loan fees and prepaid amounts, (3) understanding
  collateral burn/remint mechanics, (4) building loan-related UIs, (5) explaining loan solvency.
  Covers borrowFrom, repayLoan, reallocateCollateralFromLoan, and liquidation mechanics.
---

# REVLoans Contract Mechanics

## Problem

Building loan functionality for revnets requires understanding the REVLoans contract's
specific mechanics: how collateral works (burn vs lock), fee structures, and the
functions for borrowing, repaying, and refinancing.

## Context / Trigger Conditions

- Implementing borrow flow in a revnet UI
- Building repay or refinance functionality
- Explaining how loan fees work to users
- Calculating prepaid fee amounts
- Understanding collateral mechanics (why tokens are burned, not locked)
- Implementing liquidation detection

## Solution

### Contract Constants

```solidity
// Liquidation timeline
uint256 constant LOAN_LIQUIDATION_DURATION = 3650 days  // 10 years

// Prepaid fee bounds (basis points)
uint256 constant MIN_PREPAID_FEE_PERCENT = 25   // 0.25% minimum (6 months)
uint256 constant MAX_PREPAID_FEE_PERCENT = 500  // 5% maximum (10 years)

// REV protocol fee on prepaid amount
uint256 constant REV_PREPAID_FEE_PERCENT = 10   // 0.1% to REV
```

### Fee Structure

When a loan is taken:

1. **Prepaid Fee** (2.5% - 50%): Paid upfront, covers interest for prepaid duration
2. **REV Fee** (0.1%): Goes to REV protocol from prepaid amount
3. **Internal Fee** (2.5%): Added back to treasury as revenue

```
Total Fee = prepaidFee + revFee
Net to Borrower = borrowAmount - prepaidFee - revFee
Treasury Impact = -borrowAmount + internalFee
```

### Key Functions

#### borrowFrom - Take a Loan

```solidity
function borrowFrom(
    uint256 projectId,
    address terminal,
    address token,
    uint256 amount,           // Amount to borrow (in base token)
    uint256 collateral,       // Tokens to lock as collateral
    address beneficiary,      // Who receives borrowed funds
    uint256 prepaidFeePercent // Fee percent (25-500 basis points)
) external returns (uint256 loanId)
```

**Collateral Mechanics:**
- Collateral tokens are **BURNED** at origination, not locked
- This is key: the loan is secured by the right to remint tokens on repayment
- Burning increases floor price for all remaining holders

#### repayLoan - Repay and Unlock Collateral

```solidity
function repayLoan(
    uint256 loanId,
    uint256 collateralToReturn, // Portion of collateral to unlock
    address beneficiary         // Who receives the unlocked tokens
) external payable
```

**Repayment Mechanics:**
- Can repay partially (return some collateral)
- Tokens are **REMINTED** to beneficiary pro rata
- Repayment amount = proportional share of original borrow

```
repaymentRequired = (collateralToReturn / totalCollateral) * borrowAmount
```

#### reallocateCollateralFromLoan - Refinance

```solidity
function reallocateCollateralFromLoan(
    uint256 loanId,
    uint256 collateralToReallocate, // Collateral to move
    uint256 minBorrowAmount,        // Min additional borrow (slippage)
    address beneficiary,            // Who receives new funds
    uint256 newPrepaidFeePercent    // New prepaid duration
) external returns (uint256 newLoanId)
```

**Refinancing Mechanics:**
- Extracts value from appreciated collateral
- Original loan collateral partially/fully moved to new loan
- "Headroom" = borrowable amount - current debt

```typescript
// Calculate headroom
const borrowableNow = revLoans.borrowableAmountFrom(projectId, collateral, ...)
const headroom = borrowableNow - originalBorrowAmount
// If headroom > 0, can refinance to extract the difference
```

#### liquidateExpiredLoansFrom - Liquidate Old Loans

```solidity
function liquidateExpiredLoansFrom(
    uint256 projectId,
    uint256[] calldata loanIds,
    address payable beneficiary
) external
```

**Liquidation Mechanics:**
- Only callable after `LOAN_LIQUIDATION_DURATION` (10 years)
- Collateral is permanently burned (already was, just can't be reclaimed)
- Original borrowed funds were already withdrawn

### Calculating Borrowable Amount

The amount borrowable for a given collateral depends on the current cash-out value:

```typescript
// On-chain: REVLoans.borrowableAmountFrom()
function borrowableAmountFrom(
    uint256 projectId,
    uint256 collateral,      // Token amount as collateral
    uint256 decimals,        // Token decimals (18 for ETH)
    uint256 currency         // 1 = ETH, 2 = USDC
) external view returns (uint256)

// The borrowable amount ≈ cash-out value of collateral
// Uses bonding curve formula internally
```

### Loan State Tracking

Each loan is an ERC-721 NFT with this state:

```solidity
struct REVLoan {
    uint256 projectId;
    uint256 collateral;       // Remaining collateral
    uint256 borrowAmount;     // Original borrow amount
    uint256 prepaidDuration;  // Seconds of prepaid time remaining
    uint256 prepaidFeePercent;
    uint256 createdAt;        // Timestamp
    address terminal;
    address token;
    string tokenUri;
}
```

### Solvency Guarantee

From the academic whitepaper:

> "The revnet remains solvent for any sequence of loans, regardless of their
> number, sizes, or whether they default."

This is because:
1. Collateral is burned at origination (reduces supply)
2. Borrow amount ≤ cash-out value of burned collateral
3. Treasury backing never drops below zero

### UI Implementation Pattern

```typescript
// BorrowDialog flow
function BorrowDialog({ projectId, userBalance }) {
  const [collateral, setCollateral] = useState(0n)

  // Get borrowable amount for selected collateral
  const { data: borrowable } = useReadContract({
    address: REVLOANS_ADDRESS,
    abi: revLoansAbi,
    functionName: 'borrowableAmountFrom',
    args: [projectId, collateral, 18, 1],
  })

  // Calculate fees
  const prepaidFeePercent = 250 // 2.5% = 6 months
  const prepaidFee = (borrowable * BigInt(prepaidFeePercent)) / 10000n
  const revFee = (prepaidFee * 10n) / 10000n // 0.1%
  const netReceived = borrowable - prepaidFee - revFee

  // Execute borrow
  const { write: borrow } = useContractWrite({
    address: REVLOANS_ADDRESS,
    abi: revLoansAbi,
    functionName: 'borrowFrom',
    args: [projectId, terminal, token, borrowable, collateral, beneficiary, prepaidFeePercent],
  })

  return (
    <Dialog>
      <CollateralInput value={collateral} max={userBalance} onChange={setCollateral} />
      <BorrowableDisplay amount={borrowable} />
      <FeeBreakdown prepaid={prepaidFee} rev={revFee} net={netReceived} />
      <Button onClick={() => borrow()}>Borrow</Button>
    </Dialog>
  )
}
```

## Verification

1. Check `loanOf(loanId)` returns correct state after borrow
2. Verify `borrowableAmountFrom` matches expected cash-out value
3. Test partial repayment correctly returns proportional collateral
4. Confirm refinance extracts correct headroom amount

## Example

Complete borrow transaction:

```typescript
import { revLoansAbi } from '@/abi/revLoans'

async function borrowFromRevnet(
  wallet: WalletClient,
  params: {
    projectId: bigint
    terminal: Address
    token: Address
    collateral: bigint
    prepaidMonths: number // 6-120 months
  }
) {
  // Calculate prepaid fee percent (25 BPS = 6 months, 500 BPS = 10 years)
  const prepaidFeePercent = Math.min(
    500,
    Math.max(25, Math.floor(params.prepaidMonths / 6 * 25))
  )

  // Get borrowable amount
  const borrowable = await revLoans.read.borrowableAmountFrom([
    params.projectId,
    params.collateral,
    18n,
    1n
  ])

  // Execute borrow
  const txHash = await wallet.writeContract({
    address: REVLOANS_ADDRESS,
    abi: revLoansAbi,
    functionName: 'borrowFrom',
    args: [
      params.projectId,
      params.terminal,
      params.token,
      borrowable,
      params.collateral,
      wallet.account.address, // beneficiary
      BigInt(prepaidFeePercent)
    ]
  })

  return txHash
}
```

## Notes

- Loans are non-custodial: no one can take your collateral except you (until liquidation)
- Collateral burn is what makes loans "self-liquidating" - they secure themselves
- The 10-year liquidation duration is extremely long - most DeFi loans liquidate quickly
- Prepaid fee scales linearly: 2.5% for 6 months, 5% for 10 years
- Interest after prepaid period: 5% annual, added to repayment amount
- Multi-chain: loans exist on specific chains, can't be moved cross-chain

## References

- [REVLoans.sol](https://github.com/rev-net/revnet-core-v5/blob/main/src/REVLoans.sol)
- [useBorrowDialog.tsx](https://github.com/rev-net/revnet-app/blob/main/src/app/[slug]/components/Value/hooks/useBorrowDialog.tsx)
- Whitepaper: "Cryptoeconomics of Revnets" - Section on Loan Solvency
