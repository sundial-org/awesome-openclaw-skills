---
name: jb-deploy-ui
description: Generate minimal frontends for deploying Juicebox V5 projects and hooks. Creates standalone HTML files with wallet connection, transaction forms, and live status updates.
---

# Juicebox V5 Deployment UI Generator

Generate simple frontends for deploying Juicebox projects, hooks, and configurations. Uses shared styles and viem for blockchain interactions.

## Philosophy

> **Show users exactly what they're doing. Make wallet connection trivial. Display transactions in flight.**

- Single HTML file, no build step
- viem from ESM CDN
- Shared CSS from `/shared/styles.css`
- Clear transaction previews before signing

## Template: Project Deployment UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deploy Juicebox Project</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    .preview { background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; padding: 0.75rem; font-family: monospace; font-size: 0.75rem; margin: 0.5rem 0; white-space: pre-wrap; word-break: break-all; }
  </style>
</head>
<body>
  <div class="container" style="max-width: 640px;">
    <h1>Deploy Juicebox Project</h1>

    <div class="card">
      <button class="btn" id="connect-btn" onclick="connectWallet()">Connect Wallet</button>
      <div id="wallet-status" class="hidden" style="margin-top: 0.75rem;">
        <span class="badge-success">Connected: <span id="wallet-address"></span> on <span id="network-name"></span></span>
      </div>
    </div>

    <div class="card">
      <h2>Project Details</h2>
      <label>Project Name</label>
      <input type="text" id="project-name" placeholder="My Project">
      <label>Description</label>
      <textarea id="project-description" rows="3" placeholder="What is this project for?"></textarea>
      <label>Owner Address (defaults to connected wallet)</label>
      <input type="text" id="owner-address" placeholder="0x...">
    </div>

    <div class="card">
      <h2>Ruleset Configuration</h2>
      <label>Duration (days, 0 = no cycles)</label>
      <input type="number" id="duration" value="0" min="0">
      <label>Tokens per ETH</label>
      <input type="number" id="weight" value="1000000" min="0">
      <label>Reserved Rate (%)</label>
      <input type="number" id="reserved-rate" value="0" min="0" max="100">
      <label>Cash Out Tax Rate (%)</label>
      <input type="number" id="cash-out-tax" value="0" min="0" max="100">
    </div>

    <div class="card">
      <h2>Transaction Preview</h2>
      <div id="tx-preview" class="preview">Connect wallet to see preview</div>
      <button class="btn" id="deploy-btn" onclick="deploy()" disabled>Deploy Project</button>
    </div>

    <div id="tx-status" class="card hidden"></div>
  </div>

  <script type="module">
    import { createWalletClient, createPublicClient, custom, http, parseEther, zeroAddress } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, loadChainConfig, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };

    const CONTROLLER_ABI = [{
      name: 'launchProjectFor', type: 'function', stateMutability: 'nonpayable',
      inputs: [
        { name: 'owner', type: 'address' },
        { name: 'projectUri', type: 'string' },
        { name: 'rulesetConfigurations', type: 'tuple[]', components: [
          { name: 'mustStartAtOrAfter', type: 'uint256' },
          { name: 'duration', type: 'uint256' },
          { name: 'weight', type: 'uint256' },
          { name: 'weightCutPercent', type: 'uint256' },
          { name: 'approvalHook', type: 'address' },
          { name: 'metadata', type: 'tuple', components: [
            { name: 'reservedRate', type: 'uint256' },
            { name: 'cashOutTaxRate', type: 'uint256' },
            { name: 'baseCurrency', type: 'uint256' },
            { name: 'pausePay', type: 'bool' },
            { name: 'pauseCashOut', type: 'bool' },
            { name: 'pauseTransfers', type: 'bool' },
            { name: 'allowOwnerMinting', type: 'bool' },
            { name: 'allowTerminalMigration', type: 'bool' },
            { name: 'allowSetTerminals', type: 'bool' },
            { name: 'allowSetController', type: 'bool' },
            { name: 'allowAddAccountingContexts', type: 'bool' },
            { name: 'allowAddPriceFeed', type: 'bool' },
            { name: 'ownerMustSendPayouts', type: 'bool' },
            { name: 'holdFees', type: 'bool' },
            { name: 'useTotalSurplusForCashOuts', type: 'bool' },
            { name: 'useDataHookForPay', type: 'bool' },
            { name: 'useDataHookForCashOut', type: 'bool' },
            { name: 'dataHook', type: 'address' },
            { name: 'metadata', type: 'uint256' }
          ]},
          { name: 'splitGroups', type: 'tuple[]', components: [] },
          { name: 'fundAccessLimitGroups', type: 'tuple[]', components: [] }
        ]},
        { name: 'terminalConfigurations', type: 'tuple[]', components: [
          { name: 'terminal', type: 'address' },
          { name: 'accountingContexts', type: 'tuple[]', components: [
            { name: 'token', type: 'address' },
            { name: 'decimals', type: 'uint8' },
            { name: 'currency', type: 'uint32' }
          ]}
        ]},
        { name: 'memo', type: 'string' }
      ],
      outputs: [{ type: 'uint256' }]
    }];

    let walletClient = null;
    let publicClient = null;
    let connectedAddress = null;
    let chainId = 1;
    let chainConfig = null;

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install a web3 wallet'); return; }

      try {
        const [address] = await window.ethereum.request({ method: 'eth_requestAccounts' });
        connectedAddress = address;
        chainId = parseInt(await window.ethereum.request({ method: 'eth_chainId' }), 16);

        walletClient = createWalletClient({ chain: CHAINS[chainId], transport: custom(window.ethereum) });
        publicClient = createPublicClient({ chain: CHAINS[chainId], transport: http(CHAIN_CONFIGS[chainId]?.rpc) });
        chainConfig = await loadChainConfig();

        document.getElementById('wallet-address').textContent = truncateAddress(address);
        document.getElementById('network-name').textContent = CHAINS[chainId]?.name || `Chain ${chainId}`;
        document.getElementById('wallet-status').classList.remove('hidden');
        document.getElementById('connect-btn').classList.add('hidden');
        document.getElementById('deploy-btn').disabled = false;

        updatePreview();
      } catch (e) { console.error(e); alert('Failed to connect'); }
    };

    function getConfig() {
      return {
        owner: document.getElementById('owner-address').value || connectedAddress,
        projectUri: '',
        duration: BigInt(parseInt(document.getElementById('duration').value) * 86400),
        weight: parseEther(document.getElementById('weight').value),
        reservedRate: BigInt(parseInt(document.getElementById('reserved-rate').value) * 100),
        cashOutTaxRate: BigInt(parseInt(document.getElementById('cash-out-tax').value) * 100)
      };
    }

    function updatePreview() {
      const config = getConfig();
      document.getElementById('tx-preview').textContent = JSON.stringify({
        owner: config.owner,
        duration: `${config.duration} seconds`,
        weight: `${config.weight} wei`,
        reservedRate: `${config.reservedRate / 100n}%`,
        cashOutTaxRate: `${config.cashOutTaxRate / 100n}%`
      }, null, 2);
    }

    window.deploy = async function() {
      const config = getConfig();
      const addresses = chainConfig?.chains[chainId]?.contracts;
      if (!addresses) { alert('Unsupported network'); return; }

      showStatus('info', 'Please confirm in wallet...');

      try {
        const rulesetConfig = {
          mustStartAtOrAfter: 0n,
          duration: config.duration,
          weight: config.weight,
          weightCutPercent: 0n,
          approvalHook: zeroAddress,
          metadata: {
            reservedRate: config.reservedRate,
            cashOutTaxRate: config.cashOutTaxRate,
            baseCurrency: 0n,
            pausePay: false, pauseCashOut: false, pauseTransfers: false,
            allowOwnerMinting: false, allowTerminalMigration: false,
            allowSetTerminals: false, allowSetController: false,
            allowAddAccountingContexts: false, allowAddPriceFeed: false,
            ownerMustSendPayouts: false, holdFees: false,
            useTotalSurplusForCashOuts: false,
            useDataHookForPay: false, useDataHookForCashOut: false,
            dataHook: zeroAddress, metadata: 0n
          },
          splitGroups: [],
          fundAccessLimitGroups: []
        };

        const terminalConfig = {
          terminal: addresses.JBMultiTerminal,
          accountingContexts: [{ token: '0x000000000000000000000000000000000000EEEe', decimals: 18, currency: 0 }]
        };

        const hash = await walletClient.writeContract({
          address: addresses.JBController,
          abi: CONTROLLER_ABI,
          functionName: 'launchProjectFor',
          args: [config.owner, config.projectUri, [rulesetConfig], [terminalConfig], 'Deployed via Juicebox UI'],
          account: connectedAddress
        });

        showStatus('info', `Transaction sent: ${truncateAddress(hash)}`);
        const receipt = await publicClient.waitForTransactionReceipt({ hash });
        showStatus('success', `Project deployed! <a href="${getTxUrl(chainId, hash)}" target="_blank">View tx</a>`);
      } catch (error) {
        showStatus('error', `Failed: ${error.message}`);
      }
    };

    function showStatus(type, message) {
      const el = document.getElementById('tx-status');
      el.className = `card badge-${type}`;
      el.innerHTML = message;
      el.classList.remove('hidden');
    }

    document.querySelectorAll('input, textarea').forEach(el => el.addEventListener('input', updatePreview));
  </script>
</body>
</html>
```

## Template: 721 NFT Project Deployment

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deploy NFT Project</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    .tier-card { border: 1px dashed var(--border-color); padding: 1rem; margin-bottom: 0.75rem; border-radius: 4px; }
    .tier-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
    .remove-tier { background: var(--error); padding: 0.25rem 0.5rem; width: auto; font-size: 0.75rem; }
    .add-tier { background: var(--bg-tertiary); margin-bottom: 1rem; }
  </style>
</head>
<body>
  <div class="container" style="max-width: 640px;">
    <h1>Deploy NFT Project</h1>

    <div class="card">
      <button class="btn" id="connect-btn" onclick="connectWallet()">Connect Wallet</button>
      <div id="wallet-status" class="hidden" style="margin-top: 0.75rem;">
        <span class="badge-success">Connected: <span id="wallet-address"></span></span>
      </div>
    </div>

    <div class="card">
      <h2>Collection Details</h2>
      <label>Collection Name</label>
      <input type="text" id="collection-name" placeholder="My NFT Collection">
      <label>Symbol</label>
      <input type="text" id="collection-symbol" placeholder="MYNFT">
      <label>Base URI (IPFS folder)</label>
      <input type="text" id="base-uri" placeholder="ipfs://Qm.../">
    </div>

    <div class="card">
      <h2>NFT Tiers</h2>
      <div id="tiers-container"></div>
      <button class="add-tier btn-secondary" onclick="addTier()">+ Add Tier</button>
    </div>

    <div class="card">
      <h2>Treasury Settings</h2>
      <label>Reserved Rate (%)</label>
      <input type="number" id="reserved-rate" value="0" min="0" max="100">
      <label>Cash Out Tax Rate (%)</label>
      <input type="number" id="cash-out-tax" value="0" min="0" max="100">
    </div>

    <div class="card">
      <button class="btn" id="deploy-btn" onclick="deploy()" disabled>Deploy NFT Project</button>
    </div>

    <div id="tx-status" class="card hidden"></div>
  </div>

  <script type="module">
    import { createWalletClient, custom, parseEther, zeroAddress, zeroHash } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { loadChainConfig, truncateAddress } from '/shared/wallet-utils.js';

    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };

    let walletClient = null;
    let connectedAddress = null;
    let chainId = 1;
    let chainConfig = null;
    let tierCount = 0;

    window.addTier = function() {
      tierCount++;
      document.getElementById('tiers-container').insertAdjacentHTML('beforeend', `
        <div class="tier-card" id="tier-${tierCount}">
          <div class="tier-header">
            <strong>Tier ${tierCount}</strong>
            <button class="remove-tier btn" onclick="document.getElementById('tier-${tierCount}').remove()">Remove</button>
          </div>
          <label>Price (ETH)</label>
          <input type="number" class="tier-price" step="0.001" placeholder="0.1">
          <label>Supply</label>
          <input type="number" class="tier-supply" placeholder="100">
          <label>IPFS Hash (Qm...)</label>
          <input type="text" class="tier-ipfs" placeholder="QmYwAPJzv5CZsnA625s3Xf2...">
        </div>
      `);
    };

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install wallet'); return; }
      const [address] = await window.ethereum.request({ method: 'eth_requestAccounts' });
      connectedAddress = address;
      chainId = parseInt(await window.ethereum.request({ method: 'eth_chainId' }), 16);
      walletClient = createWalletClient({ chain: CHAINS[chainId], transport: custom(window.ethereum) });
      chainConfig = await loadChainConfig();

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');
      document.getElementById('deploy-btn').disabled = false;
    };

    function encodeIPFSUri(cid) {
      if (!cid || !cid.startsWith('Qm')) return zeroHash;
      const bs58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
      let decoded = 0n;
      for (const char of cid) decoded = decoded * 58n + BigInt(bs58.indexOf(char));
      return '0x' + decoded.toString(16).padStart(68, '0').slice(4);
    }

    function getTiers() {
      const tiers = [];
      document.querySelectorAll('.tier-card').forEach((card, i) => {
        const price = card.querySelector('.tier-price').value;
        const supply = card.querySelector('.tier-supply').value;
        const ipfs = card.querySelector('.tier-ipfs').value;
        if (price && supply) {
          tiers.push({
            price: parseEther(price),
            initialSupply: parseInt(supply),
            votingUnits: 0, reserveFrequency: 0, reserveBeneficiary: zeroAddress,
            encodedIPFSUri: encodeIPFSUri(ipfs), category: i + 1, discountPercent: 0,
            allowOwnerMint: false, useReserveBeneficiaryAsDefault: false,
            transfersPausable: false, useVotingUnits: false,
            cannotBeRemoved: false, cannotIncreaseDiscountPercent: false
          });
        }
      });
      return tiers;
    }

    window.deploy = async function() {
      const tiers = getTiers();
      if (tiers.length === 0) { alert('Add at least one tier'); return; }
      const addresses = chainConfig?.chains[chainId]?.contracts;
      if (!addresses?.JB721TiersHookProjectDeployer) { alert('721 Deployer not available'); return; }

      showStatus('info', 'Please confirm in wallet...');

      try {
        // Build hook config and launch config (simplified - full implementation needs complete struct)
        alert(`Deploy ${tiers.length} tier(s) to project via JB721TiersHookProjectDeployer.

This template provides the structure - see /jb-project for full deployment scripts.`);
        showStatus('success', 'See console for tier data');
        console.log('Tiers:', tiers);
      } catch (error) {
        showStatus('error', `Failed: ${error.message}`);
      }
    };

    function showStatus(type, msg) {
      const el = document.getElementById('tx-status');
      el.className = `card badge-${type}`;
      el.textContent = msg;
      el.classList.remove('hidden');
    }

    addTier();
  </script>
</body>
</html>
```

## Template: Revnet Deployment

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deploy Revnet</title>
  <link rel="stylesheet" href="/shared/styles.css">
</head>
<body>
  <div class="container" style="max-width: 640px;">
    <h1>Deploy Revnet</h1>
    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Launch an autonomous tokenized treasury</p>

    <div class="card">
      <button class="btn" id="connect-btn" onclick="connectWallet()">Connect Wallet</button>
      <div id="wallet-status" class="hidden" style="margin-top: 0.75rem;">
        <span class="badge-success">Connected: <span id="wallet-address"></span></span>
      </div>
    </div>

    <div class="card">
      <div class="badge-warning" style="margin-bottom: 1rem;">Revnets are autonomous - configuration is permanent after deployment.</div>
      <h2>Token Configuration</h2>
      <label>Token Name</label>
      <input type="text" id="token-name" placeholder="My Revnet Token">
      <label>Token Symbol</label>
      <input type="text" id="token-symbol" placeholder="REV">
    </div>

    <div class="card">
      <h2>Stage 1 Configuration</h2>
      <label>Initial Issuance (tokens per ETH)</label>
      <input type="number" id="initial-issuance" value="1000000" min="1">
      <label>Issuance Cut (% reduction per period)</label>
      <input type="number" id="issuance-cut" value="5" min="0" max="100" step="0.1">
      <label>Cut Frequency (days)</label>
      <input type="number" id="cut-frequency" value="30" min="1">
      <label>Cash Out Tax Rate (%)</label>
      <input type="number" id="cash-out-tax" value="40" min="0" max="100">
      <label>Split to Operator (%)</label>
      <input type="number" id="operator-split" value="20" min="0" max="100">
    </div>

    <div class="card">
      <label>Operator Address</label>
      <input type="text" id="operator-address" placeholder="0x...">
      <p style="font-size: 0.8rem; color: var(--text-muted);">Receives split percentage. Can update splits but not core rules.</p>
    </div>

    <div class="card">
      <button class="btn" id="deploy-btn" onclick="deployRevnet()" disabled>Deploy Revnet</button>
    </div>

    <div id="tx-status" class="card hidden"></div>
  </div>

  <script type="module">
    import { createWalletClient, custom } from 'https://esm.sh/viem';
    import { mainnet, sepolia } from 'https://esm.sh/viem/chains';
    import { loadChainConfig, truncateAddress } from '/shared/wallet-utils.js';

    const CHAINS = { 1: mainnet, 11155111: sepolia };
    let walletClient, connectedAddress, chainId, chainConfig;

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install wallet'); return; }
      const [address] = await window.ethereum.request({ method: 'eth_requestAccounts' });
      connectedAddress = address;
      chainId = parseInt(await window.ethereum.request({ method: 'eth_chainId' }), 16);
      walletClient = createWalletClient({ chain: CHAINS[chainId], transport: custom(window.ethereum) });
      chainConfig = await loadChainConfig();

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');
      document.getElementById('deploy-btn').disabled = false;
      if (!document.getElementById('operator-address').value) {
        document.getElementById('operator-address').value = address;
      }
    };

    window.deployRevnet = async function() {
      const revDeployer = chainConfig?.chains[chainId]?.contractsV5?.REVDeployer;
      if (!revDeployer) { alert('REVDeployer not available on this network'); return; }

      const stageConfig = {
        startsAtOrAfter: 0,
        splitPercent: parseInt(document.getElementById('operator-split').value) * 100,
        initialIssuance: parseInt(document.getElementById('initial-issuance').value),
        issuanceCutFrequency: parseInt(document.getElementById('cut-frequency').value) * 86400,
        issuanceCutPercent: parseInt(parseFloat(document.getElementById('issuance-cut').value) * 100),
        cashOutTaxRate: parseInt(document.getElementById('cash-out-tax').value) * 100
      };

      showStatus('info', 'Revnet deployment configuration ready');
      console.log('Stage config:', stageConfig);
      console.log('REVDeployer:', revDeployer);
      alert('See /jb-project and /jb-ruleset for complete Revnet deployment scripts.');
    };

    function showStatus(type, msg) {
      const el = document.getElementById('tx-status');
      el.className = `card badge-${type}`;
      el.textContent = msg;
      el.classList.remove('hidden');
    }
  </script>
</body>
</html>
```

## V5 Contract Addresses

Load from shared chain config:

```javascript
import { loadChainConfig } from '/shared/wallet-utils.js';

const config = await loadChainConfig();

// V5.1 addresses (new projects)
const controller = config.chains[1].contracts.JBController;
const terminal = config.chains[1].contracts.JBMultiTerminal;

// V5.0 addresses (revnets only)
const revDeployer = config.chains[1].contractsV5.REVDeployer;
```

## Related Skills

- `/jb-project` - Project configuration details
- `/jb-ruleset` - Ruleset parameters
- `/jb-interact-ui` - UIs for interacting with existing projects
- `/jb-omnichain-ui` - Multi-chain deployments
