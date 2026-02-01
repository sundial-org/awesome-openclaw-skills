---
name: jb-terminal-wrapper
description: |
  Terminal wrapper pattern for extending JBMultiTerminal functionality. Use when: (1) need dynamic
  splits at pay time, (2) revnet can't modify ruleset data hooks, (3) want atomic pay + distribute
  operations, (4) need to intercept/redirect tokens before delivery, (5) implementing pay-time
  configuration, (6) cash out + bridge/swap in one tx, (7) cash out + stake redeemed funds.
  Covers IJBTerminal implementation, _acceptFunds pattern from JBSwapTerminalRegistry, beneficiary
  manipulation for both pay and cash out flows, and the critical mental model that wrappers are
  additive (not restrictive).
---

# Terminal Wrapper Pattern

## Problem

Revnets and other projects often need extended payment functionality that can't be achieved through
ruleset data hooks alone. Common needs include:
- Dynamic splits specified at payment time
- Token interception and redirection
- Atomic multi-step operations (pay + distribute)
- Client-specific features without breaking permissionless access

## Context / Trigger Conditions

Apply this pattern when:
- Building payment flows that need dynamic configuration
- Working with revnets where ruleset hooks can't be edited
- Need to bundle multiple operations atomically
- Want to intercept tokens for further processing
- Implementing "pay and do X" flows

## Solution

### Core Architecture

Create a custom `IJBTerminal` that wraps `JBMultiTerminal`. Use a shared `_acceptFunds` helper
(pattern from JBSwapTerminalRegistry) to handle ETH/ERC20 consistently:

```solidity
contract PayWithSplitsTerminal is IJBTerminal {
    using SafeERC20 for IERC20;

    IJBMultiTerminal public immutable MULTI_TERMINAL;
    IJBController public immutable CONTROLLER;

    constructor(IJBMultiTerminal _multiTerminal, IJBController _controller) {
        MULTI_TERMINAL = _multiTerminal;
        CONTROLLER = _controller;
    }

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

        // 3. Accept funds (handles ETH/ERC20 uniformly)
        uint256 valueToSend = _acceptFunds(token, amount, address(MULTI_TERMINAL));

        // 4. Forward to underlying terminal
        beneficiaryTokenCount = MULTI_TERMINAL.pay{value: valueToSend}(
            projectId,
            token,
            amount,
            beneficiary,
            minReturnedTokens,
            memo,
            innerMetadata
        );

        // 5. Distribute reserved tokens
        CONTROLLER.sendReservedTokensToSplitsOf(projectId);

        return beneficiaryTokenCount;
    }

    /// @notice Accept funds from caller and prepare for forwarding.
    /// @dev Pattern from JBSwapTerminalRegistry - consolidates token handling.
    function _acceptFunds(
        address token,
        uint256 amount,
        address spender
    ) internal returns (uint256 valueToSend) {
        if (token == JBConstants.NATIVE_TOKEN) {
            return msg.value; // Forward ETH
        }

        // ERC20: pull from sender, approve spender
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        IERC20(token).forceApprove(spender, amount);
        return 0; // No ETH to forward
    }
}
```

### Beneficiary Manipulation Pattern

Intercept tokens by setting beneficiary to the wrapper itself:

```solidity
function payAndStake(
    uint256 projectId,
    address token,
    uint256 amount,
    uint256 minReturnedTokens,
    bytes calldata metadata
) external payable returns (uint256 tokenCount) {
    // Parse user's desired destination from metadata
    (address finalDestination, bytes memory stakingParams) = abi.decode(
        metadata,
        (address, bytes)
    );

    // Receive tokens to this contract
    tokenCount = MULTI_TERMINAL.pay{value: msg.value}(
        projectId,
        token,
        amount,
        address(this),  // <-- Wrapper receives tokens
        minReturnedTokens,
        "",
        ""
    );

    // Do something with the tokens
    IERC20 projectToken = IERC20(CONTROLLER.TOKENS().tokenOf(projectId));

    // Example: stake them somewhere on behalf of user
    _stakeTokens(projectToken, tokenCount, finalDestination, stakingParams);

    return tokenCount;
}
```

### Metadata Encoding (Client Side)

```typescript
import { encodeAbiParameters, parseAbiParameters } from 'viem';

// For dynamic splits
const metadata = encodeAbiParameters(
  parseAbiParameters('(address preferredBeneficiary, uint256 percent, uint256 lockedUntil)[], bytes'),
  [
    [
      { preferredBeneficiary: '0x...', percent: 500000000n, lockedUntil: 0n }, // 50%
      { preferredBeneficiary: '0x...', percent: 500000000n, lockedUntil: 0n }, // 50%
    ],
    '0x' // Inner metadata for MultiTerminal
  ]
);

// For beneficiary redirection
const metadata = encodeAbiParameters(
  parseAbiParameters('address finalDestination, bytes stakingParams'),
  [userAddress, stakingCalldata]
);
```

### Critical Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    WRAPPER IS ADDITIVE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client A ──► PayWithSplitsTerminal ──► JBMultiTerminal       │
│                    (gets special features)                      │
│                                                                 │
│   Client B ────────────────────────────► JBMultiTerminal       │
│                    (still works!)                               │
│                                                                 │
│   BOTH ARE VALID. The wrapper cannot block direct access.       │
│   This is a FEATURE, not a bug. Permissionless = good.          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Bad thinking**: "I'll use a wrapper to block payments that don't meet criteria X"
**Reality**: Users can always call `JBMultiTerminal.pay()` directly

**Good thinking**: "I'll use a wrapper to provide enhanced functionality for clients that opt in"

### Use Cases

| Use Case | How Wrapper Helps |
|----------|-------------------|
| **Pay Wrappers** | |
| Dynamic splits at pay time | Parse splits from metadata, configure before pay |
| Pay + distribute reserved | Atomic operation, no separate tx needed |
| Token interception | Receive to self, then stake/lock/forward |
| Referral tracking | Parse referrer from metadata, record on-chain |
| Conditional logic | Check conditions before forwarding to MultiTerminal |
| Multi-hop payments | Receive tokens, swap, pay another project |
| **Cash Out Wrappers** | |
| Cash out + bridge | Intercept redeemed funds, bridge to another chain |
| Cash out + swap | Swap redeemed ETH to stablecoin before delivery |
| Cash out + stake | Stake redeemed funds in another protocol |
| Cash out + LP | Add redeemed funds to liquidity pool |

### Cash Out Wrapper Pattern

Same beneficiary-to-self trick works for cash outs:

```solidity
/// @notice Cash out with automatic swap to different token.
function cashOutAndSwap(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    address tokenToReclaim,
    uint256 minTokensReclaimed,
    address tokenOut,       // Custom param: swap to this
    uint256 minAmountOut,   // Custom param: slippage
    address beneficiary,
    bytes calldata metadata
) external returns (uint256 amountOut) {
    // 1. Cash out to THIS contract (intercept funds)
    uint256 reclaimAmount = MULTI_TERMINAL.cashOutTokensOf(
        holder,
        projectId,
        tokenCount,
        tokenToReclaim,
        minTokensReclaimed,
        address(this),  // <-- Wrapper receives redeemed funds
        metadata
    );

    // 2. Swap redeemed tokens to desired output
    amountOut = _swap(tokenToReclaim, tokenOut, reclaimAmount, minAmountOut);

    // 3. Send swapped tokens to beneficiary
    _sendFunds(tokenOut, amountOut, beneficiary);

    return amountOut;
}

/// @notice Cash out with automatic bridging.
function cashOutAndBridge(
    address holder,
    uint256 projectId,
    uint256 tokenCount,
    address tokenToReclaim,
    uint256 minTokensReclaimed,
    address beneficiary,
    uint256 destChainId,
    bytes calldata metadata
) external returns (uint256 reclaimAmount) {
    // 1. Cash out to this contract
    reclaimAmount = MULTI_TERMINAL.cashOutTokensOf(
        holder,
        projectId,
        tokenCount,
        tokenToReclaim,
        minTokensReclaimed,
        address(this),
        metadata
    );

    // 2. Bridge funds to destination chain
    _bridgeFunds(tokenToReclaim, reclaimAmount, beneficiary, destChainId);

    return reclaimAmount;
}
```

### Comparison with Swap Terminal

Swap Terminal is a canonical example of this pattern:

```
User pays with USDC ──► SwapTerminal ──► Swaps to ETH ──► JBMultiTerminal
                        (wraps + transforms)
```

Your wrapper follows the same architecture but with different transformation logic.

## Verification

1. Deploy wrapper pointing to existing JBMultiTerminal
2. Test that direct MultiTerminal payments still work (permissionless)
3. Test that wrapper payments get enhanced behavior
4. Verify atomic operations complete or revert together
5. Test metadata parsing edge cases (empty, malformed)

## Example

**Complete implementation for pay-time splits:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IJBTerminal} from "@bananapus/core/src/interfaces/IJBTerminal.sol";
import {IJBMultiTerminal} from "@bananapus/core/src/interfaces/IJBMultiTerminal.sol";
import {IJBController} from "@bananapus/core/src/interfaces/IJBController.sol";
import {IJBSplits} from "@bananapus/core/src/interfaces/IJBSplits.sol";
import {JBSplit} from "@bananapus/core/src/structs/JBSplit.sol";
import {JBSplitGroup} from "@bananapus/core/src/structs/JBSplitGroup.sol";

contract DynamicSplitsTerminal is IJBTerminal {
    IJBMultiTerminal public immutable MULTI_TERMINAL;
    IJBController public immutable CONTROLLER;

    // Split group ID for reserved tokens
    uint256 constant RESERVED_TOKEN_GROUP = 1;

    error InvalidSplitTotal();

    constructor(IJBMultiTerminal _multiTerminal, IJBController _controller) {
        MULTI_TERMINAL = _multiTerminal;
        CONTROLLER = _controller;
    }

    /// @notice Pay a project with dynamic splits specified in metadata
    /// @param projectId The project to pay
    /// @param token The token to pay with (use JBConstants.NATIVE_TOKEN for ETH)
    /// @param amount The amount to pay
    /// @param beneficiary Who receives the project tokens
    /// @param minReturnedTokens Minimum tokens to receive (slippage protection)
    /// @param memo Payment memo
    /// @param metadata ABI-encoded (JBSplit[], bytes innerMetadata)
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

        // Forward payment to MultiTerminal
        beneficiaryTokenCount = MULTI_TERMINAL.pay{value: msg.value}(
            projectId,
            token,
            amount,
            beneficiary,
            minReturnedTokens,
            memo,
            innerMetadata
        );

        // Distribute reserved tokens to the new splits
        CONTROLLER.sendReservedTokensToSplitsOf(projectId);

        return beneficiaryTokenCount;
    }

    function _validateAndSetSplits(uint256 projectId, JBSplit[] memory splits) internal {
        // Validate splits sum to 100% (1e9 = JBConstants.SPLITS_TOTAL_PERCENT)
        uint256 total;
        for (uint256 i; i < splits.length; i++) {
            total += splits[i].percent;
        }
        if (total != 1e9) revert InvalidSplitTotal();

        // Get current ruleset
        uint256 rulesetId = CONTROLLER.currentRulesetOf(projectId).id;

        // Set splits for reserved token group
        JBSplitGroup[] memory groups = new JBSplitGroup[](1);
        groups[0] = JBSplitGroup({
            groupId: RESERVED_TOKEN_GROUP,
            splits: splits
        });

        CONTROLLER.setSplitGroupsOf(projectId, rulesetId, groups);
    }

    // Implement other IJBTerminal functions as pass-through...
    function addToBalanceOf(
        uint256 projectId,
        address token,
        uint256 amount,
        bool shouldReturnHeldFees,
        string calldata memo,
        bytes calldata metadata
    ) external payable {
        MULTI_TERMINAL.addToBalanceOf{value: msg.value}(
            projectId, token, amount, shouldReturnHeldFees, memo, metadata
        );
    }
}
```

## Notes

- Wrapper must be granted appropriate permissions if setting splits (add to project's permission system)
- Consider gas costs of extra operations
- Metadata parsing adds attack surface - validate carefully
- For revnets: this is often the ONLY way to add functionality post-deploy
- Multiple wrappers can exist for different purposes - they don't conflict
- Wrappers can be chained: WrapperA → WrapperB → MultiTerminal

## Related Skills

- `/jb-patterns` - All JB V5 design patterns (includes condensed version of this)
- `/jb-pay-hook` - Data hooks for pay-time logic (when ruleset allows)
- `/jb-split-hook` - Custom split distribution logic
- `/jb-v5-api` - Core terminal and controller interfaces
