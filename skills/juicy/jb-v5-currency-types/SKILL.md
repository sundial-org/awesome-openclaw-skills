---
name: jb-v5-currency-types
description: |
  Juicebox V5 currency system with two distinct types: real-world currencies and token-derived currencies.
  Use when: (1) configuring ruleset.baseCurrency, (2) setting up JBAccountingContext, (3) working with
  cross-chain projects, (4) confused about why currency values differ between chains, (5) seeing
  unexpected issuance rates across chains. Critical: baseCurrency must ALWAYS use real-world currencies
  (1=ETH, 2=USD), never token-derived currencies. Token currencies vary by chain address.
---

# Juicebox V5 Currency Types

## Problem

Juicebox V5 has two different currency systems that are easy to confuse, leading to:
- Inconsistent issuance rates across chains
- Projects vulnerable to stablecoin depegs
- Misconfigured accounting contexts
- Cross-chain ruleset interpretation failures

## Context / Trigger Conditions

Apply this knowledge when:
- Setting `ruleset.baseCurrency` for token issuance
- Configuring `JBAccountingContext.currency` for terminals
- Working with `JBCurrencyAmount` in payout limits or allowances
- Building cross-chain projects that need consistent behavior
- Debugging why issuance rates differ between chains
- Seeing different currency values for "the same" token on different chains

## Solution

### Two Currency Systems

**1. Real-World Currencies (JBCurrencies)**

Abstract values representing the concept of a currency, chain-agnostic:

| Currency | Value | Use For |
|----------|-------|---------|
| ETH | 1 | "Per ETH" pricing regardless of chain |
| USD | 2 | "Per dollar" pricing regardless of chain |

These are stable across ALL chains. `baseCurrency=2` means "issue X tokens per USD" whether you're on Ethereum, Base, Celo, or Polygon.

**2. Token-Derived Currencies**

Computed from token addresses, chain-specific:

```solidity
currency = uint32(uint160(tokenAddress))
```

| Token | Chain | Address | Currency |
|-------|-------|---------|----------|
| USDC | Ethereum | 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 | 909516616 |
| USDC | Optimism | 0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85 | 3530704773 |
| USDC | Base | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 | 3169378579 |
| USDC | Arbitrum | 0xaf88d065e77c8cC2239327C5EDb3A432268e5831 | 1156540465 |
| NATIVE_TOKEN | All | 0xEEEE...EEEe | 4008636142 |

### When to Use Which

| Field | Use | Why |
|-------|-----|-----|
| `ruleset.baseCurrency` | **Real-world only** (1 or 2) | Rulesets must be interpretable consistently across ALL chains |
| `JBAccountingContext.currency` | **Token-derived** | You're tracking a specific token at a specific address |
| `JBCurrencyAmount.currency` | Either | Depends on whether you want abstract value or token-specific |
| `JBFundAccessLimitGroup` amounts | Either | Use real-world for cross-chain consistency |

### Critical Rules

1. **NEVER use token currencies for `baseCurrency`**
   - Token addresses change across chains
   - Would cause different issuance rates per chain
   - Breaks cross-chain project consistency

2. **NEVER use NATIVE_TOKEN's currency (4008636142) for `baseCurrency`**
   - Different chains have different native tokens (ETH, CELO, MATIC, etc.)
   - NATIVE_TOKEN represents "whatever is native on this chain" - not specifically ETH
   - If you want issuance relative to ETH, use `JBCurrencies.ETH` (which is `1`)
   - JBPrices provides a 1:1 price feed between NATIVE_TOKEN currency and ETH currency on chains where ETH is the native token

3. **ALWAYS use token currencies for `JBAccountingContext`**
   - Formula: `currency = uint32(uint160(token))`
   - The terminal needs to know exactly which token it's accounting for

4. **USD vs USDC distinction matters**
   - USD (2) = abstract dollar concept
   - USDC (token-derived) = specific stablecoin
   - If USDC depegs to $0.98, a project with `baseCurrency=2` still issues tokens per dollar (protected)
   - JBPrices handles the exchange rate between USD and USDC

### JBPrices

JBPrices manages exchange rates between:
- Real-world currencies (ETH ↔ USD)
- Token currencies (USDC ↔ USD, ETH token ↔ ETH concept)
- Cross-currency conversions for payments and cash outs

## Verification

To verify correct configuration:
1. Check `baseCurrency` is 1 or 2, never a large token-derived number
2. Check `JBAccountingContext.currency` matches `uint32(uint160(token))`
3. Deploy to testnet on two different chains and verify issuance rates match

## Example

**Correct cross-chain project configuration:**

```javascript
const rulesetConfig = {
  // ... other fields
  metadata: {
    baseCurrency: 2,  // USD - same on all chains
    // ...
  }
}

const terminalConfig = {
  terminal: JBMultiTerminal5_1,
  accountingContextsToAccept: [{
    token: USDC_ADDRESS[chainId],  // Different per chain
    decimals: 6,
    currency: uint32(uint160(USDC_ADDRESS[chainId]))  // Different per chain
  }]
}
```

**Wrong:**
```javascript
const rulesetConfig = {
  metadata: {
    baseCurrency: 909516616,  // WRONG! This is Ethereum USDC's token currency
    // This would break on other chains or if USDC depegs
  }
}
```

**Also wrong:**
```javascript
const rulesetConfig = {
  metadata: {
    baseCurrency: 4008636142,  // WRONG! This is NATIVE_TOKEN's currency
    // NATIVE_TOKEN is CELO on Celo, MATIC on Polygon, etc.
    // If you want "per ETH" issuance, use 1 (JBCurrencies.ETH)
  }
}
```

## Notes

- Price feeds between all currency types are managed by JBPrices contract
- The NATIVE_TOKEN address (0xEEEE...EEEe) is special and constant across chains, but represents different actual tokens per chain
- `baseCurrency=1` (ETH) means "issue tokens relative to ETH the asset" - JBPrices correlates NATIVE_TOKEN to ETH at 1:1 on ETH-native chains
- On non-ETH-native chains (Celo, Polygon), JBPrices provides the ETH/NATIVE_TOKEN exchange rate so issuance stays ETH-denominated
- This architecture enables truly portable rulesets that behave identically regardless of deployment chain
- The separation between "real-world currency concepts" and "token-derived currencies" is what makes cross-chain consistency possible

## Related Skills

- `/jb-suckers` - Cross-chain bridging mechanics via sucker contracts
- `/jb-omnichain-ui` - Building omnichain UIs with Relayr and Bendystraw
