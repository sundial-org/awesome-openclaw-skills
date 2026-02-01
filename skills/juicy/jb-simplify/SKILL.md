---
name: jb-simplify
description: Checklist to simplify Juicebox project designs. Reduce custom contracts by leveraging native protocol mechanics.
---

# Juicebox V5 Simplification Checklist

Before writing custom contracts, run through this checklist to find simpler solutions.

## The Simplification Principle

> **Native mechanics > Off-the-shelf hooks > Custom hooks > Custom contracts**

Every level of abstraction you can avoid:
- Reduces deployment costs
- Reduces attack surface
- Improves UI compatibility
- Makes the project easier to audit

---

## Pre-Implementation Checklist

### 1. Do You Need a Custom Pay Hook?

| What You Want | Simpler Solution |
|---------------|------------------|
| Mint NFTs on payment | Use `nana-721-hook-v5` directly |
| Buy tokens from DEX if cheaper | Use `nana-buyback-hook-v5` directly |
| Restrict who can pay | Use off-chain allowlists or payment metadata |
| Different tokens per tier | Use 721 hook tiers with different prices |
| Cap individual payments | Consider if this is actually needed |

**Only write a custom pay hook if**: You need logic that modifies payment recording that no existing hook provides.

---

### 2. Do You Need a Custom Cash Out Hook?

| What You Want | Simpler Solution |
|---------------|------------------|
| Burn NFT to redeem | Use `nana-721-hook-v5` - it already does this |
| Pro-rata redemption against surplus | Set `cashOutTaxRate: 0` - native behavior |
| Partial redemption (bonding curve) | Set `cashOutTaxRate` to desired value |
| Time-locked redemptions | Use ruleset with `pauseCashOut: true`, queue future ruleset |
| Redemption against external pool | This might actually need a custom hook |

**Only write a custom cash out hook if**: Redemption value must come from somewhere other than project surplus.

---

### 3. Do You Need a Custom Split Hook?

| What You Want | Simpler Solution |
|---------------|------------------|
| Send to multiple addresses | Use multiple splits with direct beneficiaries |
| Send to another JB project | Set `projectId` in the split |
| Add to project balance instead of paying | Set `preferAddToBalance: true` |
| Restrict who can claim | Set beneficiary to a multisig/contract |
| Swap tokens before forwarding | **Yes, need split hook** |
| Add to LP position | **Yes, need split hook** |

**Only write a custom split hook if**: You need to transform tokens or interact with external protocols.

---

### 4. Do You Need Multiple Queued Rulesets?

| What You Want | Simpler Solution |
|---------------|------------------|
| Monthly distributions | One ruleset with `duration: 30 days` |
| Increasing/decreasing token issuance | Use `weightCutPercent` for automatic issuance cut |
| Different phases over time | Queue rulesets only for actual changes |
| Vesting over 12 months | One cycling ruleset, NOT 12 queued rulesets |

**Only queue multiple rulesets if**: Configuration actually changes between periods.

---

### 5. Do You Need Custom NFT Logic?

| What You Want | Simpler Solution |
|---------------|------------------|
| NFT minting on payment | Use `nana-721-hook-v5` directly |
| Different prices per tier | Configure tiers in 721 hook |
| Static artwork per tier | Use `encodedIPFSUri` in tier config |
| Dynamic/generative art | Implement `IJB721TokenUriResolver` only |
| Composable/layered NFTs | Implement `IJB721TokenUriResolver` only |
| On-chain SVG | Implement `IJB721TokenUriResolver` only |
| Custom minting logic | This might need a custom hook |

**Only write a custom pay/data hook if**: You need to change how the 721 hook processes payments. For custom content, use the resolver interface.

**Reference**: [banny-retail-v5](https://github.com/mejango/banny-retail-v5) shows composable NFTs using only a custom resolver.

---

### 5b. When DO You Need to Extend 721-Hook?

Extending the 721-hook (not just resolver) is necessary when you need to change **treasury mechanics**, not just content:

| What You Want | Why You Need Custom Delegate |
|---------------|------------------------------|
| Dynamic cash out weights | Redemption value changes based on outcomes |
| First-owner tracking | Rewards go to original minter, not current holder |
| Phase-based restrictions | Different rules during different game phases |
| On-chain governance for outcomes | Scorecard voting determines payouts |

**Reference**: [defifa-collection-deployer-v5](https://github.com/BallKidz/defifa-collection-deployer-v5) shows prediction games with dynamic weights.

---

### 6. Do You Need a Custom Contract at All?

| What You Want | Simpler Solution |
|---------------|------------------|
| Vesting | Payout limits + cycling rulesets |
| Treasury reserve | Surplus allowance |
| NFT-gated treasury | 721 hook + native cash outs |
| Immutable configuration | Transfer ownership to burn address |
| Multi-sig control | Set owner to Safe/multisig |
| Governance | Use existing governance frameworks |

---

## Simplification Questions

Ask these questions in order. Stop at the first "yes":

### For Payments
1. Can the 721 hook handle this? → **Use 721 hook**
2. Can the buyback hook handle this? → **Use buyback hook**
3. Can payment metadata + off-chain logic handle this? → **Use native pay**
4. → Consider custom pay hook

### For Redemptions
1. Is it just burning NFTs for surplus? → **Use 721 hook**
2. Is it just tokens for surplus? → **Use native cash out with tax rate**
3. Does value come from project surplus? → **Use native cash out**
4. → Consider custom cash out hook

### For Distributions
1. Are recipients just addresses? → **Use native splits**
2. Are recipients other JB projects? → **Use splits with projectId**
3. Do you need token transformation? → **Use split hook**
4. → Consider custom split hook

### For Time-Based Logic
1. Is it recurring at fixed intervals? → **Use cycling ruleset**
2. Is it a one-time schedule change? → **Queue one future ruleset**
3. Is it conditional on external events? → **Consider approval hook**
4. → Consider custom logic

### For NFT Content
1. Is artwork static per tier? → **Use encodedIPFSUri in tier config**
2. Need dynamic/generative art? → **Implement IJB721TokenUriResolver**
3. Need composable NFTs? → **Implement IJB721TokenUriResolver**
4. Need to change minting logic? → Consider wrapping 721 hook

### For Games/Predictions
1. Fixed redemption values per tier? → **Use standard 721-hook**
2. Outcome determines payout distribution? → **Extend 721-hook (Defifa pattern)**
3. Need on-chain outcome voting? → **Add Governor contract**
4. Rewards to original minter only? → **Track first-owner in delegate**

---

## Common Over-Engineering Mistakes

### Mistake 1: Wrapping the 721 Hook

```
❌ WRONG: Create DataHookWrapper that delegates to 721 hook
✅ RIGHT: Use 721 hook directly, achieve goals via ruleset config
```

### Mistake 2: Vesting Split Hook

```
❌ WRONG: VestingSplitHook that holds funds and releases over time
✅ RIGHT: Payout limits reset each cycle, achieving the same result
```

### Mistake 3: Queue 12 Rulesets for 12-Month Vesting

```
❌ WRONG: Queue 12 identical rulesets with different start times
✅ RIGHT: One ruleset with duration: 30 days that cycles automatically
```

### Mistake 4: Split Hook for Simple Forwarding

```
❌ WRONG: Split hook that just forwards ETH to an address
✅ RIGHT: Set the address as the split beneficiary directly
```

### Mistake 5: Custom Redemption Math

```
❌ WRONG: Custom hook calculating pro-rata share of surplus
✅ RIGHT: cashOutTaxRate: 0 gives linear redemption natively
```

### Mistake 6: Custom Hook for NFT Artwork

```
❌ WRONG: Write custom pay hook to generate dynamic NFT metadata
✅ RIGHT: Use 721 hook + custom IJB721TokenUriResolver for content only
```

---

## Complexity Cost Table

| Solution | Gas Cost | Audit Risk | UI Support |
|----------|----------|------------|------------|
| Native config only | Lowest | Lowest | Full |
| Off-the-shelf hooks | Low | Low | Full |
| Custom token URI resolver | Low | Low | Full |
| Custom split hook | Medium | Medium | Partial |
| Custom pay hook | Medium | Medium | Partial |
| Extended 721-hook delegate | Medium-High | Medium-High | Custom UI needed |
| Custom cash out hook | High | High | Limited |
| Full custom system | Highest | Highest | None |

### When Higher Complexity Is Justified

Not all complexity is bad. These patterns justify extending hooks:

| Pattern | Justification |
|---------|---------------|
| Prediction games (Defifa) | Dynamic weights can't be done any other way |
| Composable NFTs (Banny) | Resolver-only keeps treasury mechanics standard |
| Phase-based games | Rulesets + custom delegate is cleaner than alternatives |

**Key insight**: Extend hooks for **treasury mechanics**, use resolvers for **content only**.

---

## Final Checklist

Before finalizing your design, verify:

- [ ] No custom hook where a direct beneficiary works
- [ ] No split hook where multiple native splits work
- [ ] No wrapped data hook where using the hook directly works
- [ ] No multiple queued rulesets where one cycling ruleset works
- [ ] No custom vesting where payout limits work
- [ ] No custom treasury where surplus allowance works
- [ ] No custom redemption where native cash out works
- [ ] No custom pay hook where IJB721TokenUriResolver handles content needs

If all boxes are checked and you still need custom code, proceed with confidence that it's actually necessary.

---

## Related Skills

- `/jb-patterns` - Common design patterns with examples
- `/jb-project` - Project deployment
- `/jb-pay-hook` - When you DO need a custom pay hook
- `/jb-cash-out-hook` - When you DO need a custom cash out hook
- `/jb-split-hook` - When you DO need a custom split hook
