---
name: jb-loan-queries
description: |
  Query REVLoans data via Bendystraw GraphQL. Use when: (1) displaying a user's loans
  across all revnets, (2) showing all loans for a specific revnet/project, (3) checking
  borrow permissions, (4) building loan management UIs. Covers LoansByAccount query,
  permission checking, and multi-chain loan aggregation.
---

# Querying REVLoans via Bendystraw

## Problem

Displaying loan data in revnet UIs requires querying Bendystraw's GraphQL API with the correct
queries and understanding how to filter/aggregate loans across chains and projects.

## Context / Trigger Conditions

- Building UI to show a user's outstanding loans
- Displaying all loans for a specific revnet
- Checking if a user has permission to borrow
- Calculating loan headroom (refinanceable amount)
- Multi-chain loan aggregation

## Solution

### GraphQL Queries

#### Get All Loans for a User

```graphql
query LoansByAccount($owner: String!, $version: Int!) {
  loans(where: { owner: $owner, version: $version }) {
    items {
      borrowAmount
      collateral
      prepaidDuration
      projectId
      terminal
      token
      chainId
      createdAt
      id
      project {
        version
      }
    }
  }
}
```

**Variables:**
- `owner`: User's wallet address (lowercase)
- `version`: Protocol version (5 for V5)

#### Get Loans for Specific Project

```graphql
query LoansDetailsByAccount($owner: String!, $projectId: Int!, $version: Int!) {
  loans(where: { owner: $owner, projectId: $projectId, version: $version }) {
    items {
      borrowAmount
      collateral
      prepaidDuration
      createdAt
      projectId
      terminal
      token
      chainId
      id
      project {
        version
      }
    }
  }
}
```

#### Check Borrow Permission

```graphql
query HasPermission(
  $account: String!
  $chainId: Float!
  $projectId: Float!
  $operator: String!
  $version: Float!
) {
  permissionHolder(
    account: $account
    chainId: $chainId
    projectId: $projectId
    operator: $operator
    version: $version
  ) {
    permissions
  }
}
```

**Permission ID 1 = Borrow permission.** Check if `permissions` array includes `1`.

### Loan Entity Fields

```typescript
type Loan = {
  id: BigInt                 // Unique loan ID
  owner: String              // Borrower address
  beneficiary: String        // Recipient of borrowed funds
  borrowAmount: BigInt       // Amount borrowed (in base token wei)
  collateral: BigInt         // Tokens locked as collateral
  prepaidDuration: Int       // Seconds of prepaid fee time
  prepaidFeePercent: Int     // Basis points of prepaid fee
  projectId: Int             // Revnet project ID
  chainId: Int               // Chain where loan exists
  terminal: String           // Terminal address
  token: String              // Base token address (ETH = 0x0...0)
  createdAt: Int             // Unix timestamp
  sourceFeeAmount: BigInt    // Total fees charged
  tokenUri: String | null    // NFT metadata URI (loans are ERC-721)
  version: Int               // Protocol version
}
```

### React Hook Usage (revnet-app pattern)

```typescript
import { useBendystrawQuery } from 'juice-sdk-react'
import { LoansByAccountDocument } from '@/generated/graphql'

const LOAN_POLL_INTERVAL = 3000 // 3 seconds

function useUserLoans(address: string, version: number = 5) {
  const { data, loading, error } = useBendystrawQuery(
    LoansByAccountDocument,
    { owner: address.toLowerCase(), version },
    { pollInterval: LOAN_POLL_INTERVAL }
  )

  return {
    loans: data?.loans.items ?? [],
    loading,
    error
  }
}
```

### Filter Loans by Revnet

When showing loans for a specific revnet (which may span multiple chains):

```typescript
function filterLoansByRevnet(
  loans: Loan[],
  revnetProjectIds: number[]  // projectIds across all chains
): Loan[] {
  return loans.filter(loan =>
    revnetProjectIds.includes(Number(loan.projectId))
  )
}

// Usage: Get projectIds from suckerGroup
const { data: projectData } = useBendystrawQuery(ProjectDocument, { ... })
const revnetProjectIds = projectData.project.suckerGroup?.projects_rel
  .map(p => Number(p.projectId)) ?? [Number(projectData.project.projectId)]

const filteredLoans = filterLoansByRevnet(loans, revnetProjectIds)
```

### Calculate Loan Headroom (Refinanceable Amount)

Use contract call to get borrowable amount for existing collateral:

```typescript
import { useReadContract } from 'wagmi'
import { revLoansAbi } from '@/abi/revLoans'

function useLoanHeadroom(loan: Loan) {
  const { data: borrowableAmount } = useReadContract({
    address: REVLOANS_ADDRESS,
    abi: revLoansAbi,
    functionName: 'borrowableAmountFrom',
    args: [
      BigInt(loan.projectId),
      BigInt(loan.collateral),
      18, // decimals
      1,  // currency (ETH)
    ],
  })

  // Headroom = what you could borrow - what you already borrowed
  const headroom = borrowableAmount
    ? borrowableAmount - BigInt(loan.borrowAmount)
    : 0n

  return headroom
}
```

### Multi-Chain Token Resolution

Loans may use different tokens on different chains. Get token config from suckerGroup:

```graphql
query GetSuckerGroup($id: String!) {
  suckerGroup(id: $id) {
    projects_rel {
      projectId
      chainId
      decimals    # 18 for ETH, 6 for USDC
      currency    # 1 for ETH, 2 for USDC
    }
  }
}
```

```typescript
function getTokenConfigForLoan(loan: Loan, suckerGroup: SuckerGroup) {
  const project = suckerGroup.projects_rel.find(
    p => p.chainId === loan.chainId && p.projectId === loan.projectId
  )
  return {
    decimals: project?.decimals ?? 18,
    currency: project?.currency ?? 1,
  }
}
```

## Verification

Test with known loan data:
1. Query loans for an address known to have loans
2. Verify `borrowAmount` matches on-chain `REVLoans.loanOf()`
3. Check that `prepaidDuration` decreases over time (fee time consumed)

## Example

Complete component for displaying user loans:

```typescript
function UserLoansTable({ address, revnetProjectIds }) {
  const { loans, loading } = useUserLoans(address)

  // Filter to this revnet only
  const revnetLoans = filterLoansByRevnet(loans, revnetProjectIds)

  if (loading) return <Spinner />
  if (revnetLoans.length === 0) return <EmptyState />

  return (
    <Table>
      <thead>
        <tr>
          <th>Chain</th>
          <th>Borrowed</th>
          <th>Collateral</th>
          <th>Fee Time</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {revnetLoans.map(loan => (
          <LoanRow key={loan.id} loan={loan} />
        ))}
      </tbody>
    </Table>
  )
}
```

## Notes

- Loans are ERC-721 NFTs - each loan has a unique `tokenUri`
- `prepaidDuration` is in seconds, decreases as time passes
- After 10 years (`LOAN_LIQUIDATION_DURATION`), loans can be liquidated
- Permission checking uses Bendystraw, but actual borrow calls use on-chain contracts
- Poll interval of 3 seconds keeps UI responsive to loan state changes

## References

- [loansByAccount.graphql](https://github.com/rev-net/revnet-app/blob/main/src/graphql/loansByAccount.graphql)
- [LoansDetailsTable.tsx](https://github.com/rev-net/revnet-app/blob/main/src/app/[slug]/components/Value/LoansDetailsTable.tsx)
- [useHasBorrowPermission.ts](https://github.com/rev-net/revnet-app/blob/main/src/hooks/useHasBorrowPermission.ts)
- REVLoans contract: `/jb-revloans` skill for contract mechanics
