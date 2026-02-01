---
name: jb-interact-ui
description: Generate minimal frontends for interacting with existing Juicebox V5 projects. Pay, cash out, claim tokens, view project state - all in standalone HTML files.
---

# Juicebox V5 Interaction UI Generator

Generate simple frontends for interacting with existing Juicebox projects using viem and shared styles. Pay into treasuries, cash out tokens, view project state - no build tools required.

## Philosophy

> **Let users interact with Juicebox projects without touching a command line.**

These UIs are for:
- Paying into a project treasury
- Cashing out tokens for ETH
- Viewing project configuration and state
- Claiming ERC-20 tokens from credits

## Template: Project Payment UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pay Project</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 480px; margin: 0 auto; }
    .input-suffix { position: relative; }
    .input-suffix input { padding-right: 3rem; }
    .input-suffix span { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-75%); color: var(--text-muted); }
    .receive-preview { background: var(--bg-primary); border-radius: 4px; padding: 0.75rem; margin: 0.75rem 0; text-align: center; }
    .receive-amount { font-size: 1.25rem; font-weight: 600; }
    .receive-label { font-size: 0.75rem; color: var(--text-muted); }
    .subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <h1>Pay Project #<span id="project-id">1</span></h1>
  <p class="subtitle">Contribute ETH and receive tokens</p>

  <div class="card">
    <button id="connect-btn" class="btn" onclick="connectWallet()">Connect Wallet</button>
    <div id="wallet-status" class="hidden">
      <div class="stat-row"><span class="stat-label">Connected</span><span class="stat-value" id="wallet-address"></span></div>
      <div class="stat-row"><span class="stat-label">Balance</span><span class="stat-value" id="wallet-balance"></span></div>
    </div>
  </div>

  <div class="card" id="project-stats">
    <div class="stat-row"><span class="stat-label">Treasury Balance</span><span class="stat-value" id="treasury-balance">-</span></div>
    <div class="stat-row"><span class="stat-label">Token Supply</span><span class="stat-value" id="token-supply">-</span></div>
    <div class="stat-row"><span class="stat-label">Tokens per ETH</span><span class="stat-value" id="tokens-per-eth">-</span></div>
  </div>

  <div class="card">
    <label>Amount to Pay</label>
    <div class="input-suffix">
      <input type="number" id="pay-amount" placeholder="0.0" step="0.001" min="0" oninput="updateReceivePreview()">
      <span>ETH</span>
    </div>
    <div class="receive-preview">
      <div class="receive-amount" id="receive-amount">0</div>
      <div class="receive-label">tokens you'll receive</div>
    </div>
    <label>Memo (optional)</label>
    <input type="text" id="memo" placeholder="Thanks for building!">
    <button id="pay-btn" class="btn" onclick="pay()" disabled>Pay Project</button>
  </div>

  <div id="tx-status" class="card hidden">
    <span id="tx-state"></span>
    <a id="tx-link" href="#" target="_blank" class="hidden">View transaction</a>
  </div>

  <script type="module">
    import { createPublicClient, createWalletClient, http, custom, formatEther, parseEther, getContract } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    // Configuration
    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;

    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };
    const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe';

    const TERMINAL_ABI = [
      { name: 'pay', type: 'function', stateMutability: 'payable',
        inputs: [
          { name: 'projectId', type: 'uint256' }, { name: 'token', type: 'address' },
          { name: 'amount', type: 'uint256' }, { name: 'beneficiary', type: 'address' },
          { name: 'minReturnedTokens', type: 'uint256' }, { name: 'memo', type: 'string' },
          { name: 'metadata', type: 'bytes' }
        ],
        outputs: [{ type: 'uint256' }]
      }
    ];

    let publicClient, walletClient, address, tokensPerEth = 0n;

    document.getElementById('project-id').textContent = PROJECT_ID.toString();

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install MetaMask'); return; }

      const chain = CHAINS[CHAIN_ID];
      const rpc = CHAIN_CONFIGS[CHAIN_ID]?.rpc || chain.rpcUrls.default.http[0];

      publicClient = createPublicClient({ chain, transport: http(rpc) });
      walletClient = createWalletClient({ chain, transport: custom(window.ethereum) });

      const [addr] = await walletClient.requestAddresses();
      address = addr;

      const chainId = await walletClient.getChainId();
      if (chainId !== CHAIN_ID) {
        try { await walletClient.switchChain({ id: CHAIN_ID }); }
        catch { alert(`Please switch to the correct network (Chain ID: ${CHAIN_ID})`); return; }
      }

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      const balance = await publicClient.getBalance({ address });
      document.getElementById('wallet-balance').textContent = `${parseFloat(formatEther(balance)).toFixed(4)} ETH`;
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');
      document.getElementById('pay-btn').disabled = false;

      await loadProjectStats();
    };

    async function loadProjectStats() {
      tokensPerEth = parseEther('1000000');
      document.getElementById('treasury-balance').textContent = '10.5 ETH';
      document.getElementById('token-supply').textContent = '10,500,000';
      document.getElementById('tokens-per-eth').textContent = '1,000,000';
    }

    window.updateReceivePreview = function() {
      const amount = document.getElementById('pay-amount').value || '0';
      if (tokensPerEth > 0n) {
        const receive = parseFloat(amount) * parseFloat(formatEther(tokensPerEth));
        document.getElementById('receive-amount').textContent = receive.toLocaleString(undefined, { maximumFractionDigits: 0 });
      }
    };

    window.pay = async function() {
      const amount = document.getElementById('pay-amount').value;
      const memo = document.getElementById('memo').value || '';
      if (!amount || parseFloat(amount) <= 0) { alert('Enter an amount to pay'); return; }

      const terminal = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBMultiTerminal;
      const value = parseEther(amount);

      showTxPending('Please confirm in wallet...');

      try {
        const hash = await walletClient.writeContract({
          address: terminal,
          abi: TERMINAL_ABI,
          functionName: 'pay',
          args: [PROJECT_ID, NATIVE_TOKEN, value, address, 0n, memo, '0x'],
          value,
          account: address
        });

        showTxSent(hash);
        await publicClient.waitForTransactionReceipt({ hash });
        showTxConfirmed();
      } catch (error) {
        showTxError(error);
      }
    };

    function showTxPending(msg) {
      document.getElementById('tx-status').classList.remove('hidden');
      document.getElementById('tx-state').textContent = msg;
      document.getElementById('tx-link').classList.add('hidden');
    }
    function showTxSent(hash) {
      document.getElementById('tx-state').textContent = 'Transaction sent...';
      const link = document.getElementById('tx-link');
      link.href = getTxUrl(CHAIN_ID, hash);
      link.classList.remove('hidden');
    }
    function showTxConfirmed() { document.getElementById('tx-state').textContent = 'Payment successful!'; }
    function showTxError(error) { document.getElementById('tx-state').textContent = error.shortMessage || error.message; }
  </script>
</body>
</html>
```

## Template: Cash Out UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cash Out Tokens</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 480px; margin: 0 auto; }
    .input-suffix { position: relative; }
    .input-suffix input { padding-right: 4rem; }
    .input-suffix span { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-75%); color: var(--text-muted); }
    .receive-preview { background: var(--bg-primary); border-radius: 4px; padding: 0.75rem; margin: 0.75rem 0; text-align: center; }
    .receive-amount { font-size: 1.25rem; font-weight: 600; }
    .receive-label { font-size: 0.75rem; color: var(--text-muted); }
    .subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
    .warning { border-color: var(--error) !important; }
    .warning p { font-size: 0.875rem; color: var(--text-muted); }
  </style>
</head>
<body>
  <h1>Cash Out</h1>
  <p class="subtitle">Burn tokens to reclaim ETH from treasury</p>

  <div class="card">
    <button id="connect-btn" class="btn" onclick="connectWallet()">Connect Wallet</button>
    <div id="wallet-status" class="hidden">
      <div class="stat-row"><span class="stat-label">Your Token Balance</span><span class="stat-value" id="token-balance">-</span></div>
    </div>
  </div>

  <div class="card">
    <label>Tokens to Cash Out</label>
    <div class="input-suffix">
      <input type="number" id="cash-out-amount" placeholder="0" oninput="updateCashOutPreview()">
      <span>tokens</span>
    </div>
    <button class="btn btn-secondary" onclick="setMax()" style="margin-bottom: 0.75rem;">Max</button>
    <div class="receive-preview">
      <div class="receive-amount" id="reclaim-amount">0</div>
      <div class="receive-label">ETH you'll receive</div>
    </div>
    <button id="cashout-btn" class="btn" onclick="cashOut()" disabled>Cash Out</button>
  </div>

  <div class="card warning">
    <p>Cash outs burn your tokens permanently. You'll receive your proportional share of the treasury surplus.</p>
  </div>

  <div id="tx-status" class="card hidden"></div>

  <script type="module">
    import { createPublicClient, createWalletClient, http, custom, formatEther, parseEther } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;
    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };
    const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe';

    const TERMINAL_ABI = [
      { name: 'cashOutTokensOf', type: 'function', stateMutability: 'nonpayable',
        inputs: [
          { name: 'holder', type: 'address' }, { name: 'projectId', type: 'uint256' },
          { name: 'cashOutCount', type: 'uint256' }, { name: 'tokenToReclaim', type: 'address' },
          { name: 'minTokensReclaimed', type: 'uint256' }, { name: 'beneficiary', type: 'address' },
          { name: 'metadata', type: 'bytes' }
        ],
        outputs: [{ type: 'uint256' }]
      }
    ];

    let publicClient, walletClient, address, tokenBalance = 0n;

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install MetaMask'); return; }

      const chain = CHAINS[CHAIN_ID];
      publicClient = createPublicClient({ chain, transport: http(CHAIN_CONFIGS[CHAIN_ID]?.rpc) });
      walletClient = createWalletClient({ chain, transport: custom(window.ethereum) });

      const [addr] = await walletClient.requestAddresses();
      address = addr;

      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');
      await loadTokenBalance();
    };

    async function loadTokenBalance() {
      tokenBalance = parseEther('1000000');
      document.getElementById('token-balance').textContent = parseInt(formatEther(tokenBalance)).toLocaleString() + ' tokens';
      document.getElementById('cashout-btn').disabled = false;
    }

    window.setMax = function() {
      document.getElementById('cash-out-amount').value = parseInt(formatEther(tokenBalance));
      updateCashOutPreview();
    };

    window.updateCashOutPreview = function() {
      const amount = document.getElementById('cash-out-amount').value || '0';
      const reclaim = parseFloat(amount) * 0.00001;
      document.getElementById('reclaim-amount').textContent = reclaim.toFixed(4) + ' ETH';
    };

    window.cashOut = async function() {
      const amount = document.getElementById('cash-out-amount').value;
      const terminal = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBMultiTerminal;

      document.getElementById('tx-status').classList.remove('hidden');
      document.getElementById('tx-status').textContent = 'Please confirm in wallet...';

      try {
        const hash = await walletClient.writeContract({
          address: terminal,
          abi: TERMINAL_ABI,
          functionName: 'cashOutTokensOf',
          args: [address, PROJECT_ID, parseEther(amount), NATIVE_TOKEN, 0n, address, '0x'],
          account: address
        });

        document.getElementById('tx-status').innerHTML = `Transaction sent... <a href="${getTxUrl(CHAIN_ID, hash)}" target="_blank">View</a>`;
        await publicClient.waitForTransactionReceipt({ hash });
        document.getElementById('tx-status').textContent = 'Cash out successful!';
      } catch (error) {
        document.getElementById('tx-status').textContent = error.shortMessage || error.message;
      }
    };
  </script>
</body>
</html>
```

## Template: NFT Mint UI (721 Hook)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mint NFT</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 640px; margin: 0 auto; }
    .tiers-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
    .tier-card { cursor: pointer; transition: border-color 0.2s; }
    .tier-card:hover, .tier-card.selected { border-color: var(--jb-yellow); }
    .tier-price { font-size: 1.25rem; font-weight: 600; color: var(--jb-yellow); }
    .tier-remaining { font-size: 0.875rem; color: var(--text-muted); }
  </style>
</head>
<body>
  <h1>Mint NFT</h1>

  <div class="card">
    <button id="connect-btn" class="btn" onclick="connectWallet()">Connect Wallet</button>
    <div id="wallet-status" class="hidden">
      <div class="stat-row"><span class="stat-label">Connected</span><span class="stat-value" id="wallet-address"></span></div>
    </div>
  </div>

  <div id="tiers-container" class="tiers-grid"></div>

  <div class="card hidden" id="selected-tier">
    <h3 id="tier-name"></h3>
    <div class="stat-row"><span class="stat-label">Price</span><span class="stat-value tier-price" id="tier-price"></span></div>
    <div class="stat-row"><span class="stat-label">Remaining</span><span class="stat-value" id="tier-remaining"></span></div>
    <button class="btn" onclick="mint()">Mint for <span id="mint-price"></span> ETH</button>
  </div>

  <div id="tx-status" class="card hidden"></div>

  <script type="module">
    import { createPublicClient, createWalletClient, http, custom, parseEther, encodeAbiParameters } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;
    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };
    const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe';

    const TERMINAL_ABI = [
      { name: 'pay', type: 'function', stateMutability: 'payable',
        inputs: [
          { name: 'projectId', type: 'uint256' }, { name: 'token', type: 'address' },
          { name: 'amount', type: 'uint256' }, { name: 'beneficiary', type: 'address' },
          { name: 'minReturnedTokens', type: 'uint256' }, { name: 'memo', type: 'string' },
          { name: 'metadata', type: 'bytes' }
        ],
        outputs: [{ type: 'uint256' }]
      }
    ];

    const TIERS = [
      { id: 1, name: 'Common', price: '0.01', remaining: 100 },
      { id: 2, name: 'Rare', price: '0.1', remaining: 50 },
      { id: 3, name: 'Legendary', price: '1.0', remaining: 10 }
    ];

    let publicClient, walletClient, address, selectedTier = null;

    function renderTiers() {
      document.getElementById('tiers-container').innerHTML = TIERS.map(tier => `
        <div class="card tier-card" data-id="${tier.id}" onclick="selectTier(${tier.id})">
          <h3>${tier.name}</h3>
          <div class="tier-price">${tier.price} ETH</div>
          <div class="tier-remaining">${tier.remaining} left</div>
        </div>
      `).join('');
    }

    window.selectTier = function(tierId) {
      document.querySelectorAll('.tier-card').forEach(c => c.classList.remove('selected'));
      document.querySelector(`[data-id="${tierId}"]`).classList.add('selected');

      selectedTier = TIERS.find(t => t.id === tierId);
      document.getElementById('tier-name').textContent = selectedTier.name;
      document.getElementById('tier-price').textContent = selectedTier.price + ' ETH';
      document.getElementById('tier-remaining').textContent = selectedTier.remaining;
      document.getElementById('mint-price').textContent = selectedTier.price;
      document.getElementById('selected-tier').classList.remove('hidden');
    };

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install MetaMask'); return; }

      const chain = CHAINS[CHAIN_ID];
      publicClient = createPublicClient({ chain, transport: http(CHAIN_CONFIGS[CHAIN_ID]?.rpc) });
      walletClient = createWalletClient({ chain, transport: custom(window.ethereum) });

      const [addr] = await walletClient.requestAddresses();
      address = addr;

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');
    };

    window.mint = async function() {
      if (!selectedTier || !address) return;

      const metadata = encodeAbiParameters(
        [{ type: 'bytes4' }, { type: 'bool' }, { type: 'uint16[]' }],
        ['0x00000000', true, [selectedTier.id]]
      );

      const terminal = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBMultiTerminal;
      const value = parseEther(selectedTier.price);

      document.getElementById('tx-status').classList.remove('hidden');
      document.getElementById('tx-status').textContent = 'Please confirm in wallet...';

      try {
        const hash = await walletClient.writeContract({
          address: terminal,
          abi: TERMINAL_ABI,
          functionName: 'pay',
          args: [PROJECT_ID, NATIVE_TOKEN, value, address, 0n, '', metadata],
          value,
          account: address
        });

        document.getElementById('tx-status').innerHTML = `Transaction sent... <a href="${getTxUrl(CHAIN_ID, hash)}" target="_blank">View</a>`;
        await publicClient.waitForTransactionReceipt({ hash });
        document.getElementById('tx-status').textContent = 'NFT minted!';
      } catch (error) {
        document.getElementById('tx-status').textContent = error.shortMessage || error.message;
      }
    };

    renderTiers();
  </script>
</body>
</html>
```

## Template: Project Admin UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Admin</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 640px; margin: 0 auto; }
    .subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
    h2 { font-size: 1rem; color: var(--text-muted); margin: 1rem 0 0.75rem; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .splits-preview { background: var(--bg-primary); padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.875rem; }
  </style>
</head>
<body>
  <h1>Project #<span id="project-id">1</span> Admin</h1>
  <p class="subtitle">Manage treasury operations</p>

  <div class="card">
    <button id="connect-btn" class="btn" onclick="connectWallet()">Connect Wallet</button>
    <div id="wallet-status" class="hidden">
      <div class="stat-row"><span class="stat-label">Connected</span><span class="stat-value" id="wallet-address"></span></div>
      <div class="stat-row"><span class="stat-label">Owner Status</span><span class="stat-value" id="owner-status">Checking...</span></div>
    </div>
  </div>

  <div class="card" id="treasury-card">
    <h2>Treasury Status</h2>
    <div class="stat-row"><span class="stat-label">Balance</span><span class="stat-value" id="treasury-balance">-</span></div>
    <div class="stat-row"><span class="stat-label">Distributable</span><span class="stat-value" id="distributable">-</span></div>
    <div class="stat-row"><span class="stat-label">Payout Limit</span><span class="stat-value" id="payout-limit">-</span></div>
    <div class="stat-row"><span class="stat-label">Current Cycle</span><span class="stat-value" id="current-cycle">-</span></div>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="showTab('payouts')">Send Payouts</div>
    <div class="tab" onclick="showTab('allowance')">Use Allowance</div>
    <div class="tab" onclick="showTab('reserved')">Reserved</div>
  </div>

  <div id="payouts-tab" class="tab-content active">
    <div class="card">
      <h2>Distribute to Splits</h2>
      <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem;">Send funds to configured split recipients.</p>
      <label>Amount to Distribute (ETH)</label>
      <input type="number" id="payout-amount" placeholder="0.0" step="0.01">
      <button class="btn btn-secondary" onclick="setMaxPayout()" style="margin-bottom: 1rem;">Max Available</button>
      <div class="splits-preview">
        <strong>Split Recipients:</strong>
        <div id="splits-list" style="margin-top: 0.5rem; color: var(--text-muted);">Loading...</div>
      </div>
      <button class="btn" onclick="sendPayouts()">Send Payouts</button>
    </div>
  </div>

  <div id="allowance-tab" class="tab-content">
    <div class="card">
      <h2>Use Surplus Allowance</h2>
      <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem;">Withdraw from surplus (discretionary spending).</p>
      <div class="stat-row"><span class="stat-label">Remaining Allowance</span><span class="stat-value" id="surplus-allowance">-</span></div>
      <label>Amount to Withdraw (ETH)</label>
      <input type="number" id="allowance-amount" placeholder="0.0" step="0.01">
      <label>Beneficiary Address</label>
      <input type="text" id="allowance-beneficiary" placeholder="0x... (defaults to connected wallet)">
      <button class="btn" onclick="useAllowance()">Withdraw from Surplus</button>
    </div>
  </div>

  <div id="reserved-tab" class="tab-content">
    <div class="card">
      <h2>Distribute Reserved Tokens</h2>
      <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem;">Mint and distribute accumulated reserved tokens.</p>
      <div class="stat-row"><span class="stat-label">Pending Reserved Tokens</span><span class="stat-value" id="pending-reserved">-</span></div>
      <button class="btn" onclick="sendReservedTokens()">Distribute Reserved Tokens</button>
    </div>
  </div>

  <div id="tx-status" class="card hidden">
    <span id="tx-state"></span>
    <a id="tx-link" href="#" target="_blank" class="hidden">View transaction</a>
  </div>

  <script type="module">
    import { createPublicClient, createWalletClient, http, custom, formatEther, parseEther } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;
    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };
    const NATIVE_TOKEN = '0x000000000000000000000000000000000000EEEe';

    const TERMINAL_ABI = [
      { name: 'sendPayoutsOf', type: 'function', stateMutability: 'nonpayable',
        inputs: [
          { name: 'projectId', type: 'uint256' }, { name: 'token', type: 'address' },
          { name: 'amount', type: 'uint256' }, { name: 'currency', type: 'uint256' },
          { name: 'minTokensPaidOut', type: 'uint256' }
        ],
        outputs: [{ type: 'uint256' }]
      },
      { name: 'useAllowanceOf', type: 'function', stateMutability: 'nonpayable',
        inputs: [
          { name: 'projectId', type: 'uint256' }, { name: 'token', type: 'address' },
          { name: 'amount', type: 'uint256' }, { name: 'currency', type: 'uint256' },
          { name: 'minTokensPaidOut', type: 'uint256' }, { name: 'beneficiary', type: 'address' },
          { name: 'feeBeneficiary', type: 'address' }, { name: 'memo', type: 'string' }
        ],
        outputs: [{ type: 'uint256' }]
      }
    ];

    const CONTROLLER_ABI = [
      { name: 'sendReservedTokensToSplitsOf', type: 'function', stateMutability: 'nonpayable',
        inputs: [{ name: 'projectId', type: 'uint256' }],
        outputs: [{ type: 'uint256' }]
      }
    ];

    const PROJECTS_ABI = [
      { name: 'ownerOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'tokenId', type: 'uint256' }],
        outputs: [{ type: 'address' }]
      }
    ];

    let publicClient, walletClient, address;

    document.getElementById('project-id').textContent = PROJECT_ID.toString();

    window.showTab = function(tabName) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(`${tabName}-tab`).classList.add('active');
    };

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install MetaMask'); return; }

      const chain = CHAINS[CHAIN_ID];
      publicClient = createPublicClient({ chain, transport: http(CHAIN_CONFIGS[CHAIN_ID]?.rpc) });
      walletClient = createWalletClient({ chain, transport: custom(window.ethereum) });

      const [addr] = await walletClient.requestAddresses();
      address = addr;

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');

      const projects = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBProjects;
      const owner = await publicClient.readContract({ address: projects, abi: PROJECTS_ABI, functionName: 'ownerOf', args: [PROJECT_ID] });
      const isOwner = owner.toLowerCase() === address.toLowerCase();
      document.getElementById('owner-status').textContent = isOwner ? 'Owner' : 'Not Owner';

      await loadTreasuryStats();
    };

    async function loadTreasuryStats() {
      document.getElementById('treasury-balance').textContent = '10.5 ETH';
      document.getElementById('distributable').textContent = '8.0 ETH';
      document.getElementById('payout-limit').textContent = '8.0 ETH / cycle';
      document.getElementById('current-cycle').textContent = '3';
      document.getElementById('surplus-allowance').textContent = '2.5 ETH';
      document.getElementById('pending-reserved').textContent = '50,000 tokens';
      document.getElementById('splits-list').innerHTML = '0x1234...5678 (50%), Project #2 (50%)';
    }

    window.setMaxPayout = () => document.getElementById('payout-amount').value = '8.0';

    window.sendPayouts = async function() {
      const amount = document.getElementById('payout-amount').value;
      if (!amount || parseFloat(amount) <= 0) { alert('Enter an amount'); return; }

      const terminal = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBMultiTerminal;
      showTxPending('Please confirm in wallet...');

      try {
        const hash = await walletClient.writeContract({
          address: terminal,
          abi: TERMINAL_ABI,
          functionName: 'sendPayoutsOf',
          args: [PROJECT_ID, NATIVE_TOKEN, parseEther(amount), 0n, 0n],
          account: address
        });
        showTxSent(hash);
        await publicClient.waitForTransactionReceipt({ hash });
        showTxConfirmed();
        await loadTreasuryStats();
      } catch (error) { showTxError(error); }
    };

    window.useAllowance = async function() {
      const amount = document.getElementById('allowance-amount').value;
      const beneficiary = document.getElementById('allowance-beneficiary').value || address;
      if (!amount || parseFloat(amount) <= 0) { alert('Enter an amount'); return; }

      const terminal = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBMultiTerminal;
      showTxPending('Please confirm in wallet...');

      try {
        const hash = await walletClient.writeContract({
          address: terminal,
          abi: TERMINAL_ABI,
          functionName: 'useAllowanceOf',
          args: [PROJECT_ID, NATIVE_TOKEN, parseEther(amount), 0n, 0n, beneficiary, address, 'Surplus allowance withdrawal'],
          account: address
        });
        showTxSent(hash);
        await publicClient.waitForTransactionReceipt({ hash });
        showTxConfirmed();
        await loadTreasuryStats();
      } catch (error) { showTxError(error); }
    };

    window.sendReservedTokens = async function() {
      const controller = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBController;
      showTxPending('Please confirm in wallet...');

      try {
        const hash = await walletClient.writeContract({
          address: controller,
          abi: CONTROLLER_ABI,
          functionName: 'sendReservedTokensToSplitsOf',
          args: [PROJECT_ID],
          account: address
        });
        showTxSent(hash);
        await publicClient.waitForTransactionReceipt({ hash });
        showTxConfirmed();
        await loadTreasuryStats();
      } catch (error) { showTxError(error); }
    };

    function showTxPending(msg) {
      document.getElementById('tx-status').classList.remove('hidden');
      document.getElementById('tx-state').textContent = msg;
      document.getElementById('tx-link').classList.add('hidden');
    }
    function showTxSent(hash) {
      document.getElementById('tx-state').textContent = 'Transaction sent...';
      const link = document.getElementById('tx-link');
      link.href = getTxUrl(CHAIN_ID, hash);
      link.classList.remove('hidden');
    }
    function showTxConfirmed() { document.getElementById('tx-state').textContent = 'Transaction confirmed!'; }
    function showTxError(error) { document.getElementById('tx-state').textContent = error.shortMessage || error.message; }
  </script>
</body>
</html>
```

## Template: Claim Tokens UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claim Tokens</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 480px; margin: 0 auto; }
    .subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
    h2 { font-size: 1rem; color: var(--text-muted); margin-bottom: 1rem; }
    .info { background: var(--bg-primary); padding: 0.75rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem; }
    .warning-card { border-color: var(--accent) !important; }
    .warning-card p { font-size: 0.875rem; }
  </style>
</head>
<body>
  <h1>Claim Tokens</h1>
  <p class="subtitle">Convert credits to ERC-20 tokens</p>

  <div class="card">
    <button id="connect-btn" class="btn" onclick="connectWallet()">Connect Wallet</button>
    <div id="wallet-status" class="hidden">
      <div class="stat-row"><span class="stat-label">Connected</span><span class="stat-value" id="wallet-address"></span></div>
    </div>
  </div>

  <div class="card">
    <h2>Your Balances</h2>
    <div class="stat-row"><span class="stat-label">Credits (unclaimed)</span><span class="stat-value" id="credit-balance">-</span></div>
    <div class="stat-row"><span class="stat-label">ERC-20 Tokens</span><span class="stat-value" id="token-balance">-</span></div>
    <div class="stat-row"><span class="stat-label">Total Balance</span><span class="stat-value" id="total-balance">-</span></div>
  </div>

  <div class="card" id="claim-section">
    <div class="info">Credits are stored in the Juicebox protocol. Claiming converts them to ERC-20 tokens in your wallet.</div>
    <label>Amount to Claim</label>
    <input type="number" id="claim-amount" placeholder="0">
    <button class="btn btn-secondary" onclick="setMaxClaim()">Claim All</button>
    <button id="claim-btn" class="btn" onclick="claimTokens()" disabled>Claim Tokens</button>
  </div>

  <div class="card warning-card hidden" id="no-token-warning">
    <p>This project hasn't deployed an ERC-20 token yet. Credits cannot be claimed until the project owner deploys one.</p>
  </div>

  <div id="tx-status" class="card hidden">
    <span id="tx-state"></span>
    <a id="tx-link" href="#" target="_blank" class="hidden">View transaction</a>
  </div>

  <script type="module">
    import { createPublicClient, createWalletClient, http, custom, formatEther, parseEther, zeroAddress } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getTxUrl } from '/shared/wallet-utils.js';

    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;
    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };

    const CONTROLLER_ABI = [
      { name: 'claimTokensFor', type: 'function', stateMutability: 'nonpayable',
        inputs: [
          { name: 'holder', type: 'address' }, { name: 'projectId', type: 'uint256' },
          { name: 'tokenCount', type: 'uint256' }, { name: 'beneficiary', type: 'address' }
        ],
        outputs: []
      }
    ];

    const TOKENS_ABI = [
      { name: 'creditBalanceOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'holder', type: 'address' }, { name: 'projectId', type: 'uint256' }],
        outputs: [{ type: 'uint256' }]
      },
      { name: 'tokenOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'projectId', type: 'uint256' }],
        outputs: [{ type: 'address' }]
      },
      { name: 'totalBalanceOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'holder', type: 'address' }, { name: 'projectId', type: 'uint256' }],
        outputs: [{ type: 'uint256' }]
      }
    ];

    let publicClient, walletClient, address, creditBalance = 0n;

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install MetaMask'); return; }

      const chain = CHAINS[CHAIN_ID];
      publicClient = createPublicClient({ chain, transport: http(CHAIN_CONFIGS[CHAIN_ID]?.rpc) });
      walletClient = createWalletClient({ chain, transport: custom(window.ethereum) });

      const [addr] = await walletClient.requestAddresses();
      address = addr;

      document.getElementById('wallet-address').textContent = truncateAddress(address);
      document.getElementById('wallet-status').classList.remove('hidden');
      document.getElementById('connect-btn').classList.add('hidden');

      await loadBalances();
    };

    async function loadBalances() {
      const tokens = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBTokens;

      const tokenAddr = await publicClient.readContract({ address: tokens, abi: TOKENS_ABI, functionName: 'tokenOf', args: [PROJECT_ID] });
      const hasToken = tokenAddr !== zeroAddress;

      if (!hasToken) {
        document.getElementById('claim-section').classList.add('hidden');
        document.getElementById('no-token-warning').classList.remove('hidden');
      }

      creditBalance = await publicClient.readContract({ address: tokens, abi: TOKENS_ABI, functionName: 'creditBalanceOf', args: [address, PROJECT_ID] });
      const totalBalance = await publicClient.readContract({ address: tokens, abi: TOKENS_ABI, functionName: 'totalBalanceOf', args: [address, PROJECT_ID] });
      const tokenBalance = totalBalance - creditBalance;

      document.getElementById('credit-balance').textContent = parseInt(formatEther(creditBalance)).toLocaleString();
      document.getElementById('token-balance').textContent = parseInt(formatEther(tokenBalance)).toLocaleString();
      document.getElementById('total-balance').textContent = parseInt(formatEther(totalBalance)).toLocaleString();

      if (hasToken && creditBalance > 0n) document.getElementById('claim-btn').disabled = false;
    }

    window.setMaxClaim = () => document.getElementById('claim-amount').value = parseInt(formatEther(creditBalance));

    window.claimTokens = async function() {
      const amount = document.getElementById('claim-amount').value;
      if (!amount || parseInt(amount) <= 0) { alert('Enter an amount'); return; }

      const controller = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBController;
      showTxPending('Please confirm in wallet...');

      try {
        const hash = await walletClient.writeContract({
          address: controller,
          abi: CONTROLLER_ABI,
          functionName: 'claimTokensFor',
          args: [address, PROJECT_ID, parseEther(amount), address],
          account: address
        });
        showTxSent(hash);
        await publicClient.waitForTransactionReceipt({ hash });
        showTxConfirmed();
        await loadBalances();
      } catch (error) { showTxError(error); }
    };

    function showTxPending(msg) {
      document.getElementById('tx-status').classList.remove('hidden');
      document.getElementById('tx-state').textContent = msg;
      document.getElementById('tx-link').classList.add('hidden');
    }
    function showTxSent(hash) {
      document.getElementById('tx-state').textContent = 'Transaction sent...';
      const link = document.getElementById('tx-link');
      link.href = getTxUrl(CHAIN_ID, hash);
      link.classList.remove('hidden');
    }
    function showTxConfirmed() { document.getElementById('tx-state').textContent = 'Tokens claimed!'; }
    function showTxError(error) { document.getElementById('tx-state').textContent = error.shortMessage || error.message; }
  </script>
</body>
</html>
```

## Template: Project Dashboard UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Dashboard</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    body { max-width: 800px; margin: 0 auto; }
    .subtitle { color: var(--text-muted); margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .metric-card { text-align: center; }
    .metric-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .metric-value { font-size: 1.5rem; font-weight: 600; }
    .metric-sub { font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem; }
    h2 { font-size: 1rem; color: var(--text-muted); margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1 id="project-name">Loading...</h1>
  <p class="subtitle">Project #<span id="project-id">1</span></p>

  <div class="grid">
    <div class="card metric-card">
      <div class="metric-label">Treasury Balance</div>
      <div class="metric-value" id="treasury-balance">-</div>
      <div class="metric-sub">ETH</div>
    </div>
    <div class="card metric-card">
      <div class="metric-label">Token Supply</div>
      <div class="metric-value" id="token-supply">-</div>
      <div class="metric-sub">tokens issued</div>
    </div>
    <div class="card metric-card">
      <div class="metric-label">Token Holders</div>
      <div class="metric-value" id="holder-count">-</div>
      <div class="metric-sub">unique addresses</div>
    </div>
    <div class="card metric-card">
      <div class="metric-label">Current Cycle</div>
      <div class="metric-value" id="current-cycle">-</div>
      <div class="metric-sub" id="cycle-end">-</div>
    </div>
  </div>

  <div class="card">
    <h2>Current Ruleset</h2>
    <div class="stat-row"><span class="stat-label">Duration</span><span class="stat-value" id="duration">-</span></div>
    <div class="stat-row"><span class="stat-label">Issuance (tokens/ETH)</span><span class="stat-value" id="weight">-</span></div>
    <div class="stat-row"><span class="stat-label">Reserved Rate</span><span class="stat-value" id="reserved-rate">-</span></div>
    <div class="stat-row"><span class="stat-label">Cash Out Tax Rate</span><span class="stat-value" id="cash-out-tax">-</span></div>
    <div class="stat-row"><span class="stat-label">Payout Limit</span><span class="stat-value" id="payout-limit">-</span></div>
    <div class="stat-row"><span class="stat-label">Data Hook</span><span class="stat-value" id="data-hook">-</span></div>
  </div>

  <div class="card">
    <h2>Project Owner</h2>
    <div class="stat-row">
      <span class="stat-label">Address</span>
      <span class="stat-value"><a id="owner-link" href="#" target="_blank"><span id="owner-address">-</span></a></span>
    </div>
  </div>

  <script type="module">
    import { createPublicClient, http, formatEther, zeroAddress } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress, getAddressUrl } from '/shared/wallet-utils.js';

    const PROJECT_ID = 1n;
    const CHAIN_ID = 1;
    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };

    const CONTROLLER_ABI = [
      { name: 'currentRulesetOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'projectId', type: 'uint256' }],
        outputs: [
          { name: 'ruleset', type: 'tuple', components: [
            { name: 'cycleNumber', type: 'uint256' }, { name: 'id', type: 'uint256' },
            { name: 'basedOnId', type: 'uint256' }, { name: 'start', type: 'uint256' },
            { name: 'duration', type: 'uint256' }, { name: 'weight', type: 'uint256' },
            { name: 'weightCutPercent', type: 'uint256' }, { name: 'approvalHook', type: 'address' },
            { name: 'metadata', type: 'uint256' }
          ]},
          { name: 'metadata', type: 'tuple', components: [
            { name: 'reservedRate', type: 'uint256' }, { name: 'cashOutTaxRate', type: 'uint256' },
            { name: 'baseCurrency', type: 'uint256' }, { name: 'pausePay', type: 'bool' },
            { name: 'pauseCashOut', type: 'bool' }, { name: 'pauseTransfers', type: 'bool' },
            { name: 'allowOwnerMinting', type: 'bool' }, { name: 'allowTerminalMigration', type: 'bool' },
            { name: 'allowSetTerminals', type: 'bool' }, { name: 'allowSetController', type: 'bool' },
            { name: 'allowAddAccountingContexts', type: 'bool' }, { name: 'allowAddPriceFeed', type: 'bool' },
            { name: 'ownerMustSendPayouts', type: 'bool' }, { name: 'holdFees', type: 'bool' },
            { name: 'useTotalSurplusForCashOuts', type: 'bool' }, { name: 'useDataHookForPay', type: 'bool' },
            { name: 'useDataHookForCashOut', type: 'bool' }, { name: 'dataHook', type: 'address' },
            { name: 'metadata', type: 'uint256' }
          ]}
        ]
      },
      { name: 'totalTokenSupplyWithReservedTokensOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'projectId', type: 'uint256' }],
        outputs: [{ type: 'uint256' }]
      }
    ];

    const PROJECTS_ABI = [
      { name: 'ownerOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'tokenId', type: 'uint256' }],
        outputs: [{ type: 'address' }]
      }
    ];

    document.getElementById('project-id').textContent = PROJECT_ID.toString();

    async function loadProjectData() {
      const chain = CHAINS[CHAIN_ID];
      const rpc = CHAIN_CONFIGS[CHAIN_ID]?.rpc || chain.rpcUrls.default.http[0];
      const publicClient = createPublicClient({ chain, transport: http(rpc) });

      const controller = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBController;
      const projects = CHAIN_CONFIGS[CHAIN_ID]?.contracts?.JBProjects;

      try {
        const [rulesetData, totalSupply, owner] = await Promise.all([
          publicClient.readContract({ address: controller, abi: CONTROLLER_ABI, functionName: 'currentRulesetOf', args: [PROJECT_ID] }),
          publicClient.readContract({ address: controller, abi: CONTROLLER_ABI, functionName: 'totalTokenSupplyWithReservedTokensOf', args: [PROJECT_ID] }),
          publicClient.readContract({ address: projects, abi: PROJECTS_ABI, functionName: 'ownerOf', args: [PROJECT_ID] })
        ]);

        const [ruleset, metadata] = rulesetData;

        document.getElementById('project-name').textContent = `Project #${PROJECT_ID}`;
        document.getElementById('token-supply').textContent = parseInt(formatEther(totalSupply)).toLocaleString();
        document.getElementById('current-cycle').textContent = ruleset.cycleNumber.toString();
        document.getElementById('duration').textContent = ruleset.duration > 0 ? `${Number(ruleset.duration) / 86400} days` : 'Indefinite';
        document.getElementById('weight').textContent = parseInt(formatEther(ruleset.weight)).toLocaleString();
        document.getElementById('reserved-rate').textContent = `${Number(metadata.reservedRate) / 100}%`;
        document.getElementById('cash-out-tax').textContent = `${Number(metadata.cashOutTaxRate) / 100}%`;
        document.getElementById('data-hook').textContent = metadata.dataHook === zeroAddress ? 'None' : truncateAddress(metadata.dataHook);
        document.getElementById('owner-address').textContent = truncateAddress(owner);
        document.getElementById('owner-link').href = getAddressUrl(CHAIN_ID, owner);

        document.getElementById('treasury-balance').textContent = '-';
        document.getElementById('holder-count').textContent = '-';
        document.getElementById('payout-limit').textContent = '-';
      } catch (error) {
        console.error('Error loading project data:', error);
        document.getElementById('project-name').textContent = 'Error loading project';
      }
    }

    loadProjectData();
  </script>
</body>
</html>
```

## Generation Guidelines

1. **Project ID as config** - Make it easy to change which project the UI targets
2. **Network switching** - Detect wrong network and prompt user to switch
3. **Real-time previews** - Show expected token amounts before transaction
4. **Error handling** - Catch wallet rejections and contract reverts gracefully
5. **Loading states** - Disable buttons and show spinners during transactions
6. **Read-only mode** - Support viewing data without wallet connection

## Fetching Project Data

To show real project stats, query the contracts:

```javascript
async function getProjectStats(projectId) {
  const controller = CHAIN_CONFIGS[chainId]?.contracts?.JBController;

  const [ruleset, metadata] = await publicClient.readContract({
    address: controller,
    abi: CONTROLLER_ABI,
    functionName: 'currentRulesetOf',
    args: [projectId]
  });

  return {
    weight: ruleset.weight,
    duration: ruleset.duration,
    reservedRate: metadata.reservedRate,
    cashOutTaxRate: metadata.cashOutTaxRate
  };
}
```

## Fetching Data with Bendystraw

Instead of querying contracts directly, use Bendystraw for faster, indexed data:

```javascript
// Bendystraw client (use server-side proxy to hide API key)
async function bendystrawQuery(query, variables = {}) {
  const response = await fetch('/api/bendystraw', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables })
  });
  return (await response.json()).data;
}

// Get project stats
async function getProjectStats(projectId, chainId) {
  return bendystrawQuery(`
    query($projectId: Int!, $chainId: Int!) {
      project(projectId: $projectId, chainId: $chainId) {
        name handle logoUri owner
        balance volume volumeUsd
        tokenSupply token tokenSymbol
        paymentsCount contributorsCount
        trendingScore trendingVolume
      }
    }
  `, { projectId, chainId });
}
```

Contact [@peripheralist](https://x.com/peripheralist) for an API key.

## Related Skills

- `/jb-deploy-ui` - UIs for deploying new projects
- `/jb-omnichain-ui` - Multi-chain UIs with Relayr & Bendystraw
- `/jb-query` - Direct contract queries (when Bendystraw unavailable)
- `/jb-v5-api` - Contract function signatures
