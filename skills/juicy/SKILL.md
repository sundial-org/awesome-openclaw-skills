---
name: juicebox-v5
description: Complete Juicebox V5 protocol skills collection. Build, deploy, and interact with Juicebox projects, revnets, hooks, and omnichain deployments. Includes API reference, implementation details, UI generation, and GraphQL queries.
---

# Juicebox V5 Skills Collection

A comprehensive set of skills for building on the Juicebox V5 protocol.

## Included Skills

### Core Protocol
- **jb-v5-api** - Function signatures and API reference for all contracts
- **jb-v5-impl** - Deep implementation details, edge cases, and tradeoffs
- **jb-v5-currency-types** - Currency system with real-world and token-derived types
- **jb-v5-v51-contracts** - V5 vs V5.1 contract version separation

### Project Management
- **jb-project** - Create and configure Juicebox V5 projects
- **jb-ruleset** - Configure rulesets with rates, splits, and constraints
- **jb-query** - Query project state from the blockchain
- **jb-decode** - Decode transaction calldata and analyze history

### Hooks
- **jb-pay-hook** - Generate custom pay hooks from specifications
- **jb-cash-out-hook** - Generate custom cash out hooks
- **jb-split-hook** - Generate custom split hooks

### UI Generation
- **jb-deploy-ui** - Generate deployment frontends
- **jb-interact-ui** - Generate project interaction frontends
- **jb-explorer-ui** - Etherscan-like contract explorer
- **jb-event-explorer-ui** - Browse and decode project events
- **jb-nft-gallery-ui** - NFT gallery for 721 hooks
- **jb-ruleset-timeline-ui** - Visual timeline for ruleset history
- **jb-hook-deploy-ui** - Deploy custom hooks from browser

### Financial
- **jb-cash-out-curve** - Bonding curve redemption calculations
- **jb-fund-access-limits** - Query payout limits and surplus allowances
- **jb-protocol-fees** - Fee structures and calculations
- **jb-multi-currency** - Handle ETH vs USDC accounting
- **jb-terminal-selection** - Dynamic terminal selection for payments
- **jb-terminal-wrapper** - Terminal wrapper pattern for extending functionality
- **jb-permit2-metadata** - Encode Permit2 metadata for gasless payments

### Revnets
- **revnet-economics** - Academic findings and economic thresholds
- **revnet-modeler** - Simulate and plan revnet token dynamics
- **jb-revloans** - REVLoans contract mechanics
- **jb-loan-queries** - Query loan data via Bendystraw

### Omnichain
- **jb-omnichain-ui** - Build omnichain UIs for cross-chain projects
- **jb-omnichain-payout-limits** - Per-chain payout limit constraints
- **jb-suckers** - Cross-chain token bridging

### Data & APIs
- **jb-bendystraw** - GraphQL API for cross-chain project data
- **jb-relayr** - Multi-chain transaction bundling API
- **jb-docs** - Query Juicebox V5 documentation

### Patterns & Best Practices
- **jb-patterns** - Common design patterns for vesting, treasuries, yield
- **jb-simplify** - Checklist to reduce custom contract needs
- **jbx-fee-flows** - JBX ecosystem fee flows and revenue streams
