---
name: jb-omnichain-payout-limits
description: |
  Omnichain projects have per-chain payout limits, not aggregate limits. This is a fundamental
  constraint with no perfect solution. Use when: (1) user wants a fixed total fundraising cap
  across chains, (2) asking about aggregate payout limits on omnichain projects, (3) designing
  omnichain projects with payout constraints, (4) exploring oracle or monitoring solutions for
  cross-chain state. Covers the limitation, why it exists, and practical approaches with tradeoffs.
---

# Omnichain Payout Limit Constraints

> **Note**: This applies to projects using payout limits (standard Juicebox projects with treasury distributions). Revnets don't use payout limits - they use unlimited surplus allowances for loans via REVLoans, so this limitation doesn't affect them.

## The Problem

**Payout limits in Juicebox V5 are per-chain, not aggregate.**

When you deploy an omnichain project (linked via Suckers), each chain has its own independent payout limit. Setting a 10 ETH payout limit on a 5-chain project means you could potentially pay out 50 ETH total (10 ETH × 5 chains), not 10 ETH total.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Omnichain Project with 10 ETH "Payout Limit"                       │
│                                                                     │
│  Chain 1 (Ethereum):  Limit = 10 ETH  →  Can pay out 10 ETH        │
│  Chain 2 (Optimism):  Limit = 10 ETH  →  Can pay out 10 ETH        │
│  Chain 3 (Base):      Limit = 10 ETH  →  Can pay out 10 ETH        │
│  Chain 4 (Arbitrum):  Limit = 10 ETH  →  Can pay out 10 ETH        │
│                                          ─────────────────         │
│                                          TOTAL: 40 ETH possible    │
│                                                                     │
│  User expectation: 10 ETH max                                       │
│  Reality: 40 ETH max                                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Why This Is Fundamentally Hard

Cross-chain state is **asynchronous**. There is no atomic way to know the aggregate raised/paid across all chains in real-time.

Any solution that coordinates cross-chain state introduces:
- **Latency**: Not real-time (seconds to minutes of delay)
- **Trust assumptions**: Who runs the oracle? Who can manipulate it?
- **Manipulation windows**: Attackers can exploit sync delays
- **Gas costs**: Cross-chain messaging is expensive
- **Complexity**: More moving parts = more failure modes

This is not a bug in Juicebox - it's a fundamental property of multi-chain systems.

## Approaches

### Approach 1: Accept & Design Around It

**Best for**: Projects where approximate limits are acceptable

Set per-chain limits that sum to your target, accepting that distribution may not match expectations.

```solidity
// Goal: ~100 ETH total across 5 chains
// Strategy: 20 ETH limit per chain

// Each chain's ruleset config:
fundAccessLimitGroups: [{
    terminal: MULTI_TERMINAL,
    token: NATIVE_TOKEN,
    payoutLimits: [{
        amount: 20 ether,  // Per-chain limit
        currency: 1        // ETH
    }],
    surplusAllowances: []
}]
```

**Tradeoffs**:
- One chain might hit its limit while others have slack
- Total raised could be less than desired if distribution is uneven
- No coordination required - simplest approach

**When to use**:
- Soft caps (nice-to-have limits, not hard requirements)
- Projects where ~80-120% of target is acceptable
- Early-stage projects testing omnichain

---

### Approach 2: Monitoring + Manual Pause

**Best for**: Projects with active operators who can respond quickly

Use Bendystraw to monitor aggregate raises, manually pause payments when approaching threshold.

```typescript
const BENDYSTRAW_API = 'https://bendystraw.xyz/{API_KEY}/graphql';

// Query aggregate balance across all chains
async function getAggregateBalance(suckerGroupId: string) {
  const query = `
    query($id: String!) {
      suckerGroup(id: $id) {
        balance
        volume
        projects_rel {
          chainId
          balance
        }
      }
    }
  `;

  const data = await fetch(BENDYSTRAW_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables: { id: suckerGroupId } })
  }).then(r => r.json());

  return data.data.suckerGroup;
}

// Monitoring loop
async function monitorAndAlert(suckerGroupId: string, threshold: bigint) {
  const group = await getAggregateBalance(suckerGroupId);
  const balance = BigInt(group.balance);

  if (balance >= threshold * 90n / 100n) {
    // 90% of threshold - send alert
    console.log('ALERT: Approaching threshold, consider pausing');
  }

  if (balance >= threshold) {
    // At threshold - operator should pause
    console.log('THRESHOLD REACHED: Pause payments now');
    // Could trigger notification (email, Telegram, Discord webhook)
  }
}
```

**Manual pause action**:
```typescript
// Project owner calls on each chain
await controller.queueRulesetsOf(projectId, [{
  // ... existing config
  metadata: {
    // ... existing metadata
    pausePay: true  // Disable new payments
  }
}]);
```

**Tradeoffs**:
- Requires active monitoring (someone watching)
- Reaction time matters - payments during delay
- Human error risk (forget to pause, pause wrong chain)
- Not suitable for trustless/autonomous projects

**When to use**:
- Projects with dedicated operators
- Lower stakes where brief overruns are acceptable
- Transitional approach while building automation

---

### Approach 3: Automated Cron + Relayr

**Best for**: Projects wanting automation without full oracle complexity

A cron job monitors aggregate balance via Bendystraw, uses Relayr to pause payments across all chains when threshold approaches.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Automated Threshold Monitor                                        │
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │   Cron Job   │────►│  Bendystraw  │────►│  Check       │        │
│  │  (every 5m)  │     │    Query     │     │  Threshold   │        │
│  └──────────────┘     └──────────────┘     └──────┬───────┘        │
│                                                   │                 │
│                                    threshold met? │                 │
│                                                   ▼                 │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Relayr Bundle: Pause payments on all chains             │      │
│  │                                                          │      │
│  │  Chain 1: queueRulesetsOf(projectId, {pausePay: true})  │      │
│  │  Chain 2: queueRulesetsOf(projectId, {pausePay: true})  │      │
│  │  Chain 3: queueRulesetsOf(projectId, {pausePay: true})  │      │
│  │  Chain 4: queueRulesetsOf(projectId, {pausePay: true})  │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

**Implementation requirements**:
1. **Operator address**: Needs `QUEUE_RULESETS` permission on each chain's project
2. **Cron infrastructure**: Reliable job runner (AWS Lambda, Cloudflare Workers, dedicated server)
3. **Bendystraw API key**: For querying aggregate state
4. **Relayr integration**: For multi-chain transaction bundling

```typescript
// Simplified cron handler
async function checkAndPauseIfNeeded(config: {
  suckerGroupId: string;
  threshold: bigint;
  projectIds: { chainId: number; projectId: number }[];
  operatorKey: string;
}) {
  // 1. Check aggregate balance
  const group = await getAggregateBalance(config.suckerGroupId);
  const balance = BigInt(group.balance);

  if (balance < config.threshold) {
    return; // Under threshold, do nothing
  }

  // 2. Build pause transactions for each chain
  const pauseTxs = config.projectIds.map(({ chainId, projectId }) => ({
    chain: chainId,
    target: CONTROLLER_ADDRESSES[chainId],
    data: encodeFunctionData({
      abi: JB_CONTROLLER_ABI,
      functionName: 'queueRulesetsOf',
      args: [projectId, /* rulesetConfigs with pausePay: true */]
    }),
    value: '0'
  }));

  // 3. Submit via Relayr
  const bundle = await relayr.createBundle(pauseTxs);
  await relayr.payForBundle(bundle, config.operatorKey);

  console.log(`Paused payments across ${config.projectIds.length} chains`);
}
```

**Tradeoffs**:
- **Latency**: 5-minute cron + Relayr execution time = potential overshoot
- **Trust**: Operator key holder can act unilaterally
- **Infrastructure**: Requires running and maintaining a service
- **Cost**: Relayr fees + gas on all chains
- **Reliability**: Cron failures = missed threshold

**When to use**:
- Projects with some trust in a designated operator
- Soft caps where ~5-10% overshoot is acceptable
- Projects without resources for full oracle implementation

---

### Approach 4: Oracle in Pay Hook

**Best for**: Projects requiring hard limits with strong guarantees

A pay hook checks an oracle for aggregate state before allowing payments. The oracle is updated by a relayer watching all chains.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Oracle-Based Aggregate Limit                                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Oracle Contract (deployed on each chain)                    │   │
│  │  ├── aggregateBalance: uint256 (updated by relayer)         │   │
│  │  ├── threshold: uint256                                      │   │
│  │  └── lastUpdate: uint256 (timestamp)                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ▲                                         │
│                           │ update                                  │
│  ┌────────────────────────┴────────────────────────────────────┐   │
│  │  Relayer Service                                             │   │
│  │  ├── Watches PayEvents on all chains                        │   │
│  │  ├── Calculates aggregate balance                           │   │
│  │  └── Updates oracle on all chains                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Pay Flow:                                                          │
│  User → pay() → PayHook.beforePayRecordedWith() → Oracle.check()   │
│                                                                     │
│  If oracle.aggregateBalance + payAmount > threshold:                │
│     REVERT "Aggregate limit exceeded"                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Implementation sketch**:

```solidity
// Oracle contract
contract AggregateBalanceOracle {
    uint256 public aggregateBalance;
    uint256 public threshold;
    uint256 public lastUpdate;
    address public relayer;

    function updateBalance(uint256 newBalance) external {
        require(msg.sender == relayer, "UNAUTHORIZED");
        aggregateBalance = newBalance;
        lastUpdate = block.timestamp;
    }

    function wouldExceedThreshold(uint256 additionalAmount) external view returns (bool) {
        return aggregateBalance + additionalAmount > threshold;
    }
}

// Pay hook that checks oracle
contract AggregateLimitPayHook is IJBPayHook {
    AggregateBalanceOracle public oracle;
    uint256 public maxStaleness = 5 minutes;

    function beforePayRecordedWith(JBBeforePayRecordedContext calldata context)
        external view override returns (uint256, uint256, uint256, JBPayHookSpecification[] memory)
    {
        // Check oracle freshness
        require(
            block.timestamp - oracle.lastUpdate() <= maxStaleness,
            "Oracle stale"
        );

        // Check aggregate limit
        require(
            !oracle.wouldExceedThreshold(context.amount.value),
            "Aggregate limit exceeded"
        );

        // Allow payment
        return (context.weight, context.newlyIssuedTokenCount, context.totalSupply, new JBPayHookSpecification[](0));
    }
}
```

**Tradeoffs**:
- **Complexity**: Multiple contracts + relayer service
- **Latency**: Oracle updates lag behind reality
- **Staleness window**: Payments during oracle delay can exceed limit
- **Relayer trust**: Single point of failure/manipulation
- **Cost**: Continuous relayer operation + oracle update gas
- **UX**: Payments can fail if oracle is stale or near threshold

**When to use**:
- Hard regulatory/compliance limits that must be enforced
- High-stakes projects where overshoot is unacceptable
- Projects with resources to build and maintain infrastructure

**Current status**: No off-the-shelf implementation exists. Would need custom development.

---

### Approach 5: Single-Chain Treasury

**Best for**: Projects that can centralize treasury operations

Accept payments on all chains, but bridge all funds to a single "home" chain for treasury operations. Payout limit on home chain is the only one that matters.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Single-Chain Treasury Pattern                                      │
│                                                                     │
│  Chain 1 (Home): Treasury lives here                               │
│  ├── Payout limit: 100 ETH (THIS IS THE REAL LIMIT)               │
│  ├── Accepts payments                                               │
│  └── All payouts happen here                                       │
│                                                                     │
│  Chain 2-4: Payment collection only                                │
│  ├── Payout limit: 0 (no direct payouts)                           │
│  ├── Accept payments                                                │
│  └── Funds bridged to Chain 1 via Suckers                          │
│                                                                     │
│  Flow:                                                              │
│  User pays on Chain 2 → Tokens issued on Chain 2                   │
│                       → User bridges funds to Chain 1 (manual)     │
│                       → Chain 1 treasury grows                     │
│                       → Payouts from Chain 1 only                  │
└─────────────────────────────────────────────────────────────────────┘
```

**The blocker**: Suckers require explicit user action to bridge. The project cannot automatically sweep funds from other chains to the home chain. Users must:
1. Call `prepare()` on the source chain
2. Wait for bridging
3. Call `claim()` on the destination chain

**Potential workarounds**:
- Incentivize users to bridge (bonus tokens, lower fees on home chain)
- Build a "sweeper" bot that bridges on behalf of users (requires trust + gas)
- Accept that some funds remain distributed

**Tradeoffs**:
- **User friction**: Extra steps to bridge funds
- **Fragmentation**: Funds spread across chains until bridged
- **Complexity**: Users must understand the pattern
- **Cannot enforce**: Can't force users to bridge

**When to use**:
- Projects where most activity naturally happens on one chain
- Projects willing to accept some treasury fragmentation
- Transitional approach for projects moving toward single-chain

---

## Comparison Matrix

| Approach | Enforcement | Latency | Trust Required | Complexity | Best For |
|----------|-------------|---------|----------------|------------|----------|
| Accept & Design | Soft | N/A | None | Low | Soft caps |
| Manual Monitoring | Soft | Minutes | Operator | Low | Active teams |
| Cron + Relayr | Soft | ~5-10 min | Operator | Medium | Automation |
| Oracle Pay Hook | Hard* | Seconds | Relayer | High | Compliance |
| Single-Chain | Medium | N/A | None | Medium | Centralized ops |

*Oracle enforcement has latency window during updates

---

## Recommendations by Use Case

### "We need a hard cap for regulatory compliance"
**Answer**: This is very difficult in omnichain. Consider:
1. Single-chain only (no omnichain)
2. Oracle pay hook (complex, custom development)
3. Accept that enforcement is approximate

### "We want a fundraising goal but it's not legally binding"
**Answer**: Use Approach 1 (Accept & Design) or Approach 2 (Manual Monitoring)
- Set per-chain limits that sum to ~80% of your goal
- Monitor via Bendystraw
- Pause manually when approaching target

### "We have an operator who can manage this"
**Answer**: Use Approach 3 (Cron + Relayr)
- Automate the monitoring and pausing
- Accept 5-10% potential overshoot
- Ensure operator key security

### "We're building a revnet"
**Answer**: This limitation doesn't apply to revnets
- Revnets don't use payout limits - they use surplus allowances for loans (via REVLoans)
- Surplus allowances are unlimited by design (for loan collateral access)
- If you need aggregate fundraising caps on a revnet, see the oracle or monitoring approaches above

---

## Future Considerations

### Could Juicebox natively support aggregate limits?

Theoretically, but it would require:
1. **Cross-chain messaging protocol**: Native integration with bridges
2. **Consensus on aggregate state**: Which chain is source of truth?
3. **Latency acceptance**: Users accept payments may fail during sync
4. **Cost distribution**: Who pays for cross-chain messages?

This is a significant protocol-level change, not a simple feature add.

### Could a shared oracle service exist?

Yes - a community-run oracle service could:
- Watch all Juicebox projects across chains
- Provide aggregate state queries
- Update on-chain oracles

This could be built as infrastructure, but requires:
- Ongoing operational funding
- Trust in the service operator
- Integration with pay hooks

---

## Related Skills

- `/jb-omnichain-ui` - Building omnichain frontends
- `/jb-suckers` - Cross-chain token bridging mechanics
- `/jb-bendystraw` - Querying aggregate project data
- `/jb-relayr` - Multi-chain transaction bundling
- `/jb-fund-access-limits` - Per-chain payout limit configuration
