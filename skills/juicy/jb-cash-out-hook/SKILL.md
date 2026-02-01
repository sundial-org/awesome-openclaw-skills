---
name: jb-cash-out-hook
description: Generate custom Juicebox V5 cash out hooks from natural language specifications. Creates Solidity contracts implementing IJBCashOutHook and/or IJBRulesetDataHook with Foundry tests. First evaluates if off-the-shelf solutions (721 hook, Revnet) fit the use case.
---

# Juicebox V5 Cash Out Hook Generator

Generate custom cash out hooks for Juicebox V5 projects based on natural language specifications.

## Before Writing Custom Code

**Always evaluate if an off-the-shelf solution fits the user's needs:**

| User Need | Recommended Solution |
|-----------|---------------------|
| Burn NFTs to reclaim funds | Deploy **nana-721-hook-v5** directly |
| Fee extraction on cash outs | Deploy a **Revnet** (extracts 2.5% fees) |
| Autonomous treasury with cash out rules | Use **revnet-core-v5** |

If off-the-shelf solutions fit, guide the user to deploy them instead of generating custom code.

## V5 Cash Out Hook Architecture

Cash out hooks in V5 follow a two-stage pattern:

### Stage 1: Data Hook (beforeCashOutRecordedWith)
- Receives cash out info before recording
- Returns tax rate, count, supply, and hook specifications
- Can modify the effective cash out calculation
- Implements `IJBRulesetDataHook`

### Stage 2: Cash Out Hook (afterCashOutRecordedWith)
- Executes after cash out is recorded
- Receives forwarded funds and context
- Implements `IJBCashOutHook`

## JBAfterCashOutRecordedContext Fields

```solidity
struct JBAfterCashOutRecordedContext {
    address holder;                 // Token holder cashing out
    uint256 projectId;              // Project ID
    uint256 rulesetId;              // Current ruleset ID
    uint256 cashOutCount;           // Tokens being cashed out
    JBTokenAmount reclaimedAmount;  // Amount reclaimed by holder
    JBTokenAmount forwardedAmount;  // Amount forwarded to hook
    uint256 cashOutTaxRate;         // Tax rate (0-10000)
    address payable beneficiary;    // Receives reclaimed funds
    bytes hookMetadata;             // Data from data hook
    bytes cashOutMetadata;          // Data from cash out initiator
}
```

## Design Patterns

### Simple Cash Out Hook (afterCashOutRecordedWith only)
Use when you only need to execute logic after cash out without modifying calculations.

```solidity
contract SimpleCashOutHook is IJBCashOutHook, ERC165 {
    function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context) external payable {
        // Validate caller is a project terminal
        // Execute custom logic with forwarded funds
    }

    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(IJBCashOutHook).interfaceId || super.supportsInterface(interfaceId);
    }
}
```

### Data Hook + Cash Out Hook (full control)
Use when you need to modify tax rate, supply calculations, or intercept funds.

```solidity
contract FullCashOutHook is IJBRulesetDataHook, IJBCashOutHook, ERC165 {
    function beforeCashOutRecordedWith(JBBeforeCashOutRecordedContext calldata context)
        external view returns (
            uint256 cashOutTaxRate,
            uint256 cashOutCount,
            uint256 totalSupply,
            JBCashOutHookSpecification[] memory hookSpecifications
        )
    {
        // Calculate custom tax rate or modify supply
        // Specify hooks and forwarded amounts
    }

    function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context) external payable {
        // Execute with forwarded funds
        // Handle fee extraction, burning, etc.
    }

    function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
        external view returns (uint256 weight, JBPayHookSpecification[] memory hookSpecifications)
    {
        // Pass through if not handling payments
        return (context.weight, new JBPayHookSpecification[](0));
    }

    function hasMintPermissionFor(uint256) external pure returns (bool) {
        return false;
    }
}
```

### Fee Extraction Pattern (from revnet-core-v5)
Route a percentage of cash outs to a fee beneficiary.

```solidity
function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context) external payable {
    // Forward fee to beneficiary
    uint256 feeAmount = context.forwardedAmount.value;
    if (feeAmount > 0) {
        // Process fee payment
    }
}
```

### NFT Burning Pattern (from nana-721-hook-v5)
Burn NFTs when cashing out to reclaim proportional funds.

```solidity
function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context) external payable {
    // Decode token IDs from metadata
    uint256[] memory tokenIds = abi.decode(context.cashOutMetadata, (uint256[]));

    // Verify ownership and burn
    for (uint256 i; i < tokenIds.length; i++) {
        _burn(tokenIds[i]);
    }
}
```

## Generation Guidelines

1. **Ask clarifying questions** about the desired cash out behavior
2. **Evaluate off-the-shelf options** first
3. **Choose the simplest pattern** that meets requirements
4. **Include terminal validation** in afterCashOutRecordedWith
5. **Generate Foundry tests** with fork testing
6. **Use correct V5 terminology** (cash out, not redemption)

## Example Prompts

- "Create a cash out hook that burns an NFT to unlock full reclaim value"
- "I want to extract a 5% fee on all cash outs to a treasury address"
- "Build a hook that only allows cash outs after a vesting period"
- "Create a hook that requires holding a specific NFT to cash out"

## Reference Implementations

- **nana-721-hook-v5**: https://github.com/Bananapus/nana-721-hook-v5 (burns NFTs on cash out)
- **revnet-core-v5**: https://github.com/rev-net/revnet-core-v5 (fee extraction)

## Output Format

Generate:
1. Main contract in `src/`
2. Interface in `src/interfaces/` if needed
3. Test file in `test/`
4. Deployment script in `script/` if requested

Use Foundry project structure with forge-std.
