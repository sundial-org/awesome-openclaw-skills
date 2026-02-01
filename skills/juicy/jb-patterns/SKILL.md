---
name: jb-patterns
description: |
  Common Juicebox V5 design patterns for vesting, NFT treasuries, terminal wrappers, yield integration, and
  governance-minimal configurations. Use when: (1) need treasury vesting without custom contracts, (2) building
  NFT-gated redemptions, (3) extending revnet functionality via pay wrappers, (4) implementing custom ERC20
  tokens, (5) integrating yield protocols like Aave, (6) deciding between native mechanics vs custom code.
  Covers 11 patterns including terminal wrapper for dynamic pay-time splits, yield-generating hooks for
  Aave/DeFi integration, and token interception. Golden rule: prefer configuration over custom contracts.
---

# Juicebox V5 Design Patterns

Proven patterns for common use cases using native Juicebox mechanics. **Always prefer configuration over custom contracts.**

## Golden Rule

> Before writing custom code, ask: "Can this be achieved with payout limits, surplus allowance, splits, and cycling rulesets?"

---

## Pattern 1: Vesting via Native Mechanics

**Use case**: Release funds to a beneficiary over time (e.g., team vesting, milestone-based releases)

**Solution**: Use cycling rulesets with payout limits

### How It Works

| Mechanism | Behavior | Use For |
|-----------|----------|---------|
| **Payout Limit** | Resets each cycle | Recurring distributions (vesting) |
| **Surplus Allowance** | One-time per ruleset | Discretionary treasury access |
| **Cycle Duration** | Determines distribution frequency | Monthly = 30 days |

### Configuration

```solidity
JBRulesetConfig({
    duration: 30 days,                    // Monthly cycles
    // ... other config
    fundAccessLimitGroups: [
        JBFundAccessLimitGroup({
            terminal: address(TERMINAL),
            token: JBConstants.NATIVE_TOKEN,
            payoutLimits: [
                JBCurrencyAmount({
                    amount: 6.67 ether,   // Monthly vesting amount
                    currency: nativeCurrency
                })
            ],
            surplusAllowances: [
                JBCurrencyAmount({
                    amount: 20 ether,     // One-time treasury (doesn't reset)
                    currency: nativeCurrency
                })
            ]
        })
    ]
});
```

### Capital Flow

```
Month 0: Balance = 100 ETH
         Surplus = Balance - Payout Limit = 93.33 ETH (redeemable)

Month 1: Team calls sendPayoutsOf() → receives 6.67 ETH
         Balance = 93.33 ETH
         Surplus = 86.67 ETH

Month 12: All vested, Balance = 20 ETH (treasury allowance)
```

### Key Insight

- **Payout limits protect vesting funds** from redemption
- **Surplus = unvested funds** available for token holder cash outs
- **No custom contracts needed**

---

## Pattern 2: NFT-Gated Treasury

**Use case**: Sell NFTs, allow holders to redeem against treasury surplus

**Solution**: Use nana-721-hook-v5 with native cash outs

### Configuration

1. Deploy project with `JB721TiersHookProjectDeployer`
2. Configure 721 hook as data hook for pay AND cash out
3. Set `cashOutTaxRate: 0` for full redemption value

```solidity
JBRulesetMetadata({
    cashOutTaxRate: 0,              // Full redemption
    useDataHookForPay: true,        // 721 hook mints NFTs
    useDataHookForCashOut: true,    // 721 hook handles burns
    dataHook: address(0),           // Set by deployer
    // ...
});
```

### How Cash Outs Work

1. User calls `cashOutTokensOf()` on terminal
2. 721 hook intercepts, calculates: `(NFT price / total prices) × surplus`
3. NFT is burned, ETH sent to user

**No custom cash out hook needed** - the 721 hook handles everything.

---

## Pattern 3: Governance-Minimal Treasury

**Use case**: Immutable treasury with no admin controls

**Solution**: Transfer ownership to burn address after setup

### Configuration

```solidity
// 1. Deploy project with restrictive metadata
JBRulesetMetadata({
    allowOwnerMinting: false,
    allowTerminalMigration: false,
    allowSetTerminals: false,
    allowSetController: false,
    allowAddAccountingContext: false,
    allowAddPriceFeed: false,
    // ...
});

// 2. After deployment, burn ownership
PROJECTS.transferFrom(deployer, 0x000000000000000000000000000000000000dEaD, projectId);
```

### What This Achieves

- No one can change rulesets
- No one can add/remove terminals
- No one can mint tokens arbitrarily
- Payouts/cash outs work as configured forever

---

## Pattern 4: Split Recipients Without Custom Hooks

**Use case**: Distribute payouts to multiple addresses

**Solution**: Use native splits with direct beneficiaries

### Configuration

```solidity
JBSplit[] memory splits = new JBSplit[](3);

splits[0] = JBSplit({
    percent: 500_000_000,           // 50%
    beneficiary: payable(team1),
    projectId: 0,
    hook: IJBSplitHook(address(0)), // No hook needed!
    // ...
});

splits[1] = JBSplit({
    percent: 300_000_000,           // 30%
    beneficiary: payable(team2),
    // ...
});

splits[2] = JBSplit({
    percent: 200_000_000,           // 20%
    beneficiary: payable(treasury),
    // ...
});
```

**Only use split hooks when you need custom logic** (e.g., swapping tokens, adding to LP).

---

## Pattern 5: NFT + Vesting Combined

**Use case**: Sell NFTs with funds vesting to team over time, holders can exit by burning

**Solution**: Combine patterns 1 + 2

### Architecture

```
┌─────────────────────────────────────────────────┐
│  JB Project with 721 Hook                       │
│                                                 │
│  • NFT tier: 100 supply, 1 ETH each            │
│  • Payout limit: 6.67 ETH/month (vesting)      │
│  • Surplus allowance: 20 ETH (treasury)        │
│  • Cash out tax: 0%                            │
│  • Owner: burn address                         │
│                                                 │
│  Treasury Flow:                                │
│  ├── Month 0: 80 ETH surplus (all unvested)   │
│  ├── Month 6: 40 ETH surplus                  │
│  └── Month 12: 0 ETH surplus (fully vested)   │
│                                                 │
│  NFT Holder: Can burn anytime for pro-rata    │
│              share of current surplus          │
└─────────────────────────────────────────────────┘
```

### Complete Example

See the Drip x Juicebox deployment script for a full implementation:
- 100 NFTs at 1 ETH each
- 20 ETH immediate treasury (surplus allowance)
- 80 ETH vests over 12 months (payout limits)
- NFT holders can burn to exit at any time
- Zero custom contracts

---

## Pattern 6: Custom NFT Content via Resolver

**Use case**: NFT project with custom artwork, composable assets, or dynamic metadata while using 721-hook off-the-shelf

**Solution**: Implement `IJB721TokenUriResolver` for custom content, use standard 721-hook for treasury mechanics

### Why This Pattern?

The 721-hook handles all the hard stuff:
- Payment processing and tier selection
- Token minting and supply tracking
- Cash out weight calculations
- Reserved token mechanics

You only need custom code for **content generation** (artwork, metadata, composability).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Standard 721-Hook (off-the-shelf)                          │
│  ├── Handles payments, minting, cash outs                   │
│  ├── Manages tier supply and pricing                        │
│  └── Calls tokenUriResolver.tokenUriOf() for metadata       │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Custom TokenUriResolver (your code)                │   │
│  │  ├── Implements IJB721TokenUriResolver              │   │
│  │  ├── tokenUriOf() → dynamic SVG/metadata            │   │
│  │  └── Custom behaviors (composability, decoration)   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Interface

```solidity
interface IJB721TokenUriResolver {
    /// @notice Get the token URI for a given token.
    /// @param hook The 721 hook address.
    /// @param tokenId The token ID.
    /// @return The token URI (typically base64-encoded JSON with SVG).
    function tokenUriOf(address hook, uint256 tokenId)
        external view returns (string memory);
}
```

### Basic Resolver Implementation

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {IJB721TokenUriResolver} from "@bananapus/721-hook/src/interfaces/IJB721TokenUriResolver.sol";
import {IJB721TiersHook} from "@bananapus/721-hook/src/interfaces/IJB721TiersHook.sol";

contract CustomTokenUriResolver is IJB721TokenUriResolver {
    /// @notice Generate token URI with custom artwork/metadata.
    function tokenUriOf(address hook, uint256 tokenId)
        external view override returns (string memory)
    {
        // Get tier info from the hook
        IJB721TiersHook tiersHook = IJB721TiersHook(hook);
        uint256 tierId = tiersHook.tierIdOfToken(tokenId);

        // Generate your custom metadata/artwork
        string memory name = _getNameForTier(tierId);
        string memory svg = _generateSvgForToken(tokenId, tierId);

        // Return base64-encoded JSON
        return string(abi.encodePacked(
            "data:application/json;base64,",
            Base64.encode(bytes(abi.encodePacked(
                '{"name":"', name, '",',
                '"image":"data:image/svg+xml;base64,', Base64.encode(bytes(svg)), '"}'
            )))
        ));
    }

    function _getNameForTier(uint256 tierId) internal view returns (string memory) {
        // Your tier naming logic
    }

    function _generateSvgForToken(uint256 tokenId, uint256 tierId) internal view returns (string memory) {
        // Your SVG generation logic
    }
}
```

### Advanced: Composable NFTs (Banny Pattern)

For composable NFTs where items can be attached to base tokens:

```solidity
contract ComposableTokenUriResolver is IJB721TokenUriResolver {
    // Track which items are attached to which base tokens
    mapping(address hook => mapping(uint256 baseTokenId => uint256[])) public attachedItems;

    // Prevent changes for a duration (e.g., 7 days)
    mapping(address hook => mapping(uint256 tokenId => uint256)) public lockedUntil;

    /// @notice Attach items to a base token.
    function decorateWith(
        address hook,
        uint256 baseTokenId,
        uint256[] calldata itemIds
    ) external {
        // Verify caller owns both base token and items
        require(IJB721TiersHook(hook).ownerOf(baseTokenId) == msg.sender);
        require(lockedUntil[hook][baseTokenId] < block.timestamp, "LOCKED");

        for (uint256 i; i < itemIds.length; i++) {
            require(IJB721TiersHook(hook).ownerOf(itemIds[i]) == msg.sender);
            // Transfer item to this contract (escrow while attached)
            IJB721TiersHook(hook).transferFrom(msg.sender, address(this), itemIds[i]);
        }

        attachedItems[hook][baseTokenId] = itemIds;
    }

    /// @notice Lock outfit changes for 7 days.
    function lockChangesFor(address hook, uint256 baseTokenId) external {
        require(IJB721TiersHook(hook).ownerOf(baseTokenId) == msg.sender);
        lockedUntil[hook][baseTokenId] = block.timestamp + 7 days;
    }

    /// @notice Generate composite SVG from base + attached items.
    function tokenUriOf(address hook, uint256 tokenId) external view override returns (string memory) {
        uint256[] memory items = attachedItems[hook][tokenId];

        // Generate layered SVG combining base + all attached items
        string memory svg = _generateCompositeSvg(hook, tokenId, items);

        return _encodeAsDataUri(svg);
    }
}
```

### Deployment Integration

```solidity
// 1. Deploy your custom resolver
CustomTokenUriResolver resolver = new CustomTokenUriResolver();

// 2. Configure 721 hook with resolver
REVDeploy721TiersHookConfig memory hookConfig = REVDeploy721TiersHookConfig({
    baseline721HookConfiguration: JBDeploy721TiersHookConfig({
        // ... tier configs
        tokenUriResolver: IJB721TokenUriResolver(address(resolver)),
        // ...
    }),
    // ...
});

// 3. Deploy project/revnet with hook config
deployer.deployWith721sFor(projectId, hookConfig, ...);
```

### When to Use This Pattern

| Requirement | Use Resolver? |
|-------------|---------------|
| Static tier images (IPFS) | No - use `encodedIPFSUri` in tier config |
| Dynamic/generative art | **Yes** |
| Composable/layered NFTs | **Yes** |
| On-chain SVG storage | **Yes** |
| Token-specific metadata | **Yes** |
| Standard ERC-721 metadata | No - use default |

### Reference Implementation

**banny-retail-v5**: https://github.com/mejango/banny-retail-v5
- `Banny721TokenUriResolver.sol` - Composable SVG NFTs with outfit decoration
- `Deploy.s.sol` - Deployment with custom resolver
- `Drop1.s.sol` - Adding tiers with custom categories

Key features demonstrated:
- On-chain SVG storage with hash verification
- Composable outfits (attach items to base Banny)
- Outfit locking (7-day freeze)
- Category-based slot system
- Multi-chain deployment via Revnet

---

## Pattern 7: Prediction Games with Dynamic Cash Out Weights

**Use case**: Games where outcomes determine payout distribution (prediction markets, fantasy sports, competitions)

**Solution**: Extend 721-hook with custom delegate, use on-chain governance for outcome resolution

### Why This Pattern Requires Extending 721-Hook

Unlike Pattern 6 (resolver-only), prediction games need to change **core treasury mechanics**:

| Requirement | Why Resolver Isn't Enough |
|-------------|---------------------------|
| Dynamic cash out weights | Cash out calculation is in the hook, not resolver |
| First-owner tracking | Rewards original minters, not current holders |
| Phase enforcement | Different rules per game phase |
| Governance integration | Scorecard ratification triggers weight changes |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Game Lifecycle (via Juicebox Rulesets)                     │
│                                                             │
│  COUNTDOWN → MINT → REFUND → SCORING → COMPLETE             │
│      │         │       │        │          │                │
│      │    Players   Early    Holders    Winners             │
│      │    mint      exit     vote on    cash out            │
│      │    NFTs      OK       scorecard  winnings            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Custom Delegate (extends JB721Hook)                        │
│  ├── Tracks first owners (for fair reward distribution)     │
│  ├── Phase-aware cash out logic                             │
│  ├── Dynamic tier weights (set by governor)                 │
│  └── Enforces phase restrictions                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Governor Contract                                          │
│  ├── NFT holders propose scorecards                         │
│  ├── Tier-weighted voting (own 25% of tier = 25% of votes)  │
│  ├── 50% quorum required for ratification                   │
│  └── Ratification sets tier cash out weights                │
└─────────────────────────────────────────────────────────────┘
```

### Game Phases

```solidity
enum DefifaGamePhase {
    COUNTDOWN,           // Game announced, no minting yet
    MINT,                // Players can mint NFTs (pick teams)
    REFUND,              // Early exit window (get mint cost back)
    SCORING,             // Game over, holders vote on scorecard
    COMPLETE,            // Scorecard ratified, winners cash out
    NO_CONTEST_INEVITABLE, // Not enough participation
    NO_CONTEST           // Game cancelled, full refunds
}
```

### Dynamic Cash Out Weights

Standard 721-hook: `cashOutWeight = tierPrice` (fixed)

Defifa pattern: `cashOutWeight = scorecardWeight[tierId]` (dynamic)

```solidity
// Total weight is 1e18 (100%), distributed among tiers by scorecard
uint256 constant TOTAL_CASH_OUT_WEIGHT = 1e18;

struct DefifaTierCashOutWeight {
    uint256 id;           // Tier ID
    uint256 cashOutWeight; // Share of total (e.g., 0.5e18 = 50%)
}

// Example: 4-team tournament, Team A wins
// Team A: 1e18 (100% of pot)
// Team B: 0
// Team C: 0
// Team D: 0

// Example: Fantasy league with scoring
// Team A (1st): 0.5e18 (50%)
// Team B (2nd): 0.3e18 (30%)
// Team C (3rd): 0.15e18 (15%)
// Team D (4th): 0.05e18 (5%)
```

### First Owner Tracking

Critical for fair games - rewards go to original minters, not secondary buyers:

```solidity
// Track who first minted each token
mapping(uint256 tokenId => address) public firstOwnerOf;

// In _processPayment():
firstOwnerOf[tokenId] = beneficiary;

// In cash out calculation:
// Only firstOwnerOf[tokenId] receives the full reward
// Current owner can transfer, but original minter gets payout
```

### Governor Voting

```solidity
// Attestation power = share of tier tokens you own
// If you own 25 of 100 tokens in Tier 1, you have 25% of Tier 1's voting power

function attestToScorecardFrom(
    address attester,
    DefifaScorecard calldata scorecard
) external {
    // Verify attester hasn't already voted
    // Add attester's voting power to scorecard
    // If quorum reached, scorecard can be ratified
}

function ratifyScorecard(DefifaScorecard calldata scorecard) external {
    // Verify scorecard has 50% attestation across all minted tiers
    // Set tier cash out weights on delegate
    // Game moves to COMPLETE phase
}
```

### When to Use This Pattern

| Use Case | Fits Pattern? |
|----------|---------------|
| Sports predictions | **Yes** - teams = tiers, outcomes = weights |
| Fantasy leagues | **Yes** - players draft teams, scoring determines payouts |
| Tournament brackets | **Yes** - bracket picks = tiers |
| Election predictions | **Yes** - candidates = tiers |
| Price predictions | **Yes** - price ranges = tiers |
| Art competitions | **Yes** - entries = tiers, votes = weights |
| Standard NFT collection | **No** - use Pattern 6 instead |
| Fixed-price redemptions | **No** - use native 721-hook |

### Key Implementation Considerations

1. **Phase transitions via rulesets**: Use ruleset durations to enforce timing
2. **Refund window**: Allow early exit before outcomes are known
3. **Quorum design**: Too high = deadlock, too low = manipulation
4. **First-owner vs current-owner**: Decide who receives rewards
5. **No-contest handling**: What if not enough participation?

### Reference Implementation

**defifa-collection-deployer-v5**: https://github.com/BallKidz/defifa-collection-deployer-v5

Key contracts:
- `DefifaDelegate.sol` - Extends JB721Hook with phase logic and dynamic weights
- `DefifaGovernor.sol` - On-chain voting for scorecard ratification
- `DefifaDeployer.sol` - Factory for launching games
- `DefifaTokenUriResolver.sol` - Dynamic metadata showing pot share

Features demonstrated:
- Phase-based game lifecycle
- Tier-weighted governance voting
- Dynamic cash out weight redistribution
- First-owner tracking for fair rewards
- No-contest handling for failed games

---

## Pattern 8: Custom ERC20 Project Tokens

**Use case**: Projects requiring custom tokenomics beyond standard mint/burn mechanics

**Solution**: Implement `IJBToken` interface and use `setTokenFor()` instead of `deployERC20For()`

### Why This Pattern?

Default Juicebox tokens (credits or JBERC20) work for most projects, but some use cases require custom token logic:

| Default Token Limitation | Custom Token Solution |
|--------------------------|----------------------|
| No transfer fees | Implement tax-on-transfer |
| Fixed supply mechanics | Use rebasing/elastic supply |
| No governance features | Extend ERC20Votes |
| Immutable name/symbol | Add setName/setSymbol functions |
| Uniform holder treatment | Add allowlists/denylists |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Juicebox Protocol (unchanged)                              │
│  ├── JBController calls mint/burn on token                  │
│  ├── JBTokens tracks credits + token supply                 │
│  └── JBMultiTerminal handles payments/cash outs             │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Custom ERC20 Token (your code)                     │   │
│  │  ├── Implements IJBToken interface                  │   │
│  │  ├── Authorizes JBController for mint/burn          │   │
│  │  ├── Uses 18 decimals (REQUIRED)                    │   │
│  │  └── Custom logic: taxes, rebasing, governance, etc │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Interface Requirements

```solidity
interface IJBToken is IERC20 {
    /// @notice Must return true for the target project ID
    function canBeAddedTo(uint256 projectId) external view returns (bool);

    /// @notice Called by JBController when payments are received
    function mint(address holder, uint256 amount) external;

    /// @notice Called by JBController when tokens are cashed out
    function burn(address holder, uint256 amount) external;
}
```

### Example: Transfer Tax Token

Revenue-generating token that collects fees on every transfer:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract TaxedProjectToken is ERC20 {
    uint256 public constant TAX_BPS = 100; // 1%
    address public immutable controller;
    address public immutable treasury;
    uint256 public immutable projectId;

    constructor(
        string memory name,
        string memory symbol,
        address _controller,
        uint256 _projectId,
        address _treasury
    ) ERC20(name, symbol) {
        controller = _controller;
        projectId = _projectId;
        treasury = _treasury;
    }

    function decimals() public pure override returns (uint8) { return 18; }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _burn(from, amount);
    }

    function _update(address from, address to, uint256 amount) internal override {
        // No tax on mints, burns, or controller operations
        if (from == address(0) || to == address(0) || msg.sender == controller) {
            super._update(from, to, amount);
            return;
        }

        // Apply transfer tax
        uint256 tax = (amount * TAX_BPS) / 10000;
        super._update(from, treasury, tax);
        super._update(from, to, amount - tax);
    }
}
```

**Deployment**:
```solidity
// 1. Deploy custom token (before or after project creation)
TaxedProjectToken token = new TaxedProjectToken(
    "Taxed Token",
    "TAX",
    address(CONTROLLER),
    projectId,
    treasuryAddress
);

// 2. Set as project token (requires SET_TOKEN permission)
CONTROLLER.setTokenFor(projectId, IJBToken(address(token)));
```

### Example: Governance Token with Voting

Enable on-chain governance while maintaining treasury mechanics:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20Votes, ERC20} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {Nonces} from "@openzeppelin/contracts/utils/Nonces.sol";

contract GovernanceProjectToken is ERC20Votes {
    address public immutable controller;
    uint256 public immutable projectId;

    constructor(
        string memory name,
        string memory symbol,
        address _controller,
        uint256 _projectId
    ) ERC20(name, symbol) EIP712(name, "1") {
        controller = _controller;
        projectId = _projectId;
    }

    function decimals() public pure override returns (uint8) { return 18; }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _burn(from, amount);
    }

    // Inherits: delegate(), delegateBySig(), getVotes(), getPastVotes(), etc.
}
```

**Usage with Governor**:
```solidity
// Deploy governor that uses token's voting power
GovernorBravo governor = new GovernorBravo(
    GovernanceProjectToken(token),
    timelockAddress,
    votingDelay,
    votingPeriod,
    proposalThreshold
);

// Token holders delegate and vote
token.delegate(voterAddress);  // Self-delegate to activate voting
governor.propose(...);
governor.castVote(proposalId, support);
```

### Example: Editable Name/Symbol Token

Allow project owners to rebrand without deploying a new token:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IJBProjects} from "@bananapus/core/src/interfaces/IJBProjects.sol";

contract EditableProjectToken is ERC20 {
    IJBProjects public immutable PROJECTS;
    address public immutable controller;
    uint256 public immutable projectId;

    string private _tokenName;
    string private _tokenSymbol;

    event NameUpdated(string oldName, string newName);
    event SymbolUpdated(string oldSymbol, string newSymbol);

    constructor(
        string memory initialName,
        string memory initialSymbol,
        address _controller,
        uint256 _projectId,
        IJBProjects projects
    ) ERC20(initialName, initialSymbol) {
        _tokenName = initialName;
        _tokenSymbol = initialSymbol;
        controller = _controller;
        projectId = _projectId;
        PROJECTS = projects;
    }

    modifier onlyProjectOwner() {
        require(msg.sender == PROJECTS.ownerOf(projectId), "NOT_OWNER");
        _;
    }

    function name() public view override returns (string memory) {
        return _tokenName;
    }

    function symbol() public view override returns (string memory) {
        return _tokenSymbol;
    }

    function decimals() public pure override returns (uint8) { return 18; }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _burn(from, amount);
    }

    /// @notice Update token name. Only callable by project owner.
    function setName(string calldata newName) external onlyProjectOwner {
        emit NameUpdated(_tokenName, newName);
        _tokenName = newName;
    }

    /// @notice Update token symbol. Only callable by project owner.
    function setSymbol(string calldata newSymbol) external onlyProjectOwner {
        emit SymbolUpdated(_tokenSymbol, newSymbol);
        _tokenSymbol = newSymbol;
    }
}
```

**Use cases**:
- Project rebranding without migrating liquidity
- Seasonal/event-based name changes
- Fixing typos discovered post-launch
- Community-voted name updates

**Tradeoff**: Some DEXs and aggregators cache token metadata. Changes may not propagate immediately to all interfaces.

### Example: Vesting Token

Enforce time-based vesting at the token level - useful for team allocations, investor locks, or contributor rewards where tokens should vest over time:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IJBProjects} from "@bananapus/core/src/interfaces/IJBProjects.sol";

/// @notice Project token with per-address vesting schedules.
/// @dev Vesting restricts transfers, not minting/burning. Combined with treasury
/// vesting (payout limits), this creates layered protection.
contract VestingProjectToken is ERC20 {
    struct VestingSchedule {
        uint256 totalAmount;     // Total tokens in this schedule
        uint256 released;        // Already released/transferred
        uint40 start;            // Vesting start timestamp
        uint40 cliff;            // Cliff end timestamp (0 = no cliff)
        uint40 duration;         // Total vesting duration from start
    }

    IJBProjects public immutable PROJECTS;
    address public immutable controller;
    uint256 public immutable projectId;

    mapping(address => VestingSchedule) public vestingOf;

    event VestingScheduleSet(
        address indexed beneficiary,
        uint256 totalAmount,
        uint40 start,
        uint40 cliff,
        uint40 duration
    );

    error CliffNotReached();
    error InsufficientVestedBalance();
    error VestingAlreadyExists();

    constructor(
        string memory name,
        string memory symbol,
        address _controller,
        uint256 _projectId,
        IJBProjects projects
    ) ERC20(name, symbol) {
        controller = _controller;
        projectId = _projectId;
        PROJECTS = projects;
    }

    modifier onlyProjectOwner() {
        require(msg.sender == PROJECTS.ownerOf(projectId), "NOT_OWNER");
        _;
    }

    function decimals() public pure override returns (uint8) { return 18; }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _burn(from, amount);
    }

    /// @notice Set a vesting schedule for an address.
    /// @dev Call this AFTER minting tokens to the beneficiary.
    /// @param beneficiary Address whose tokens will vest.
    /// @param totalAmount Total tokens subject to vesting (should match balance).
    /// @param start When vesting begins (can be in the past).
    /// @param cliffDuration Seconds until cliff ends (0 for no cliff).
    /// @param vestingDuration Total seconds for full vesting from start.
    function setVestingSchedule(
        address beneficiary,
        uint256 totalAmount,
        uint40 start,
        uint40 cliffDuration,
        uint40 vestingDuration
    ) external onlyProjectOwner {
        if (vestingOf[beneficiary].totalAmount > 0) revert VestingAlreadyExists();

        vestingOf[beneficiary] = VestingSchedule({
            totalAmount: totalAmount,
            released: 0,
            start: start,
            cliff: start + cliffDuration,
            duration: vestingDuration
        });

        emit VestingScheduleSet(
            beneficiary,
            totalAmount,
            start,
            start + cliffDuration,
            vestingDuration
        );
    }

    /// @notice Calculate how many tokens have vested for an address.
    function vestedAmountOf(address account) public view returns (uint256) {
        VestingSchedule memory schedule = vestingOf[account];

        // No vesting schedule = all tokens are vested (freely transferable)
        if (schedule.totalAmount == 0) return balanceOf(account);

        // Before cliff = nothing vested
        if (block.timestamp < schedule.cliff) return 0;

        // After full duration = everything vested
        if (block.timestamp >= schedule.start + schedule.duration) {
            return schedule.totalAmount;
        }

        // Linear vesting between cliff and end
        uint256 elapsed = block.timestamp - schedule.start;
        return (schedule.totalAmount * elapsed) / schedule.duration;
    }

    /// @notice Calculate transferable (vested and unreleased) tokens.
    function transferableOf(address account) public view returns (uint256) {
        VestingSchedule memory schedule = vestingOf[account];

        // No vesting = full balance transferable
        if (schedule.totalAmount == 0) return balanceOf(account);

        uint256 vested = vestedAmountOf(account);
        uint256 locked = schedule.totalAmount > vested
            ? schedule.totalAmount - vested
            : 0;

        uint256 balance = balanceOf(account);
        return balance > locked ? balance - locked : 0;
    }

    function _update(address from, address to, uint256 amount) internal override {
        // Skip vesting checks for mints, burns, and controller operations
        if (from == address(0) || to == address(0) || msg.sender == controller) {
            super._update(from, to, amount);
            return;
        }

        VestingSchedule storage schedule = vestingOf[from];

        // No vesting schedule = normal transfer
        if (schedule.totalAmount == 0) {
            super._update(from, to, amount);
            return;
        }

        // Before cliff = no transfers allowed
        if (block.timestamp < schedule.cliff) revert CliffNotReached();

        // Check transferable amount
        uint256 transferable = transferableOf(from);
        if (amount > transferable) revert InsufficientVestedBalance();

        // Track released amount for accounting
        schedule.released += amount;

        super._update(from, to, amount);
    }
}
```

**Key Design Decisions**:
- Vesting is per-address, set by project owner after minting
- No vesting schedule = freely transferable (normal ERC20 behavior)
- Cliff period: no transfers until cliff is reached
- Linear vesting after cliff
- Controller operations (mint/burn for payments/cash outs) bypass vesting

**Usage Pattern**:
```solidity
// 1. Deploy and set as project token
VestingProjectToken token = new VestingProjectToken(...);
CONTROLLER.setTokenFor(projectId, IJBToken(address(token)));

// 2. Team member receives tokens via payment or reserved distribution
// (tokens minted by controller - no vesting restriction on mint)

// 3. Project owner sets vesting schedule
token.setVestingSchedule(
    teamMember,
    1_000_000e18,           // 1M tokens vest
    uint40(block.timestamp), // Start now
    365 days,               // 1 year cliff
    4 * 365 days            // 4 year total vest
);

// Result:
// - Year 0-1: 0 tokens transferable (cliff)
// - Year 1: 250k tokens transferable (25% vested)
// - Year 2: 500k tokens transferable (50% vested)
// - Year 4+: All tokens transferable
```

**Combining with Treasury Vesting**:

| Layer | Protects | Mechanism |
|-------|----------|-----------|
| Token vesting | Holder's tokens | Transfer restrictions |
| Treasury vesting | Treasury funds | Payout limits |

For comprehensive protection, use both:
1. **Treasury vesting** (Pattern 1): Prevents premature fund withdrawal
2. **Token vesting**: Prevents premature token sales by recipients

**When to Use Token Vesting vs Treasury Vesting**:

| Scenario | Use Token Vesting | Use Treasury Vesting |
|----------|-------------------|---------------------|
| Team allocations with cliff | ✅ | Optional |
| Investor lock-ups | ✅ | Optional |
| Recurring payroll/grants | ❌ | ✅ |
| Milestone-based releases | ❌ | ✅ |
| All-holder protection | ❌ | ✅ |
| Per-person schedules | ✅ | ❌ |

**Tradeoffs**:
- Adds complexity vs standard token
- Vesting schedules are permanent once set
- Does not prevent cash outs (controller operations are exempt)
- Must set schedule after minting, not before

---

### Example: Concentration Limited Token

Prevent any single holder from accumulating too large a share:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ConcentrationLimitedToken is ERC20 {
    uint256 public maxHolderBps = 200;  // 2% max per holder
    address public immutable controller;
    uint256 public immutable projectId;
    mapping(address => bool) public isExempt;

    constructor(
        string memory name,
        string memory symbol,
        address _controller,
        uint256 _projectId
    ) ERC20(name, symbol) {
        controller = _controller;
        projectId = _projectId;
        isExempt[_controller] = true;  // Controller always exempt
    }

    function decimals() public pure override returns (uint8) { return 18; }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        _burn(from, amount);
    }

    function _update(address from, address to, uint256 amount) internal override {
        // Skip checks for mints, burns, and exempt addresses
        if (from == address(0) || to == address(0) || isExempt[to]) {
            super._update(from, to, amount);
            return;
        }

        // Check concentration limit
        uint256 maxBalance = (totalSupply() * maxHolderBps) / 10000;
        require(balanceOf(to) + amount <= maxBalance, "EXCEEDS_MAX_HOLDING");

        super._update(from, to, amount);
    }

    function setExempt(address account, bool exempt) external {
        require(msg.sender == controller, "UNAUTHORIZED");
        isExempt[account] = exempt;
    }
}
```

**Use cases**:
- Encourage broad token distribution
- Prevent governance centralization
- Reduce market manipulation risk

**Tradeoff**: Liquidity pools and the controller must be marked exempt. New holders during early high-supply periods may hit limits before supply grows.

### When to Use This Pattern

| Use Case | Custom Token? | Alternative |
|----------|---------------|-------------|
| Simple fundraising | No | Use credits or JBERC20 |
| Transfer fees/taxes | **Yes** | - |
| Rebasing mechanics | **Yes** | - |
| Governance voting | **Yes** | External governance |
| Pre-existing token | **Yes** | Migrate to new project |
| Per-holder token vesting | **Yes** | - |
| Treasury fund vesting | No | Use payout limits (Pattern 1) |
| Compliance restrictions | **Yes** | - |
| Editable name/symbol | **Yes** | Redeploy token |
| Concentration limits | **Yes** | - |

### Key Tradeoffs

| Aspect | Standard Token | Custom Token |
|--------|----------------|--------------|
| Complexity | Low | High |
| Audit burden | Audited by JB | Your responsibility |
| Gas costs | Optimized | Variable |
| Integration | Seamless | Requires testing |
| Flexibility | Limited | Full control |
| Risk | Low | Higher (custom code) |

### Critical Constraints

1. **18 decimals mandatory** - All Juicebox math assumes 18 decimals
2. **Controller must be authorized** - Mint/burn must work without approval
3. **One token per project** - Can't swap tokens after setting
4. **totalSupply() accuracy** - Cash outs depend on correct supply
5. **No fee-on-transfer during mint** - Minted amount must equal requested

### Deployment Checklist

- [ ] Token implements `canBeAddedTo(projectId)` returning true
- [ ] Token uses exactly 18 decimals
- [ ] Controller address authorized for mint()
- [ ] Controller address authorized for burn() (without approval)
- [ ] Custom logic (taxes, limits) exempts controller operations
- [ ] Tested with Juicebox payment flow
- [ ] Tested with Juicebox cash out flow
- [ ] Tested credit claiming after token is set
- [ ] Security audit completed (recommended)

---

## Decision Tree: When to Write Custom Code

```
Need custom payment logic?
├── Can 721 hook handle it? → Use 721 hook
├── Can buyback hook handle it? → Use buyback hook
└── Neither works? → Write custom pay hook

Need custom redemption logic?
├── Does 721 hook's burn-to-redeem work? → Use 721 hook
├── Is redemption just against surplus? → Use native cash out
└── Need external data source? → Write custom cash out hook

Need custom payout routing?
├── Can direct beneficiary addresses work? → Use native splits
├── Need token swapping? → Write split hook
├── Need LP deposits? → Write split hook
└── Just multi-recipient? → Use native splits

Need vesting/time-locks?
├── Treasury funds over time? → Use cycling rulesets + payout limits
├── Milestone-based releases? → Queue multiple rulesets
├── Per-holder token locks? → Custom ERC20 with vesting schedules
├── Investor/team cliffs? → Custom ERC20 with vesting schedules
└── Complex conditions? → Consider Revnet or custom

Need time-limited campaign?
├── Fundraise then close forever? → Two rulesets (active + paused)
├── Want immutability? → Burn ownership after deploy
└── May run another campaign? → Keep ownership

Need custom NFT content?
├── Static images per tier? → Use encodedIPFSUri in tier config
├── Dynamic/generative art? → Write IJB721TokenUriResolver
├── Composable/layered NFTs? → Write IJB721TokenUriResolver
└── On-chain SVG? → Write IJB721TokenUriResolver

Need prediction/game mechanics?
├── Fixed redemption values? → Use standard 721-hook
├── Outcome-based payouts? → Extend 721-hook (Defifa pattern)
├── On-chain outcome voting? → Add Governor contract
└── First-owner rewards? → Track in custom delegate

Need custom token mechanics?
├── Standard ERC20 sufficient? → Use deployERC20For()
├── Transfer taxes/fees? → Custom ERC20 with _update override
├── Governance voting? → Custom ERC20Votes
├── Rebasing/elastic supply? → Custom ERC20 (careful with totalSupply)
├── Editable name/symbol? → Custom ERC20 with setName/setSymbol
├── Concentration limits? → Custom ERC20 with max holder checks
├── Per-holder vesting/cliffs? → Custom ERC20 with vesting schedules
└── Pre-existing token? → Wrap with IJBToken interface

Need extended pay functionality on locked project/revnet?
├── Dynamic splits at pay time? → Terminal wrapper
├── Atomic pay + distribute? → Terminal wrapper
├── Token interception/staking? → Terminal wrapper (beneficiary-to-self)
├── Multi-hop payments? → Terminal wrapper
├── Block certain payments? → CAN'T DO (permissionless is a feature)
└── Standard payments work fine? → Use MultiTerminal directly
```

---

## Anti-Patterns to Avoid

### 1. Wrapping the 721 Hook

**Wrong**: Creating a data hook that wraps/delegates to 721 hook
**Right**: Use 721 hook directly, achieve vesting via ruleset configuration

### 2. Custom Vesting Contracts for Treasury Funds

**Wrong**: Writing a VestingSplitHook to hold and release funds
**Right**: Use payout limits (reset each cycle) for recurring distributions

**Exception**: Per-holder token vesting (team cliffs, investor locks) IS appropriate as a custom ERC20. See Pattern 8 - Vesting Token.

### 3. Multiple Queued Rulesets for Simple Cycles

**Wrong**: Queueing 12 rulesets for 12-month vesting
**Right**: One ruleset with 30-day duration that cycles automatically

### 4. Split Hooks for Direct Transfers

**Wrong**: Split hook that just forwards to an address
**Right**: Set the address as direct split beneficiary

### 5. Custom Cash Out Hooks for Standard Redemptions

**Wrong**: Writing hook to calculate pro-rata redemption
**Right**: Set `cashOutTaxRate: 0` and let terminal handle it

---

## Pattern 9: Time-Limited Campaign

**Use case**: Fundraise for a specific period, then close payments permanently

**Solution**: Deploy with two queued rulesets - active campaign, then paused

### Why This Pattern?

Many projects don't need ongoing payments forever. A time-limited campaign is cleaner:
- Crowdfunds with a deadline
- NFT mints with a defined window
- Grant rounds with cutoff dates
- "Set it and forget it" treasuries

### Configuration

```solidity
// Ruleset 1: Active Campaign
JBRulesetConfig({
    duration: 30 days,              // Campaign length
    weight: 1e18,                   // Token issuance rate
    decayPercent: 0,
    approvalHook: IJBRulesetApprovalHook(address(0)),
    metadata: JBRulesetMetadata({
        // ... normal settings
        pausePay: false,            // Payments ENABLED
    }),
    // ... splits, fund access, etc.
});

// Ruleset 2: Campaign End (queued immediately)
JBRulesetConfig({
    duration: 0,                    // Lasts forever
    weight: 0,                      // No more tokens issued
    decayPercent: 0,
    approvalHook: IJBRulesetApprovalHook(address(0)),
    metadata: JBRulesetMetadata({
        pausePay: true,             // Payments DISABLED
        // Keep cash outs enabled if desired
    }),
    // No payout limits needed - campaign is over
});
```

### Ownership Options

After deployment, the project owner decides:

**Option A: Keep Ownership**
- Can queue new rulesets later (run another campaign)
- Can adjust splits or fund access
- Maintains flexibility

**Option B: Lock Forever**
```solidity
// Transfer ownership to burn address
PROJECTS.transferFrom(
    deployer,
    0x000000000000000000000000000000000000dEaD,
    projectId
);
```
- No one can ever change the rules
- Fully trustless and immutable
- Cannot be undone

### Complete Flow

```
Deploy with 2 rulesets
         │
         ▼
┌─────────────────────────────────────┐
│  Ruleset 1: Active Campaign         │
│  ├── Duration: 30 days              │
│  ├── Payments: enabled              │
│  └── Tokens issued to payers        │
└─────────────────────────────────────┘
         │
         │ (30 days pass automatically)
         ▼
┌─────────────────────────────────────┐
│  Ruleset 2: Campaign Over           │
│  ├── Duration: forever              │
│  ├── Payments: paused               │
│  └── Cash outs still work           │
└─────────────────────────────────────┘
         │
         ▼
   Owner decides:
   ├── Keep ownership → can modify later
   └── Burn ownership → locked forever
```

### When to Use

| Scenario | Good Fit? |
|----------|-----------|
| One-time crowdfund | ✅ |
| NFT mint with deadline | ✅ |
| Grant distribution round | ✅ |
| Ongoing membership/subscription | ❌ Use cycling rulesets |
| Revnet with autonomous issuance | ❌ Use Revnet deployer |

### Key Benefits

1. **Simple** - Just two rulesets, no custom contracts
2. **Clear expectations** - Everyone knows when it ends
3. **Optional immutability** - Lock it or keep flexibility
4. **No ongoing management** - Set and forget

---

## Pattern 10: Terminal Wrapper (Pay Wrapper)

**Use case**: Extend payment functionality without modifying rulesets - especially for revnets where hooks can't be edited

**Solution**: Create an `IJBTerminal` that wraps `JBMultiTerminal`, like Swap Terminal does

### Why This Pattern?

Revnets and locked projects can't modify ruleset data hooks. But you can still add functionality by wrapping the terminal:

| Need | How Wrapper Solves It |
|------|----------------------|
| Dynamic splits at pay time | Parse from metadata, configure before forwarding |
| Pay + distribute atomically | Bundle operations in one tx |
| Token interception | Set beneficiary to wrapper, then stake/forward |
| Referral tracking | Parse referrer from metadata, record on-chain |
| Multi-hop payments | Receive tokens, swap, pay another project |

### Core Architecture

```solidity
contract PayWithSplitsTerminal is IJBTerminal {
    IJBMultiTerminal public immutable MULTI_TERMINAL;
    IJBController public immutable CONTROLLER;

    function pay(
        uint256 projectId,
        address token,
        uint256 amount,
        address beneficiary,
        uint256 minReturnedTokens,
        string calldata memo,
        bytes calldata metadata
    ) external payable returns (uint256 beneficiaryTokenCount) {
        // 1. Parse custom metadata
        (JBSplit[] memory splits, bytes memory innerMetadata) = _parseMetadata(metadata);

        // 2. Configure splits if provided
        if (splits.length > 0) {
            _configureSplits(projectId, splits);
        }

        // 3. Forward to underlying terminal
        beneficiaryTokenCount = MULTI_TERMINAL.pay{value: msg.value}(
            projectId, token, amount, beneficiary,
            minReturnedTokens, memo, innerMetadata
        );

        // 4. Distribute reserved tokens
        CONTROLLER.sendReservedTokensToSplitsOf(projectId);

        return beneficiaryTokenCount;
    }
}
```

### Beneficiary-to-Self Pattern

Intercept tokens by making the wrapper the beneficiary:

```solidity
function payAndStake(uint256 projectId, ..., bytes calldata metadata) external payable {
    (address finalDestination, bytes memory stakingParams) = abi.decode(metadata, (address, bytes));

    // Wrapper receives tokens
    uint256 tokenCount = MULTI_TERMINAL.pay{value: msg.value}(
        projectId, token, amount,
        address(this),  // <-- Beneficiary is wrapper
        minReturnedTokens, "", ""
    );

    // Do something with them
    _stakeTokens(projectToken, tokenCount, finalDestination, stakingParams);
}
```

### Critical Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    WRAPPER IS ADDITIVE                          │
├─────────────────────────────────────────────────────────────────┤
│   Client A ──► PayWrapper ──► JBMultiTerminal                   │
│                (gets special features)                          │
│                                                                 │
│   Client B ─────────────────► JBMultiTerminal                   │
│                (still works!)                                   │
│                                                                 │
│   BOTH ARE VALID. Wrapper cannot block direct access.           │
│   This is a FEATURE. Permissionless = good.                     │
└─────────────────────────────────────────────────────────────────┘
```

**Bad thinking**: "I'll use a wrapper to block payments that don't meet criteria X"

**Good thinking**: "I'll provide enhanced functionality for clients that opt in"

### Comparison with Swap Terminal

Swap Terminal is the canonical example:

```
User pays USDC ──► SwapTerminal ──► Swaps to ETH ──► JBMultiTerminal
```

Your wrapper follows the same architecture with different transformation logic.

### Cash Out Wrappers

The same pattern applies to cash outs. Wrap `cashOutTokensOf` to intercept redeemed funds:

```solidity
/// @notice Cash out with automatic bridging of redeemed funds.
function cashOutAndBridge(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    address tokenToReclaim,
    uint256 minTokensReclaimed,
    address beneficiary,
    uint256 destChainId,    // Custom: where to bridge
    bytes calldata metadata
) external returns (uint256 reclaimAmount) {
    // 1. Cash out to THIS contract (intercept funds)
    reclaimAmount = MULTI_TERMINAL.cashOutTokensOf(
        holder,
        projectId,
        tokenCount,
        tokenToReclaim,
        minTokensReclaimed,
        address(this),  // <-- Wrapper receives funds
        metadata
    );

    // 2. Bridge the redeemed funds to destination chain
    _bridgeFunds(tokenToReclaim, reclaimAmount, beneficiary, destChainId);

    return reclaimAmount;
}

/// @notice Cash out with automatic swap to different token.
function cashOutAndSwap(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    address tokenToReclaim,
    uint256 minTokensReclaimed,
    address tokenOut,       // Custom: swap to this token
    uint256 minAmountOut,   // Custom: slippage protection
    address beneficiary,
    bytes calldata metadata
) external returns (uint256 amountOut) {
    // 1. Cash out to this contract
    uint256 reclaimAmount = MULTI_TERMINAL.cashOutTokensOf(
        holder,
        projectId,
        tokenCount,
        tokenToReclaim,
        minTokensReclaimed,
        address(this),
        metadata
    );

    // 2. Swap redeemed tokens
    amountOut = _swap(tokenToReclaim, tokenOut, reclaimAmount, minAmountOut);

    // 3. Send swapped tokens to beneficiary
    _sendFunds(tokenOut, amountOut, beneficiary);

    return amountOut;
}
```

### When to Use

| Scenario | Terminal Wrapper? | Alternative |
|----------|-------------------|-------------|
| **Pay Wrappers** | | |
| Revnet needs new pay-time features | **Yes** | Can't modify hooks |
| Dynamic splits specified by payer | **Yes** | Native splits are static |
| Atomic pay + distribute | **Yes** | Two separate txs |
| Token interception/staking | **Yes** | - |
| **Cash Out Wrappers** | | |
| Cash out + bridge in one tx | **Yes** | Two separate txs |
| Cash out + swap to different token | **Yes** | Manual swap after |
| Cash out + stake redeemed funds | **Yes** | - |
| Cash out + LP deposit | **Yes** | - |
| **Both** | | |
| Simple operations with existing hooks | No | Use MultiTerminal directly |
| Need to block payments/cashouts | **No** | Wrappers can't enforce this |

### Complete Example: Pay-Time Splits Terminal

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {IJBTerminal} from "@bananapus/core/src/interfaces/IJBTerminal.sol";
import {IJBMultiTerminal} from "@bananapus/core/src/interfaces/IJBMultiTerminal.sol";
import {IJBController} from "@bananapus/core/src/interfaces/IJBController.sol";
import {JBSplit} from "@bananapus/core/src/structs/JBSplit.sol";
import {JBSplitGroup} from "@bananapus/core/src/structs/JBSplitGroup.sol";
import {JBConstants} from "@bananapus/core/src/libraries/JBConstants.sol";
import {JBPermissionIds} from "@bananapus/permission-ids/src/JBPermissionIds.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @notice Terminal wrapper that allows payers to specify reserved token splits at pay time.
/// @dev Useful for revnets where ruleset hooks can't be modified post-deploy.
/// @dev Follows JBSwapTerminalRegistry pattern with shared _acceptFunds helper.
contract PayWithSplitsTerminal is IJBTerminal {
    using SafeERC20 for IERC20;

    // ═══════════════════════════════════════════════════════════════════════
    // ERRORS
    // ═══════════════════════════════════════════════════════════════════════

    error InvalidSplitTotal();

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTANTS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Split group ID for reserved tokens.
    uint256 public constant RESERVED_TOKEN_GROUP = 1;

    /// @notice The underlying terminal this wrapper forwards to.
    IJBMultiTerminal public immutable MULTI_TERMINAL;

    /// @notice The controller for setting splits and distributing reserved tokens.
    IJBController public immutable CONTROLLER;

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    /// @param _multiTerminal The JBMultiTerminal to wrap.
    /// @param _controller The JBController for this deployment.
    constructor(IJBMultiTerminal _multiTerminal, IJBController _controller) {
        MULTI_TERMINAL = _multiTerminal;
        CONTROLLER = _controller;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // EXTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Pay a project with optional dynamic splits specified in metadata.
    /// @dev If metadata contains splits, they're applied before payment. Reserved tokens
    ///      are distributed after payment completes.
    /// @param projectId The project to pay.
    /// @param token The token to pay with (JBConstants.NATIVE_TOKEN for ETH).
    /// @param amount The amount to pay (ignored for ETH, uses msg.value).
    /// @param beneficiary Who receives the project tokens.
    /// @param minReturnedTokens Minimum tokens to receive (slippage protection).
    /// @param memo Payment memo.
    /// @param metadata ABI-encoded (JBSplit[] splits, bytes innerMetadata).
    ///        - splits: Reserved token split configuration (empty array to skip)
    ///        - innerMetadata: Passed through to MultiTerminal (for hooks, etc.)
    /// @return beneficiaryTokenCount The number of tokens minted to beneficiary.
    function pay(
        uint256 projectId,
        address token,
        uint256 amount,
        address beneficiary,
        uint256 minReturnedTokens,
        string calldata memo,
        bytes calldata metadata
    ) external payable returns (uint256 beneficiaryTokenCount) {
        bytes memory innerMetadata;

        // Parse and apply splits if metadata provided
        if (metadata.length > 0) {
            JBSplit[] memory splits;
            (splits, innerMetadata) = abi.decode(metadata, (JBSplit[], bytes));

            if (splits.length > 0) {
                _validateAndSetSplits(projectId, splits);
            }
        }

        // Accept funds and get value to forward
        uint256 valueToSend = _acceptFunds(token, amount, address(MULTI_TERMINAL));

        // Forward payment to MultiTerminal
        beneficiaryTokenCount = MULTI_TERMINAL.pay{value: valueToSend}(
            projectId,
            token,
            amount,
            beneficiary,
            minReturnedTokens,
            memo,
            innerMetadata
        );

        // Distribute reserved tokens to the configured splits
        CONTROLLER.sendReservedTokensToSplitsOf(projectId);

        return beneficiaryTokenCount;
    }

    /// @notice Add to a project's balance without receiving tokens.
    /// @dev Pass-through to MultiTerminal.
    function addToBalanceOf(
        uint256 projectId,
        address token,
        uint256 amount,
        bool shouldReturnHeldFees,
        string calldata memo,
        bytes calldata metadata
    ) external payable {
        // Accept funds and get value to forward
        uint256 valueToSend = _acceptFunds(token, amount, address(MULTI_TERMINAL));

        MULTI_TERMINAL.addToBalanceOf{value: valueToSend}(
            projectId,
            token,
            amount,
            shouldReturnHeldFees,
            memo,
            metadata
        );
    }

    /// @notice Check accounting contexts accepted by underlying terminal.
    function accountingContextForTokenOf(
        uint256 projectId,
        address token
    ) external view returns (JBAccountingContext memory) {
        return MULTI_TERMINAL.accountingContextForTokenOf(projectId, token);
    }

    /// @notice Get all accounting contexts for a project.
    function accountingContextsOf(
        uint256 projectId
    ) external view returns (JBAccountingContext[] memory) {
        return MULTI_TERMINAL.accountingContextsOf(projectId);
    }

    /// @notice Get current surplus in a project's terminal.
    function currentSurplusOf(
        uint256 projectId,
        JBAccountingContext[] calldata accountingContexts,
        uint256 decimals,
        uint256 currency
    ) external view returns (uint256) {
        return MULTI_TERMINAL.currentSurplusOf(
            projectId,
            accountingContexts,
            decimals,
            currency
        );
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Accept funds from the caller and prepare them for forwarding.
    /// @dev For ERC20s: transfers from sender, approves spender.
    /// @dev For ETH: returns msg.value to forward.
    /// @dev Pattern from JBSwapTerminalRegistry - consolidates token handling.
    /// @param token The token being paid (NATIVE_TOKEN for ETH).
    /// @param amount The amount being paid.
    /// @param spender The address that will spend the tokens (the terminal).
    /// @return valueToSend The ETH value to forward (0 for ERC20s).
    function _acceptFunds(
        address token,
        uint256 amount,
        address spender
    ) internal returns (uint256 valueToSend) {
        if (token == JBConstants.NATIVE_TOKEN) {
            // For ETH, just return msg.value to forward
            return msg.value;
        }

        // For ERC20s: pull tokens from sender
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        // Approve the spender (terminal) to pull tokens
        IERC20(token).forceApprove(spender, amount);

        // No ETH to forward for ERC20 payments
        return 0;
    }

    /// @notice Validate splits sum to 100% and set them on the controller.
    /// @dev This wrapper must have SET_SPLIT_GROUPS permission on the project.
    function _validateAndSetSplits(uint256 projectId, JBSplit[] memory splits) internal {
        // Validate splits sum to 100%
        uint256 total;
        for (uint256 i; i < splits.length; i++) {
            total += splits[i].percent;
        }
        if (total != JBConstants.SPLITS_TOTAL_PERCENT) revert InvalidSplitTotal();

        // Get current ruleset ID
        (JBRuleset memory ruleset,) = CONTROLLER.currentRulesetOf(projectId);

        // Build split group
        JBSplitGroup[] memory groups = new JBSplitGroup[](1);
        groups[0] = JBSplitGroup({
            groupId: RESERVED_TOKEN_GROUP,
            splits: splits
        });

        // Set splits (requires SET_SPLIT_GROUPS permission)
        CONTROLLER.setSplitGroupsOf(projectId, ruleset.id, groups);
    }

    /// @notice Required for receiving ETH refunds from terminal.
    receive() external payable {}
}
```

### Client-Side Usage (TypeScript)

```typescript
import {
  encodeFunctionData,
  encodeAbiParameters,
  parseAbiParameters,
  parseUnits,
  Address
} from 'viem';

const SPLITS_TOTAL_PERCENT = 1_000_000_000n; // 1e9

// Build split configuration
function encodeSplits(recipients: { address: Address; percent: number }[]) {
  // Convert percentages (0-100) to JB format (0-1e9)
  const splits = recipients.map(r => ({
    preferredProjectId: 0n,
    preferredBeneficiary: r.address,
    percent: BigInt(Math.floor(r.percent * 10_000_000)), // 1% = 10_000_000
    lockedUntil: 0n,
    hook: '0x0000000000000000000000000000000000000000' as Address,
  }));

  return splits;
}

// Encode metadata for pay call
function encodePayMetadata(
  splits: ReturnType<typeof encodeSplits>,
  innerMetadata: `0x${string}` = '0x'
) {
  return encodeAbiParameters(
    parseAbiParameters([
      '(uint256 preferredProjectId, address preferredBeneficiary, uint256 percent, uint256 lockedUntil, address hook)[]',
      'bytes'
    ]),
    [splits, innerMetadata]
  );
}

// Example: Pay with dynamic splits
async function payWithSplits(
  walletClient: WalletClient,
  wrapperAddress: Address,
  projectId: bigint,
  paymentAmount: bigint,
  recipients: { address: Address; percent: number }[]
) {
  const splits = encodeSplits(recipients);
  const metadata = encodePayMetadata(splits);

  const NATIVE_TOKEN = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';

  const hash = await walletClient.writeContract({
    address: wrapperAddress,
    abi: PAY_WITH_SPLITS_ABI,
    functionName: 'pay',
    args: [
      projectId,
      NATIVE_TOKEN,
      paymentAmount,
      walletClient.account.address, // beneficiary
      0n, // minReturnedTokens
      'Payment with custom splits',
      metadata
    ],
    value: paymentAmount
  });

  return hash;
}

// Usage
await payWithSplits(
  walletClient,
  '0x...wrapper',
  3n, // projectId
  parseUnits('1', 18), // 1 ETH
  [
    { address: '0xaaa...', percent: 50 }, // 50% to address A
    { address: '0xbbb...', percent: 30 }, // 30% to address B
    { address: '0xccc...', percent: 20 }, // 20% to address C
  ]
);
```

### Deployment & Permissions

```solidity
// Deploy the wrapper
PayWithSplitsTerminal wrapper = new PayWithSplitsTerminal(
    IJBMultiTerminal(MULTI_TERMINAL_ADDRESS),
    IJBController(CONTROLLER_ADDRESS)
);

// Grant SET_SPLIT_GROUPS permission to wrapper
// (Must be called by project owner or someone with SET_PERMISSIONS)
JBPermissionsData[] memory permissions = new JBPermissionsData[](1);
permissions[0] = JBPermissionsData({
    operator: address(wrapper),
    projectId: PROJECT_ID,
    permissionIds: _asSingletonArray(JBPermissionIds.SET_SPLIT_GROUPS)
});

PERMISSIONS.setPermissionsFor(projectOwner, permissions);
```

### Key Notes

- Wrapper must be granted permissions if setting splits
- Multiple wrappers can exist for different purposes - they don't conflict
- Wrappers can be chained: WrapperA → WrapperB → MultiTerminal
- For revnets: often the ONLY way to add functionality post-deploy
- Validate metadata carefully - parsing adds attack surface

---

## Pattern 11: Yield-Generating Hook (Aave Integration)

**Use case**: Deposit contributions to yield protocols (Aave, Compound, etc.), route yield to project balance while allowing principal cash-outs

**Solution**: Combined pay/cash-out hook that deposits to Aave, tracks principal separately from yield

### Why This Pattern?

Create "YeeHaw" style funding where:
- Investor contributions earn yield via DeFi
- Investors can always cash out their principal
- Yield flows to project balance for team operations
- Clear separation between protected principal and operational yield

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Payment Flow                                                    │
│  User pays → Hook deposits to Aave → Principal tracked           │
│                                                                  │
│  Yield Flow                                                      │
│  Aave earns yield → Hook withdraws → addToBalanceOf()           │
│                     → Appears in project balance                 │
│                     → Team uses sendPayoutsOf()                  │
│                                                                  │
│  Cash Out Flow                                                   │
│  User cashes out → Hook withdraws from Aave → Direct to user    │
│                    (bypasses terminal, separate from yield)      │
└─────────────────────────────────────────────────────────────────┘
```

### Core Hook Structure

```solidity
contract YieldHook is IJBPayHook, IJBCashOutHook, IJBRulesetDataHook {
    IPool public immutable AAVE_POOL;
    IJBTerminal public immutable TERMINAL;

    mapping(uint256 projectId => uint256) public principalDeposited;
    mapping(uint256 projectId => uint256) public principalWithdrawn;
    mapping(uint256 projectId => uint256) public yieldWithdrawn;

    struct ProjectConfig {
        address principalToken;    // USDC, ETH, etc.
        address aToken;           // Corresponding aToken
        uint256 yieldThreshold;   // Min yield before transfer
        bool active;
    }
}
```

### Data Hook: Route Payments to Hook

```solidity
function beforePayRecordedWith(
    JBBeforePayRecordedContext calldata context
) external view override returns (
    uint256 weight,
    JBPayHookSpecification[] memory hookSpecifications
) {
    weight = context.weight;

    // Forward ALL payment funds to this hook for Aave deposit
    hookSpecifications = new JBPayHookSpecification[](1);
    hookSpecifications[0] = JBPayHookSpecification({
        hook: IJBPayHook(address(this)),
        amount: context.amount.value,  // Must be explicit, not 0
        metadata: ""
    });
}
```

### Pay Hook: Deposit to Aave

```solidity
function afterPayRecordedWith(
    JBAfterPayRecordedContext calldata context
) external payable override {
    ProjectConfig storage config = projectConfigs[context.projectId];
    uint256 amount = context.forwardedAmount.value;

    // Deposit to Aave
    IERC20(config.principalToken).forceApprove(address(AAVE_POOL), amount);
    AAVE_POOL.supply(config.principalToken, amount, address(this), 0);

    // Track principal
    principalDeposited[context.projectId] += amount;

    // Check if yield should be transferred
    _maybeTransferYield(context.projectId);
}
```

### Cash Out Hook: Principal Withdrawal

```solidity
function beforeCashOutRecordedWith(
    JBBeforeCashOutRecordedContext calldata context
) external view override returns (
    uint256 cashOutTaxRate,
    uint256 cashOutCount,
    uint256 totalSupply,
    JBCashOutHookSpecification[] memory hookSpecifications
) {
    // Calculate user's share of principal
    uint256 availablePrincipal = principalDeposited[context.projectId]
                                - principalWithdrawn[context.projectId];
    uint256 userShare = (availablePrincipal * context.cashOutCount) / context.totalSupply;

    cashOutTaxRate = 0;  // No tax on principal
    cashOutCount = context.cashOutCount;
    totalSupply = context.totalSupply;

    // Route to this hook for Aave withdrawal
    hookSpecifications = new JBCashOutHookSpecification[](1);
    hookSpecifications[0] = JBCashOutHookSpecification({
        hook: IJBCashOutHook(address(this)),
        amount: userShare,
        metadata: ""
    });
}

function afterCashOutRecordedWith(
    JBAfterCashOutRecordedContext calldata context
) external payable override {
    ProjectConfig storage config = projectConfigs[context.projectId];
    uint256 amount = context.forwardedAmount.value;

    // Withdraw principal from Aave directly to user
    AAVE_POOL.withdraw(config.principalToken, amount, context.beneficiary);
    principalWithdrawn[context.projectId] += amount;
}
```

### Yield Management: Route to Project Balance

```solidity
function _maybeTransferYield(uint256 projectId) internal {
    ProjectConfig storage config = projectConfigs[projectId];
    uint256 availableYield = _calculateAvailableYield(projectId);

    if (availableYield >= config.yieldThreshold) {
        // Withdraw yield from Aave to this contract
        uint256 withdrawn = AAVE_POOL.withdraw(
            config.principalToken,
            availableYield,
            address(this)
        );

        // Approve terminal
        IERC20(config.principalToken).forceApprove(address(TERMINAL), withdrawn);

        // Add to project balance (team can then use sendPayoutsOf)
        TERMINAL.addToBalanceOf(
            projectId,
            config.principalToken,
            withdrawn,
            false,  // shouldReturnHeldFees
            "",     // memo
            ""      // metadata
        );

        yieldWithdrawn[projectId] += withdrawn;
    }
}

function _calculateAvailableYield(uint256 projectId) internal view returns (uint256) {
    ProjectConfig storage config = projectConfigs[projectId];
    uint256 totalBalance = IERC20(config.aToken).balanceOf(address(this));
    uint256 principalRemaining = principalDeposited[projectId] - principalWithdrawn[projectId];

    if (totalBalance > principalRemaining + yieldWithdrawn[projectId]) {
        return totalBalance - principalRemaining - yieldWithdrawn[projectId];
    }
    return 0;
}
```

### Project Configuration

```solidity
// Ruleset must enable data hooks
JBRulesetMetadata({
    useDataHookForPay: true,      // Enable beforePay/afterPay
    useDataHookForCashOut: true,  // Enable beforeCashOut/afterCashOut
    dataHook: address(yieldHook), // Your hook address
    // ...
});
```

### When to Use

| Scenario | Fits Pattern? |
|----------|---------------|
| Yield-backed funding | ✅ |
| Aave/Compound integration | ✅ |
| Principal-protected investing | ✅ |
| Staking rewards integration | ✅ (adapt for staking protocol) |
| Standard fundraising | ❌ Use native terminals |
| NFT-based funding | ❌ Use 721 hook |

### Key Implementation Notes

1. **amount in JBPayHookSpecification**: Must be `context.amount.value` to forward funds, not 0
2. **Yield routing**: Use `addToBalanceOf()` to add yield to project balance
3. **Principal tracking**: Separate tracking for deposits vs withdrawals
4. **Emergency fallback**: Include direct withdrawal function for emergencies
5. **Gas optimization**: Use yield threshold to batch transfers

### Reference

- YeeHaw concept: Yield-backed crowdfunding
- Uses pattern from jb-yield-to-balance-pattern skill

---

## Reference Implementations

- **Vesting + NFT**: Drip x Juicebox (see `/jb-project` for deployment script)
- **Autonomous Treasury**: Revnet (`revnet-core-v5`)
- **NFT Rewards**: Any project using `JB721TiersHookProjectDeployer`
- **Custom NFT Content**: [banny-retail-v5](https://github.com/mejango/banny-retail-v5) - composable SVG NFTs with outfit decoration
- **Prediction Games**: [defifa-collection-deployer-v5](https://github.com/BallKidz/defifa-collection-deployer-v5) - dynamic cash out weights with on-chain governance
- **Yield-Generating Hook**: YeeHaw concept - Aave integration for yield-backed funding

## Related Skills

- `/jb-simplify` - Checklist to reduce custom code
- `/jb-project` - Project deployment and configuration
- `/jb-ruleset` - Ruleset configuration details
- `/jb-v5-impl` - Deep implementation mechanics
- `/jb-terminal-wrapper` - Full terminal wrapper implementation details
