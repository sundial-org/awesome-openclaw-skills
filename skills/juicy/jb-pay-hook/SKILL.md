---
name: jb-pay-hook
description: Generate custom Juicebox V5 pay hooks from natural language specifications. Creates Solidity contracts implementing IJBPayHook and/or IJBRulesetDataHook with Foundry tests. First evaluates if off-the-shelf solutions (buyback hook, 721 hook, Revnet) fit the use case.
---

# Juicebox V5 Pay Hook Generator

Generate custom pay hooks for Juicebox V5 projects based on natural language specifications.

## Before Writing Custom Code

**Always evaluate if an off-the-shelf solution fits the user's needs:**

| User Need | Recommended Solution |
|-----------|---------------------|
| Token buybacks via Uniswap | Deploy **nana-buyback-hook-v5** directly |
| Tiered NFT rewards on payment | Deploy **nana-721-hook-v5** directly |
| Autonomous tokenized treasury | Deploy a **Revnet** via revnet-core-v5 |
| Revnet with NFT tiers | Use **Tiered721RevnetDeployer** |
| Revnet with custom pay hooks | Use **PayHookRevnetDeployer** |

If off-the-shelf solutions fit, guide the user to deploy them instead of generating custom code.

## V5 Pay Hook Architecture

Pay hooks in V5 follow a two-stage pattern:

### Stage 1: Data Hook (beforePayRecordedWith)
- Receives payment info before recording
- Returns adjusted weight and hook specifications
- Implements `IJBRulesetDataHook`

### Stage 2: Pay Hook (afterPayRecordedWith)
- Executes after payment is recorded
- Receives forwarded funds and context
- Implements `IJBPayHook`

A contract can implement both interfaces (like the buyback hook) or just the pay hook.

## JBAfterPayRecordedContext Fields

```solidity
struct JBAfterPayRecordedContext {
    address payer;                  // Payment originator
    uint256 projectId;              // Project being paid
    uint256 rulesetId;              // Current ruleset ID
    JBTokenAmount amount;           // Payment amount
    JBTokenAmount forwardedAmount;  // Amount forwarded to hook
    uint256 weight;                 // Token minting weight
    uint256 newlyIssuedTokenCount;  // Tokens minted
    address beneficiary;            // Token recipient
    bytes hookMetadata;             // Data from data hook
    bytes payerMetadata;            // Data from payer
}
```

## Design Patterns

### Simple Pay Hook (afterPayRecordedWith only)
Use when you only need to execute logic after payment without modifying minting behavior.

```solidity
contract SimplePayHook is IJBPayHook, ERC165 {
    function afterPayRecordedWith(JBAfterPayRecordedContext calldata context) external payable {
        // Validate caller is a project terminal
        // Execute custom logic
    }

    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(IJBPayHook).interfaceId || super.supportsInterface(interfaceId);
    }
}
```

### Data Hook + Pay Hook (full control)
Use when you need to modify weight, intercept funds, or control hook routing.

```solidity
contract FullPayHook is IJBRulesetDataHook, IJBPayHook, ERC165 {
    function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
        external view returns (uint256 weight, JBPayHookSpecification[] memory hookSpecifications)
    {
        // Analyze payment, determine routing
        // Return weight and hook specs
    }

    function afterPayRecordedWith(JBAfterPayRecordedContext calldata context) external payable {
        // Execute with forwarded funds
    }

    function beforeCashOutRecordedWith(JBBeforeCashOutRecordedContext calldata context)
        external view returns (uint256, uint256, uint256, JBCashOutHookSpecification[] memory)
    {
        // Pass through if not handling cash outs
        return (context.ruleset.cashOutTaxRate, context.cashOutCount, context.totalSupply, new JBCashOutHookSpecification[](0));
    }

    function hasMintPermissionFor(uint256) external pure returns (bool) {
        return false; // Only true if hook needs to mint
    }
}
```

### Contract-as-Owner Pattern
Use when the project needs to be autonomous with structured rules and delegated permissions.

Reference: **revnet-core-v5** (REVDeployer)
- Contract owns the Juicebox project NFT
- Implements hooks and controls project configuration
- Delegates authority via JBPermissions

## Generation Guidelines

1. **Ask clarifying questions** about the desired behavior
2. **Evaluate off-the-shelf options** first
3. **Choose the simplest pattern** that meets requirements
4. **Include terminal validation** in afterPayRecordedWith
5. **Generate Foundry tests** with fork testing against deployed contracts
6. **Use correct V5 terminology** (ruleset, cash out, weight, reserved rate)

## Example Prompts

- "Create a pay hook that mints a custom ERC20 token proportional to payments"
- "I want to reward payers with points based on payment amount"
- "Build a hook that routes 10% of payments to a charity address"
- "Create an autonomous project that caps individual payment amounts"

## Reference Implementations

- **nana-buyback-hook-v5**: https://github.com/Bananapus/nana-buyback-hook-v5
- **nana-721-hook-v5**: https://github.com/Bananapus/nana-721-hook-v5
- **revnet-core-v5**: https://github.com/rev-net/revnet-core-v5

## Output Format

Generate:
1. Main contract in `src/`
2. Interface in `src/interfaces/` if needed
3. Test file in `test/`
4. Deployment script in `script/` if requested

Use Foundry project structure with forge-std.
