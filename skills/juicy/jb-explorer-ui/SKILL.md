---
name: jb-explorer-ui
description: Etherscan-like contract explorer for Juicebox projects. Read contract state, write transactions, and decode events.
---

# Juicebox V5 Contract Explorer UI

Build Etherscan-like interfaces for reading contract state, executing transactions, and exploring Juicebox project data.

## Compatibility

- **nana-core-v5**: v5.0.0+
- **Last verified**: 2025-01-16

## Uses Shared Components

This skill uses components from `/shared/`:

| Component | Purpose |
|-----------|---------|
| `styles.css` | Dark theme, buttons, cards, forms |
| `wallet-utils.js` | Wallet connection, chain switching |
| `chain-config.json` | RPC URLs, contract addresses |
| `abis/*.json` | JBController, JBMultiTerminal, JBProjects |

## Features

- **Read Tab**: Call any view/pure function, auto-decode results
- **Write Tab**: Submit transactions with wallet signing
- **Events Tab**: Browse and filter contract events
- **Quick Actions**: One-click project overview, ruleset info

## Template Structure

```
┌─────────────────────────────────────────┐
│ Contract Explorer                       │
├─────────────────────────────────────────┤
│ [Contract Address] [Chain ▼] [Load]     │
├─────────────────────────────────────────┤
│ Wallet: [Connect] / 0x1234...5678       │
├─────────────────────────────────────────┤
│ [Read] [Write] [Events]                 │
├─────────────────────────────────────────┤
│ Quick Actions:                          │
│ [Project Overview] [Current Ruleset]    │
│ [Token Supply] [Pending Reserved]       │
├─────────────────────────────────────────┤
│ Function List                           │
│ ┌────────────────────────────────────┐  │
│ │ functionName(param1, param2)       │  │
│ │ [input] [input] [Query]            │  │
│ │ Result: {...}                      │  │
│ └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Core JavaScript Logic

```javascript
/**
 * Contract Explorer - Core Logic
 * Requires: ethers.js v6, /shared/wallet-utils.js
 */
class ContractExplorer {
  constructor() {
    this.wallet = new JBWallet();
    this.provider = null;
    this.contract = null;
    this.abi = null;
    this.chainId = 1;
  }

  async load(address, chainId) {
    this.chainId = chainId;
    const config = await loadChainConfig();
    this.provider = new ethers.JsonRpcProvider(config.chains[chainId].rpc);

    // Try to match known JB contracts, otherwise fetch from explorer
    this.abi = await this.fetchABI(address, chainId, config);
    this.contract = new ethers.Contract(address, this.abi, this.provider);

    return this.categorize();
  }

  async fetchABI(address, chainId, config) {
    // Check if it's a known JB contract
    const contracts = config.chains[chainId]?.contracts || {};
    for (const [name, addr] of Object.entries(contracts)) {
      if (addr.toLowerCase() === address.toLowerCase()) {
        const res = await fetch(`/shared/abis/${name}.json`);
        if (res.ok) return res.json();
      }
    }

    // Fallback to Etherscan API
    const explorers = {
      1: 'api.etherscan.io', 10: 'api-optimistic.etherscan.io',
      8453: 'api.basescan.org', 42161: 'api.arbiscan.io',
      11155111: 'api-sepolia.etherscan.io'
    };
    const url = `https://${explorers[chainId]}/api?module=contract&action=getabi&address=${address}`;
    const data = await (await fetch(url)).json();
    if (data.status === '1') return JSON.parse(data.result);
    throw new Error('ABI not found');
  }

  categorize() {
    const items = this.abi.filter(x => x.type === 'function');
    return {
      read: items.filter(f => ['view', 'pure'].includes(f.stateMutability)),
      write: items.filter(f => !['view', 'pure'].includes(f.stateMutability)),
      events: this.abi.filter(x => x.type === 'event')
    };
  }

  async call(fnName, args = []) {
    return await this.contract[fnName](...args);
  }

  async send(fnName, args = [], value = '0') {
    if (!this.wallet.signer) await this.wallet.connect(this.chainId);
    const connected = this.contract.connect(this.wallet.signer);
    return await connected[fnName](...args, { value: ethers.parseEther(value) });
  }

  format(result) {
    if (typeof result === 'bigint') return result.toString();
    if (Array.isArray(result)) {
      return result.map(r => this.format(r));
    }
    if (result && typeof result === 'object') {
      const obj = {};
      for (const key of Object.keys(result)) {
        if (isNaN(key)) obj[key] = this.format(result[key]);
      }
      return obj;
    }
    return result;
  }
}

// Quick Actions for JB contracts
const QUICK_ACTIONS = [
  {
    name: 'Project Overview',
    contract: 'JBController',
    fn: 'currentRulesetOf',
    args: (projectId) => [projectId]
  },
  {
    name: 'Token Supply',
    contract: 'JBController',
    fn: 'totalTokenSupplyWithReservedTokensOf',
    args: (projectId) => [projectId]
  },
  {
    name: 'Pending Reserved',
    contract: 'JBController',
    fn: 'pendingReservedTokenBalanceOf',
    args: (projectId) => [projectId]
  }
];
```

## HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Juicebox Contract Explorer</title>
  <script src="https://cdn.jsdelivr.net/npm/ethers@6/dist/ethers.umd.min.js"></script>
  <style>
    /* Load from /shared/styles.css or inline the CSS variables and classes */
    :root {
      --jb-yellow: #ffcc00; --bg-primary: #0d0d0d; --bg-secondary: #1a1a1a;
      --bg-tertiary: #2a2a2a; --text-primary: #fff; --text-muted: #888;
      --border-color: #333; --font-mono: monospace;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, sans-serif; background: var(--bg-primary); color: #e0e0e0; padding: 20px; }
    .container { max-width: 1000px; margin: 0 auto; }
    h1 { color: var(--jb-yellow); margin-bottom: 20px; }
    .card { background: var(--bg-secondary); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; }
    input, select { flex: 1; min-width: 150px; padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 8px; color: #fff; }
    button { padding: 12px 20px; background: var(--jb-yellow); color: #000; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    button:hover { background: #e6b800; }
    button.secondary { background: var(--bg-tertiary); color: #fff; border: 1px solid var(--border-color); }
    .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
    .tab { padding: 10px 20px; background: transparent; border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-muted); cursor: pointer; }
    .tab.active { background: var(--jb-yellow); color: #000; border-color: var(--jb-yellow); }
    .fn-card { background: var(--bg-tertiary); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .fn-name { font-family: var(--font-mono); font-weight: 600; margin-bottom: 12px; }
    .fn-inputs { margin-bottom: 12px; }
    .fn-inputs input { margin-bottom: 8px; }
    .result { background: var(--bg-primary); border-radius: 6px; padding: 12px; margin-top: 12px; font-family: var(--font-mono); font-size: 13px; white-space: pre-wrap; word-break: break-all; }
    .quick-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
    .quick-btn { padding: 8px 16px; font-size: 13px; }
    .label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
    .loading { text-align: center; padding: 20px; color: var(--text-muted); }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
    .badge.success { background: rgba(0,255,136,0.2); color: #0f8; }
    .badge.error { background: rgba(255,68,68,0.2); color: #f44; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Contract Explorer</h1>

    <div class="card">
      <div class="row">
        <input type="text" id="address" placeholder="Contract address (0x...)">
        <select id="chain">
          <option value="1">Ethereum</option>
          <option value="10">Optimism</option>
          <option value="8453">Base</option>
          <option value="42161">Arbitrum</option>
          <option value="11155111">Sepolia</option>
        </select>
        <button onclick="loadContract()">Load Contract</button>
      </div>
    </div>

    <div class="card" id="walletSection" style="display:none;">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <span id="walletStatus">Not connected</span>
        <button class="secondary" id="connectBtn" onclick="connectWallet()">Connect Wallet</button>
      </div>
    </div>

    <div id="quickActions" class="quick-actions" style="display:none;"></div>

    <div class="tabs" id="tabs" style="display:none;">
      <button class="tab active" onclick="showTab('read')">Read</button>
      <button class="tab" onclick="showTab('write')">Write</button>
      <button class="tab" onclick="showTab('events')">Events</button>
    </div>

    <div id="content"></div>
  </div>

  <script>
    let explorer = null;
    let functions = { read: [], write: [], events: [] };
    let currentTab = 'read';

    async function loadContract() {
      const address = document.getElementById('address').value;
      const chainId = parseInt(document.getElementById('chain').value);
      if (!address) return alert('Enter a contract address');

      document.getElementById('content').innerHTML = '<div class="loading">Loading contract...</div>';

      try {
        explorer = new ContractExplorer();
        functions = await explorer.load(address, chainId);

        document.getElementById('walletSection').style.display = 'block';
        document.getElementById('tabs').style.display = 'flex';
        renderQuickActions();
        showTab('read');
      } catch (e) {
        document.getElementById('content').innerHTML = `<div class="badge error">${e.message}</div>`;
      }
    }

    function renderQuickActions() {
      const el = document.getElementById('quickActions');
      el.style.display = 'flex';
      el.innerHTML = `
        <span style="color:#888;margin-right:8px;">Quick:</span>
        <input type="number" id="quickProjectId" placeholder="Project ID" style="width:120px;padding:8px;">
        ${QUICK_ACTIONS.map(a => `<button class="secondary quick-btn" onclick="runQuickAction('${a.name}')">${a.name}</button>`).join('')}
      `;
    }

    async function runQuickAction(name) {
      const action = QUICK_ACTIONS.find(a => a.name === name);
      const projectId = document.getElementById('quickProjectId').value;
      if (!projectId) return alert('Enter a project ID');

      const config = await loadChainConfig();
      const addr = config.chains[explorer.chainId].contracts[action.contract];
      const tempExplorer = new ContractExplorer();
      await tempExplorer.load(addr, explorer.chainId);

      try {
        const result = await tempExplorer.call(action.fn, action.args(projectId));
        alert(JSON.stringify(tempExplorer.format(result), null, 2));
      } catch (e) {
        alert('Error: ' + e.message);
      }
    }

    function showTab(tab) {
      currentTab = tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelector(`.tab:nth-child(${tab === 'read' ? 1 : tab === 'write' ? 2 : 3})`).classList.add('active');
      renderFunctions();
    }

    function renderFunctions() {
      const list = currentTab === 'events' ? functions.events : functions[currentTab];
      const content = document.getElementById('content');

      if (currentTab === 'events') {
        content.innerHTML = list.map(e => `
          <div class="fn-card">
            <div class="fn-name">${e.name}</div>
            <div style="color:#888;font-size:13px;">${e.inputs?.map(i => `${i.type} ${i.name}`).join(', ') || 'No parameters'}</div>
          </div>
        `).join('') || '<div class="loading">No events found</div>';
        return;
      }

      content.innerHTML = list.map((fn, idx) => `
        <div class="fn-card" id="fn-${idx}">
          <div class="fn-name">${fn.name}(${fn.inputs?.map(i => i.type).join(', ') || ''})</div>
          ${fn.inputs?.length ? `<div class="fn-inputs">
            ${fn.inputs.map((inp, i) => `
              <div class="label">${inp.name || 'param' + i} (${inp.type})</div>
              <input type="text" data-fn="${idx}" data-param="${i}" placeholder="${inp.type}">
            `).join('')}
          </div>` : ''}
          ${currentTab === 'write' && fn.stateMutability === 'payable' ? `
            <div class="label">ETH Value</div>
            <input type="text" data-fn="${idx}" data-value="true" placeholder="0.0">
          ` : ''}
          <button ${currentTab === 'write' ? '' : 'class="secondary"'} onclick="callFn(${idx})">
            ${currentTab === 'write' ? 'Write' : 'Query'}
          </button>
          <div class="result" id="result-${idx}" style="display:none;"></div>
        </div>
      `).join('') || '<div class="loading">No functions found</div>';
    }

    async function callFn(idx) {
      const fn = functions[currentTab][idx];
      const inputs = [...document.querySelectorAll(`[data-fn="${idx}"][data-param]`)].map(el => el.value);
      const valueEl = document.querySelector(`[data-fn="${idx}"][data-value]`);
      const value = valueEl?.value || '0';
      const resultEl = document.getElementById(`result-${idx}`);

      resultEl.style.display = 'block';
      resultEl.textContent = 'Loading...';

      try {
        if (currentTab === 'write') {
          const tx = await explorer.send(fn.name, inputs, value);
          resultEl.innerHTML = `<span class="badge success">TX: ${tx.hash}</span>`;
          await tx.wait();
          resultEl.innerHTML += `<br><span class="badge success">Confirmed!</span>`;
        } else {
          const result = await explorer.call(fn.name, inputs);
          resultEl.textContent = JSON.stringify(explorer.format(result), null, 2);
        }
      } catch (e) {
        resultEl.innerHTML = `<span class="badge error">${e.message}</span>`;
      }
    }

    async function connectWallet() {
      try {
        await explorer.wallet.connect(explorer.chainId);
        document.getElementById('walletStatus').textContent = `Connected: ${explorer.wallet.address.slice(0,6)}...${explorer.wallet.address.slice(-4)}`;
        document.getElementById('connectBtn').textContent = 'Connected';
      } catch (e) {
        alert(e.message);
      }
    }

    // Inline ContractExplorer and loadChainConfig from above
    class ContractExplorer {
      constructor() { this.wallet = { signer: null, address: null, connect: async (chainId) => {
        if (!window.ethereum) throw new Error('No wallet found');
        const provider = new ethers.BrowserProvider(window.ethereum);
        await provider.send('eth_requestAccounts', []);
        try { await window.ethereum.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: '0x' + chainId.toString(16) }] }); } catch(e) {}
        this.signer = await provider.getSigner();
        this.address = await this.signer.getAddress();
      }}; this.provider = null; this.contract = null; this.abi = null; this.chainId = 1; }
      async load(address, chainId) {
        this.chainId = chainId;
        const config = await loadChainConfig();
        this.provider = new ethers.JsonRpcProvider(config.chains[chainId].rpc);
        this.abi = await this.fetchABI(address, chainId, config);
        this.contract = new ethers.Contract(address, this.abi, this.provider);
        return this.categorize();
      }
      async fetchABI(address, chainId, config) {
        const explorers = { 1: 'api.etherscan.io', 10: 'api-optimistic.etherscan.io', 8453: 'api.basescan.org', 42161: 'api.arbiscan.io', 11155111: 'api-sepolia.etherscan.io' };
        const url = `https://${explorers[chainId]}/api?module=contract&action=getabi&address=${address}`;
        const data = await (await fetch(url)).json();
        if (data.status === '1') return JSON.parse(data.result);
        throw new Error('ABI not found - contract may not be verified');
      }
      categorize() {
        const items = this.abi.filter(x => x.type === 'function');
        return { read: items.filter(f => ['view', 'pure'].includes(f.stateMutability)), write: items.filter(f => !['view', 'pure'].includes(f.stateMutability)), events: this.abi.filter(x => x.type === 'event') };
      }
      async call(fnName, args = []) { return await this.contract[fnName](...args); }
      async send(fnName, args = [], value = '0') {
        if (!this.wallet.signer) await this.wallet.connect(this.chainId);
        const connected = this.contract.connect(this.wallet.signer);
        const opts = value !== '0' ? { value: ethers.parseEther(value) } : {};
        return await connected[fnName](...args, opts);
      }
      format(result) {
        if (typeof result === 'bigint') return result.toString();
        if (Array.isArray(result)) return result.map(r => this.format(r));
        if (result && typeof result === 'object') { const obj = {}; for (const k of Object.keys(result)) if (isNaN(k)) obj[k] = this.format(result[k]); return obj; }
        return result;
      }
    }

    async function loadChainConfig() {
      return { chains: {
        1: { rpc: 'https://eth.llamarpc.com', contracts: { JBController: '0x0Ae7403b3C3B4C5222bBbE664bdD8600C593b23e' }},
        10: { rpc: 'https://optimism.llamarpc.com', contracts: { JBController: '0x0Ae7403b3C3B4C5222bBbE664bdD8600C593b23e' }},
        8453: { rpc: 'https://base.llamarpc.com', contracts: { JBController: '0x0Ae7403b3C3B4C5222bBbE664bdD8600C593b23e' }},
        42161: { rpc: 'https://arbitrum.llamarpc.com', contracts: { JBController: '0x0Ae7403b3C3B4C5222bBbE664bdD8600C593b23e' }},
        11155111: { rpc: 'https://sepolia.drpc.org', contracts: { JBController: '0x0Ae7403b3C3B4C5222bBbE664bdD8600C593b23e' }}
      }};
    }

    const QUICK_ACTIONS = [
      { name: 'Project Overview', contract: 'JBController', fn: 'currentRulesetOf', args: (p) => [p] },
      { name: 'Token Supply', contract: 'JBController', fn: 'totalTokenSupplyWithReservedTokensOf', args: (p) => [p] },
      { name: 'Pending Reserved', contract: 'JBController', fn: 'pendingReservedTokenBalanceOf', args: (p) => [p] }
    ];
  </script>
</body>
</html>
```

## Customization Points

| What | Where |
|------|-------|
| Add quick actions | Extend `QUICK_ACTIONS` array |
| Change styling | Override CSS variables in `:root` |
| Add ABI sources | Modify `fetchABI()` method |
| Custom result formatting | Extend `format()` method |

## Example Prompts

- "Create an explorer for JBController on Optimism"
- "Build a read-only explorer (no write tab)"
- "Add a quick action to check project splits"

## See Also

- `/jb-event-explorer-ui` - Event-focused browsing
- `/jb-hook-deploy-ui` - Deploy custom hooks
- `/jb-ruleset-timeline-ui` - Ruleset history visualization
