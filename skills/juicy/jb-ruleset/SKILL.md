---
name: jb-ruleset
description: Configure and queue Juicebox V5 rulesets. Design ruleset parameters including issuance rate, reserved rate, cash out tax rate, splits, payout limits, and approval hooks. Generate scripts for queueing new rulesets.
---

# Juicebox V5 Ruleset Configuration

Design and queue rulesets for Juicebox V5 projects.

## What Are Rulesets?

Rulesets are time-bounded configuration packages that define project behavior:
- **Token economics**: Weight (minting rate), reserved rate
- **Cash out behavior**: Cash out tax rate
- **Fund distribution**: Payout limits, splits
- **Governance**: Approval hooks for change control

When a ruleset ends, the next queued ruleset becomes active. If no ruleset is queued, the current one recycles (with optional issuance cut).

## Ruleset Parameters

### JBRuleset (Read-Only State)

```solidity
struct JBRuleset {
    uint256 cycleNumber;        // Increments each cycle
    uint256 id;                 // Unique ruleset ID
    uint256 basedOnId;          // Previous ruleset ID
    uint256 start;              // Start timestamp
    uint256 duration;           // Duration (0 = indefinite)
    uint256 weight;             // Token minting weight (18 decimals)
    uint256 weightCutPercent;   // Weight cut per cycle (0-1000000000, where 1e9 = 100%)
    IJBRulesetApprovalHook approvalHook;
    JBRulesetMetadata metadata;
}
```

### JBRulesetMetadata

```solidity
struct JBRulesetMetadata {
    uint256 reservedRate;       // Reserved tokens (0-10000, where 10000 = 100%)
    uint256 cashOutTaxRate;     // Tax on cash outs (0-10000)
    uint256 baseCurrency;       // Base currency for accounting
    bool pausePay;              // Pause payments
    bool pauseCashOut;          // Pause cash outs
    bool pauseTransfers;        // Pause token transfers
    bool allowOwnerMinting;     // Owner can mint tokens
    bool allowTerminalMigration;
    bool allowSetTerminals;
    bool allowSetController;
    bool allowAddAccountingContexts;
    bool allowAddPriceFeed;
    bool ownerMustSendPayouts;
    bool holdFees;              // Hold fees for potential refund
    bool useTotalSurplusForCashOuts;
    bool useDataHookForPay;     // Enable pay data hook
    bool useDataHookForCashOut; // Enable cash out data hook
    address dataHook;           // Data hook address
    uint256 metadata;           // Custom metadata bits
}
```

## Queue Rulesets

Use `JBController.queueRulesetsOf()` to queue future rulesets:

```solidity
function queueRulesetsOf(
    uint256 projectId,
    JBRulesetConfig[] calldata rulesetConfigurations,
    string calldata memo
) external returns (uint256 rulesetId);
```

## Configuration Examples

### Basic Ruleset (Indefinite Duration)

```solidity
JBRulesetMetadata memory metadata = JBRulesetMetadata({
    reservedRate: 1000,         // 10% reserved
    cashOutTaxRate: 0,          // No cash out tax
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

JBRulesetConfig memory config = JBRulesetConfig({
    mustStartAtOrAfter: 0,
    duration: 0,                // Indefinite
    weight: 1e18,               // 1 token per unit
    weightCutPercent: 0,
    approvalHook: IJBRulesetApprovalHook(address(0)),
    metadata: metadata,
    splitGroups: new JBSplitGroup[](0),
    fundAccessLimitGroups: new JBFundAccessLimitGroup[](0)
});
```

### Weekly Cycles with Weight Cut

```solidity
JBRulesetConfig memory config = JBRulesetConfig({
    mustStartAtOrAfter: 0,
    duration: 7 days,           // 1 week cycles
    weight: 1000e18,            // Start at 1000 tokens/ETH
    weightCutPercent: 50000000, // 5% weight cut per cycle (50000000 / 1e9)
    approvalHook: IJBRulesetApprovalHook(address(0)),
    metadata: metadata,
    splitGroups: splitGroups,
    fundAccessLimitGroups: fundAccessLimits
});
```

### With Approval Hook (3-Day Delay)

```solidity
// JBDeadline requires 3 days notice for ruleset changes
IJBRulesetApprovalHook approvalHook = IJBRulesetApprovalHook(JB_DEADLINE);

JBRulesetConfig memory config = JBRulesetConfig({
    mustStartAtOrAfter: 0,
    duration: 30 days,
    weight: 1e18,
    weightCutPercent: 0,
    approvalHook: approvalHook,  // Requires advance notice
    metadata: metadata,
    splitGroups: splitGroups,
    fundAccessLimitGroups: fundAccessLimits
});
```

### With Data Hook

```solidity
JBRulesetMetadata memory metadata = JBRulesetMetadata({
    // ... other fields
    useDataHookForPay: true,
    useDataHookForCashOut: false,
    dataHook: address(myBuybackHook),
    // ...
});
```

## Splits Configuration

### Payout Splits

Distribute funds when payouts are triggered:

```solidity
JBSplit[] memory payoutSplits = new JBSplit[](2);

// 50% to treasury
payoutSplits[0] = JBSplit({
    preferAddToBalance: false,
    percent: 500_000_000,       // 50% (out of 1e9)
    projectId: 0,               // Not a project
    beneficiary: payable(treasuryAddress),
    lockedUntil: 0,
    hook: IJBSplitHook(address(0))
});

// 50% to another project
payoutSplits[1] = JBSplit({
    preferAddToBalance: true,   // Add to balance, not pay
    percent: 500_000_000,
    projectId: otherProjectId,
    beneficiary: payable(address(0)),
    lockedUntil: 0,
    hook: IJBSplitHook(address(0))
});

JBSplitGroup[] memory splitGroups = new JBSplitGroup[](1);
splitGroups[0] = JBSplitGroup({
    groupId: 1,                 // Payout splits group
    splits: payoutSplits
});
```

### Reserved Token Splits

Distribute reserved tokens:

```solidity
JBSplit[] memory reservedSplits = new JBSplit[](1);

reservedSplits[0] = JBSplit({
    preferAddToBalance: false,
    percent: 1_000_000_000,     // 100%
    projectId: 0,
    beneficiary: payable(teamMultisig),
    lockedUntil: block.timestamp + 365 days,  // Locked for 1 year
    hook: IJBSplitHook(address(0))
});

splitGroups[1] = JBSplitGroup({
    groupId: 2,                 // Reserved tokens group
    splits: reservedSplits
});
```

## Fund Access Limits

Set payout limits and surplus allowance:

```solidity
JBCurrencyAmount[] memory payoutLimits = new JBCurrencyAmount[](1);
payoutLimits[0] = JBCurrencyAmount({
    amount: 10 ether,
    currency: uint32(uint160(JBConstants.NATIVE_TOKEN))
});

JBCurrencyAmount[] memory surplusAllowances = new JBCurrencyAmount[](1);
surplusAllowances[0] = JBCurrencyAmount({
    amount: 0,                  // No discretionary access
    currency: uint32(uint160(JBConstants.NATIVE_TOKEN))
});

JBFundAccessLimitGroup[] memory fundAccessLimits = new JBFundAccessLimitGroup[](1);
fundAccessLimits[0] = JBFundAccessLimitGroup({
    terminal: address(TERMINAL),
    token: JBConstants.NATIVE_TOKEN,
    payoutLimits: payoutLimits,
    surplusAllowances: surplusAllowances
});
```

## Queue Script Example

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {Script} from "forge-std/Script.sol";
import {IJBController} from "@bananapus/core/src/interfaces/IJBController.sol";
// ... other imports

contract QueueRuleset is Script {
    IJBController constant CONTROLLER = IJBController(0x...);
    uint256 constant PROJECT_ID = 1;

    function run() external {
        vm.startBroadcast();

        // Build ruleset config...
        JBRulesetConfig[] memory configs = new JBRulesetConfig[](1);
        configs[0] = /* config */;

        CONTROLLER.queueRulesetsOf(PROJECT_ID, configs, "Update ruleset");

        vm.stopBroadcast();
    }
}
```

## Generation Guidelines

1. **Understand current ruleset** - check existing parameters before changes
2. **Consider timing** - rulesets activate when current one ends
3. **Use approval hooks** for governance-controlled projects
4. **Configure appropriate limits** - payout limits prevent rug pulls
5. **Lock critical splits** with `lockedUntil` timestamp

## Example Prompts

- "Queue a ruleset that increases reserved rate to 20%"
- "Set up monthly payout cycles of 5 ETH max"
- "Add a 3-day approval delay for ruleset changes"
- "Configure splits to send 30% to a DAO treasury"

## Reference

- **nana-core-v5**: https://github.com/Bananapus/nana-core-v5
