---
name: jb-split-hook
description: Generate custom Juicebox V5 split hooks from natural language specifications. Creates Solidity contracts implementing IJBSplitHook with Foundry tests. Split hooks process individual payout or reserved token splits with custom logic like DeFi integrations.
---

# Juicebox V5 Split Hook Generator

Generate custom split hooks for Juicebox V5 projects based on natural language specifications.

## What Are Split Hooks?

Split hooks allow custom processing when funds are distributed through payout splits or reserved token splits. They're useful for:

- **DeFi integrations**: Route payouts to liquidity pools, staking, or yield protocols
- **Multi-recipient routing**: Split a single split further among multiple addresses
- **Token swaps**: Convert received tokens before forwarding
- **Custom accounting**: Track or transform distributions

**Note**: Split hooks can be added to **Revnets** for token distribution just like any other Juicebox project.

## V5 Split Hook Architecture

Split hooks implement a single function that receives funds optimistically and processes them.

```solidity
interface IJBSplitHook is IERC165 {
    /// @notice Process a single split with custom logic.
    /// @dev Tokens and native currency are optimistically transferred to the hook.
    /// @param context The context passed by the terminal or controller.
    function processSplitWith(JBSplitHookContext calldata context) external payable;
}
```

## JBSplitHookContext Fields

```solidity
struct JBSplitHookContext {
    address token;          // Token being distributed (address(0) for native)
    uint256 amount;         // Amount sent to this split
    uint256 decimals;       // Token decimals
    uint256 projectId;      // Project distributing funds
    uint256 groupId;        // Split group ID
    JBSplit split;          // The split configuration
}
```

## JBSplit Configuration

```solidity
struct JBSplit {
    bool preferAddToBalance;    // Add to project balance instead of paying
    uint256 percent;            // Percent of distribution (out of 1000000000)
    uint256 projectId;          // Project to pay (0 for wallet)
    address payable beneficiary; // Wallet if projectId is 0
    uint256 lockedUntil;        // Timestamp until split is locked
    IJBSplitHook hook;          // This split hook address
}
```

## Design Patterns

### Basic Split Hook

```solidity
contract BasicSplitHook is IJBSplitHook, ERC165 {
    function processSplitWith(JBSplitHookContext calldata context) external payable override {
        // Funds have been transferred to this contract
        // Process them according to custom logic

        if (context.token == address(0)) {
            // Handle native currency (ETH)
            uint256 amount = address(this).balance;
            // ... custom logic
        } else {
            // Handle ERC20 token
            uint256 amount = IERC20(context.token).balanceOf(address(this));
            // ... custom logic
        }
    }

    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(IJBSplitHook).interfaceId || super.supportsInterface(interfaceId);
    }
}
```

### Uniswap V3 LP Split Hook Pattern

Route payouts to a Uniswap V3 liquidity position.

```solidity
contract UniswapV3LPSplitHook is IJBSplitHook, ERC165 {
    INonfungiblePositionManager public immutable POSITION_MANAGER;
    uint256 public tokenId; // LP position NFT ID

    function processSplitWith(JBSplitHookContext calldata context) external payable override {
        if (context.token == address(0)) {
            // Wrap ETH to WETH
            WETH.deposit{value: msg.value}();
        }

        // Add liquidity to existing position or create new one
        // ...
    }
}
```

### Multi-Recipient Split Hook

Split funds further among multiple recipients.

```solidity
contract MultiRecipientSplitHook is IJBSplitHook, ERC165 {
    struct Recipient {
        address payable addr;
        uint256 percent; // Out of 10000
    }

    Recipient[] public recipients;

    function processSplitWith(JBSplitHookContext calldata context) external payable override {
        uint256 total = context.amount;

        for (uint256 i; i < recipients.length; i++) {
            uint256 share = (total * recipients[i].percent) / 10000;

            if (context.token == address(0)) {
                recipients[i].addr.transfer(share);
            } else {
                IERC20(context.token).transfer(recipients[i].addr, share);
            }
        }
    }
}
```

### Token Swap Split Hook

Swap received tokens before forwarding.

```solidity
contract SwapSplitHook is IJBSplitHook, ERC165 {
    ISwapRouter public immutable ROUTER;
    address public immutable OUTPUT_TOKEN;
    address public immutable BENEFICIARY;

    function processSplitWith(JBSplitHookContext calldata context) external payable override {
        // Approve router
        IERC20(context.token).approve(address(ROUTER), context.amount);

        // Swap to output token
        uint256 amountOut = ROUTER.exactInputSingle(
            ISwapRouter.ExactInputSingleParams({
                tokenIn: context.token,
                tokenOut: OUTPUT_TOKEN,
                fee: 3000,
                recipient: BENEFICIARY,
                amountIn: context.amount,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            })
        );
    }
}
```

## Configuring Split Hooks

To use a split hook, configure it in a project's split group:

```solidity
JBSplit memory split = JBSplit({
    preferAddToBalance: false,
    percent: 100_000_000, // 10% (out of 1_000_000_000)
    projectId: 0,
    beneficiary: payable(address(0)),
    lockedUntil: 0,
    hook: IJBSplitHook(address(mySplitHook))
});
```

## Generation Guidelines

1. **Understand the distribution flow** - splits receive funds during payout or reserved token distribution
2. **Handle both ETH and ERC20** - check `context.token` to determine token type
3. **Consider gas costs** - complex DeFi operations may be expensive
4. **Include proper error handling** - failed external calls should be handled gracefully
5. **Generate Foundry tests** with fork testing for DeFi integrations

## Example Prompts

- "Create a split hook that deposits ETH into Lido and sends stETH to a beneficiary"
- "I want to route 50% of payouts to a Uniswap V3 LP position"
- "Build a split hook that swaps tokens to USDC before sending to treasury"
- "Create a hook that splits incoming funds among 5 DAO multisigs"

## Reference Implementations

- **uniswapv3-lp-split-hook**: https://github.com/kyzooghost/uniswapv3-lp-split-hook

## Output Format

Generate:
1. Main contract in `src/`
2. Interface in `src/interfaces/` if needed
3. Test file in `test/`
4. Deployment script in `script/` if requested

Use Foundry project structure with forge-std.
