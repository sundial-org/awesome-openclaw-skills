---
name: jb-v5-api
description: Juicebox V5 protocol API reference. Function signatures, parameters, and return values for all contracts. Use for "what functions exist?" and "what are the signatures?" questions. For internal mechanics and tradeoffs, use /jb-v5-impl instead.
---

# Juicebox V5 API Reference

Function signatures, parameters, and return values for the entire Juicebox V5 protocol ecosystem.

> **Note**: For deep implementation details, edge cases, and tradeoffs, use `/jb-v5-impl` instead.

## Protocol Architecture Overview

The V5 protocol consists of interconnected repositories:

| Repository | Purpose |
|------------|---------|
| **nana-core-v5** | Core infrastructure: projects, rulesets, tokens, terminals |
| **nana-suckers-v5** | Cross-chain token bridging via merkle proofs |
| **nana-buyback-hook-v5** | Uniswap V3 token buyback integration |
| **nana-swap-terminal-v5** | Accept any token, auto-swap to ETH |
| **nana-721-hook-v5** | Tiered NFT minting on payment |
| **nana-permission-ids-v5** | Permission ID constants |
| **nana-ownable-v5** | Juicebox-aware ownership pattern |
| **nana-omnichain-deployers-v5** | Multi-chain project deployment |
| **revnet-core-v5** | Autonomous tokenized treasury networks |
| **croptop-core-v5** | Public NFT posting and contribution |

---

## NANA-CORE-V5: Core Protocol

### Contract Layers

**Core Contracts** (State Management):
- `JBProjects` - ERC-721 project ownership
- `JBRulesets` - Time-bounded configuration queuing
- `JBTokens` - Credit and ERC-20 accounting
- `JBDirectory` - Terminal and controller mapping
- `JBPermissions` - Access control delegation
- `JBFundAccessLimits` - Withdrawal constraints
- `JBPrices` - Currency price feeds
- `JBSplits` - Payment distribution lists

**Surface Contracts** (User Entry Points):
- `JBController` - Ruleset and token coordination
- `JBMultiTerminal` - Payments, cash outs, distributions
- `JBTerminalStore` - Transaction bookkeeping

**Utility Contracts**:
- `JBDeadline` - Ruleset approval with advance notice
- `JBERC20` - Standard project token
- `JBFeelessAddresses` - Fee exemption registry
- `JBChainlinkV3PriceFeed` - Chainlink integration

---

### JBController Functions

#### Project Lifecycle

```solidity
// Create a new project with initial rulesets
function launchProjectFor(
    address owner,                              // Receives project NFT
    string calldata projectUri,                 // IPFS metadata URI
    JBRulesetConfig[] calldata rulesetConfigurations,
    JBTerminalConfig[] calldata terminalConfigurations,
    string calldata memo
) external returns (uint256 projectId);

// Queue rulesets for existing project (first time setup)
function launchRulesetsFor(
    uint256 projectId,
    JBRulesetConfig[] calldata rulesetConfigurations,
    JBTerminalConfig[] calldata terminalConfigurations,
    string calldata memo
) external returns (uint256 rulesetId);

// Add rulesets to end of queue
function queueRulesetsOf(
    uint256 projectId,
    JBRulesetConfig[] calldata rulesetConfigurations,
    string calldata memo
) external returns (uint256 rulesetId);

// Migrate to a different controller
function migrate(uint256 projectId, IERC165 to) external;
```

#### Token Operations

```solidity
// Mint tokens to beneficiary
function mintTokensOf(
    uint256 projectId,
    uint256 tokenCount,
    address beneficiary,
    string calldata memo,
    bool useReservedPercent    // Apply reserved rate?
) external returns (uint256 beneficiaryTokenCount);

// Burn tokens from holder
function burnTokensOf(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    string calldata memo
) external;

// Deploy ERC-20 for project (enables token claiming)
function deployERC20For(
    uint256 projectId,
    string calldata name,
    string calldata symbol,
    bytes32 salt              // For deterministic address
) external returns (IJBToken token);

// Convert credits to ERC-20 tokens
function claimTokensFor(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    address beneficiary
) external;

// Transfer credits between addresses
function transferCreditsFrom(
    address holder,
    uint256 projectId,
    address recipient,
    uint256 creditCount
) external;

// Distribute pending reserved tokens
function sendReservedTokensToSplitsOf(uint256 projectId)
    external returns (uint256);
```

#### Configuration

```solidity
// Update project metadata URI
function setUriOf(uint256 projectId, string calldata uri) external;

// Set project's ERC-20 token
function setTokenFor(uint256 projectId, IJBToken token) external;

// Update split groups
function setSplitGroupsOf(
    uint256 projectId,
    uint256 rulesetId,
    JBSplitGroup[] calldata splitGroups
) external;

// Add price feed for currency conversion
function addPriceFeed(
    uint256 projectId,
    uint256 pricingCurrency,
    uint256 unitCurrency,
    IJBPriceFeed feed
) external;
```

#### View Functions

```solidity
function currentRulesetOf(uint256 projectId)
    external view returns (JBRuleset, JBRulesetMetadata);

function upcomingRulesetOf(uint256 projectId)
    external view returns (JBRuleset, JBRulesetMetadata);

function latestQueuedRulesetOf(uint256 projectId)
    external view returns (JBRuleset, JBRulesetMetadata, JBApprovalStatus);

function getRulesetOf(uint256 projectId, uint256 rulesetId)
    external view returns (JBRuleset, JBRulesetMetadata);

function allRulesetsOf(uint256 projectId, uint256 startingId, uint256 size)
    external view returns (JBRulesetWithMetadata[]);

function totalTokenSupplyWithReservedTokensOf(uint256 projectId)
    external view returns (uint256);

function setTerminalsAllowed(uint256 projectId) external view returns (bool);
function setControllerAllowed(uint256 projectId) external view returns (bool);
```

---

### JBTokens Functions

Manages project token accounting, including credits (unclaimed balances) and ERC20 tokens.

#### Token Deployment

```solidity
// Deploy standard JBERC20 for a project
function deployERC20For(
    uint256 projectId,
    string calldata name,
    string calldata symbol,
    bytes32 salt              // For deterministic address (0 for non-deterministic)
) external returns (IJBToken token);

// Set a custom ERC20 as the project token
function setTokenFor(
    uint256 projectId,
    IJBToken token            // Must implement IJBToken interface
) external;
```

#### Token Operations

```solidity
// Mint tokens to a holder (called by controller)
function mintFor(
    address holder,
    uint256 projectId,
    uint256 count
) external;

// Burn tokens from a holder (called by controller)
function burnFrom(
    address holder,
    uint256 projectId,
    uint256 count
) external;

// Convert credits to ERC20 tokens
function claimTokensFor(
    address holder,
    uint256 projectId,
    uint256 count,
    address beneficiary
) external;

// Transfer credits between addresses
function transferCreditsFrom(
    address holder,
    uint256 projectId,
    address recipient,
    uint256 count
) external;
```

#### View Functions

```solidity
// Get the ERC20 token for a project (address(0) if credits-only)
function tokenOf(uint256 projectId) external view returns (IJBToken);

// Get the project ID for a token
function projectIdOf(IJBToken token) external view returns (uint256);

// Get credit balance for a holder
function creditBalanceOf(address holder, uint256 projectId) external view returns (uint256);

// Get total credit supply for a project
function totalCreditSupplyOf(uint256 projectId) external view returns (uint256);

// Get total balance (credits + ERC20) for a holder
function totalBalanceOf(address holder, uint256 projectId) external view returns (uint256);

// Get total supply (credits + ERC20) for a project
function totalSupplyOf(uint256 projectId) external view returns (uint256);
```

#### IJBToken Interface (for Custom Tokens)

Custom tokens must implement this interface:

```solidity
interface IJBToken is IERC20 {
    // Standard ERC20 functions (name, symbol, decimals, totalSupply, balanceOf, transfer, etc.)

    /// @notice Check if this token can be added to a project.
    /// @dev Must return true for setTokenFor() to succeed.
    function canBeAddedTo(uint256 projectId) external view returns (bool);

    /// @notice Mint tokens. Called by JBTokens on payments.
    function mint(address holder, uint256 amount) external;

    /// @notice Burn tokens. Called by JBTokens on cash outs.
    function burn(address holder, uint256 amount) external;
}
```

#### Custom Token Requirements

| Requirement | Details |
|-------------|---------|
| **18 decimals** | `decimals()` must return 18 |
| **canBeAddedTo** | Must return true for the target project ID |
| **Unique assignment** | Cannot be assigned to multiple projects |
| **Controller access** | Must allow JBController to mint/burn |

---

### JBMultiTerminal Functions

#### Payments

```solidity
// Pay a project
function pay(
    uint256 projectId,
    address token,              // address(0) for native
    uint256 amount,
    address beneficiary,        // Receives minted tokens
    uint256 minReturnedTokens,  // Slippage protection
    string calldata memo,
    bytes calldata metadata     // Hook data
) external payable returns (uint256 beneficiaryTokenCount);

// Add funds without minting tokens
function addToBalanceOf(
    uint256 projectId,
    address token,
    uint256 amount,
    bool shouldReturnHeldFees,
    string calldata memo,
    bytes calldata metadata
) external payable;
```

#### Cash Outs (Redemptions)

```solidity
// Cash out tokens for funds
function cashOutTokensOf(
    address holder,
    uint256 projectId,
    uint256 cashOutCount,       // Tokens to burn
    address tokenToReclaim,     // Which token to receive
    uint256 minTokensReclaimed, // Slippage protection
    address payable beneficiary,
    bytes calldata metadata
) external returns (uint256 reclaimAmount);
```

#### Distributions

```solidity
// Send payouts to splits (within payout limit)
function sendPayoutsOf(
    uint256 projectId,
    address token,
    uint256 amount,
    uint256 currency,
    uint256 minTokensPaidOut
) external returns (uint256 amountPaidOut);

// Use surplus allowance (discretionary withdrawal)
function useAllowanceOf(
    uint256 projectId,
    address token,
    uint256 amount,
    uint256 currency,
    uint256 minTokensPaidOut,
    address payable beneficiary,
    address payable feeBeneficiary,
    string calldata memo
) external returns (uint256 netAmountPaidOut);
```

#### Terminal Management

```solidity
// Add token accounting contexts
function addAccountingContextsFor(
    uint256 projectId,
    JBAccountingContext[] calldata accountingContexts
) external;

// Migrate to new terminal
function migrateBalanceOf(
    uint256 projectId,
    address token,
    IJBTerminal to
) external returns (uint256 balance);

// Process held fees
function processHeldFeesOf(
    uint256 projectId,
    address token,
    uint256 count
) external;
```

#### View Functions

```solidity
function currentSurplusOf(
    uint256 projectId,
    JBAccountingContext[] memory accountingContexts,
    uint256 decimals,
    uint256 currency
) external view returns (uint256);

function accountingContextsOf(uint256 projectId)
    external view returns (JBAccountingContext[]);

function accountingContextForTokenOf(uint256 projectId, address token)
    external view returns (JBAccountingContext);

function heldFeesOf(uint256 projectId, address token, uint256 count)
    external view returns (JBFee[]);
```

---

## NANA-SUCKERS-V5: Cross-Chain Bridging

### What Are Suckers?

Suckers enable cross-chain token transfers between Juicebox projects. When a user burns tokens on one chain, they receive equivalent tokens on another chain. The sucker redeems locally and bridges funds to the peer network.

### Supported Bridges

- `JBOptimismSucker` - Ethereum ↔ Optimism
- `JBBaseSucker` - Ethereum ↔ Base
- `JBArbitrumSucker` - Ethereum ↔ Arbitrum

### Core Functions

```solidity
// Prepare tokens for bridging (burns locally)
function prepare(
    uint256 projectTokenAmount,
    address beneficiary,
    uint256 minTokensReclaimed,
    address tokenToReclaim
) external returns (uint256 terminalTokenAmount);

// Bridge outbox tree to remote chain
function toRemote(address token) external payable;

// Claim tokens on remote chain with merkle proof
function claim(JBClaim[] calldata claims) external;

// Get merkle root for verification
function outboxTreeRoot(address token) external view returns (bytes32);
```

### Requirements for Projects

- Present on both chains with same project ID
- 100% cash out rate enabled
- Owner minting enabled
- ERC-20 tokens deployed on both chains

---

## NANA-BUYBACK-HOOK-V5: Token Buybacks

### Purpose

Automatically routes payments through Uniswap V3 when swapping yields more tokens than direct minting. Acts as both a data hook and pay hook.

### How It Works

1. `beforePayRecordedWith()` compares: mint tokens vs. swap tokens
2. If swap is better, specifies this contract as pay hook with swap amount
3. `afterPayRecordedWith()` executes swap, burns received tokens, re-mints with reserved rate

### Core Functions

```solidity
// Set Uniswap pool for a project
function setPoolFor(
    uint256 projectId,
    address token,
    uint24 fee,
    uint32 twapWindow,
    uint256 twapSlippageTolerance
) external;

// Get pool configuration
function poolOf(uint256 projectId, address token)
    external view returns (IUniswapV3Pool);

// Data hook: determine payment route
function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
    external view returns (uint256 weight, JBPayHookSpecification[]);

// Pay hook: execute swap if beneficial
function afterPayRecordedWith(JBAfterPayRecordedContext calldata context)
    external payable;
```

---

## NANA-SWAP-TERMINAL-V5: Multi-Token Acceptance

### Purpose

Accept payments in any ERC-20 token and automatically swap to ETH/native token via Uniswap V3.

### Flow

1. User pays with any token (e.g., USDC)
2. Terminal swaps to ETH via configured Uniswap pool
3. ETH forwarded to primary terminal
4. Tokens minted for beneficiary

### Core Functions

```solidity
// Pay with any token (auto-swaps to ETH)
function pay(
    uint256 projectId,
    address token,              // Any ERC-20
    uint256 amount,
    address beneficiary,
    uint256 minReturnedTokens,
    string calldata memo,
    bytes calldata metadata     // Can include swap params
) external returns (uint256 beneficiaryTokenCount);

// Configure default Uniswap pool for token
function addDefaultPool(
    uint256 projectId,
    address token,
    IUniswapV3Pool pool
) external;
```

---

## NANA-721-HOOK-V5: Tiered NFTs

### Purpose

Mint tiered NFTs (ERC-721) when payments are received. Each tier has configurable price, supply, artwork, and voting power.

### Tier Properties

- **price**: Cost to mint from this tier
- **initialSupply**: Maximum mintable quantity
- **votingUnits**: Governance votes per NFT
- **reserveFrequency**: Auto-mint 1 bonus per N purchased
- **category**: Grouping for organization
- **encodedIPFSUri**: Artwork/metadata location
- **allowOwnerMint**: Owner can mint directly
- **transfersPausable**: Can restrict transfers

### Core Functions

```solidity
// Data hook: specify NFT minting
function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
    external view returns (uint256 weight, JBPayHookSpecification[]);

// Pay hook: mint NFTs based on payment
function afterPayRecordedWith(JBAfterPayRecordedContext calldata context)
    external payable;

// Cash out hook: burn NFTs to reclaim funds
function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context)
    external payable;

// Get tiers for a hook
function tiersOf(
    address hook,
    uint256[] calldata categories,
    bool includeResolvedUri,
    uint256 startingId,
    uint256 size
) external view returns (JB721Tier[]);

// Adjust tiers (add/remove)
function adjustTiers(JB721TierConfig[] calldata tierConfigs) external;

// Owner mint from specific tiers
function mintFor(
    uint256[] calldata tierIds,
    address beneficiary
) external returns (uint256[] tokenIds);
```

---

## NANA-PERMISSION-IDS-V5: Access Control

### All Permission IDs

| ID | Name | Allows |
|----|------|--------|
| 1 | ROOT | All operations (superuser) |
| 2 | QUEUE_RULESETS | Queue new rulesets |
| 3 | CASH_OUT_TOKENS | Cash out tokens on behalf of holder |
| 4 | SEND_PAYOUTS | Trigger payout distributions |
| 5 | MIGRATE_TERMINAL | Migrate terminal balance |
| 6 | SET_PROJECT_URI | Update project metadata URI |
| 7 | DEPLOY_ERC20 | Deploy ERC-20 token for project |
| 8 | SET_TOKEN | Set project's token |
| 9 | MINT_TOKENS | Mint project tokens |
| 10 | BURN_TOKENS | Burn tokens |
| 11 | CLAIM_TOKENS | Convert credits to ERC-20 |
| 12 | TRANSFER_CREDITS | Transfer credits between addresses |
| 13 | SET_CONTROLLER | Change project controller |
| 14 | SET_TERMINALS | Modify project terminals |
| 15 | SET_PRIMARY_TERMINAL | Set primary terminal for token |
| 16 | USE_ALLOWANCE | Use surplus allowance |
| 17 | SET_SPLIT_GROUPS | Modify split groups |
| 18 | ADD_PRICE_FEED | Add currency price feed |
| 19 | ADD_ACCOUNTING_CONTEXTS | Add token acceptance |
| 20 | ADJUST_721_TIERS | Modify NFT tiers |
| 21 | SET_721_METADATA | Update NFT metadata |
| 22 | MINT_721 | Mint NFTs directly |
| 23 | SET_721_DISCOUNT_PERCENT | Set NFT discount |
| 24 | SET_BUYBACK_TWAP | Configure buyback TWAP |
| 25 | SET_BUYBACK_POOL | Set buyback Uniswap pool |
| 26 | ADD_SWAP_TERMINAL_POOL | Add swap terminal pool |
| 27 | ADD_SWAP_TERMINAL_TWAP_PARAMS | Set swap terminal TWAP |
| 28 | MAP_SUCKER_TOKEN | Map sucker token |
| 29 | DEPLOY_SUCKERS | Deploy cross-chain suckers |
| 30 | SUCKER_SAFETY | Sucker safety operations |

### Permission Ranges by Repository

| ID Range | Repository |
|----------|------------|
| 1 | ROOT (all contracts) |
| 2-19 | nana-core |
| 20-23 | nana-721-hook |
| 24-25 | nana-buyback-hook |
| 26-27 | nana-swap-terminal |
| 28-30 | nana-suckers |

### JBPermissions Functions

```solidity
// Grant permissions
function setPermissionsFor(
    address account,
    JBPermissionsData calldata permissionsData
) external;

// Check permission
function hasPermission(
    address operator,
    address account,
    uint256 projectId,
    uint256 permissionId,
    bool includeRoot,
    bool includeWildcardProjectId
) external view returns (bool);

// Get all permissions for operator
function permissionsOf(
    address operator,
    address account,
    uint256 projectId
) external view returns (uint256);
```

---

## NANA-OWNABLE-V5: Project-Based Ownership

### Purpose

Extend OpenZeppelin Ownable to support Juicebox project ownership and permission delegation.

### Key Features

1. **Project Ownership**: Transfer ownership to a Juicebox project (any project owner has access)
2. **Permission Delegation**: Grant `onlyOwner` access via JBPermissions
3. **Meta-Transaction Support**: Compatible with ERC-2771

### Contracts

- `JBOwnable` - For contracts without existing ownership
- `JBOwnableOverride` - For contracts inheriting OpenZeppelin Ownable

---

## NANA-OMNICHAIN-DEPLOYERS-V5: Multi-Chain Deployment

### Purpose

Deploy Juicebox projects with suckers across multiple chains in a single transaction.

### Supported Networks

- Ethereum Mainnet
- Sepolia Testnet
- Optimism Mainnet/Testnet

### Usage

Deploy project configuration that automatically sets up:
- Project on each target chain
- Sucker pairs for cross-chain bridging
- Consistent project configuration

---

## REVNET-CORE-V5: Autonomous Treasury Networks

### What Is a Revnet?

A Revnet is an **unowned Juicebox project** that operates autonomously after deployment. The deployer contract owns the project NFT, implementing hooks and delegating limited permissions.

### Deployer Options

| Deployer | Features |
|----------|----------|
| `BasicRevnetDeployer` | Standard revnet |
| `PayHookRevnetDeployer` | + custom pay hooks |
| `Tiered721RevnetDeployer` | + tiered NFT support |
| `CroptopRevnetDeployer` | + public posting |

### Key Concepts

**Stages**: Revnets progress through stages with different parameters
- Initial weight, price ceiling, price floor
- Reserved rate distribution
- Boost periods for early supporters

**Premint**: Tokens minted to beneficiaries at launch

**Boost**: Temporary increased token allocation for specified recipients

### REVDeployer Functions

```solidity
// Deploy a new revnet
function deployFor(
    uint256 revnetId,
    REVConfig calldata configuration,
    JBTerminalConfig[] calldata terminalConfigurations,
    REVBuybackHookConfig calldata buybackHookConfiguration,
    REVSuckerDeploymentConfig calldata suckerDeploymentConfiguration
) external returns (uint256 projectId);

// Data hook: route payments through buyback
function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
    external view returns (uint256 weight, JBPayHookSpecification[]);

// Cash out hook: extract fees
function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context)
    external payable;
```

---

## CROPTOP-CORE-V5: Public NFT Posting

### What Is Croptop?

Croptop opens a project's NFT collection for public contributions. Anyone can post new NFT tiers if they meet criteria set by the project owner.

### CTPublisher Functions

```solidity
// Configure posting criteria
function configurePostingCriteriaFor(
    IJB721TiersHook hook,
    uint256 category,
    uint256 minimumPrice,
    uint256 minimumTotalSupply,
    uint256 maximumTotalSupply,
    address[] calldata allowedAddresses
) external;

// Post new NFT and mint initial copies
function mintFrom(
    IJB721TiersHook hook,
    JBDeploy721TierConfig[] calldata tierConfigs,
    address beneficiary,
    address payable feeBeneficiary,
    bytes calldata additionalPayMetadata
) external payable;

// Get posting criteria
function allowanceFor(IJB721TiersHook hook, uint256 category)
    external view returns (CTAllowedPost);

// Get tier data for URIs
function tiersFor(IJB721TiersHook hook, string[] calldata uris)
    external view returns (JB721Tier[]);
```

### Posting Flow

1. Owner calls `configurePostingCriteriaFor()` with price/supply requirements
2. Anyone posts via `mintFrom()` with tier config and payment
3. System validates against criteria (price ≥ minimum, supply within range)
4. NFT tier created, fee (1/20th) sent to fee treasury
5. Beneficiary receives initial mint

---

## Fee Structure

### Standard Fees (2.5%)

Applied by JBMultiTerminal on:
- Payouts to wallets (project-to-project exempt)
- Surplus allowance withdrawals
- Cash outs with < 100% cash out rate

### Fee Processing

- Fees route to Project #1 (protocol treasury)
- "Held fees" mode allows 28-day refund window
- Feeless addresses can be registered for exemption

---

## Protocol Constants

```solidity
// Native token identifier
address constant NATIVE_TOKEN = 0x000000000000000000000000000000000000EEEe;

// Max values
uint256 constant MAX_RESERVED_RATE = 10000;      // 100%
uint256 constant MAX_CASH_OUT_TAX_RATE = 10000;  // 100%
uint256 constant MAX_FEE = 250;                   // 2.5%

// Split percent precision
uint256 constant SPLITS_TOTAL_PERCENT = 1_000_000_000;  // 100%
```

---

## Example Workflows

### Create Project with Buyback Hook

1. Deploy `JBBuybackHook` for your token
2. Call `launchProjectFor()` with ruleset metadata:
   - `useDataHookForPay: true`
   - `dataHook: buybackHookAddress`
3. Payments automatically route through Uniswap when beneficial

### Deploy a Revnet

1. Choose deployer (Basic, PayHook, Tiered721, Croptop)
2. Configure stages, premint, boost parameters
3. Call `deployFor()` with configuration
4. Revnet operates autonomously

### Enable Cross-Chain

1. Deploy project on both chains with same ID
2. Deploy sucker pair via `JBSuckerRegistry`
3. Enable 100% cash out rate and owner minting
4. Users can `prepare()` on one chain, `claim()` on other

---

## Source Repositories

- [nana-core-v5](https://github.com/Bananapus/nana-core-v5)
- [nana-suckers-v5](https://github.com/Bananapus/nana-suckers-v5)
- [nana-buyback-hook-v5](https://github.com/Bananapus/nana-buyback-hook-v5)
- [nana-swap-terminal-v5](https://github.com/Bananapus/nana-swap-terminal-v5)
- [nana-721-hook-v5](https://github.com/Bananapus/nana-721-hook-v5)
- [nana-permission-ids-v5](https://github.com/Bananapus/nana-permission-ids-v5)
- [nana-ownable-v5](https://github.com/Bananapus/nana-ownable-v5)
- [nana-omnichain-deployers-v5](https://github.com/Bananapus/nana-omnichain-deployers-v5)
- [revnet-core-v5](https://github.com/rev-net/revnet-core-v5)
- [croptop-core-v5](https://github.com/mejango/croptop-core-v5)
