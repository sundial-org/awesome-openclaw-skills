---
name: jb-v5-v51-contracts
description: |
  Juicebox V5 vs V5.1 contract version separation rules. Use when: (1) determining which
  contracts to use for a project, (2) versioned contracts show unexpected behavior,
  (3) transactions fail with "invalid terminal" or similar errors, (4) deploying new
  projects vs interacting with existing projects. CRITICAL: Versioned contracts must never mix.
---

# Juicebox V5 vs V5.1 Contract Separation

## Problem

Juicebox has two contract versions: V5 (original) and V5.1 (upgraded). When contracts
have both versions, mixing them causes transactions to fail. A project using
JBController5_1 MUST use JBMultiTerminal5_1, not the V5 terminal.

## Context / Trigger Conditions

- Deploying new projects or terminals
- Transactions failing with "invalid terminal" or permission errors
- Querying rulesets returns unexpected data
- Paying a project fails despite correct addresses
- Determining which contracts to use for a given project

## Solution

### The Rule

**When a contract has both V5 and V5.1 versions, you MUST use matching versions.**

Contracts that only have ONE version (no 5_1 variant) work with both V5 and V5.1 projects.

### Detecting Project Version (CRITICAL)

**IMPORTANT: Some non-revnet projects also use V5.0 contracts.** You cannot assume that
a project is on V5.1 just because it's not a revnet. The ONLY authoritative way to
determine which contracts a project uses is to query `JBDirectory.controllerOf()`.

**Always check JBDirectory.controllerOf() to get the actual controller address, then
compare against known V5 and V5.1 controller addresses.**

```typescript
const JB_DIRECTORY = '0x0061e516886a0540f63157f112c0588ee0651dcf'
const JB_CONTROLLER_V5 = '0x27da30646502e2f642be5281322ae8c394f7668a'
const JB_CONTROLLER_V5_1 = '0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1'

// Query JBDirectory for the project's controller
const controller = await publicClient.readContract({
  address: JB_DIRECTORY,
  abi: JB_DIRECTORY_ABI,
  functionName: 'controllerOf',
  args: [BigInt(projectId)],
})

// Determine version by comparing controller address
const isV5 = controller.toLowerCase() === JB_CONTROLLER_V5.toLowerCase()
const isV5_1 = controller.toLowerCase() === JB_CONTROLLER_V5_1.toLowerCase()

if (isV5) {
  // Use V5.0 contracts (JBMultiTerminal, JBRulesets, etc.)
} else if (isV5_1) {
  // Use V5.1 contracts (JBMultiTerminal5_1, JBRulesets5_1, etc.)
} else {
  // Unknown controller - handle edge case
}
```

**Why not check owner?** While revnets are owned by REVDeployer and always use V5.0,
some regular projects deployed before V5.1 also use V5.0. Checking the owner only
tells you if it's a revnet, not which contract version the project actually uses.

### Contract Address Reference

**Shared Contracts (work with BOTH V5 and V5.1)**

| Contract | Address |
|----------|---------|
| JBProjects | 0x885f707efa18d2cb12f05a3a8eba6b4b26c8c1d4 |
| JBTokens | 0x4d0edd347fb1fa21589c1e109b3474924be87636 |
| JBDirectory | 0x0061e516886a0540f63157f112c0588ee0651dcf |
| JBSplits | 0x7160a322fea44945a6ef9adfd65c322258df3c5e |
| JBFundAccessLimits | 0x3a46b21720c8b70184b0434a2293b2fdcc497ce7 |
| JBPermissions | 0xba948dab74e875b19cf0e2ca7a4546c0c2defc40 |
| JBPrices | 0x6e92e3b5ce1e7a4344c6d27c0c54efd00df92fb6 |
| JBFeelessAddresses | 0xf76f7124f73abc7c30b2f76121afd4c52be19442 |

**V5.1 Contracts (for NEW projects)**

| Contract | Address |
|----------|---------|
| JBController5_1 | 0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1 |
| JBMultiTerminal5_1 | 0x52869db3d61dde1e391967f2ce5039ad0ecd371c |
| JBRulesets5_1 | 0xd4257005ca8d27bbe11f356453b0e4692414b056 |
| JBTerminalStore5_1 | 0x82239c5a21f0e09573942caa41c580fa36e27071 |
| JBOmnichainDeployer5_1 | 0x587bf86677ec0d1b766d9ba0d7ac2a51c6c2fc71 |

**V5 Contracts (for REVNETS)**

| Contract | Address |
|----------|---------|
| JBController | 0x27da30646502e2f642be5281322ae8c394f7668a |
| JBMultiTerminal | 0x2db6d704058e552defe415753465df8df0361846 |
| JBRulesets | 0x6292281d69c3593fcf6ea074e5797341476ab428 |
| REVDeployer | 0x2ca27bde7e7d33e353b44c27acfcf6c78dde251d |

### Code Pattern

```typescript
// Known controller addresses (same on all chains via CREATE2)
const CONTROLLERS = {
  V5: '0x27da30646502e2f642be5281322ae8c394f7668a',
  V5_1: '0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1',
}

// Versioned contracts by version
const VERSIONED_CONTRACTS = {
  V5: {
    controller: '0x27da30646502e2f642be5281322ae8c394f7668a',  // JBController
    terminal: '0x2db6d704058e552defe415753465df8df0361846',    // JBMultiTerminal
    rulesets: '0x6292281d69c3593fcf6ea074e5797341476ab428',    // JBRulesets
  },
  V5_1: {
    controller: '0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1',  // JBController5_1
    terminal: '0x52869db3d61dde1e391967f2ce5039ad0ecd371c',    // JBMultiTerminal5_1
    rulesets: '0xd4257005ca8d27bbe11f356453b0e4692414b056',    // JBRulesets5_1
  },
}

// Shared contracts work with any project
const SHARED = {
  directory: '0x0061e516886a0540f63157f112c0588ee0651dcf',
  splits: '0x7160a322fea44945a6ef9adfd65c322258df3c5e',
  fundAccessLimits: '0x3a46b21720c8b70184b0434a2293b2fdcc497ce7',
  projects: '0x885f707efa18d2cb12f05a3a8eba6b4b26c8c1d4',
  tokens: '0x4d0edd347fb1fa21589c1e109b3474924be87636',
}

// Helper to get correct contracts for a project
// ALWAYS queries JBDirectory.controllerOf() - the ONLY authoritative source
async function getContractsForProject(projectId: number): Promise<{
  controller: `0x${string}`,
  terminal: `0x${string}`,
  rulesets: `0x${string}`,
  version: 'V5' | 'V5_1',
}> {
  // Step 1: Query JBDirectory for the project's actual controller
  const controller = await publicClient.readContract({
    address: SHARED.directory,
    abi: JB_DIRECTORY_ABI,
    functionName: 'controllerOf',
    args: [BigInt(projectId)],
  })

  // Step 2: Determine version by comparing controller address
  const controllerLower = controller.toLowerCase()

  if (controllerLower === CONTROLLERS.V5.toLowerCase()) {
    return { ...VERSIONED_CONTRACTS.V5, version: 'V5' }
  }

  if (controllerLower === CONTROLLERS.V5_1.toLowerCase()) {
    return { ...VERSIONED_CONTRACTS.V5_1, version: 'V5_1' }
  }

  // Unknown controller - this shouldn't happen for valid Juicebox projects
  throw new Error(`Unknown controller ${controller} for project ${projectId}`)
}
```

### Cast Command to Check Version

```bash
# Get controller for a project - this is the authoritative source
cast call 0x0061e516886a0540f63157f112c0588ee0651dcf \
  "controllerOf(uint256)(address)" $PROJECT_ID --rpc-url $RPC_URL

# Compare result:
# 0x27da30646502e2f642be5281322ae8c394f7668a = V5.0
# 0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1 = V5.1
```

## Verification

- Payment transactions succeed without "invalid terminal" errors
- Ruleset queries return expected data
- Project creation uses correct contract set

## Example

Paying NANA (Project #1, a Revnet):
```bash
cast call 0x0061e516886a0540f63157f112c0588ee0651dcf "controllerOf(uint256)(address)" 1
# Returns: 0x27da30646502e2f642be5281322ae8c394f7668a (V5 controller)
# → Use V5 contracts: JBMultiTerminal 0x2db6d704058e552defe415753465df8df0361846
```

Paying a project deployed with V5.1:
```bash
cast call 0x0061e516886a0540f63157f112c0588ee0651dcf "controllerOf(uint256)(address)" 123
# Returns: 0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1 (V5.1 controller)
# → Use V5.1 contracts: JBMultiTerminal5_1 0x52869db3d61dde1e391967f2ce5039ad0ecd371c
```

## Notes

- **CRITICAL**: Always check `JBDirectory.controllerOf()` to determine version - never assume based on ownership
- Some non-revnet projects use V5.0 contracts (deployed before V5.1 existed)
- All addresses are deterministic across all chains (Ethereum, Optimism, Base, Arbitrum)
- JBOmnichainDeployer5_1 deploys to all chains at once using V5.1 contracts
- Source of truth: [nana-core-v5/deployments](https://github.com/Bananapus/nana-core-v5/tree/main/deployments) and [docs.juicebox.money/dev/v5/addresses](https://docs.juicebox.money/dev/v5/addresses)

## References

- JBDirectory (for controllerOf lookup): 0x0061e516886a0540f63157f112c0588ee0651dcf
- JBController V5: 0x27da30646502e2f642be5281322ae8c394f7668a
- JBController V5.1: 0xf3cc99b11bd73a2e3b8815fb85fe0381b29987e1
- Official docs: https://docs.juicebox.money/dev/v5/addresses
