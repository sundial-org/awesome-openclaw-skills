---
name: jb-bendystraw
description: Bendystraw GraphQL API reference for querying Juicebox project data across all chains. Get project stats, payments, token holders, loans, NFT tiers, unified activity feeds, historical snapshots, and cross-chain aggregations.
---

# Bendystraw: Cross-Chain Juicebox Data API

Bendystraw is a GraphQL indexer for Juicebox V5 events across all supported chains. It aggregates data and provides unified cross-chain queries for projects, payments, token holders, and NFTs.

## API Base URLs

```
Production: https://bendystraw.xyz/{API_KEY}/graphql
Testnet: https://testnet.bendystraw.xyz/{API_KEY}/graphql
Playground: https://bendystraw.xyz (browser-based GraphQL explorer)
```

## Authentication

**API key required.** Contact [@peripheralist](https://x.com/peripheralist) on Twitter/X to get one.

```javascript
const response = await fetch(`https://bendystraw.xyz/${API_KEY}/graphql`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '...',
    variables: { ... }
  })
});
```

**Important:** Never expose API keys in frontend code. Use a server-side proxy.

---

## Supported Chains

| Chain | Chain ID | Network |
|-------|----------|---------|
| Ethereum | 1 | Mainnet |
| Optimism | 10 | Mainnet |
| Base | 8453 | Mainnet |
| Arbitrum | 42161 | Mainnet |
| Sepolia | 11155111 | Testnet |

---

## GraphQL Schema Reference

### Project Entity

```graphql
type Project {
  # Identifiers
  id: String!                    # "{chainId}-{projectId}-{version}"
  projectId: Int!
  chainId: Int!
  version: Int!                  # Protocol version (4 or 5)

  # Metadata
  handle: String
  name: String
  description: String
  logoUri: String
  infoUri: String
  owner: String!
  deployer: String

  # Financial
  balance: String!               # Current balance (wei)
  volume: String!                # Total received (wei)
  volumeUsd: String              # USD equivalent
  redeemVolume: String!          # Total redeemed (wei)
  redeemVolumeUsd: String

  # Tokens
  tokenSupply: String!           # Total token supply
  token: String                  # ERC20 address if deployed
  tokenSymbol: String

  # Activity counts
  paymentsCount: Int!
  redeemCount: Int!
  contributorsCount: Int!
  nftsMintedCount: Int!

  # Trending (7-day window)
  trendingScore: Float
  trendingVolume: String
  trendingPaymentsCount: Int

  # Omnichain
  suckerGroupId: String          # Linked cross-chain group

  # Timestamps
  createdAt: Int!
  deployedAt: Int
}
```

### SuckerGroup Entity (Omnichain Projects)

```graphql
type SuckerGroup {
  id: String!                    # Unique group identifier
  projects: [String!]!           # Array of project IDs

  # Aggregated totals across all chains
  volume: String!
  volumeUsd: String
  balance: String!
  tokenSupply: String!
  paymentsCount: Int!
  contributorsCount: Int!

  # Related projects (expanded)
  projects_rel: [Project!]!
}
```

### Participant Entity (Token Holders)

```graphql
type Participant {
  id: String!                    # "{chainId}-{projectId}-{address}"
  address: String!
  projectId: Int!
  chainId: Int!

  # Balances
  balance: String!               # Total balance (credits + ERC20)
  creditBalance: String!         # Unclaimed credits
  erc20Balance: String!          # Claimed ERC20 tokens

  # Activity
  volume: String!                # Total contributed
  volumeUsd: String
  paymentsCount: Int!
  redeemCount: Int!

  # Timestamps
  lastPaidAt: Int
  firstPaidAt: Int
}
```

### PayEvent Entity

```graphql
type PayEvent {
  id: String!
  projectId: Int!
  chainId: Int!
  rulesetId: Int!

  # Transaction
  txHash: String!
  timestamp: Int!
  logIndex: Int!
  blockNumber: Int!

  # Payment details
  from: String!                  # Payer address
  beneficiary: String!           # Token recipient
  amount: String!                # Payment amount (wei)
  amountUsd: String
  distributionFromPayAmount: String!

  # Tokens
  newlyIssuedTokenCount: String!
  beneficiaryTokenCount: String!

  # Metadata
  memo: String
  feeFromPayAmount: String
}
```

### CashOutEvent Entity

```graphql
type CashOutEvent {
  id: String!
  projectId: Int!
  chainId: Int!
  rulesetId: Int!

  # Transaction
  txHash: String!
  timestamp: Int!

  # Redemption details
  holder: String!
  beneficiary: String!
  cashOutCount: String!          # Tokens burned
  reclaimAmount: String!         # ETH received
  reclaimAmountUsd: String
  metadata: String
}
```

### NFT Entity

```graphql
type NFT {
  id: String!
  tokenId: Int!
  projectId: Int!
  chainId: Int!
  hook: String!                  # 721 hook address

  # Tier
  tierId: Int!
  tierCategory: Int

  # Ownership
  owner: String!
  createdAt: Int!

  # Metadata
  tokenUri: String
}
```

### ActivityEvent Entity (Unified Activity Feed)

A polymorphic event type that provides a unified view of all project activity. Query this instead of individual event types when building activity feeds.

```graphql
type ActivityEvent {
  id: String!
  chainId: Int!
  projectId: Int!
  suckerGroupId: String
  version: Int!

  # Transaction
  txHash: String!
  timestamp: Int!
  from: String!

  # Event type discriminator
  type: ActivityEventType!       # Determines which embedded event is populated

  # Embedded events (one will be non-null based on type)
  payEvent: PayEvent
  cashOutTokensEvent: CashOutTokensEvent
  mintNftEvent: MintNftEvent
  sendPayoutsEvent: SendPayoutsEvent
  sendPayoutToSplitEvent: SendPayoutToSplitEvent
  borrowLoanEvent: BorrowLoanEvent
  repayLoanEvent: RepayLoanEvent
  liquidateLoanEvent: LiquidateLoanEvent
  deployErc20Event: DeployErc20Event
  burnEvent: BurnEvent
  mintTokensEvent: MintTokensEvent
  projectCreateEvent: ProjectCreateEvent
  addToBalanceEvent: AddToBalanceEvent
  useAllowanceEvent: UseAllowanceEvent
  decorateBannyEvent: DecorateBannyEvent
  # ... and more

  # Relations
  project: Project
  suckerGroup: SuckerGroup
}

enum ActivityEventType {
  payEvent
  cashOutTokensEvent
  mintNftEvent
  sendPayoutsEvent
  sendPayoutToSplitEvent
  borrowLoanEvent
  repayLoanEvent
  liquidateLoanEvent
  reallocateLoanEvent
  deployErc20Event
  burnEvent
  mintTokensEvent
  manualMintTokensEvent
  manualBurnEvent
  autoIssueEvent
  projectCreateEvent
  addToBalanceEvent
  useAllowanceEvent
  sendReservedTokensToSplitEvent
  sendReservedTokensToSplitsEvent
  decorateBannyEvent
}
```

### Loan Entity (RevLoans)

Active loan state from the RevLoans protocol.

```graphql
type Loan {
  id: BigInt!                    # Loan ID (NFT token ID)
  projectId: Int!
  chainId: Int!
  version: Int!
  createdAt: Int!

  # Loan terms
  borrowAmount: BigInt!          # Amount borrowed (wei)
  collateral: BigInt!            # Collateral locked (project tokens)
  sourceFeeAmount: BigInt!       # Fee amount
  prepaidDuration: Int!          # Prepaid period in seconds
  prepaidFeePercent: Int!        # Fee percent (basis points)

  # Addresses
  beneficiary: String!           # Who receives borrowed funds
  owner: String!                 # Loan NFT owner
  token: String!                 # Collateral token address
  terminal: String!              # Terminal address

  # Metadata
  tokenUri: String               # Loan NFT metadata URI

  # Relations
  project: Project
  participant: Participant
  wallet: Wallet
}
```

### Wallet Entity

Wallet-level aggregation across all project participations.

```graphql
type Wallet {
  address: String!               # Wallet address

  # Aggregated stats
  volume: BigInt!                # Total volume across all projects
  volumeUsd: BigInt!             # USD equivalent (18 decimals)
  lastPaidTimestamp: Int         # Most recent payment timestamp

  # Relations
  participants: ParticipantPage  # All project participations
  nfts: NFTPage                  # All owned NFTs
}
```

### NFTTier Entity

NFT tier configuration with pricing and supply.

```graphql
type NFTTier {
  chainId: Int!
  projectId: Int!
  version: Int!
  tierId: Int!

  # Pricing
  price: BigInt!                 # Price in terminal token (wei)

  # Supply
  initialSupply: Int!            # Original supply
  remainingSupply: Int!          # Current available

  # Configuration
  allowOwnerMint: Boolean!       # Owner can mint without payment
  cannotBeRemoved: Boolean!      # Tier is permanent
  transfersPausable: Boolean!    # Transfers can be paused
  votingUnits: BigInt!           # Governance weight per NFT
  category: Int                  # Tier category
  reserveFrequency: Int          # Reserve rate
  reserveBeneficiary: String     # Reserve recipient

  # Metadata
  encodedIpfsUri: String         # IPFS hash (encoded)
  resolvedUri: String            # Full resolved URI
  metadata: JSON                 # Parsed metadata
  svg: String                    # SVG content if available

  createdAt: Int!

  # Relations
  hook: NFTHook
  nfts: NFTPage                  # Minted NFTs in this tier
  project: Project
}
```

### NFTHook Entity

721 hook contract configuration.

```graphql
type NFTHook {
  chainId: Int!
  projectId: Int!
  version: Int!
  createdAt: Int!

  address: String!               # Hook contract address
  name: String                   # Collection name
  symbol: String                 # Collection symbol

  # Relations
  nfts: NFTPage
  nftTiers: NFTTierPage
  project: Project
}
```

### ProjectMoment Entity (Historical Snapshots)

Point-in-time snapshots of project state. Useful for historical charts and analytics.

```graphql
type ProjectMoment {
  projectId: Int!
  chainId: Int!
  version: Int!

  # Snapshot point
  block: Int!                    # Block number
  timestamp: Int!                # Unix timestamp

  # State at snapshot
  volume: BigInt!
  volumeUsd: BigInt!
  balance: BigInt!
  trendingScore: BigInt!

  # Relations
  project: Project
}
```

### SuckerGroupMoment Entity

Point-in-time snapshots of cross-chain aggregated state.

```graphql
type SuckerGroupMoment {
  suckerGroupId: String!

  # Snapshot point
  block: Int!
  timestamp: Int!

  # Aggregated state
  volume: BigInt!
  volumeUsd: BigInt!
  balance: BigInt!
  tokenSupply: BigInt!

  # Relations
  suckerGroup: SuckerGroup
}
```

### SuckerTransaction Entity (Cross-Chain Bridging)

Token bridging transactions between chains via suckers.

```graphql
type SuckerTransaction {
  index: Int!                    # Transaction index
  projectId: Int!
  chainId: Int!                  # Source chain
  version: Int!
  suckerGroupId: String!
  createdAt: Int!

  # Bridge details
  token: String!                 # Token being bridged
  sucker: String!                # Source sucker address
  peer: String!                  # Destination sucker address
  peerChainId: Int!              # Destination chain
  beneficiary: String!           # Recipient address

  # Amounts
  projectTokenCount: BigInt!     # Project tokens bridged
  terminalTokenAmount: BigInt!   # Terminal tokens (if any)

  # State
  root: String                   # Merkle root
  status: SuckerTransactionStatus!

  # Relations
  suckerGroup: SuckerGroup
}

enum SuckerTransactionStatus {
  pending
  completed
  failed
}
```

### SendPayoutsEvent Entity

Payout distribution events from the terminal.

```graphql
type SendPayoutsEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  logIndex: Int!

  # Payout details
  caller: String!                # Who triggered payout
  from: String!                  # Source address
  rulesetId: Int!
  rulesetCycleNumber: Int!

  # Amounts
  amount: BigInt!                # Total payout amount
  amountUsd: BigInt!
  amountPaidOut: BigInt!         # Actually distributed
  amountPaidOutUsd: BigInt!
  netLeftoverPayoutAmount: BigInt!  # Remaining after splits
  fee: BigInt!                   # Protocol fee
  feeUsd: BigInt!

  # Relations
  project: Project
}
```

### UseAllowanceEvent Entity

Surplus allowance usage events.

```graphql
type UseAllowanceEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!

  # Transaction
  txHash: String!
  timestamp: Int!

  # Allowance details
  caller: String!
  beneficiary: String!           # Who receives funds
  rulesetId: Int!
  rulesetCycleNumber: Int!

  # Amounts
  amount: BigInt!                # Amount used
  amountUsd: BigInt!
  netAmount: BigInt!             # After fees
  netAmountUsd: BigInt!

  # Relations
  project: Project
}
```

### PermissionHolder Entity

Operator permissions granted to accounts.

```graphql
type PermissionHolder {
  chainId: Int!
  projectId: Int!
  version: Int!

  account: String!               # Account with permissions
  operator: String!              # Operator address
  permissions: [Int!]!           # Permission IDs granted
  isRevnetOperator: Boolean!     # Is a revnet operator

  # Relations
  project: Project
}
```

### BorrowLoanEvent Entity

Loan creation events from RevLoans.

```graphql
type BorrowLoanEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Loan details
  borrowAmount: BigInt!          # Amount borrowed
  collateral: BigInt!            # Collateral locked
  sourceFeeAmount: BigInt!       # Fee paid
  prepaidDuration: Int!          # Prepaid period (seconds)
  prepaidFeePercent: Int!        # Fee percent (basis points)
  beneficiary: String!           # Loan recipient
  token: String!                 # Collateral token
  terminal: String!              # Terminal address

  # Relations
  project: Project
}
```

### RepayLoanEvent Entity

Loan repayment events.

```graphql
type RepayLoanEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Repayment details
  loanId: BigInt!                # Loan being repaid
  paidOffLoanId: BigInt          # If fully paid off
  repayBorrowAmount: BigInt!     # Amount repaid
  collateralCountToReturn: BigInt!  # Collateral returned

  # Relations
  project: Project
}
```

### LiquidateLoanEvent Entity

Loan liquidation events.

```graphql
type LiquidateLoanEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Liquidation details
  borrowAmount: BigInt!          # Outstanding borrow
  collateral: BigInt!            # Collateral seized

  # Relations
  project: Project
}
```

### ReallocateLoanEvent Entity

Loan reallocation events (moving collateral between loans).

```graphql
type ReallocateLoanEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Reallocation details
  loanId: BigInt!                # Source loan
  reallocatedLoanId: BigInt!     # Target loan
  removedCollateralCount: BigInt!  # Collateral moved

  # Relations
  project: Project
}
```

### BurnEvent Entity

Token burn events (from cash outs).

```graphql
type BurnEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  from: String!

  # Burn details
  amount: BigInt!                # Total burned
  creditAmount: BigInt!          # Credits burned
  erc20Amount: BigInt!           # ERC20 burned

  # Relations
  project: Project
}
```

### MintTokensEvent Entity

Token minting events (from payments).

```graphql
type MintTokensEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Mint details
  beneficiary: String!           # Token recipient
  beneficiaryTokenCount: BigInt! # Tokens to beneficiary
  reservedPercent: BigInt!       # Reserved rate
  tokenCount: BigInt!            # Total minted
  memo: String                   # Payment memo

  # Relations
  project: Project
}
```

### ManualMintTokensEvent Entity

Manual token minting by project owner.

```graphql
type ManualMintTokensEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Mint details
  beneficiary: String!
  beneficiaryTokenCount: BigInt!
  reservedPercent: BigInt!
  tokenCount: BigInt!
  memo: String

  # Relations
  project: Project
}
```

### ManualBurnEvent Entity

Manual token burning.

```graphql
type ManualBurnEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  from: String!

  # Burn details
  amount: BigInt!
  creditAmount: BigInt!
  erc20Amount: BigInt!

  # Relations
  project: Project
}
```

### MintNftEvent Entity

NFT minting events.

```graphql
type MintNftEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Mint details
  hook: String!                  # 721 hook address
  beneficiary: String!           # NFT recipient
  tierId: Int!                   # Tier minted
  tokenId: BigInt!               # Token ID
  totalAmountPaid: BigInt!       # Amount paid

  # Relations
  project: Project
  tier: NFTTier
  nft: NFT
}
```

### DeployErc20Event Entity

ERC20 token deployment events.

```graphql
type DeployErc20Event {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Token details
  symbol: String!                # Token symbol
  name: String!                  # Token name
  token: String!                 # Token address

  # Relations
  project: Project
}
```

### ProjectCreateEvent Entity

Project creation events.

```graphql
type ProjectCreateEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Relations
  project: Project
}
```

### AddToBalanceEvent Entity

Direct balance addition events.

```graphql
type AddToBalanceEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Details
  amount: BigInt!                # Amount added
  memo: String                   # Memo
  metadata: String               # Additional metadata
  returnedFees: BigInt           # Fees returned

  # Relations
  project: Project
}
```

### SendPayoutToSplitEvent Entity

Individual split payout events.

```graphql
type SendPayoutToSplitEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Split details
  rulesetId: Int!
  group: BigInt!                 # Split group
  beneficiary: String!           # Split recipient
  splitProjectId: Int            # If split to project
  hook: String                   # Split hook if any

  # Amounts
  amount: BigInt!                # Gross amount
  netAmount: BigInt!             # After fees
  amountUsd: BigInt!
  percent: Int!                  # Split percent
  lockedUntil: BigInt            # Lock timestamp
  preferAddToBalance: Boolean!   # Add to balance vs pay

  # Relations
  project: Project
}
```

### SendReservedTokensToSplitEvent Entity

Reserved token distribution to individual split.

```graphql
type SendReservedTokensToSplitEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Split details
  rulesetId: Int!
  groupId: BigInt!
  beneficiary: String!
  splitProjectId: Int
  hook: String
  tokenCount: BigInt!            # Tokens sent
  percent: Int!
  lockedUntil: BigInt
  preferAddToBalance: Boolean!

  # Relations
  project: Project
}
```

### SendReservedTokensToSplitsEvent Entity

Batch reserved token distribution event.

```graphql
type SendReservedTokensToSplitsEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!
  suckerGroupId: String

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Distribution details
  rulesetId: Int!
  rulesetCycleNumber: Int!
  owner: String!                 # Project owner
  tokenCount: BigInt!            # Total distributed
  leftoverAmount: BigInt!        # Remaining after splits

  # Relations
  project: Project
}
```

### AutoIssueEvent Entity

Auto-issuance events (revnet stage transitions).

```graphql
type AutoIssueEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Issuance details
  stageId: BigInt!               # Revnet stage
  beneficiary: String!           # Token recipient
  count: BigInt!                 # Tokens issued

  # Relations
  project: Project
}
```

### StoreAutoIssuanceAmountEvent Entity

Auto-issuance configuration events.

```graphql
type StoreAutoIssuanceAmountEvent {
  id: String!
  chainId: Int!
  version: Int!
  projectId: Int!

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Config details
  stageId: BigInt!               # Revnet stage
  beneficiary: String!           # Configured recipient
  count: BigInt!                 # Amount to auto-issue

  # Relations
  project: Project
}
```

### DecorateBannyEvent Entity

Banny NFT decoration events.

```graphql
type DecorateBannyEvent {
  id: String!
  chainId: Int!
  version: Int!

  # Transaction
  txHash: String!
  timestamp: Int!
  caller: String!
  from: String!
  logIndex: Int!

  # Decoration details
  bannyBodyId: BigInt!           # Banny being decorated
  outfitIds: [BigInt!]!          # Outfit NFT IDs
  backgroundId: BigInt           # Background NFT ID
  tokenUri: String               # Updated token URI
  tokenUriMetadata: JSON         # Parsed metadata

  # Relations
  bannyNft: NFT
}
```

### CashOutTaxSnapshot Entity

Historical cash-out tax rate snapshots.

```graphql
type CashOutTaxSnapshot {
  chainId: Int!
  projectId: Int!
  suckerGroupId: String
  version: Int!

  # Snapshot period
  start: BigInt!                 # Period start timestamp
  duration: BigInt!              # Period duration
  rulesetId: BigInt!             # Ruleset ID

  # Tax rate
  cashOutTax: Int!               # Tax rate (basis points)
}
```

### ParticipantSnapshot Entity (GraphQL)

Historical participant balance snapshots via GraphQL (alternative to REST endpoint).

```graphql
type ParticipantSnapshot {
  chainId: Int!
  projectId: Int!
  suckerGroupId: String
  version: Int!

  # Snapshot point
  block: Int!
  timestamp: Int!

  # Participant
  address: String!

  # Balances at snapshot
  balance: BigInt!
  creditBalance: BigInt!
  erc20Balance: BigInt!
  volume: BigInt!
  volumeUsd: BigInt!
}
```

---

## Critical Concepts

### Project Identity

**A Juicebox project is uniquely identified by three fields: `projectId + chainId + version`.**

This is crucial because:
- **V4 and V5 are completely different protocols.** Project #64 on Ethereum V4 is NOT the same project as Project #64 on Ethereum V5.
- The same projectId can exist on multiple chains (via suckers/omnichain), but those ARE the same project.
- Always include `version` when querying or displaying projects.

```javascript
// WRONG: Groups V4 and V5 together
const groupKey = `${project.projectId}-${project.chainId}`;

// CORRECT: Keeps V4 and V5 separate
const groupKey = `${project.projectId}-v${project.version}`;
```

### Multi-Chain Grouping

When displaying "top projects" or aggregating stats:
- **Same projectId + version across chains** → Group together (same project via suckers)
- **Same projectId, different version** → Keep separate (completely different projects)

```javascript
// Group projects by projectId + version (V4 and V5 are different projects!)
const grouped = new Map();

for (const project of projects) {
  const groupKey = `${project.projectId}-v${project.version || 4}`;
  const existing = grouped.get(groupKey);

  if (existing) {
    // Add chain to existing group
    if (!existing.chainIds.includes(project.chainId)) {
      existing.chainIds.push(project.chainId);
    }
    // Sum volumes
    existing.totalVolumeUsd += parseFloat(project.volumeUsd || '0');
  } else {
    grouped.set(groupKey, {
      ...project,
      chainIds: [project.chainId],
      totalVolumeUsd: parseFloat(project.volumeUsd || '0')
    });
  }
}
```

### USD Value Formatting

The `volumeUsd`, `amountUsd`, and similar fields use **18 decimal format** (like wei). You must convert properly:

```javascript
function formatVolumeUsd(volumeUsd) {
  if (!volumeUsd || volumeUsd === '0') return '$0';

  try {
    // volumeUsd comes in 18 decimal format
    // Use BigInt to avoid precision loss on large numbers
    const raw = BigInt(volumeUsd.split('.')[0]);
    const usd = Number(raw / BigInt(1e12)) / 1e6; // Divide in steps

    if (usd >= 1_000_000) return `$${(usd / 1_000_000).toFixed(1)}M`;
    if (usd >= 1_000) return `$${(usd / 1_000).toFixed(1)}k`;
    if (usd >= 1) return `$${usd.toFixed(0)}`;
    return `$${usd.toFixed(2)}`;
  } catch {
    return '$0';
  }
}
```

**Warning:** Do NOT use `parseFloat()` directly on volumeUsd for large values—JavaScript loses precision beyond ~15 digits.

### Filtering by Version

When querying projects, filter by version to avoid mixing V4 and V5 data:

```graphql
# Get only V5 projects
query V5Projects($limit: Int!) {
  projects(
    where: { version: 5 }
    orderBy: "volumeUsd"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      projectId
      chainId
      version
      name
      volumeUsd
    }
  }
}
```

To display both versions, query them separately and handle grouping in your application.

---

## Query Examples

### Get Single Project

```graphql
query GetProject($projectId: Int!, $chainId: Int!) {
  project(projectId: $projectId, chainId: $chainId) {
    id
    name
    handle
    owner
    balance
    volume
    volumeUsd
    tokenSupply
    paymentsCount
    contributorsCount
    suckerGroupId
  }
}
```

### Get Participant (Token Holder)

```graphql
query GetParticipant($projectId: Int!, $chainId: Int!, $address: String!) {
  participant(projectId: $projectId, chainId: $chainId, address: $address) {
    balance
    creditBalance
    erc20Balance
    volume
    volumeUsd
    paymentsCount
  }
}
```

### Get Sucker Group (Omnichain Totals)

```graphql
query GetSuckerGroup($id: String!) {
  suckerGroup(id: $id) {
    id
    volume
    volumeUsd
    balance
    tokenSupply
    paymentsCount
    contributorsCount
    projects_rel {
      projectId
      chainId
      name
      balance
      volume
    }
  }
}
```

### List Projects

```graphql
query ListProjects($chainId: Int, $version: Int, $limit: Int!, $offset: Int!) {
  projects(
    where: { chainId: $chainId, version: $version }
    orderBy: "volumeUsd"
    orderDirection: "desc"
    limit: $limit
    offset: $offset
  ) {
    items {
      projectId
      chainId
      version
      name
      handle
      volumeUsd
      balance
      paymentsCount
    }
    totalCount
  }
}
```

### List Recent Payments

```graphql
query ListPayments($projectId: Int!, $chainId: Int!, $limit: Int!) {
  payEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      from
      beneficiary
      amount
      amountUsd
      memo
      newlyIssuedTokenCount
    }
  }
}
```

### List Top Token Holders

```graphql
query ListParticipants($projectId: Int!, $chainId: Int!, $limit: Int!) {
  participants(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "balance"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      address
      balance
      creditBalance
      erc20Balance
      volume
      paymentsCount
    }
    totalCount
  }
}
```

### Get Trending Projects

```graphql
query TrendingProjects($limit: Int!) {
  projects(
    orderBy: "trendingScore"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      projectId
      chainId
      name
      handle
      trendingScore
      trendingVolume
      trendingPaymentsCount
    }
  }
}
```

### List Cash Out Events

```graphql
query ListCashOuts($projectId: Int!, $chainId: Int!, $limit: Int!) {
  cashOutEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      holder
      beneficiary
      cashOutCount
      reclaimAmount
      reclaimAmountUsd
    }
  }
}
```

### List NFTs for Project

```graphql
query ListNFTs($projectId: Int!, $chainId: Int!, $limit: Int!) {
  nfts(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "createdAt"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      tokenId
      tierId
      tierCategory
      owner
      createdAt
      tokenUri
    }
  }
}
```

### Get Unified Activity Feed

The most powerful query for building activity feeds. Returns all event types in a single query.

```graphql
query GetActivityFeed($projectId: Int!, $chainId: Int!, $limit: Int!) {
  activityEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      id
      timestamp
      txHash
      from
      type                        # Discriminator for event type

      # Include fields from each possible event type
      payEvent {
        amount
        amountUsd
        beneficiary
        memo
      }
      cashOutTokensEvent {
        cashOutCount
        reclaimAmount
        holder
      }
      mintNftEvent {
        tierId
        tokenId
      }
      sendPayoutsEvent {
        amount
        amountPaidOut
        fee
      }
      borrowLoanEvent {
        borrowAmount
        collateral
      }
    }
  }
}
```

### Get Omnichain Activity Feed

Query activity across all chains for a sucker group.

```graphql
query GetOmnichainActivity($suckerGroupId: String!, $limit: Int!) {
  activityEvents(
    where: { suckerGroupId: $suckerGroupId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      chainId
      timestamp
      type
      txHash
      from
      payEvent { amount, memo }
      cashOutTokensEvent { cashOutCount, reclaimAmount }
    }
  }
}
```

### List Active Loans

```graphql
query ListLoans($projectId: Int!, $chainId: Int!, $limit: Int!) {
  loans(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "createdAt"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      id
      borrowAmount
      collateral
      prepaidDuration
      prepaidFeePercent
      owner
      beneficiary
      createdAt
    }
    totalCount
  }
}
```

### Get Loan by ID

```graphql
query GetLoan($id: BigInt!) {
  loan(id: $id) {
    id
    projectId
    chainId
    borrowAmount
    collateral
    sourceFeeAmount
    prepaidDuration
    prepaidFeePercent
    beneficiary
    owner
    token
    terminal
    tokenUri
    createdAt
  }
}
```

### Get Wallet Portfolio

```graphql
query GetWallet($address: String!) {
  wallet(address: $address) {
    address
    volume
    volumeUsd
    lastPaidTimestamp
    participants(limit: 100) {
      items {
        projectId
        chainId
        balance
        volume
      }
    }
    nfts(limit: 50) {
      items {
        projectId
        chainId
        tokenId
        tierId
      }
    }
  }
}
```

### List NFT Tiers

```graphql
query ListNFTTiers($projectId: Int!, $chainId: Int!, $limit: Int!) {
  nftTiers(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "tierId"
    orderDirection: "asc"
    limit: $limit
  ) {
    items {
      tierId
      price
      initialSupply
      remainingSupply
      category
      votingUnits
      resolvedUri
      metadata
      svg
    }
  }
}
```

### Get NFT Hook Details

```graphql
query GetNFTHook($projectId: Int!, $chainId: Int!) {
  nftHooks(
    where: { projectId: $projectId, chainId: $chainId }
    limit: 1
  ) {
    items {
      address
      name
      symbol
      nftTiers(limit: 100) {
        items {
          tierId
          price
          remainingSupply
        }
      }
    }
  }
}
```

### Get Historical Project Snapshots

```graphql
query GetProjectHistory($projectId: Int!, $chainId: Int!, $limit: Int!) {
  projectMoments(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      block
      timestamp
      volume
      volumeUsd
      balance
      trendingScore
    }
  }
}
```

### Get Cross-Chain Bridge Transactions

```graphql
query GetSuckerTransactions($suckerGroupId: String!, $limit: Int!) {
  suckerTransactions(
    where: { suckerGroupId: $suckerGroupId }
    orderBy: "createdAt"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      index
      chainId
      peerChainId
      beneficiary
      projectTokenCount
      terminalTokenAmount
      status
      createdAt
    }
  }
}
```

### List Payout Events

```graphql
query ListPayouts($projectId: Int!, $chainId: Int!, $limit: Int!) {
  sendPayoutsEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      caller
      rulesetCycleNumber
      amount
      amountPaidOut
      fee
      netLeftoverPayoutAmount
    }
  }
}
```

### List Allowance Usage

```graphql
query ListAllowanceUsage($projectId: Int!, $chainId: Int!, $limit: Int!) {
  useAllowanceEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      caller
      beneficiary
      amount
      netAmount
      rulesetCycleNumber
    }
  }
}
```

### List Loan Events (Borrow/Repay/Liquidate)

```graphql
query ListBorrowEvents($projectId: Int!, $chainId: Int!, $limit: Int!) {
  borrowLoanEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      borrowAmount
      collateral
      prepaidDuration
      beneficiary
    }
  }
}

query ListRepayEvents($projectId: Int!, $chainId: Int!, $limit: Int!) {
  repayLoanEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      loanId
      repayBorrowAmount
      collateralCountToReturn
    }
  }
}

query ListLiquidations($projectId: Int!, $chainId: Int!, $limit: Int!) {
  liquidateLoanEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      borrowAmount
      collateral
    }
  }
}
```

### List Token Burns

```graphql
query ListBurns($projectId: Int!, $chainId: Int!, $limit: Int!) {
  burnEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      from
      amount
      creditAmount
      erc20Amount
    }
  }
}
```

### List NFT Mints

```graphql
query ListNFTMints($projectId: Int!, $chainId: Int!, $limit: Int!) {
  mintNftEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      beneficiary
      tierId
      tokenId
      totalAmountPaid
    }
  }
}
```

### Get Permission Holders

```graphql
query ListPermissionHolders($projectId: Int!, $chainId: Int!) {
  permissionHolders(
    where: { projectId: $projectId, chainId: $chainId }
    limit: 100
  ) {
    items {
      account
      operator
      permissions
      isRevnetOperator
    }
  }
}
```

### List Project Creations

```graphql
query ListProjectCreations($chainId: Int!, $limit: Int!) {
  projectCreateEvents(
    where: { chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      projectId
      caller
      project {
        name
        handle
        owner
      }
    }
  }
}
```

### List ERC20 Deployments

```graphql
query ListERC20Deployments($chainId: Int!, $limit: Int!) {
  deployErc20Events(
    where: { chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      projectId
      name
      symbol
      token
    }
  }
}
```

### Get Cash Out Tax History

```graphql
query GetCashOutTaxHistory($projectId: Int!, $chainId: Int!, $limit: Int!) {
  cashOutTaxSnapshots(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "start"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      start
      duration
      rulesetId
      cashOutTax
    }
  }
}
```

### Get Participant History (GraphQL Snapshots)

```graphql
query GetParticipantHistory(
  $projectId: Int!,
  $chainId: Int!,
  $address: String!,
  $limit: Int!
) {
  participantSnapshots(
    where: { projectId: $projectId, chainId: $chainId, address: $address }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      block
      timestamp
      balance
      creditBalance
      erc20Balance
      volume
      volumeUsd
    }
  }
}
```

### List Reserved Token Distributions

```graphql
query ListReservedDistributions($projectId: Int!, $chainId: Int!, $limit: Int!) {
  sendReservedTokensToSplitsEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      rulesetCycleNumber
      tokenCount
      leftoverAmount
      owner
    }
  }
}
```

### List Split Payouts

```graphql
query ListSplitPayouts($projectId: Int!, $chainId: Int!, $limit: Int!) {
  sendPayoutToSplitEvents(
    where: { projectId: $projectId, chainId: $chainId }
    orderBy: "timestamp"
    orderDirection: "desc"
    limit: $limit
  ) {
    items {
      timestamp
      txHash
      beneficiary
      splitProjectId
      amount
      netAmount
      percent
    }
  }
}
```

---

## Filtering

The `where` clause supports these operators:

```graphql
where: {
  # Exact match
  projectId: 1
  chainId: 1

  # Multiple values (OR)
  chainId_in: [1, 10, 8453]

  # Comparison operators
  balance_gt: "1000000000000000000"
  balance_gte: "1000000000000000000"
  balance_lt: "100000000000000000000"
  balance_lte: "100000000000000000000"
  timestamp_gte: 1704067200

  # Text search
  name_contains: "dao"
  handle_starts_with: "jb"
}
```

---

## Sorting

```graphql
orderBy: "volume"           # Field to sort by
orderDirection: "desc"      # "asc" or "desc"
```

**Sortable Fields by Entity:**

| Entity | Sortable Fields |
|--------|-----------------|
| Project | `volume`, `balance`, `tokenSupply`, `paymentsCount`, `createdAt`, `trendingScore` |
| Participant | `balance`, `volume`, `paymentsCount` |
| PayEvent | `timestamp`, `amount` |
| CashOutEvent | `timestamp`, `reclaimAmount` |
| NFT | `createdAt`, `tokenId` |
| ActivityEvent | `timestamp` |
| Loan | `createdAt`, `borrowAmount`, `collateral` |
| Wallet | `volume`, `volumeUsd`, `lastPaidTimestamp` |
| NFTTier | `tierId`, `price`, `createdAt` |
| ProjectMoment | `timestamp`, `block` |
| SuckerTransaction | `createdAt` |
| SendPayoutsEvent | `timestamp`, `amount` |
| UseAllowanceEvent | `timestamp`, `amount` |
| BorrowLoanEvent | `timestamp`, `borrowAmount` |
| RepayLoanEvent | `timestamp`, `repayBorrowAmount` |
| LiquidateLoanEvent | `timestamp` |
| BurnEvent | `timestamp`, `amount` |
| MintTokensEvent | `timestamp`, `tokenCount` |
| MintNftEvent | `timestamp`, `tokenId` |
| DeployErc20Event | `timestamp` |
| ProjectCreateEvent | `timestamp` |
| SendPayoutToSplitEvent | `timestamp`, `amount` |
| CashOutTaxSnapshot | `start` |
| ParticipantSnapshot | `timestamp`, `block` |

---

## Pagination

All list queries support pagination:

```graphql
query PaginatedPayments(
  $projectId: Int!,
  $chainId: Int!,
  $limit: Int!,
  $offset: Int!
) {
  payEvents(
    where: { projectId: $projectId, chainId: $chainId }
    limit: $limit
    offset: $offset
  ) {
    items { ... }
    totalCount
  }
}
```

**Parameters:**
- `limit`: Max items to return (default: 100, max: 1000)
- `offset`: Number of items to skip

---

## Special Endpoints

### Participant Snapshots

Get historical participant balances at a specific timestamp. Useful for governance snapshots and airdrops.

```
POST https://bendystraw.xyz/{API_KEY}/participants
```

**Request:**
```json
{
  "suckerGroupId": "0x...",
  "timestamp": 1704067200
}
```

**Response:**
```json
{
  "participants": [
    {
      "address": "0x...",
      "balance": "1000000000000000000000",
      "chains": {
        "1": "600000000000000000000",
        "10": "400000000000000000000"
      }
    }
  ]
}
```

---

## Complete JavaScript Example

```javascript
const BENDYSTRAW_URL = 'https://bendystraw.xyz';
const API_KEY = process.env.BENDYSTRAW_API_KEY;

/**
 * Execute GraphQL query
 */
async function query(graphql, variables = {}) {
  const response = await fetch(`${BENDYSTRAW_URL}/${API_KEY}/graphql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: graphql, variables })
  });

  const result = await response.json();

  if (result.errors) {
    throw new Error(result.errors[0].message);
  }

  return result.data;
}

/**
 * Get project stats
 */
async function getProject(projectId, chainId) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!) {
      project(projectId: $projectId, chainId: $chainId) {
        name
        handle
        owner
        balance
        volume
        volumeUsd
        tokenSupply
        paymentsCount
        contributorsCount
        suckerGroupId
      }
    }
  `, { projectId, chainId });

  return data.project;
}

/**
 * Get omnichain totals for sucker group
 */
async function getOmnichainStats(suckerGroupId) {
  const data = await query(`
    query($id: String!) {
      suckerGroup(id: $id) {
        volume
        volumeUsd
        balance
        tokenSupply
        contributorsCount
        projects_rel {
          chainId
          name
          balance
          volume
        }
      }
    }
  `, { id: suckerGroupId });

  return data.suckerGroup;
}

/**
 * Get recent payments
 */
async function getRecentPayments(projectId, chainId, limit = 20) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $limit: Int!) {
      payEvents(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "timestamp"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          timestamp
          from
          beneficiary
          amount
          amountUsd
          memo
          newlyIssuedTokenCount
        }
      }
    }
  `, { projectId, chainId, limit });

  return data.payEvents.items;
}

/**
 * Get top token holders
 */
async function getTopHolders(projectId, chainId, limit = 100) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $limit: Int!) {
      participants(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "balance"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          address
          balance
          creditBalance
          erc20Balance
          volume
        }
        totalCount
      }
    }
  `, { projectId, chainId, limit });

  return {
    holders: data.participants.items,
    total: data.participants.totalCount
  };
}

/**
 * Get participant balance
 */
async function getParticipant(projectId, chainId, address) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $address: String!) {
      participant(projectId: $projectId, chainId: $chainId, address: $address) {
        balance
        creditBalance
        erc20Balance
        volume
        volumeUsd
        paymentsCount
      }
    }
  `, { projectId, chainId, address });

  return data.participant;
}

/**
 * Get trending projects
 */
async function getTrendingProjects(chainId = null, limit = 10) {
  const where = chainId ? { chainId } : {};

  const data = await query(`
    query($where: ProjectWhereInput, $limit: Int!) {
      projects(
        where: $where
        orderBy: "trendingScore"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          projectId
          chainId
          name
          handle
          trendingScore
          trendingVolume
          trendingPaymentsCount
        }
      }
    }
  `, { where, limit });

  return data.projects.items;
}

/**
 * Get historical snapshot for governance
 */
async function getSnapshot(suckerGroupId, timestamp) {
  const response = await fetch(`${BENDYSTRAW_URL}/${API_KEY}/participants`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suckerGroupId, timestamp })
  });

  return await response.json();
}

/**
 * Get unified activity feed (all event types)
 */
async function getActivityFeed(projectId, chainId, limit = 50) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $limit: Int!) {
      activityEvents(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "timestamp"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          id
          timestamp
          txHash
          from
          type
          payEvent { amount, amountUsd, beneficiary, memo }
          cashOutTokensEvent { cashOutCount, reclaimAmount, holder }
          mintNftEvent { tierId, tokenId }
          sendPayoutsEvent { amount, amountPaidOut, fee }
          borrowLoanEvent { borrowAmount, collateral }
        }
      }
    }
  `, { projectId, chainId, limit });

  return data.activityEvents.items;
}

/**
 * Get active loans for a project
 */
async function getLoans(projectId, chainId, limit = 100) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $limit: Int!) {
      loans(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "createdAt"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          id
          borrowAmount
          collateral
          prepaidDuration
          prepaidFeePercent
          owner
          beneficiary
          createdAt
        }
        totalCount
      }
    }
  `, { projectId, chainId, limit });

  return {
    loans: data.loans.items,
    total: data.loans.totalCount
  };
}

/**
 * Get wallet portfolio across all projects
 */
async function getWalletPortfolio(address) {
  const data = await query(`
    query($address: String!) {
      wallet(address: $address) {
        address
        volume
        volumeUsd
        lastPaidTimestamp
        participants(limit: 100) {
          items {
            projectId
            chainId
            balance
            volume
            project { name, handle }
          }
        }
      }
    }
  `, { address });

  return data.wallet;
}

/**
 * Get NFT tier details with metadata
 */
async function getNFTTiers(projectId, chainId) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!) {
      nftTiers(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "tierId"
        orderDirection: "asc"
        limit: 100
      ) {
        items {
          tierId
          price
          initialSupply
          remainingSupply
          category
          votingUnits
          resolvedUri
          metadata
          svg
        }
      }
    }
  `, { projectId, chainId });

  return data.nftTiers.items;
}

/**
 * Get historical project snapshots for charting
 */
async function getProjectHistory(projectId, chainId, limit = 100) {
  const data = await query(`
    query($projectId: Int!, $chainId: Int!, $limit: Int!) {
      projectMoments(
        where: { projectId: $projectId, chainId: $chainId }
        orderBy: "timestamp"
        orderDirection: "desc"
        limit: $limit
      ) {
        items {
          block
          timestamp
          volume
          volumeUsd
          balance
          trendingScore
        }
      }
    }
  `, { projectId, chainId, limit });

  return data.projectMoments.items;
}

// Example usage
async function main() {
  // Get project on Ethereum mainnet
  const project = await getProject(1, 1);
  console.log(`${project.name}: ${project.balance} wei balance`);

  // If omnichain, get aggregated stats
  if (project.suckerGroupId) {
    const omni = await getOmnichainStats(project.suckerGroupId);
    console.log(`Omnichain total: ${omni.volume} wei volume across ${omni.projects_rel.length} chains`);
  }

  // Get recent activity
  const payments = await getRecentPayments(1, 1, 5);
  console.log(`Last ${payments.length} payments:`);
  payments.forEach(p => {
    console.log(`  ${p.from.slice(0,8)}... paid ${p.amount} wei`);
  });

  // Get top holders
  const { holders, total } = await getTopHolders(1, 1, 10);
  console.log(`Top 10 of ${total} holders:`);
  holders.forEach((h, i) => {
    console.log(`  ${i + 1}. ${h.address.slice(0,8)}... - ${h.balance} tokens`);
  });
}

main().catch(console.error);
```

---

## BendystrawClient Class

```javascript
class BendystrawClient {
  constructor(apiKey, isTestnet = false) {
    this.baseUrl = isTestnet
      ? 'https://testnet.bendystraw.xyz'
      : 'https://bendystraw.xyz';
    this.apiKey = apiKey;
  }

  async query(graphql, variables = {}) {
    const response = await fetch(`${this.baseUrl}/${this.apiKey}/graphql`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: graphql, variables })
    });

    if (!response.ok) {
      throw new Error(`Bendystraw request failed: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.errors) {
      throw new Error(result.errors[0].message);
    }

    return result.data;
  }

  // Convenience methods
  async getProject(projectId, chainId) { ... }
  async getSuckerGroup(id) { ... }
  async getPayments(projectId, chainId, limit) { ... }
  async getParticipants(projectId, chainId, limit) { ... }
  async getSnapshot(suckerGroupId, timestamp) { ... }
}
```

---

## Server-Side Proxy

Since the API key must be kept secret, use a server-side proxy:

### Next.js API Route

```typescript
// pages/api/bendystraw.ts
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const response = await fetch(
    `https://bendystraw.xyz/${process.env.BENDYSTRAW_API_KEY}/graphql`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    }
  );

  const data = await response.json();
  res.json(data);
}
```

### Express Middleware

```javascript
app.post('/api/bendystraw', async (req, res) => {
  const response = await fetch(
    `https://bendystraw.xyz/${process.env.BENDYSTRAW_API_KEY}/graphql`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    }
  );

  res.json(await response.json());
});
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Unauthorized` | Invalid API key | Verify API key is correct |
| `Rate limited` | Too many requests | Add backoff/retry logic |
| `Invalid query` | GraphQL syntax error | Check query structure |
| `Not found` | Entity doesn't exist | Verify projectId/chainId |
| `Timeout` | Query too complex | Reduce limit, add filters |

---

## Gotchas & Common Pitfalls

### V4 vs V5 Protocol Confusion

**CRITICAL:** V4 and V5 are completely different protocols with different contract addresses.
Project #1 on V4 is NOT the same as Project #1 on V5. Never mix V4 and V5 addresses.

### V5.0 vs V5.1 Contract Confusion

**CRITICAL:** Within V5, there are two contract versions: V5.0 and V5.1. Contracts that have
both versions MUST NOT be mixed. A project using JBController5_1 MUST use JBMultiTerminal5_1.

**Shared contracts (work with both V5.0 and V5.1):**

| Contract | Address |
|----------|---------|
| JBProjects | `0x885f707efa18d2cb12f05a3a8eba6b4b26c8c1d4` |
| JBTokens | `0x4d0edd347fb1fa21589c1e109b3474924be87636` |
| JBDirectory | `0x0061e516886a0540f63157f112c0588ee0651dcf` |
| JBSplits | `0x7160a322fea44945a6ef9adfd65c322258df3c5e` |

**V5.0 contracts (for revnets and older projects):**

| Contract | Address |
|----------|---------|
| JBController | `0x27da30646502e2f642be5281322ae8c394f7668a` |
| JBMultiTerminal | `0x2db6d704058e552defe415753465df8df0361846` |
| JBRulesets | `0x6292281d69c3593fcf6ea074e5797341476ab428` |
| REVDeployer | `0x2ca27bde7e7d33e353b44c27acfcf6c78dde251d` |
| JB721TiersHookDeployer | `0x7e4f7bfeab74bbae3eb12a62f2298bf2be16fc93` |

**V5.1 contracts (for new projects):**

| Contract | Address |
|----------|---------|
| JBController5_1 | `0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1` |
| JBMultiTerminal5_1 | `0x52869db3d61dde1e391967f2ce5039ad0ecd371c` |
| JBRulesets5_1 | `0xd4257005ca8d27bbe11f356453b0e4692414b056` |
| JBOmnichainDeployer5_1 | `0x587bf86677ec0d1b766d9ba0d7ac2a51c6c2fc71` |
| JB721TiersHookDeployer5_1 | `0x7e6e7db5081c59f2df3c83b54eb0c4d029e9898e` |

**Determining project version:** Query `JBDirectory.controllerOf(projectId)` and compare:
- `0x27da30646502e2f642be5281322ae8c394f7668a` = V5.0 (use JBMultiTerminal, JBRulesets)
- `0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1` = V5.1 (use JBMultiTerminal5_1, JBRulesets5_1)

See `/jb-v5-v51-contracts` for complete reference and code patterns.

### Token Symbol Confusion

**CRITICAL:** The `tokenSymbol` field in Bendystraw returns the **base/accounting token** (e.g., "ETH" or "USDC"), NOT the project's issued ERC20 token symbol (e.g., "NANA" for Bananapus).

To get the project's issued token symbol, you must query the blockchain directly:

```javascript
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

// JBTokens address (same on all V5 chains)
const JB_TOKENS = '0x4d0edd347fb1fa21589c1e109b3474924be87636'

const TOKEN_ABI = [
  {
    name: 'tokenOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'projectId', type: 'uint256' }],
    outputs: [{ name: '', type: 'address' }],
  },
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'string' }],
  },
]

async function getProjectTokenSymbol(projectId: number, chainId: number) {
  const client = createPublicClient({ chain: mainnet, transport: http() })

  // Get the token address from JBTokens
  const tokenAddress = await client.readContract({
    address: JB_TOKENS,
    abi: TOKEN_ABI,
    functionName: 'tokenOf',
    args: [BigInt(projectId)],
  })

  // Zero address means no ERC20 deployed yet (using credits only)
  if (tokenAddress === '0x0000000000000000000000000000000000000000') {
    return null
  }

  // Get symbol from the token contract
  return await client.readContract({
    address: tokenAddress,
    abi: TOKEN_ABI,
    functionName: 'symbol',
  })
}
```

### GraphQL Type Inconsistencies

Different queries expect different GraphQL types for the same conceptual values. This causes silent failures if you use the wrong type:

| Query | projectId type | chainId type | version type |
|-------|---------------|--------------|--------------|
| `project()` | `Float!` | `Float!` | `Float!` |
| `payEvents()` | `Int!` | `Int!` | `Int!` |
| `participants()` | `Int!` | `Int` | - |
| `projects()` | - | - | - |

**Example of the issue:**

```graphql
# This works (project query uses Float)
query GetProject($projectId: Float!, $chainId: Float!, $version: Float!) {
  project(projectId: $projectId, chainId: $chainId, version: $version) { ... }
}

# This fails silently if you pass Float instead of Int
query GetPayEvents($projectId: Int!, $chainId: Int!, $version: Int!) {
  payEvents(where: { projectId: $projectId, chainId: $chainId, version: $version }) { ... }
}
```

**Best practice:** Check the schema or use the GraphQL playground to verify expected types for each query.

### SuckerGroup Cross-Chain Aggregation

For omnichain projects, use `suckerGroupId` to get aggregated data across all chains instead of querying each chain separately:

```javascript
// INEFFICIENT: Query each chain separately
const chains = [1, 10, 8453, 42161]
const balances = await Promise.all(
  chains.map(chainId => getProjectBalance(projectId, chainId))
)
const totalBalance = balances.reduce((sum, b) => sum + b, 0n)

// EFFICIENT: Use suckerGroup for cross-chain totals
const project = await getProject(projectId, chainId)
if (project.suckerGroupId) {
  const group = await getSuckerGroup(project.suckerGroupId)
  // group.balance is already the cross-chain total
  // group.projects_rel has per-chain breakdown
}
```

The `suckerGroup` query returns:
- Pre-aggregated totals (`balance`, `volume`, `tokenSupply`, etc.)
- Per-chain breakdown via `projects_rel`
- Consistent data without race conditions from parallel queries

### ETH vs USDC Project Currency

**CRITICAL:** Projects can use different base currencies (ETH or USDC). The `amount`, `balance`, and `volume` fields use different decimal precision depending on the currency:

| Currency | Decimals | Code |
|----------|----------|------|
| ETH | 18 | 1 |
| USDC | 6 | 2 |

The currency info is available from the `suckerGroup` or `participants` query:

```graphql
query GetSuckerGroup($id: String!) {
  suckerGroup(id: $id) {
    projects_rel {
      projectId
      chainId
      decimals       # 18 for ETH, 6 for USDC
      currency       # 1 for ETH, 2 for USDC
      balance
    }
  }
}
```

**Formatting amounts correctly:**

```javascript
import { formatUnits } from 'viem'

function formatAmount(wei, decimals, currency) {
  const num = parseFloat(formatUnits(BigInt(wei), decimals))
  const symbol = currency === 2 ? 'USDC' : 'ETH'
  // USDC uses fewer decimal places for display
  const precision = currency === 2 ? 2 : 4
  return `${num.toFixed(precision)} ${symbol}`
}

// Example: USDC project (6 decimals)
formatAmount('1000000', 6, 2)    // "1.00 USDC"

// Example: ETH project (18 decimals)
formatAmount('1000000000000000000', 18, 1)  // "1.0000 ETH"
```

**Common mistake:** Using `formatEther()` (assumes 18 decimals) for USDC projects will show wildly incorrect values. Always detect the currency first and use `formatUnits()` with the correct decimals.

---

## Best Practices

1. **Use server-side proxy** - Never expose API key in frontend code
2. **Cache responses** - Data updates every ~1 minute, cache accordingly
3. **Query only needed fields** - Reduces payload size and latency
4. **Use pagination** - Don't fetch thousands of records at once
5. **Handle nulls** - Fields like `volumeUsd`, `handle` may be null
6. **Consider freshness** - Indexer may lag 1-2 blocks behind chain
7. **Use filters** - Narrow queries by chainId, projectId when possible
8. **Always include version** - V4 and V5 projects with the same projectId are completely different
9. **Use BigInt for USD values** - volumeUsd is 18 decimals; parseFloat loses precision on large values
10. **Group by projectId + version** - Same project across chains should be grouped, but different versions should not
11. **Check GraphQL types** - Different queries expect Float vs Int for the same fields
12. **Use suckerGroup for cross-chain data** - More efficient than querying each chain separately
13. **Fetch token symbols from chain** - Bendystraw's tokenSymbol is the accounting token, not the project's issued token
14. **Detect currency before formatting** - Use `formatUnits(wei, decimals)` not `formatEther(wei)` since USDC projects use 6 decimals

---

## Use Cases

- **Project dashboards** - Display stats, activity, holders
- **Unified activity feeds** - Use `activityEvents` for all-in-one activity streams
- **Governance snapshots** - Get token balances at specific timestamps
- **Analytics** - Track trends, volumes, contributor growth via `projectMoments`
- **Portfolio tracking** - Use `wallet` query for user positions across all projects
- **Omnichain aggregation** - Unified view via `suckerGroup` and `suckerGroupMoments`
- **Airdrops** - Generate recipient lists from holder data
- **Loan dashboards** - Track RevLoans borrowing, repayments, liquidations
- **NFT galleries** - Full tier metadata via `nftTiers` including SVGs and pricing
- **Cross-chain tracking** - Monitor token bridging via `suckerTransactions`
- **Treasury management** - Track payouts and allowance usage

---

## Related Skills

- `/jb-relayr` - Execute multi-chain transactions
- `/jb-omnichain-ui` - Build UIs with Bendystraw data
- `/jb-query` - Direct on-chain queries via cast/ethers
- `/jb-revloans` - RevLoans protocol integration
- `/jb-loan-queries` - Loan-specific query patterns
- `/jb-nft-gallery-ui` - Build NFT galleries with tier data
