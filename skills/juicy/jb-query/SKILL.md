---
name: jb-query
description: Query Juicebox V5 project state from the blockchain. Read project configurations, rulesets, terminal balances, token holder data, and splits using cast or ethers.js. Supports mainnet and testnets.
---

# Juicebox V5 Chain Queries

Query on-chain state for Juicebox V5 projects.

## Quick Reference - Contract Functions

### JBProjects (ERC-721)
```solidity
count() → uint256                    // Total projects created
ownerOf(projectId) → address         // Project owner
tokenURI(projectId) → string         // Project metadata URI
```

### JBDirectory
```solidity
controllerOf(projectId) → address              // Project's controller (CRITICAL for version detection!)
terminalsOf(projectId) → IJBTerminal[]         // All terminals
primaryTerminalOf(projectId, token) → address  // Primary terminal for token
isTerminalOf(projectId, terminal) → bool       // Check terminal validity
```

**IMPORTANT**: `controllerOf()` is the ONLY authoritative way to determine which contract version
a project uses. Compare the returned address against known V5/V5.1 controller addresses:
- V5.0: `0x27da30646502e2f642be5281322ae8c394f7668a`
- V5.1: `0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1`

Some non-revnet projects use V5.0 contracts. Never assume version based on ownership.

### JBController
```solidity
currentRulesetOf(projectId) → (JBRuleset, JBRulesetMetadata)
getRulesetOf(projectId, rulesetId) → (JBRuleset, JBRulesetMetadata)
upcomingRulesetOf(projectId) → (JBRuleset, JBRulesetMetadata)
latestQueuedRulesetOf(projectId) → (JBRuleset, JBRulesetMetadata, approvalStatus)
totalTokenSupplyWithReservedTokensOf(projectId) → uint256
pendingReservedTokenBalanceOf(projectId) → uint256
```

### JBTokens
```solidity
tokenOf(projectId) → address         // ERC-20 token address
totalBalanceOf(holder, projectId) → uint256   // Holder's token balance
totalCreditSupplyOf(projectId) → uint256      // Unclaimed credits
```

### JBMultiTerminal
```solidity
currentSurplusOf(projectId, accountingContexts, decimals, currency) → uint256
```

### JBSplits
```solidity
splitsOf(projectId, rulesetId, groupId) → JBSplit[]
```

### JBFundAccessLimits
```solidity
payoutLimitOf(projectId, rulesetId, terminal, token, currency) → uint256
usedPayoutLimitOf(projectId, terminal, token, rulesetCycleNumber) → uint256
surplusAllowanceOf(projectId, rulesetId, terminal, token, currency) → uint256
usedSurplusAllowanceOf(projectId, terminal, token, rulesetId) → uint256
```

## Cast Commands (Foundry)

### Get Project Owner
```bash
cast call $JB_PROJECTS "ownerOf(uint256)(address)" $PROJECT_ID --rpc-url $RPC_URL
```

### Get Current Ruleset
```bash
cast call $JB_CONTROLLER "currentRulesetOf(uint256)" $PROJECT_ID --rpc-url $RPC_URL
```

### Get Project Token
```bash
cast call $JB_TOKENS "tokenOf(uint256)(address)" $PROJECT_ID --rpc-url $RPC_URL
```

### Get Terminal Balance
```bash
cast call $JB_TERMINAL "currentSurplusOf(uint256,address[],uint256,uint256)" \
    $PROJECT_ID \
    "[$NATIVE_TOKEN]" \
    18 \
    $NATIVE_TOKEN \
    --rpc-url $RPC_URL
```

### Get Splits
```bash
# Reserved token splits (groupId = 1, JBSplitGroupIds.RESERVED_TOKENS)
cast call $JB_SPLITS "splitsOf(uint256,uint256,uint256)" \
    $PROJECT_ID $RULESET_ID 1 \
    --rpc-url $RPC_URL

# Payout splits - groupId = uint256(uint160(token))
# For ETH payouts: groupId = uint256(uint160(0x000000000000000000000000000000000000EEEe))
# The payout split group is derived from the token address being paid out
NATIVE_TOKEN="0x000000000000000000000000000000000000EEEe"
ETH_PAYOUT_GROUP=$(cast --to-uint256 $NATIVE_TOKEN)
cast call $JB_SPLITS "splitsOf(uint256,uint256,uint256)" \
    $PROJECT_ID $RULESET_ID $ETH_PAYOUT_GROUP \
    --rpc-url $RPC_URL

# For USDC payouts (example on mainnet):
USDC_ADDRESS="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_PAYOUT_GROUP=$(cast --to-uint256 $USDC_ADDRESS)
cast call $JB_SPLITS "splitsOf(uint256,uint256,uint256)" \
    $PROJECT_ID $RULESET_ID $USDC_PAYOUT_GROUP \
    --rpc-url $RPC_URL
```

### Get Token Balance
```bash
cast call $JB_TOKENS "totalBalanceOf(address,uint256)(uint256)" \
    $HOLDER_ADDRESS $PROJECT_ID \
    --rpc-url $RPC_URL
```

## TypeScript Examples (ethers.js)

### Setup
```typescript
import { ethers } from 'ethers';

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);

// Contract ABIs (simplified)
const PROJECTS_ABI = ['function ownerOf(uint256) view returns (address)'];
const CONTROLLER_ABI = ['function currentRulesetOf(uint256) view returns (tuple, tuple)'];
const TOKENS_ABI = ['function tokenOf(uint256) view returns (address)'];

const projects = new ethers.Contract(JB_PROJECTS, PROJECTS_ABI, provider);
const controller = new ethers.Contract(JB_CONTROLLER, CONTROLLER_ABI, provider);
const tokens = new ethers.Contract(JB_TOKENS, TOKENS_ABI, provider);
```

### Query Project Info
```typescript
async function getProjectInfo(projectId: number) {
    const owner = await projects.ownerOf(projectId);
    const [ruleset, metadata] = await controller.currentRulesetOf(projectId);
    const tokenAddress = await tokens.tokenOf(projectId);

    return {
        owner,
        ruleset: {
            cycleNumber: ruleset.cycleNumber,
            weight: ruleset.weight,
            duration: ruleset.duration,
        },
        metadata: {
            reservedRate: metadata.reservedRate,
            cashOutTaxRate: metadata.cashOutTaxRate,
            dataHook: metadata.dataHook,
        },
        tokenAddress,
    };
}
```

### Query Token Holders
```typescript
async function getTokenBalance(holder: string, projectId: number) {
    const balance = await tokens.totalBalanceOf(holder, projectId);
    return ethers.formatEther(balance);
}
```

## Common Queries

### "Which contract version does project X use?"
**ALWAYS start here before making any other queries that involve versioned contracts.**
```bash
# Check JBDirectory.controllerOf() - the authoritative source
cast call 0x0061e516886a0540f63157f112c0588ee0651dcf \
  "controllerOf(uint256)(address)" $PROJECT_ID --rpc-url $RPC_URL

# V5.0 controller: 0x27da30646502e2f642be5281322ae8c394f7668a
# V5.1 controller: 0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1
```
Then use the matching versioned contracts (terminal, rulesets, etc.) for all subsequent queries.

### "What's the current state of project X?"
1. **First**: Get controller version via `JBDirectory.controllerOf(projectId)` - determines which contracts to use
2. Get owner: `JBProjects.ownerOf(projectId)`
3. Get ruleset: Use correct versioned `JBController.currentRulesetOf(projectId)`
4. Get token: `JBTokens.tokenOf(projectId)`
5. Get terminals: `JBDirectory.terminalsOf(projectId)`
6. Get surplus: Use correct versioned `JBMultiTerminal.currentSurplusOf(...)`

### "Who are the split recipients?"
1. Get current ruleset ID from `currentRulesetOf`
2. Query reserved splits: `JBSplits.splitsOf(projectId, rulesetId, 1)` (group 1 = RESERVED_TOKENS)
3. Query payout splits: `JBSplits.splitsOf(projectId, rulesetId, uint256(uint160(token)))`
   - For native token (ETH): group = uint256(uint160(JBConstants.NATIVE_TOKEN))
   - For USDC: group = uint256(uint160(USDC_ADDRESS))

### "How much can be paid out?"
1. Get payout limit: `JBFundAccessLimits.payoutLimitOf(...)`
2. Get used amount: `JBFundAccessLimits.usedPayoutLimitOf(...)`
3. Remaining = limit - used

### "What hooks are configured?"
1. Get ruleset metadata from `currentRulesetOf`
2. Check `useDataHookForPay` and `useDataHookForCashOut`
3. Get hook address from `dataHook`

## Network RPC URLs

| Network | RPC URL |
|---------|---------|
| Ethereum | `https://eth.llamarpc.com` |
| Sepolia | `https://rpc.sepolia.org` |
| Optimism | `https://mainnet.optimism.io` |
| Arbitrum | `https://arb1.arbitrum.io/rpc` |
| Base | `https://mainnet.base.org` |

## Generation Guidelines

1. **Identify the data needed** from user's question
2. **Determine which contracts** to query
3. **Provide cast commands** for quick CLI queries
4. **Provide TypeScript** for programmatic access
5. **Use the /jb-docs skill** to get current contract addresses

## Example Prompts

- "What's the current ruleset for project 123?"
- "Who owns project 456?"
- "How much surplus does project 789 have?"
- "List all payout splits for project 42"
- "What's my token balance in project 100?"
