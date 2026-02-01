---
name: jb-v5-impl
description: Deep implementation knowledge for Juicebox V5 protocol. Covers internal mechanics, edge cases, tradeoffs, gas considerations, and critical integration patterns. Use when reasoning about how things work internally.
---

# Juicebox V5 Implementation Deep Dive

This skill provides deep implementation knowledge for integrators, covering internal mechanics, edge cases, tradeoffs, and critical considerations.

---

## Payment Flow Internals

### JBMultiTerminal.pay() Execution

```
User calls pay()
  → _pay() internal
    → STORE.recordPaymentFrom()
      → Validates ruleset exists and !pausePay
      → Invokes data hook if useDataHookForPay
      → Calculates tokens: mulDiv(amount, weight, weightRatio)
      → Returns hook specifications
    → TOKENS.mintFor() via controller
    → Executes pay hook specifications
    → Emits Pay event
  → Validates minReturnedTokens
```

### Critical Implementation Details

**Weight Calculation**: Token minting uses fixed-point math with 18 decimals:
```solidity
tokenCount = mulDiv(amount.value, weight, 10**18)
```
The `weight` is the ruleset's configured weight (tokens per unit of currency).

**Data Hook Override**: When `useDataHookForPay` is true, the data hook can:
- Return a modified weight (affecting token count)
- Specify pay hooks to receive forwarded funds
- Pass custom metadata to pay hooks

**Hook Execution Order**: Pay hooks execute sequentially after token minting. Each hook receives its specified amount from the payment.

### Edge Cases

1. **Zero weight**: No tokens minted, but payment still accepted
2. **Data hook reverts**: Entire payment reverts
3. **Pay hook reverts**: Entire payment reverts (no partial execution)
4. **Insufficient minReturnedTokens**: Reverts after all execution (gas wasted)

### Gas Considerations

- Single payment without hooks: ~150k gas
- With data hook: +50-100k gas depending on hook complexity
- Each pay hook: +variable gas based on hook logic
- Metadata decoding adds ~5k gas per 32 bytes

---

## Cash Out (Redemption) Mechanics

### Bonding Curve Formula

The cash out calculation implements a modified bonding curve:

```
Base = (surplus × cashOutCount) / totalSupply

taxFactor = (MAX_RATE - taxRate) + (taxRate × cashOutCount / totalSupply)

reclaimAmount = base × taxFactor / MAX_RATE
```

Where `MAX_RATE = 10000` (representing 100%).

### Tax Rate Implications

| Tax Rate | Effect |
|----------|--------|
| 0% | Linear redemption: get proportional share of surplus |
| 50% | Partial penalty: larger redemptions penalized more |
| 100% | No redemption possible: returns 0 |

**Critical Insight**: The tax rate creates a curve where:
- Small redemptions get closer to proportional value
- Large redemptions (relative to supply) are penalized exponentially
- At 100% tax rate, surplus is locked forever

### Surplus Calculation

Surplus is calculated as:
```
surplus = balance - remainingPayoutLimit
```

The `useTotalSurplusForCashOuts` metadata flag determines whether to use:
- **Terminal surplus**: Only this terminal's balance minus its payout limit
- **Total surplus**: Aggregated across all project terminals

**Tradeoff**: Total surplus provides more accurate valuation but costs more gas due to multi-terminal queries.

### Edge Cases

1. **Zero surplus**: No reclaim possible regardless of token count
2. **100% tax rate**: Returns 0, tokens still burned
3. **Cash out count > total supply**: Reverts
4. **Paused cash outs**: Reverts via ruleset check

---

## Ruleset Transition Mechanics

### Approval Hook Flow

```
Queue ruleset
  → approvalHook.approvalStatusOf() called
  → If ApprovalExpected: queued but not yet active
  → If Approved: becomes current when start time reached
  → If Failed/Empty: reverts to base ruleset
```

**JBDeadline Implementation**: Requires `DURATION()` seconds between queue time and ruleset start. If queued too late, approval fails.

### Weight Cut Algorithm

Weight is cut exponentially each cycle:
```solidity
newWeight = weight × (MAX_CUT - weightCutPercent) / MAX_CUT
```

Applied iteratively for each cycle that has passed.

**Optimization**: For large cycle counts (>1000), the contract uses cached intermediate values to avoid O(n) computation:
```solidity
if (multiple > 1000) {
    // Use cached values at 50,000 interval checkpoints
}
```

### Ruleset Inheritance

When a ruleset is queued:
1. It inherits from the current (or latest approved) ruleset
2. Only changed parameters override inherited values
3. The `basedOnId` field tracks inheritance chain

**Critical Consideration**: If an approval hook rejects a ruleset, the system walks backward through the inheritance chain to find the latest approved ancestor.

### Cycle Number Derivation

```solidity
cycleNumber = 1 + (currentTime - start) / duration
```

For rulesets with `duration = 0` (infinite), cycle number stays at 1.

---

## Reserved Token Distribution

### Accumulation Model

Reserved tokens don't mint immediately. Instead:
```solidity
pendingReservedTokenBalanceOf[projectId] += (tokenCount × reservedRate) / MAX_RATE
```

Tokens accumulate until `sendReservedTokensToSplitsOf()` is called.

### Distribution Flow

```
sendReservedTokensToSplitsOf()
  → Reads pendingReservedTokenBalanceOf
  → Resets pending balance to 0
  → Mints all reserved tokens to controller
  → Distributes via _sendReservedTokensToSplitGroupOf()
    → For each split:
      → If projectId set: pay that project
      → If hook set: call hook
      → Else: transfer to beneficiary
  → Leftover sent to project owner
```

### Tradeoffs

**Batched Distribution**:
- Pro: Gas efficient (one mint operation)
- Con: Recipients wait for manual trigger
- Con: Large accumulations can hit gas limits

**Per-Payment Distribution** (alternative pattern):
- Pro: Immediate distribution
- Con: Higher per-payment gas cost

---

## Splits System Details

### Storage Packing

Splits use packed storage for gas efficiency:
```
Slot 1: percent (32) | projectId (64) | beneficiary (160)
Slot 2: preferAddToBalance (1) | lockedUntil (48) | hook (160)
```

### Locked Splits Behavior

When updating splits:
1. All currently locked splits must be included
2. Lock period can only be extended, never shortened
3. Other properties of locked splits cannot change

**Edge Case**: If a locked split's beneficiary becomes a contract that can't receive funds, those funds are stuck until lock expires.

### Split Execution

```solidity
for each split:
    amount = totalAmount × split.percent / SPLITS_TOTAL_PERCENT

    if (split.hook != address(0)):
        // Optimistically transfer to hook
        hook.processSplitWith(context)
    else if (split.projectId != 0):
        if (split.preferAddToBalance):
            terminal.addToBalanceOf(projectId, ...)
        else:
            terminal.pay(projectId, ...)
    else:
        // Direct transfer to beneficiary
```

**Critical**: Split hooks receive funds optimistically before `processSplitWith()` is called. Malicious hooks could steal funds.

---

## Buyback Hook Decision Logic

### Mint vs Swap Comparison

```
mintTokens = amount × weight / 10^18
swapTokens = TWAP_quote - slippageTolerance

if (swapTokens > mintTokens):
    route through swap
else:
    standard mint
```

### TWAP Calculation

1. Fetch oldest observation from Uniswap pool
2. If observation window < configured TWAP window, use available window
3. Calculate arithmetic mean tick over window
4. Convert tick to price quote
5. Apply slippage tolerance based on swap size vs. pool liquidity

### Slippage Tolerance Tiers

```
base = (amountIn × 10 × DENOMINATOR) / poolLiquidity

if base > 150 bps: tolerance = 12%
if base > 100 bps: tolerance = 33%
if base > 75 bps: tolerance = 5%
... (progressive reduction)
```

### Failure Handling

```solidity
try uniswapPool.swap(...) returns (int256 amount0, int256 amount1) {
    // Process successful swap
} catch {
    // Return 0, triggering fallback to standard mint
}
```

**Critical**: Failed swaps don't revert the entire payment. The hook gracefully falls back to standard minting.

### Leftover Handling

After swap execution:
```solidity
if (leftoverAmount > 0) {
    controller.mintTokensOf(projectId, leftoverAmount, beneficiary, ...)
}
```

Ensures no user funds are lost to rounding or partial swaps.

---

## 721 Hook Tier Mechanics

### Payment Processing Flow

```
afterPayRecordedWith()
  → Decode metadata for tier IDs
  → If no tiers specified: auto-select based on price
  → STORE.recordMint() validates:
    → Total tier prices ≤ payment amount
    → Tiers have remaining supply
    → Tiers are active
  → Mint NFTs to beneficiary
  → Handle leftover as credits or revert
```

### Credit System

```solidity
payCreditsOf[payer] += leftover

// On next payment:
effectiveAmount = payment + payCreditsOf[payer]
payCreditsOf[payer] = 0
```

**Tradeoff**: Credits provide flexibility but:
- Accumulate dust from rounding
- Can't be withdrawn, only used for NFTs
- Lost if hook is changed

### Cash Out Weight

Each NFT's cash out value equals its tier price:
```solidity
weight = tier.price × redemptionRate
```

The `totalCashOutWeight()` aggregates all outstanding NFT values for proportion calculations.

**Critical**: If NFT prices vary significantly, small-price NFT holders receive proportionally less than their initial payment.

---

## Fee Mechanics

### Fee Calculation

```solidity
FEE = 25  // 2.5% (out of 1000)
feeAmount = amount × FEE / (1000 + FEE)  // ~2.44% of gross
```

Note: Fee is calculated as a portion of the gross amount, not added on top.

### Fee Applicability

Fees apply to:
- Payouts to non-project addresses
- Surplus allowance usage
- Cash outs with tax rate < 100%

Fees exempt:
- Project-to-project payments
- Feeless addresses (registered in JBFeelessAddresses)
- Internal transfers

### Held Fees

When `holdFees` is true in ruleset metadata:
```solidity
heldFeesOf[projectId][token].push(fee)
// Fees held for 28 days
// Can be refunded by adding equivalent to balance
```

After 28 days, held fees can be processed to the fee beneficiary (Project #1).

---

## Integration Recommendations

### For Payment Integrators

1. **Always set reasonable minReturnedTokens** to protect against frontrunning
2. **Consider data hook gas costs** when estimating transaction costs
3. **Handle pay hook reverts** gracefully in UI
4. **Validate metadata encoding** matches hook expectations

### For Hook Developers

1. **Keep beforePayRecordedWith() view-only and light** - it runs on every payment
2. **Handle failures gracefully** in afterPayRecordedWith() - don't lock user funds
3. **Validate msg.sender** is an authorized terminal
4. **Consider reentrancy** - hooks receive funds before execution

### For Project Operators

1. **Lock critical splits** to prevent rug pulls
2. **Use approval hooks** for governance-controlled projects
3. **Monitor pending reserved tokens** and distribute regularly
4. **Set appropriate payout limits** to constrain risk

### Gas Optimization Tips

1. **Batch operations** when possible (queue multiple rulesets)
2. **Use credits** for 721 hook instead of exact payments
3. **Distribute reserved tokens** during low-gas periods
4. **Consider total vs terminal surplus** tradeoff for cash outs

---

## Common Pitfalls

1. **Setting minReturnedTokens = 0**: Vulnerable to sandwich attacks
2. **Forgetting to include locked splits**: Update transaction reverts
3. **Assuming immediate reserved distribution**: Tokens accumulate
4. **Not handling hook metadata correctly**: Silent failures or reverts
5. **Ignoring approval hook delays**: Rulesets rejected if queued late
6. **Underestimating gas for multi-hook payments**: Transaction fails
7. **Not validating surplus exists before cash out**: Wasted gas on revert

---

## Core Infrastructure Contracts

### JBDirectory

The directory manages terminal and controller assignments for projects.

#### Storage Architecture

```solidity
mapping(uint256 projectId => IJBController) public controllerOf;
mapping(uint256 projectId => IJBTerminal[]) internal _terminalsOf;
mapping(uint256 projectId => mapping(address token => IJBTerminal)) internal _primaryTerminalOf;
mapping(address => bool) public isAllowedToSetFirstController;
```

#### Terminal Management

**setTerminalsOf()** replaces the entire terminal array:
- Validates no duplicates via nested loop
- Requires `SET_TERMINALS` permission OR caller is project controller
- Checks ruleset's `setTerminalsAllowed` flag (bypassed if controller is caller)

**primaryTerminalOf()** resolution:
1. Return explicitly-set primary terminal if still valid
2. Otherwise, return first terminal accepting that token
3. Return zero address if none found

#### Controller Migration

**setControllerOf()** handles migration:
1. Validates `SET_CONTROLLER` permission OR first-time setup via allowlist
2. Checks ruleset's `setControllerAllowed` flag
3. Calls `IJBMigratable.migrate()` on old controller if interface supported

**Critical**: First controller can only be set by addresses on the `isAllowedToSetFirstController` allowlist.

---

### JBProjects

ERC-721 contract where each token represents a Juicebox project.

#### Project Creation

```solidity
function createFor(address owner) external returns (uint256 projectId) {
    projectId = ++count;
    _mint(owner, projectId);
}
```

The `count` variable acts as both total project counter and next project ID.

#### Metadata Resolution

```solidity
function tokenURI(uint256 projectId) public view override returns (string memory) {
    if (address(tokenUriResolver) == address(0)) return "";
    return tokenUriResolver.tokenUriOf(address(this), projectId);
}
```

**Graceful Degradation**: Returns empty string if no resolver set, preventing reverts.

#### ERC-2771 Support

Overrides `_msgSender()`, `_msgData()`, and `_contextSuffixLength()` for meta-transaction support via trusted forwarder.

---

### JBPermissions

Bitmap-based permission system enabling granular access control.

#### Storage Architecture

```solidity
mapping(
    address operator => mapping(
        address account => mapping(
            uint256 projectId => uint256 packedPermissions
        )
    )
) public permissionsOf;
```

Each bit in the `uint256` represents one of 256 possible permissions. Project ID `0` is the wildcard, granting permissions across all projects.

#### Permission Checking

**hasPermission()** implements hierarchical evaluation:

```
1. If includeRoot && operator has ROOT permission:
   → Check specific project OR wildcard project
   → Return true if ROOT found

2. Check specific permissionId bit on specific project

3. If includeWildcardProjectId:
   → Check specific permissionId bit on project 0
```

**hasPermissions()** (batch check):
- Returns true immediately if ROOT permission exists
- Iterates through all requested permissions
- Returns false if ANY permission missing

#### Security Constraints in setPermissionsFor()

```solidity
// Only account holder or authorized operators can modify
if (_msgSender() != account) {
    // Operators cannot grant ROOT permission
    if (permissionsData.permissionIds contains ROOT) revert;

    // ROOT operators cannot modify wildcard project
    if (projectId == 0) revert;

    // Must have ROOT on specific project to modify
    if (!hasPermission(ROOT, projectId)) revert;
}
```

**Edge Cases**:
- Permission ID 0 is reserved, cannot be set
- Permission IDs > 255 revert with `PermissionIdOutOfBounds`
- Empty permission arrays are valid (clears all permissions)

---

### JBTokens

Dual-balance system supporting both unclaimed credits and ERC-20 tokens.

#### Storage Design

```solidity
mapping(address holder => mapping(uint256 projectId => uint256)) public creditBalanceOf;
mapping(uint256 projectId => uint256) public totalCreditSupplyOf;
mapping(uint256 projectId => IJBToken) public tokenOf;
mapping(IJBToken token => uint256) public projectIdOf;
```

#### Minting Logic

**mintFor()** chooses based on ERC-20 existence:
```solidity
if (tokenOf[projectId] != address(0)) {
    token.mint(holder, count);  // Direct ERC-20 mint
} else {
    creditBalanceOf[holder][projectId] += count;  // Store as credits
    totalCreditSupplyOf[projectId] += count;
}
```

#### Burning Priority

**burnFrom()** burns credits first, then tokens:
```solidity
uint256 creditBalance = creditBalanceOf[holder][projectId];
uint256 tokensToBurn = creditBalance < count ? count - creditBalance : 0;
uint256 creditsToBurn = count - tokensToBurn;

// Burn credits
creditBalanceOf[holder][projectId] -= creditsToBurn;
totalCreditSupplyOf[projectId] -= creditsToBurn;

// Burn tokens
if (tokensToBurn > 0) token.burn(holder, tokensToBurn);
```

#### ERC-20 Deployment

**deployERC20For()** uses minimal proxy clones:
- Validates project doesn't already have token
- Deploys via `Clones.clone()` or `Clones.cloneDeterministic()`
- Links bidirectionally: `tokenOf[projectId]` and `projectIdOf[token]`

**setTokenFor()** validates external tokens:
- Token must use 18 decimals
- Token must return true from `canBeAddedTo(projectId)`
- Token must not be assigned to another project

---

### Custom ERC20 Token Integration

The JBTokens system supports custom ERC20 tokens, enabling advanced tokenomics while preserving Juicebox's payment and redemption mechanics.

#### How Custom Tokens Work

When `setTokenFor()` is called with a custom token:

```solidity
function setTokenFor(uint256 projectId, IJBToken token) external {
    // 1. Validate token is compatible
    if (token.decimals() != 18) revert JBTokens_TokensMustHave18Decimals();
    if (!token.canBeAddedTo(projectId)) revert JBTokens_TokenCannotBeAddedTo();
    if (projectIdOf[token] != 0) revert JBTokens_TokenAlreadyAssigned();

    // 2. Store bidirectional mapping
    tokenOf[projectId] = token;
    projectIdOf[token] = projectId;

    // 3. Existing credits remain claimable
    // totalCreditSupplyOf[projectId] stays unchanged
}
```

**Key Insight**: Setting a custom token doesn't migrate existing credits. Credit holders must call `claimTokensFor()` to convert credits to the ERC20.

#### Mint/Burn Flow with Custom Tokens

When payments are received:
```
pay() → mintTokensOf() → JBTokens.mintFor()
                              ↓
                         customToken.mint(holder, amount)
```

When cash outs occur:
```
cashOutTokensOf() → burnTokensOf() → JBTokens.burnFrom()
                                          ↓
                                     // Burns credits first, then tokens
                                     customToken.burn(holder, tokensToBurn)
```

**Critical**: The controller calls `mint()` and `burn()` directly on your token. Your token MUST grant these permissions to the controller address.

#### Custom Token Requirements

| Requirement | Reason |
|-------------|--------|
| **18 decimals** | All Juicebox math (weights, rates) assumes 18 decimals |
| **canBeAddedTo()** | Validates token agrees to serve this project |
| **mint(address, uint256)** | Controller must mint on payments |
| **burn(address, uint256)** | Controller must burn on cash outs |
| **Controller access** | Token must authorize JBController for mint/burn |

#### Common Custom Token Patterns

**1. Transfer Tax Token**
```solidity
function _update(address from, address to, uint256 amount) internal override {
    // Skip tax for controller operations (mints/burns)
    if (from == address(0) || to == address(0) || msg.sender == controller) {
        super._update(from, to, amount);
        return;
    }
    // Apply tax on transfers
    uint256 tax = (amount * TAX_RATE) / 10000;
    super._update(from, taxRecipient, tax);
    super._update(from, to, amount - tax);
}
```

**Tradeoff**: Tax revenue goes to `taxRecipient`, not the Juicebox treasury. Consider routing tax to the project via `addToBalanceOf()`.

**2. Rebasing Token**
```solidity
// Track shares instead of balances
mapping(address => uint256) private _shares;
uint256 public totalShares;
uint256 public rebaseIndex = 1e18; // Starts at 1:1

function balanceOf(address account) public view override returns (uint256) {
    return (_shares[account] * rebaseIndex) / 1e18;
}

function rebase(uint256 newIndex) external onlyOwner {
    rebaseIndex = newIndex;
    // All balances scale proportionally
}
```

**Tradeoff**: Cash out calculations use `totalSupply()`. Rebasing changes supply without minting, which affects redemption value.

**3. Governance Token (ERC20Votes)**
```solidity
import {ERC20Votes} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

contract GovernanceProjectToken is ERC20Votes {
    address public controller;

    function mint(address to, uint256 amount) external {
        require(msg.sender == controller, "Only controller");
        _mint(to, amount);
    }

    // Inherits delegation, checkpointing, getPastVotes()
}
```

**Benefit**: Token holders can vote on external governance proposals while maintaining Juicebox treasury mechanics.

**4. Editable Name/Symbol Token**
```solidity
contract EditableProjectToken is ERC20 {
    string private _tokenName;
    string private _tokenSymbol;

    function name() public view override returns (string memory) { return _tokenName; }
    function symbol() public view override returns (string memory) { return _tokenSymbol; }

    function setName(string calldata newName) external onlyProjectOwner {
        _tokenName = newName;
    }

    function setSymbol(string calldata newSymbol) external onlyProjectOwner {
        _tokenSymbol = newSymbol;
    }
}
```

**Benefit**: Rebrand without redeploying token or migrating liquidity. Project owner controls metadata.

**5. Vesting Token with Per-Address Schedules**
```solidity
contract VestingProjectToken is ERC20 {
    struct VestingSchedule {
        uint256 totalAmount;     // Total tokens in this schedule
        uint256 released;        // Already released/transferred
        uint40 start;            // Vesting start timestamp
        uint40 cliff;            // Cliff end timestamp
        uint40 duration;         // Total vesting duration
    }

    mapping(address => VestingSchedule) public vestingOf;

    function vestedAmountOf(address account) public view returns (uint256) {
        VestingSchedule memory schedule = vestingOf[account];
        if (schedule.totalAmount == 0) return balanceOf(account);
        if (block.timestamp < schedule.cliff) return 0;
        if (block.timestamp >= schedule.start + schedule.duration) {
            return schedule.totalAmount;
        }
        uint256 elapsed = block.timestamp - schedule.start;
        return (schedule.totalAmount * elapsed) / schedule.duration;
    }

    function _update(address from, address to, uint256 amount) internal override {
        // Skip vesting checks for mints, burns, controller ops
        if (from == address(0) || to == address(0) || msg.sender == controller) {
            super._update(from, to, amount);
            return;
        }

        VestingSchedule storage schedule = vestingOf[from];
        if (schedule.totalAmount == 0) {
            super._update(from, to, amount);
            return;
        }

        require(block.timestamp >= schedule.cliff, "Cliff not reached");
        uint256 transferable = vestedAmountOf(from) - schedule.released;
        require(amount <= transferable, "Insufficient vested balance");
        schedule.released += amount;
        super._update(from, to, amount);
    }

    function setVestingSchedule(
        address beneficiary,
        uint256 totalAmount,
        uint40 start,
        uint40 cliffDuration,
        uint40 vestingDuration
    ) external onlyProjectOwner {
        vestingOf[beneficiary] = VestingSchedule({
            totalAmount: totalAmount,
            released: 0,
            start: start,
            cliff: start + cliffDuration,
            duration: vestingDuration
        });
    }
}
```

**Key Difference from Treasury Vesting**:
- **Treasury vesting** (payout limits): Controls when funds leave the treasury
- **Token vesting**: Controls when individual holders can transfer tokens

**Use Case**: Team allocations, investor lock-ups, contributor rewards where tokens should vest per-person with individual cliffs and durations. Can be combined with treasury vesting for layered protection.

**Tradeoff**: Does not prevent cash outs (controller operations bypass vesting). If you need to prevent recipients from cashing out, combine with a ruleset that has `pauseCashOut: true` during the vesting period, or set a high `cashOutTaxRate`.

#### Edge Cases and Gotchas

1. **Token assigned twice**: A token can only serve one project. `setTokenFor()` reverts if token already assigned.

2. **Credit/token split during cash out**: Burns credits first, then tokens:
   ```solidity
   // If user has 100 credits and 50 tokens, burning 120:
   // - Burns all 100 credits
   // - Burns 20 tokens
   ```

3. **Transfer restrictions**: If your token blocks certain transfers, ensure controller operations (mint/burn) are always allowed.

4. **Pausable tokens**: Pausing transfers will break cash outs if tokens can't be burned.

5. **Fee-on-transfer tokens**: Not directly supported. The minted amount must equal the amount the controller requested.

6. **Approval requirements**: JBTokens calls `burn()` directly. If your token requires approval for burns, this will fail. Use `burnFrom` pattern that allows controller without approval.

#### Integration Checklist

Before using a custom token:

- [ ] Token uses exactly 18 decimals
- [ ] `canBeAddedTo(projectId)` returns true for your project
- [ ] Controller address has mint permission
- [ ] Controller address has burn permission (without approval)
- [ ] Token not assigned to another project
- [ ] Mint/burn don't have unexpected side effects (fees, rebasing)
- [ ] Transfer restrictions exempt controller operations
- [ ] Considered interaction with cash out tax rate
- [ ] Tested credit → token claiming works
- [ ] Verified `totalSupply()` reflects actual redeemable tokens

---

### JBFundAccessLimits

Packed storage for payout limits and surplus allowances.

#### Bit Packing

```solidity
// Bits 0-223: amount (up to ~2^224 wei)
// Bits 224-255: currency (32-bit identifier)
uint256 packed = uint256(amount) | (uint256(currency) << 224);
```

#### Currency Ordering Enforcement

**setFundAccessLimitsFor()** requires strictly increasing currency order:
```solidity
for (uint256 i = 1; i < payoutLimits.length; i++) {
    if (payoutLimits[i].currency <= payoutLimits[i-1].currency) {
        revert JBFundAccessLimits_InvalidPayoutLimitCurrencyOrdering();
    }
}
```

This prevents duplicates and enables O(n) iteration during lookups.

#### Zero Filtering

Zero-amount limits are filtered during storage, not stored:
```solidity
if (limit.amount > 0) {
    _packedPayoutLimitsDataOf[projectId][rulesetId][terminal][token].push(packed);
}
```

---

## Fund Access Limit Lifecycle

Understanding the lifecycle of payout limits vs surplus allowances is critical for project design. **This is a common source of confusion.**

### Payout Limits: Reset Each Cycle

Payout limits reset when a new cycle begins:

```
Cycle 1: Payout limit = 10 ETH
  → Team sends 10 ETH payouts
  → Remaining limit = 0

Cycle 2: Payout limit = 10 ETH (RESET!)
  → Team can send another 10 ETH
  → This continues every cycle
```

**Key Insight**: The payout limit is defined per-ruleset, and when a cycling ruleset starts a new cycle, the limit refreshes. This enables **recurring distributions** without queuing multiple rulesets.

### Surplus Allowance: One-Time Per Ruleset

Surplus allowance does NOT reset each cycle:

```
Cycle 1: Surplus allowance = 20 ETH
  → Team uses 15 ETH from surplus
  → Remaining allowance = 5 ETH

Cycle 2: Surplus allowance = 5 ETH (NOT reset!)
  → Still only 5 ETH available
  → Allowance only resets if NEW RULESET is queued
```

**Key Insight**: Surplus allowance is a one-time budget per ruleset configuration. It's designed for **discretionary treasury access**, not recurring distributions.

### How Remaining Limits Are Tracked

The terminal store tracks used amounts separately from configured limits:

```solidity
// JBTerminalStore
mapping(address terminal =>
    mapping(uint256 projectId =>
        mapping(address token =>
            mapping(uint256 rulesetCycleNumber => uint256)
        )
    )
) public usedPayoutLimitOf;

mapping(address terminal =>
    mapping(uint256 projectId =>
        mapping(address token =>
            mapping(uint256 rulesetId => uint256)
        )
    )
) public usedSurplusAllowanceOf;
```

Notice the key difference:
- **Payout limit**: Keyed by `rulesetCycleNumber` → resets each cycle
- **Surplus allowance**: Keyed by `rulesetId` → persists across cycles

### Surplus Calculation

Surplus (redeemable amount) is calculated as:
```
surplus = balance - remainingPayoutLimit
```

Where `remainingPayoutLimit` is the configured limit minus used amount for the current cycle.

**Implication**: Payout limits **protect funds from cash outs**. If you set a 10 ETH payout limit, that 10 ETH cannot be cashed out by token holders until it's distributed or the cycle ends.

### Design Pattern: Vesting via Native Mechanics

Combine both limit types for sophisticated treasury management:

| Mechanism | Behavior | Use Case |
|-----------|----------|----------|
| Payout Limit | Resets each cycle | Recurring vesting/salaries |
| Surplus Allowance | One-time per ruleset | Emergency fund / discretionary |

**Example: 12-Month Vesting with Treasury Reserve**

```solidity
// Single cycling ruleset (NOT 12 separate rulesets!)
JBRulesetConfig({
    duration: 30 days,  // Monthly cycles
    // ...
    fundAccessLimitGroups: [
        JBFundAccessLimitGroup({
            terminal: address(TERMINAL),
            token: JBConstants.NATIVE_TOKEN,
            payoutLimits: [
                JBCurrencyAmount({
                    amount: 6.67 ether,   // Monthly vesting (80 ETH / 12)
                    currency: nativeCurrency
                })
            ],
            surplusAllowances: [
                JBCurrencyAmount({
                    amount: 20 ether,     // One-time treasury access
                    currency: nativeCurrency
                })
            ]
        })
    ]
});
```

**Result over 12 months:**
- Month 1: Team can withdraw 6.67 ETH (payout) + up to 20 ETH (surplus allowance)
- Month 2-12: Team can withdraw 6.67 ETH/month (payout limit resets each cycle)
- Surplus allowance does NOT reset - once used, it's gone until new ruleset

### Common Mistakes

1. **Queueing 12 rulesets for 12-month vesting**
   - Wrong: Queue separate ruleset for each month
   - Right: One cycling ruleset with monthly payout limit

2. **Expecting surplus allowance to reset**
   - Wrong: Plan to use 10 ETH each month from surplus allowance
   - Right: Use payout limits for recurring distributions

3. **Not understanding surplus protection**
   - Payout limits protect funds from redemption
   - Funds within the payout limit are NOT part of surplus

---

### JBPrices

Hierarchical price feed system with inverse calculation support.

#### Price Resolution Order

**pricePerUnitOf()** follows this order:
```
1. Same currency? Return 10^decimals (1:1 ratio)
2. Direct feed exists? Use feed.currentUnitPrice()
3. Inverse feed exists? Calculate reciprocal
4. Project-specific not found? Try default (projectId=0)
5. Nothing found? Revert with PriceFeedNotFound
```

#### Inverse Calculation

```solidity
// If only priceFeedFor[project][B][A] exists, calculate A→B:
price = mulDiv(10**decimals, 10**decimals, inverseFeed.currentUnitPrice(decimals));
```

#### Feed Immutability

Price feeds are append-only:
- Cannot modify existing feeds
- Cannot remove feeds
- Validates both direct and inverse don't already exist before adding

**Access Control**:
- Default feeds (projectId=0): Owner only
- Project-specific feeds: Controller only

---

## Hook & Terminal Implementations

### JBSwapTerminal Deep Dive

Wraps Uniswap V3 swaps into a Juicebox terminal interface.

#### Payment Flow

```
pay()/addToBalanceOf()
  → _acceptFundsFor() // Transfer or Permit2
  → _handleTokenTransfersAndSwap()
    → _beforeTransferFor() // Wrap ETH if needed
    → _swap() // Execute Uniswap swap
  → Forward to primary terminal for output token
```

#### TWAP Integration

```solidity
function _getQuote(IUniswapV3Pool pool, uint256 amountIn) internal view returns (uint256) {
    uint32 secondsAgo = OracleLibrary.getOldestObservationSecondsAgo(address(pool));

    // Cap at configured window (2 min to 2 days)
    if (secondsAgo > twapWindow) secondsAgo = twapWindow;

    (int24 arithmeticMeanTick,) = OracleLibrary.consult(pool, secondsAgo);
    return OracleLibrary.getQuoteAtTick(arithmeticMeanTick, amountIn, tokenIn, tokenOut);
}
```

#### Pool Configuration

**addDefaultPool()** setup:
1. Validates pool deployed by stored factory
2. Increases observation cardinality to minimum 10
3. Stores accounting context (decimals, etc.)

#### Hierarchical Defaults

Project-specific configs override global defaults:
```solidity
pool = poolOf[projectId][tokenIn][tokenOut];
if (pool == address(0)) {
    pool = poolOf[DEFAULT_PROJECT_ID][tokenIn][tokenOut];
}
```

---

### JB721TiersHook Deep Dive

Tiered NFT system with integrated payment processing and cash out support. Uses JBOwnable for flexible ownership.

#### Architecture

The 721 hook implements three hook interfaces:
- **IJBRulesetDataHook**: `beforePayRecordedWith()`, `beforeCashOutRecordedWith()`
- **IJBPayHook**: `afterPayRecordedWith()`
- **IJBCashOutHook**: `afterCashOutRecordedWith()`

Plus extends **JBOwnable** for project-based or EOA ownership with permission delegation.

#### Tier Storage (JB721TiersHookStore)

```solidity
struct JB721Tier {
    uint104 price;              // Price in terminal token
    uint32 initialSupply;       // Starting supply
    uint32 remainingSupply;     // Current available
    uint16 votingUnits;         // Governance weight
    uint16 reserveFrequency;    // Reserved mint ratio (1 in N)
    uint24 category;            // Grouping identifier
    bool transfersPausable;     // Can transfers be paused
    bool cannotBeRemoved;       // Permanent tier flag
}
```

#### Payment Processing (`_processPayment`)

```
afterPayRecordedWith()
  → _processPayment()
    → Normalize payment to tier pricing currency via JBPrices
    → Add existing payCreditsOf[beneficiary] if payer == beneficiary
    → Decode metadata for tier IDs to mint
    → If no tiers specified: auto-select best fit tiers
    → Call STORE.recordMint() for each tier
      → Validates tier active and has supply
      → Handles reserved mints (1 per reserveFrequency)
    → Mint NFTs via _mint()
    → Handle leftover:
      → If allowOverspending: add to payCreditsOf
      → Else: revert if leftover exists
```

#### Auto-Tier Selection

When payer doesn't specify tiers, the hook selects automatically:
```solidity
function _selectAutoTiers(uint256 amount) internal view returns (uint256[] tiers) {
    // Iterate tiers by price descending
    // Select highest-priced tier that fits remaining amount
    // Repeat until amount exhausted or no tier fits
}
```

**Tradeoff**: Auto-selection may not match user intent; explicit tier selection preferred for UX.

#### Credit System Implementation

```solidity
mapping(address payer => uint256) public payCreditsOf;

// On payment:
if (payer == beneficiary) {
    effectiveAmount = payment.amount + payCreditsOf[payer];
    payCreditsOf[payer] = 0;  // Use all credits
}

// After minting:
if (leftover > 0 && allowOverspending) {
    payCreditsOf[beneficiary] += leftover;
    emit AddPayCredits(beneficiary, leftover, ...);
}
```

**Edge Cases**:
- Credits lost if hook is replaced
- Credits cannot be withdrawn, only spent on NFTs
- Accumulated dust from rounding

#### Cash Out Weight Calculation

Each NFT's value equals its tier price:
```solidity
function cashOutWeightOf(uint256[] tokenIds) public view returns (uint256 weight) {
    for (uint256 i; i < tokenIds.length; i++) {
        JB721Tier tier = STORE.tierOfTokenId(tokenIds[i]);
        weight += tier.price;
    }
}
```

Total outstanding value:
```solidity
function totalCashOutWeight() public view returns (uint256) {
    return STORE.totalCashOutWeight(address(this));
}
```

**Cash Out Proportion**:
```
userShare = (userNFTWeight / totalCashOutWeight) × surplus × (1 - taxRate)
```

#### Reserved Minting

Tiers can reserve NFTs for the project:
```solidity
// If reserveFrequency = 10, every 10th mint goes to reserved beneficiary
if (mintCount % tier.reserveFrequency == 0) {
    _mint(reservedBeneficiary, tokenId);
} else {
    _mint(payer, tokenId);
}
```

Reserved NFTs are minted inline during payment, not accumulated.

#### Ownership via JBOwnable

The hook extends JBOwnable for flexible access control:
```solidity
// Project-based ownership (common pattern):
constructor(..., uint256 projectId, ...) {
    _transferOwnership(projectId);  // Owner = project NFT holder
}

// Permission delegation:
// Owner can grant ADJUST_721_TIERS to operators via JBPermissions
// Operators can then call adjustTiers() without being owner
```

**Permission IDs used**:
- `ADJUST_721_TIERS` (17): Add/remove tiers
- `SET_721_METADATA` (18): Update tier metadata
- `MINT_721` (19): Manual minting
- `SET_721_DISCOUNT_PERCENT` (27): Adjust pricing

#### Tier Adjustment

```solidity
function adjustTiers(JB721TierConfig[] tiersToAdd, uint256[] tierIdsToRemove) external {
    // Requires ADJUST_721_TIERS permission or owner

    // Remove tiers (if not cannotBeRemoved)
    for (uint256 id : tierIdsToRemove) {
        require(!tier.cannotBeRemoved, "TIER_LOCKED");
        STORE.recordRemoveTierOf(id);
    }

    // Add new tiers
    for (JB721TierConfig config : tiersToAdd) {
        STORE.recordAddTier(config);
    }
}
```

#### Metadata Encoding

Payer metadata structure for specifying tiers:
```solidity
bytes4 constant METADATA_ID = bytes4(keccak256("JB721TiersHook"));

// Encoded as: [METADATA_ID][allowOverspending (bool)][tierIds (uint16[])]
bytes memory metadata = abi.encode(
    true,                    // allowOverspending
    [uint16(1), uint16(3)]   // Mint tier 1 and tier 3
);
```

---

## Extending 721-Hook: Dynamic Cash Out Weights

When building prediction games or outcome-based systems, you need to extend the 721-hook to change treasury mechanics. This section covers the key implementation patterns from Defifa.

### Why Extend vs. Use Resolver Only

| Need | Resolver | Extended Hook |
|------|----------|---------------|
| Custom artwork/metadata | ✅ | ✅ |
| Dynamic cash out weights | ❌ | ✅ |
| First-owner tracking | ❌ | ✅ |
| Phase-based restrictions | ❌ | ✅ |
| Governor integration | ❌ | ✅ |

**Rule of thumb**: If you need to change how money flows, extend the hook. If you only need to change how tokens look, use a resolver.

### Dynamic Cash Out Weight Implementation

Standard 721-hook uses fixed weights based on tier price:
```solidity
// Standard: weight = tier.price
function cashOutWeightOf(uint256[] tokenIds) returns (uint256 weight) {
    for (uint256 i; i < tokenIds.length; i++) {
        weight += STORE.tierOfTokenId(tokenIds[i]).price;
    }
}
```

For dynamic weights (e.g., prediction games), override with configurable weights:
```solidity
// Extended: weight = configurable per tier
uint256 constant TOTAL_CASH_OUT_WEIGHT = 1e18; // 100% distributed among tiers

mapping(uint256 tierId => uint256) public tierCashOutWeight;

function cashOutWeightOf(uint256[] tokenIds) returns (uint256 weight) {
    for (uint256 i; i < tokenIds.length; i++) {
        uint256 tierId = STORE.tierIdOfToken(tokenIds[i]);
        weight += tierCashOutWeight[tierId];
    }
}

// Called by governor after outcome is known
function setTierCashOutWeightsTo(DefifaTierCashOutWeight[] calldata weights) external {
    // Verify caller is authorized (governor)
    // Verify total weights sum to TOTAL_CASH_OUT_WEIGHT
    for (uint256 i; i < weights.length; i++) {
        tierCashOutWeight[weights[i].id] = weights[i].cashOutWeight;
    }
}
```

### First-Owner Tracking

For games where rewards should go to original minters (not secondary buyers):

```solidity
// Track original minter
mapping(uint256 tokenId => address) public firstOwnerOf;

// In _processPayment() after minting:
function _processPayment(JBAfterPayRecordedContext calldata context) internal override {
    // ... mint logic ...

    // Record first owner
    for (uint256 i; i < mintedTokenIds.length; i++) {
        firstOwnerOf[mintedTokenIds[i]] = context.beneficiary;
    }
}

// In cash out, rewards go to first owner:
function afterCashOutRecordedWith(JBAfterCashOutRecordedContext calldata context) external {
    // Verify current owner initiated cash out
    // But send rewards to firstOwnerOf[tokenId]
    address rewardRecipient = firstOwnerOf[tokenId];

    // Transfer rewards to original minter
    _transferRewards(rewardRecipient, amount);
}
```

**Trade-off**: First-owner tracking adds storage costs but ensures fair game mechanics where secondary market purchases don't steal rewards from original participants.

### Phase-Based Cash Out Logic

Different phases have different cash out rules:

```solidity
enum GamePhase { COUNTDOWN, MINT, REFUND, SCORING, COMPLETE, NO_CONTEST }

function beforeCashOutRecordedWith(JBBeforeCashOutRecordedContext calldata context)
    external view override
    returns (uint256 cashOutTaxRate, uint256 cashOutCount, uint256 totalSupply, JBCashOutHookSpecification[] memory)
{
    GamePhase phase = currentPhase();

    if (phase == GamePhase.REFUND) {
        // During refund: return mint cost (full refund)
        return _refundCashOut(context);
    }

    if (phase == GamePhase.COMPLETE) {
        // After scoring: return weighted share of pot
        return _scoredCashOut(context);
    }

    // Other phases: no cash out allowed
    revert CashOutNotAllowed();
}
```

### Governor Integration Pattern

The governor contract calls into the delegate to set weights:

```solidity
// In Governor contract:
function ratifyScorecard(DefifaScorecard calldata scorecard) external {
    // Verify quorum reached
    require(attestationCount[scorecard.id] >= quorum(), "Quorum not reached");

    // Set weights on delegate
    IDefifaDelegate(delegate).setTierCashOutWeightsTo(scorecard.weights);

    // Emit event
    emit ScorecardRatified(scorecard.id);
}

// In Delegate contract:
function setTierCashOutWeightsTo(DefifaTierCashOutWeight[] calldata weights) external {
    // Only governor can set weights
    require(msg.sender == governor, "Only governor");

    // Only during SCORING phase
    require(currentPhase() == GamePhase.SCORING, "Wrong phase");

    // Verify weights sum to 100%
    uint256 total;
    for (uint256 i; i < weights.length; i++) {
        tierCashOutWeight[weights[i].id] = weights[i].cashOutWeight;
        total += weights[i].cashOutWeight;
    }
    require(total == TOTAL_CASH_OUT_WEIGHT, "Invalid total");

    // Transition to COMPLETE phase
    _setPhase(GamePhase.COMPLETE);
}
```

### Voting Power Calculation

NFT holders vote with power proportional to their holdings:

```solidity
// Voting power = (tokens owned in tier / total minted in tier) * MAX_POWER_PER_TIER
function getAttestationPowerOf(address account, uint256[] calldata tierIds)
    public view returns (uint256 power)
{
    for (uint256 i; i < tierIds.length; i++) {
        uint256 tierId = tierIds[i];
        uint256 owned = balanceOfTier(account, tierId);
        uint256 totalMinted = STORE.tier(tierId).initialSupply - STORE.tier(tierId).remainingSupply;

        if (totalMinted > 0) {
            power += (owned * MAX_ATTESTATION_POWER_TIER) / totalMinted;
        }
    }
}
```

### Reference Implementation

See [defifa-collection-deployer-v5](https://github.com/BallKidz/defifa-collection-deployer-v5) for complete implementation including:
- `DefifaDelegate.sol` - Extended 721-hook with all patterns above
- `DefifaGovernor.sol` - On-chain voting with tier-weighted power
- `DefifaDeployer.sol` - Factory for deploying games

---

## Contract-as-Owner Pattern

### REVDeployer Architecture

REVDeployer owns Juicebox projects (revnets), enabling autonomous governance.

#### Deployment Flow

```
deployFor()
  → Calculate next projectId via PROJECTS.count() + 1
  → CONTROLLER.launchProjectFor()
    → Creates project, transfers NFT to REVDeployer
  → _deployRevnetFor()
    → Deploy ERC-20 token
    → Configure buyback hook with pools
    → Set up split operator permissions
    → Deploy suckers for cross-chain
```

#### Permission Delegation Model

REVDeployer grants permissions to designated operators:
```solidity
function _setSplitOperatorOf(uint256 revnetId, address operator) internal {
    uint256[] memory permissions = _splitOperatorPermissionIndexesOf(revnetId);

    _setPermissionsFor(
        operator,
        revnetId,
        permissions
    );
}
```

**Default Split Operator Permissions** (6 total):
1. SET_SPLIT_GROUPS
2. SET_BUYBACK_POOL
3. SET_BUYBACK_TWAP
4. SET_PROJECT_URI
5. DEPLOY_SUCKERS
6. SET_CONTROLLER (for suckers)

Plus any custom permissions in `_extraOperatorPermissions[revnetId]`.

#### Stage Mechanics

Stages define temporal revenue phases:
```solidity
struct REVStageConfig {
    uint40 startsAtOrAfter;      // Stage start time
    uint16 splitPercent;          // Operator split %
    uint16 initialIssuance;       // Starting weight
    uint40 issuanceCutFrequency; // How often weight cuts
    uint16 issuanceCutPercent;    // Weight cut amount
    uint16 cashOutTaxRate;        // Cash out penalty
}
```

**Validation Rules**:
- Stages must have increasing start times
- Split percent requires non-empty splits
- Cash out tax rate must allow some cash outs (< 100%)

#### Auto-Issuance

Pre-mint tokens to beneficiaries after stage starts:
```solidity
function autoIssueFor(uint256 revnetId, uint256 stageId, address beneficiary) external {
    uint256 amount = amountToAutoIssue[revnetId][stageId][beneficiary];
    amountToAutoIssue[revnetId][stageId][beneficiary] = 0;

    CONTROLLER.mintTokensOf(revnetId, amount, beneficiary, "", true);
}
```

---

### REVLoans: Token-Backed Lending

#### Collateralization Model

Borrowers provide revnet tokens as collateral:
```
borrowable = cashOutValue(collateral) - existingDebt
```

Where `cashOutValue` considers surplus, tax rate, and total supply.

#### Three-Tier Fee Structure

```solidity
uint256 constant MIN_PREPAID_FEE_PERCENT = 25;   // 2.5% minimum
uint256 constant MAX_PREPAID_FEE_PERCENT = 500;  // 50% maximum
uint256 constant REV_PREPAID_FEE_PERCENT = 10;   // 1% to REV
```

Higher prepaid fees = longer interest-free periods:
```solidity
prepaidDuration = (prepaidFeePercent / MAX_PREPAID_FEE_PERCENT) × LOAN_LIQUIDATION_DURATION
```

#### Interest After Prepaid Period

Linear interpolation from 0% to 100% over remaining loan duration:
```solidity
timeSincePrepaid = block.timestamp - (loan.createdAt + prepaidDuration);
remainingDuration = LOAN_LIQUIDATION_DURATION - prepaidDuration;

feePercent = (timeSincePrepaid × 100%) / remainingDuration;
```

#### Liquidation

After 10 years (3,650 days):
- Anyone can call `liquidateExpiredLoansFrom()`
- ERC-721 loan token burned
- Collateral remains burned (not returned)
- Borrowed amount tracking decremented

---

## JBOwnable: Flexible Ownership

Shared utility for Juicebox-aware ownership. Used by JB721TiersHook, custom hooks, and any contract needing project-based access control.

#### Dual Ownership Modes

**Project-Based**:
```solidity
function owner() public view returns (address) {
    if (jbOwner.projectId != 0) {
        return PROJECTS.ownerOf(jbOwner.projectId);
    }
    return jbOwner.owner;
}
```

**EOA-Based**: Direct address stored in `jbOwner.owner`.

#### Permission Integration

Project-based ownership enables delegation:
```solidity
// Owner can grant permissions via JBPermissions
PERMISSIONS.setPermissionsFor(
    operator,
    jbOwner.projectId,
    [jbOwner.permissionId]
);

// Operator can now call onlyOwner functions
```

---

## Croptop Publisher

### CTPublisher: Permissioned NFT Publishing

#### Posting Flow

```
mintFrom(posts[])
  → For each post:
    → Validate against allowance (min/max price, supply)
    → Check caller in allowlist
    → Create or reuse tier via hook.adjustTiers()
    → Accumulate total price
  → Pay primary project (value - fee)
  → Pay fee project (5% via FEE_DIVISOR = 20)
```

#### Tier Deduplication

IPFS URIs map to tier IDs:
```solidity
if (tierIdOfEncodedIPFSUri[encodedUri] != 0) {
    // Mint from existing tier
} else {
    // Create new tier, store mapping
    tierIdOfEncodedIPFSUri[encodedUri] = newTierId;
}
```

#### Allowance Configuration

Packed configuration per project:
```
Bits 0-103:   minPrice
Bits 104-135: minTotalSupply
Bits 136-167: maxTotalSupply
+ Address[] allowlist
```

---

## Cross-Chain: Suckers

### JBSucker Architecture

Bidirectional cross-chain bridge using merkle trees.

#### Dual Merkle Tree System

**Outbox** (local → remote):
- Stores claims from `prepare()` calls
- Root sent via `toRemote()`
- Cleared after successful bridge

**Inbox** (remote → local):
- Receives roots via `fromRemote()`
- Claims validated against stored root
- BitMap prevents replay

#### Prepare & Bridge Flow

**Phase 1: prepare()**
```solidity
function prepare(uint256 projectTokenCount, address beneficiary, ...) external {
    // 1. Transfer tokens to sucker
    TOKENS.transferCreditsFrom(msg.sender, address(this), projectId, projectTokenCount);

    // 2. Cash out for backing assets
    terminal.cashOutTokensOf(projectId, projectTokenCount, ...);

    // 3. Insert into outbox tree
    _insertIntoTree(
        keccak256(abi.encode(projectTokenCount, terminalTokenAmount, beneficiary)),
        OUTBOX
    );
}
```

**Phase 2: toRemote()**
```solidity
function toRemote(JBRemoteToken[] remoteTokens) external {
    for each token:
        // Validate mapping and minimum amount
        // Send root + balance to remote peer
        _sendRootOverAMB(peer, root, balance, minGas);

        // Clear outbox
        outboxOf[token].balance = 0;
        outboxOf[token].nonce++;
}
```

#### Claiming on Destination

```solidity
function claim(JBClaim[] claims) external {
    for each claim:
        // 1. Validate merkle proof against inbox root
        _validate(leaf, proof, INBOX);

        // 2. Mark leaf as executed (prevent replay)
        _executedOf[token][leafIndex] = true;

        // 3. Mint project tokens
        CONTROLLER.mintTokensOf(projectId, tokenCount, beneficiary, ...);

        // 4. Optionally add backing to balance
        if (addToBalanceMode == ON_CLAIM) {
            terminal.addToBalanceOf(projectId, terminalAmount, ...);
        }
}
```

#### Emergency Exit

When bridge fails, users can reclaim from outbox:
```solidity
function emergencyExit(JBClaim[] claims, address token) external {
    // Must be enabled for this token
    require(emergencyHatchEnabledFor[token]);

    // Validate against OUTBOX tree (not inbox)
    _validateForEmergencyExit(leaf, proof);

    // Return terminal tokens directly
    terminal.pay(projectId, terminalAmount, beneficiary, ...);
}
```

**Critical**: Once emergency hatch is enabled, it cannot be disabled.

#### Deprecation Flow

Three-stage sunset:
1. **DEPRECATION_PENDING**: Warning state
2. **SENDING_DISABLED**: Accept incoming, prevent new sends
3. **DEPRECATED**: Reject all operations

Minimum delay enforced between stages for message propagation.

#### Token Mapping Constraints

```solidity
function mapToken(JBTokenMapping mapping) external {
    // Cannot remap if outbox has entries
    if (outboxOf[token].tree.count > 0) revert;

    // Native tokens can only map to native or zero
    if (token == JBConstants.NATIVE_TOKEN) {
        require(remoteToken == NATIVE_TOKEN || remoteToken == address(0));
    }
}
```

---

## Extended Integration Patterns

### When to Use Contract-as-Owner

**Use REVDeployer/Contract Owner When**:
- Project should operate autonomously without EOA control
- Structured access needed (split operators, loan contracts)
- Cross-chain deployment requires coordinated setup
- Token economics should be immutable after launch

**Use EOA Owner When**:
- Rapid iteration expected
- Full control required for governance
- Simple single-owner model sufficient

### Cross-Chain Deployment Checklist

1. Deploy suckers on each chain via REVDeployer
2. Map tokens with appropriate minimums and gas limits
3. Set up terminals on each chain
4. Verify peer addresses are correct
5. Test with small amounts before production

### Loan Integration Considerations

1. Collateral value depends on current surplus and supply
2. Higher prepaid fees reduce ongoing interest burden
3. Liquidation deadline is absolute (10 years)
4. Collateral is burned, not locked (can't be recovered)

### Croptop Integration

1. Configure allowances before enabling publishing
2. Set appropriate min/max prices for tier creation
3. Monitor tier creation for duplicate IPFS URIs
4. Fee extraction is automatic (5% to fee project)
