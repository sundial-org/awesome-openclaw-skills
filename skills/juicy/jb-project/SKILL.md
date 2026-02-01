---
name: jb-project
description: Create and configure Juicebox V5 projects. Generate deployment scripts for launching projects with rulesets, terminals, and splits using JBController. Also helps with project ownership transfer and metadata updates.
---

# Juicebox V5 Project Management

Create and manage Juicebox V5 projects including deployment, configuration, and ownership.

## Project Identity

**A Juicebox project is uniquely identified by: `projectId + chainId + version`**

This matters because:
- **V4 and V5 are different protocols.** Project #64 on V4 is NOT the same as Project #64 on V5, even on the same chain.
- **Project IDs cannot be coordinated across chains.** Each chain assigns the next available ID independently. If you deploy to Ethereum you might get project #42, and deploying to Optimism might give you project #17.
- **Suckers link projects across chains.** To create an "omnichain project," you deploy separate projects on each chain (with different IDs) and connect them using Suckers. This enables token bridging while maintaining treasury backing.
- When referencing a project, always specify the version and chain to avoid confusion.

## V5.1 Contract Update (Dec 2025)

**Only JBRulesets has a code change** (one-line approval hook fix). Other contracts were redeployed due to dependency chains (JBTerminalStore→JBMultiTerminal, JB721TiersHook→JB721TiersHookDeployer→JBOmnichainDeployer).

| Deploying... | Use These Contracts |
|--------------|---------------------|
| New project | **V5.1** (JBController5_1, JBMultiTerminal5_1, etc.) |
| Revnet | **V5.0** (REVDeployer uses V5.0 JBController) |

**Do not mix V5.0 and V5.1 contracts** - use one complete set or the other.

See `references/v5-addresses.md` or `shared/chain-config.json` for addresses.

## Before Writing Custom Code

**Always check if native mechanics can achieve your goal:**

| User Need | Recommended Solution |
|-----------|---------------------|
| Autonomous tokenized treasury | Deploy a **Revnet** via revnet-core-v5 |
| Project with structured rules and no EOA owner | Use contract-as-owner pattern |
| Simple fundraising project | Use this skill to generate deployment |
| Vesting/time-locked distributions | Use **payout limits + cycling rulesets** (no custom contracts) |
| NFT-gated treasury | Use **nana-721-hook-v5** with native cash outs |
| Governance-minimal/immutable | Transfer ownership to **burn address** after setup |
| One-time treasury access | Use **surplus allowance** (doesn't reset each cycle) |
| Custom token mechanics | Use **custom ERC20** via `setTokenFor()` |

**See `/jb-patterns` for detailed examples of these patterns.**
**See `/jb-simplify` for a checklist to reduce custom code.**

## Project Creation Overview

Projects are created through `JBController.launchProjectFor()` which:
1. Creates a new project NFT via JBProjects
2. Sets the controller for the project
3. Configures the first ruleset
4. Sets up terminal configurations

## Core Functions

### Launch a Project

```solidity
function launchProjectFor(
    address owner,                              // Project owner (receives NFT)
    string calldata projectUri,                 // IPFS metadata URI
    JBRulesetConfig[] calldata rulesetConfigs,  // Initial ruleset(s)
    JBTerminalConfig[] calldata terminalConfigs, // Terminal setup
    string calldata memo                        // Launch memo
) external returns (uint256 projectId);
```

### Project Metadata (projectUri)

The `projectUri` should point to a JSON file (typically on IPFS) with:

```json
{
  "name": "Project Name",
  "description": "Project description",
  "logoUri": "ipfs://...",
  "infoUri": "https://...",
  "twitter": "@handle",
  "discord": "https://discord.gg/...",
  "telegram": "https://t.me/..."
}
```

## Configuration Structs

### JBRulesetConfig

```solidity
struct JBRulesetConfig {
    uint256 mustStartAtOrAfter;     // Earliest start time (0 = now)
    uint256 duration;               // Duration in seconds (0 = indefinite)
    uint256 weight;                 // Token minting weight (18 decimals)
    uint256 weightCutPercent;       // Weight cut per cycle (0-1000000000)
    IJBRulesetApprovalHook approvalHook;  // Approval hook (e.g., JBDeadline)
    JBRulesetMetadata metadata;     // Ruleset settings
    JBSplitGroup[] splitGroups;     // Payout and reserved splits
    JBFundAccessLimitGroup[] fundAccessLimitGroups;  // Payout limits
}
```

### JBTerminalConfig

```solidity
struct JBTerminalConfig {
    IJBTerminal terminal;                   // Terminal contract
    JBAccountingContext[] accountingContexts;  // Accepted tokens
}
```

### JBAccountingContext

```solidity
struct JBAccountingContext {
    address token;          // Token address (address(0) for native)
    uint8 decimals;         // Token decimals
    uint32 currency;        // Currency ID for accounting
}
```

## Deployment Script Example

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {Script} from "forge-std/Script.sol";
import {IJBController} from "@bananapus/core/src/interfaces/IJBController.sol";
import {IJBMultiTerminal} from "@bananapus/core/src/interfaces/IJBMultiTerminal.sol";
import {JBRulesetConfig} from "@bananapus/core/src/structs/JBRulesetConfig.sol";
import {JBRulesetMetadata} from "@bananapus/core/src/structs/JBRulesetMetadata.sol";
import {JBTerminalConfig} from "@bananapus/core/src/structs/JBTerminalConfig.sol";
import {JBAccountingContext} from "@bananapus/core/src/structs/JBAccountingContext.sol";
import {JBSplitGroup} from "@bananapus/core/src/structs/JBSplitGroup.sol";
import {JBSplit} from "@bananapus/core/src/structs/JBSplit.sol";
import {JBFundAccessLimitGroup} from "@bananapus/core/src/structs/JBFundAccessLimitGroup.sol";
import {JBCurrencyAmount} from "@bananapus/core/src/structs/JBCurrencyAmount.sol";
import {JBConstants} from "@bananapus/core/src/libraries/JBConstants.sol";

contract DeployProject is Script {
    // V5.1 Mainnet Addresses (use for new projects)
    // See /references/v5-addresses.md for all networks
    // NOTE: For revnets, use V5.0 addresses instead
    IJBController constant CONTROLLER = IJBController(0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1);
    IJBMultiTerminal constant TERMINAL = IJBMultiTerminal(0x52869db3d61dde1e391967f2ce5039ad0ecd371c);

    function run() external {
        vm.startBroadcast();

        // Configure ruleset metadata
        JBRulesetMetadata memory metadata = JBRulesetMetadata({
            reservedRate: 0,                    // No reserved tokens
            cashOutTaxRate: 0,                  // No cash out tax
            baseCurrency: uint32(uint160(JBConstants.NATIVE_TOKEN)),
            pausePay: false,
            pauseCashOut: false,
            pauseTransfers: false,
            allowOwnerMinting: false,
            allowTerminalMigration: false,
            allowSetTerminals: false,
            allowSetController: false,
            allowAddAccountingContexts: false,
            allowAddPriceFeed: false,
            ownerMustSendPayouts: false,
            holdFees: false,
            useTotalSurplusForCashOuts: false,
            useDataHookForPay: false,
            useDataHookForCashOut: false,
            dataHook: address(0),
            metadata: 0
        });

        // Configure splits (empty for now)
        JBSplitGroup[] memory splitGroups = new JBSplitGroup[](0);

        // Configure fund access limits
        JBFundAccessLimitGroup[] memory fundAccessLimits = new JBFundAccessLimitGroup[](0);

        // Build ruleset config
        JBRulesetConfig[] memory rulesetConfigs = new JBRulesetConfig[](1);
        rulesetConfigs[0] = JBRulesetConfig({
            mustStartAtOrAfter: 0,
            duration: 0,                        // Indefinite
            weight: 1e18,                       // 1 token per unit paid
            weightCutPercent: 0,                // No weight cut
            approvalHook: IJBRulesetApprovalHook(address(0)),
            metadata: metadata,
            splitGroups: splitGroups,
            fundAccessLimitGroups: fundAccessLimits
        });

        // Configure terminal to accept ETH
        JBAccountingContext[] memory accountingContexts = new JBAccountingContext[](1);
        accountingContexts[0] = JBAccountingContext({
            token: JBConstants.NATIVE_TOKEN,
            decimals: 18,
            currency: uint32(uint160(JBConstants.NATIVE_TOKEN))
        });

        JBTerminalConfig[] memory terminalConfigs = new JBTerminalConfig[](1);
        terminalConfigs[0] = JBTerminalConfig({
            terminal: TERMINAL,
            accountingContexts: accountingContexts
        });

        // Launch the project
        uint256 projectId = CONTROLLER.launchProjectFor(
            msg.sender,                         // Owner
            "ipfs://...",                       // Project metadata URI
            rulesetConfigs,
            terminalConfigs,
            "Project launch"                    // Memo
        );

        vm.stopBroadcast();
    }
}
```

## Custom ERC20 Project Tokens

By default, Juicebox projects use **credits** (unclaimed internal balances). You can upgrade to an ERC20 token two ways:

### Option 1: Deploy Standard JBERC20

```solidity
// Deploy the default Juicebox ERC20 token
IJBToken token = CONTROLLER.deployERC20For(
    projectId,
    "Project Token",    // name
    "PROJ",             // symbol
    bytes32(0)          // salt (for deterministic address, or 0)
);
```

This creates a standard `JBERC20` that the controller can mint/burn. Simple and works for most projects.

### Option 2: Use a Custom ERC20

For advanced tokenomics, you can bring your own ERC20:

```solidity
// Set an existing/custom ERC20 as the project token
CONTROLLER.setTokenFor(projectId, IJBToken(myCustomToken));
```

**Requirements for custom tokens:**
1. Must use **18 decimals**
2. Must implement `canBeAddedTo(uint256 projectId)` returning `true`
3. Must not be assigned to another Juicebox project
4. Controller needs mint/burn permissions (typically via ownership or access control)

### Custom Token Interface

```solidity
interface IJBToken is IERC20 {
    /// @notice Verify this token can be added to a project.
    /// @param projectId The project ID to check.
    /// @return True if the token can be added.
    function canBeAddedTo(uint256 projectId) external view returns (bool);

    /// @notice Mint tokens to an account.
    /// @param holder The account to mint to.
    /// @param amount The amount to mint.
    function mint(address holder, uint256 amount) external;

    /// @notice Burn tokens from an account.
    /// @param holder The account to burn from.
    /// @param amount The amount to burn.
    function burn(address holder, uint256 amount) external;
}
```

### When to Use Custom ERC20s

| Use Case | Why Custom ERC20 |
|----------|------------------|
| **Transfer taxes** | Implement fees on transfers (e.g., reflection tokens) |
| **Rebasing tokens** | Elastic supply that adjusts balances automatically |
| **Pre-existing tokens** | Integrate a community token with established holders |
| **Governance features** | Voting snapshots, delegation, checkpointing |
| **Vesting schedules** | Built-in unlock mechanics in the token itself |
| **Allowlist/denylist** | Transfer restrictions for compliance |
| **Concentration limits** | Cap max holdings per address for distribution |
| **Editable metadata** | Rebrand name/symbol without redeploying |

### Example: Custom Token with Transfer Tax

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract TaxedProjectToken is ERC20, Ownable {
    uint256 public constant TAX_RATE = 100; // 1% (basis points)
    uint256 public constant TAX_DENOMINATOR = 10000;
    address public taxRecipient;
    address public controller;
    uint256 public projectId;

    constructor(
        string memory name,
        string memory symbol,
        address _controller,
        uint256 _projectId,
        address _taxRecipient
    ) ERC20(name, symbol) Ownable(msg.sender) {
        controller = _controller;
        projectId = _projectId;
        taxRecipient = _taxRecipient;
    }

    function decimals() public pure override returns (uint8) {
        return 18; // REQUIRED: Must be 18 decimals
    }

    function canBeAddedTo(uint256 _projectId) external view returns (bool) {
        return _projectId == projectId; // Only allow for our project
    }

    function mint(address holder, uint256 amount) external {
        require(msg.sender == controller, "Only controller");
        _mint(holder, amount);
    }

    function burn(address holder, uint256 amount) external {
        require(msg.sender == controller || msg.sender == holder, "Not authorized");
        _burn(holder, amount);
    }

    function _update(address from, address to, uint256 amount) internal override {
        // Skip tax for mints, burns, and controller operations
        if (from == address(0) || to == address(0) || msg.sender == controller) {
            super._update(from, to, amount);
            return;
        }

        // Apply transfer tax
        uint256 tax = (amount * TAX_RATE) / TAX_DENOMINATOR;
        uint256 netAmount = amount - tax;

        super._update(from, taxRecipient, tax);
        super._update(from, to, netAmount);
    }
}
```

### Example: Integrating Existing Community Token

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/// @notice Wrapper to make an existing token compatible with Juicebox.
/// @dev For tokens that already exist - create a wrapper that the JB controller can mint.
contract JBCompatibleToken is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    uint256 public immutable targetProjectId;

    constructor(
        string memory name,
        string memory symbol,
        uint256 _projectId,
        address controller
    ) ERC20(name, symbol) {
        targetProjectId = _projectId;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, controller);
    }

    function decimals() public pure override returns (uint8) {
        return 18;
    }

    function canBeAddedTo(uint256 projectId) external view returns (bool) {
        return projectId == targetProjectId;
    }

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external onlyRole(MINTER_ROLE) {
        _burn(from, amount);
    }
}
```

### Example: Editable Name/Symbol Token

Allows project owners to rebrand without redeploying or migrating liquidity:

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

    function name() public view override returns (string memory) { return _tokenName; }
    function symbol() public view override returns (string memory) { return _tokenSymbol; }
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

**Note**: Some DEXs/aggregators cache metadata. Changes may take time to propagate.

### Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| **Credits only** | Zero deployment cost, simplest | Not transferable, no DeFi integration |
| **Standard JBERC20** | Simple, compatible, audited | No custom mechanics |
| **Custom ERC20** | Full control over tokenomics | More complexity, audit burden, must maintain 18 decimals |

### Critical Considerations

1. **Controller must have mint/burn access** - The JBController needs to mint tokens on payments and burn on cash outs
2. **18 decimals is mandatory** - The entire Juicebox math assumes 18 decimal tokens
3. **One token per project** - A token can only be assigned to one project
4. **Credits convert to tokens** - Existing credit holders can claim tokens after ERC20 is set
5. **Token can't be changed** - Once set, you cannot swap to a different token contract

## Other Project Operations

### Transfer Ownership

Project ownership is an ERC-721 NFT. Transfer using standard ERC-721:

```solidity
IJBProjects(PROJECTS).transferFrom(currentOwner, newOwner, projectId);
```

### Set Project Metadata

```solidity
IJBProjects(PROJECTS).setTokenURI(projectId, "ipfs://newUri");
```

### Add Terminals

```solidity
IJBDirectory(DIRECTORY).setTerminalsOf(projectId, terminals);
```

## Generation Guidelines

1. **Ask about project requirements** - ownership model, token economics, payout structure
2. **Consider Revnets** if autonomous operation is desired
3. **Configure appropriate metadata** - reserved rate, cash out tax, permissions
4. **Set up splits** for payouts and reserved tokens
5. **Generate deployment scripts** using Foundry

## Example Prompts

- "Create a project that mints 1000 tokens per ETH with 10% reserved"
- "Set up a project with weekly payout cycles to 3 addresses"
- "Deploy a project with a 3-day approval delay for ruleset changes"
- "Create a project that accepts both ETH and USDC"

## Reference

- **nana-core-v5**: https://github.com/Bananapus/nana-core-v5
- **revnet-core-v5**: https://github.com/rev-net/revnet-core-v5
