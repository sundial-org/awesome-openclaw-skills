---
name: jb-nft-gallery-ui
description: Interactive gallery for browsing and managing NFTs from Juicebox 721 hooks. Displays tier information, owned NFTs, and minting interfaces.
---

# Juicebox V5 NFT Gallery UI

Interactive gallery for browsing and managing NFTs from Juicebox 721 hooks. Displays tier information, owned NFTs, and minting interfaces.

## Overview

This skill generates vanilla JS/HTML interfaces for:
- Browsing all NFT tiers for a project
- Viewing owned NFTs by wallet
- Minting NFTs from available tiers
- Tier metadata and supply tracking
- NFT transfer functionality

## NFT Gallery UI Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Juicebox NFT Gallery</title>
  <link rel="stylesheet" href="/shared/styles.css">
  <style>
    /* NFT-specific styles */
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }
    .nft-card {
      background: var(--bg-secondary);
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .nft-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .nft-image {
      width: 100%;
      aspect-ratio: 1;
      background: var(--bg-tertiary);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .nft-image img { width: 100%; height: 100%; object-fit: cover; }
    .nft-image .placeholder { font-size: 48px; color: #444; }
    .tier-badge, .supply-badge, .owned-badge {
      position: absolute;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }
    .tier-badge { top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: var(--jb-yellow); }
    .supply-badge { top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: var(--success); }
    .supply-badge.sold-out { color: var(--error); }
    .owned-badge { bottom: 10px; left: 10px; background: var(--success); color: #000; }
    .nft-info { padding: 15px; }
    .nft-name { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 5px; }
    .nft-description {
      font-size: 13px; color: var(--text-muted); margin-bottom: 10px;
      line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2;
      -webkit-box-orient: vertical; overflow: hidden;
    }
    .nft-meta {
      display: flex; justify-content: space-between; align-items: center;
      padding-top: 10px; border-top: 1px solid var(--border-color);
    }
    .nft-price { font-size: 1.1rem; font-weight: 700; color: var(--jb-yellow); }
    .nft-votes { font-size: 12px; color: var(--text-muted); }
    .mint-btn {
      width: 100%; padding: 12px; background: var(--jb-yellow); color: #000;
      border: none; border-radius: 8px; font-weight: 600; cursor: pointer; margin-top: 10px;
    }
    .mint-btn:hover { background: var(--jb-yellow-hover); }
    .mint-btn:disabled { background: var(--bg-tertiary); color: var(--text-muted); cursor: not-allowed; }
    .category-filter { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
    .category-chip {
      padding: 6px 14px; background: var(--bg-tertiary); border-radius: 20px;
      font-size: 13px; cursor: pointer; color: var(--text-muted);
    }
    .category-chip.active { background: var(--jb-yellow); color: #000; }
    .modal {
      display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.9); z-index: 1000; padding: 20px; overflow-y: auto;
    }
    .modal.visible { display: flex; justify-content: center; align-items: flex-start; }
    .modal-content { background: var(--bg-secondary); border-radius: 12px; max-width: 600px; width: 100%; margin-top: 40px; }
    .modal-image { width: 100%; aspect-ratio: 1; background: var(--bg-tertiary); }
    .modal-image img { width: 100%; height: 100%; object-fit: contain; }
    .modal-info { padding: 20px; }
    .modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
    .modal-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
    .close-btn { background: none; border: none; color: var(--text-muted); font-size: 28px; cursor: pointer; }
    .modal-description { color: var(--text-muted); line-height: 1.6; margin-bottom: 20px; }
    .modal-attributes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
    .attribute { background: var(--bg-tertiary); padding: 12px; border-radius: 8px; }
    .attribute-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; }
    .attribute-value { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-top: 4px; }
    .action-buttons { display: flex; gap: 10px; }
    .action-btn { flex: 1; padding: 14px; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
    .action-btn.primary { background: var(--jb-yellow); color: #000; }
    .action-btn.secondary { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); }
  </style>
</head>
<body>
  <div class="container">
    <h1>NFT Gallery</h1>

    <div class="card" style="margin-bottom: 20px;">
      <div class="input-row">
        <input type="text" id="hookAddress" placeholder="721 Hook Address (0x...)">
        <select id="chainSelect">
          <option value="1">Ethereum</option>
          <option value="10">Optimism</option>
          <option value="8453">Base</option>
          <option value="42161">Arbitrum</option>
          <option value="11155111">Sepolia</option>
        </select>
        <button class="btn" onclick="loadGallery()">Load Gallery</button>
      </div>
    </div>

    <div class="card" id="walletSection" style="display: none; margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span id="walletStatus">Not connected</span>
          <span class="code" id="walletAddress" style="margin-left: 10px;"></span>
        </div>
        <button class="btn-secondary" id="connectBtn" onclick="connectWallet()">Connect Wallet</button>
      </div>
    </div>

    <div class="stats" id="statsBar" style="display: none; margin-bottom: 20px;">
      <div class="stat-card">
        <div class="stat-value" id="totalTiers">-</div>
        <div class="stat-label">Total Tiers</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="totalMinted">-</div>
        <div class="stat-label">Total Minted</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="totalSupply">-</div>
        <div class="stat-label">Max Supply</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="floorPrice">-</div>
        <div class="stat-label">Floor Price</div>
      </div>
    </div>

    <div class="tabs" id="tabsContainer" style="display: none;">
      <div class="tab active" data-tab="tiers" onclick="switchTab('tiers')">All Tiers</div>
      <div class="tab" data-tab="owned" onclick="switchTab('owned')">My NFTs</div>
    </div>

    <div class="category-filter" id="categoryFilter"></div>

    <div class="filter-bar" id="filterBar" style="display: none; margin-bottom: 20px;">
      <button class="tab active" data-filter="all" onclick="filterTiers('all')">All</button>
      <button class="tab" data-filter="available" onclick="filterTiers('available')">Available</button>
      <button class="tab" data-filter="sold-out" onclick="filterTiers('sold-out')">Sold Out</button>
    </div>

    <div id="galleryContainer"></div>
  </div>

  <div class="modal" id="nftModal">
    <div class="modal-content">
      <div class="modal-image" id="modalImage"></div>
      <div class="modal-info">
        <div class="modal-header">
          <div>
            <div class="modal-title" id="modalTitle">-</div>
            <span class="code" id="modalTokenId"></span>
          </div>
          <button class="close-btn" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-description" id="modalDescription"></div>
        <div class="modal-attributes" id="modalAttributes"></div>
        <div class="action-buttons" id="modalActions"></div>
      </div>
    </div>
  </div>

  <script type="module">
    import { createPublicClient, http, getContract, formatEther, isAddress, createWalletClient, custom } from 'https://esm.sh/viem';
    import { mainnet, optimism, base, arbitrum, sepolia } from 'https://esm.sh/viem/chains';
    import { CHAIN_CONFIGS, truncateAddress } from '/shared/wallet-utils.js';

    const CHAINS = { 1: mainnet, 10: optimism, 8453: base, 42161: arbitrum, 11155111: sepolia };

    const HOOK_ABI = [
      { name: 'STORE', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] },
      { name: 'PROJECT_ID', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
      { name: 'name', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'string' }] },
      { name: 'symbol', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'string' }] },
      { name: 'tokenURI', type: 'function', stateMutability: 'view', inputs: [{ name: 'tokenId', type: 'uint256' }], outputs: [{ type: 'string' }] },
      { name: 'balanceOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'owner', type: 'address' }], outputs: [{ type: 'uint256' }] },
      { name: 'tokenOfOwnerByIndex', type: 'function', stateMutability: 'view', inputs: [{ name: 'owner', type: 'address' }, { name: 'index', type: 'uint256' }], outputs: [{ type: 'uint256' }] },
      { name: 'ownerOf', type: 'function', stateMutability: 'view', inputs: [{ name: 'tokenId', type: 'uint256' }], outputs: [{ type: 'address' }] },
      { name: 'totalSupply', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
      { name: 'transferFrom', type: 'function', stateMutability: 'nonpayable', inputs: [{ name: 'from', type: 'address' }, { name: 'to', type: 'address' }, { name: 'tokenId', type: 'uint256' }], outputs: [] }
    ];

    const STORE_ABI = [
      { name: 'tiersOf', type: 'function', stateMutability: 'view',
        inputs: [{ name: 'hook', type: 'address' }, { name: 'categories', type: 'uint256[]' }, { name: 'includeResolvedUri', type: 'bool' }, { name: 'startingId', type: 'uint256' }, { name: 'size', type: 'uint256' }],
        outputs: [{ type: 'tuple[]', components: [
          { name: 'id', type: 'uint256' }, { name: 'price', type: 'uint256' }, { name: 'remainingSupply', type: 'uint256' },
          { name: 'initialSupply', type: 'uint256' }, { name: 'votingUnits', type: 'uint256' }, { name: 'reserveFrequency', type: 'uint256' },
          { name: 'reserveBeneficiary', type: 'address' }, { name: 'encodedIPFSUri', type: 'bytes32' }, { name: 'category', type: 'uint256' },
          { name: 'discountPercent', type: 'uint8' }, { name: 'allowOwnerMint', type: 'bool' }, { name: 'transfersPausable', type: 'bool' },
          { name: 'useVotingUnits', type: 'bool' }, { name: 'cannotBeRemoved', type: 'bool' }, { name: 'resolvedUri', type: 'string' }
        ]}]
      },
      { name: 'tierIdOfToken', type: 'function', stateMutability: 'view', inputs: [{ name: 'tokenId', type: 'uint256' }], outputs: [{ type: 'uint256' }] }
    ];

    let publicClient = null;
    let walletClient = null;
    let hookContract = null;
    let storeContract = null;
    let allTiers = [];
    let ownedNFTs = [];
    let currentTab = 'tiers';
    let currentFilter = 'all';
    let selectedCategory = null;
    let hookAddress = '';
    let chainId = 1;
    let connectedAddress = null;

    window.loadGallery = async function() {
      hookAddress = document.getElementById('hookAddress').value;
      chainId = parseInt(document.getElementById('chainSelect').value);

      if (!hookAddress || !isAddress(hookAddress)) {
        alert('Please enter a valid hook address');
        return;
      }

      const container = document.getElementById('galleryContainer');
      container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading NFT collection...</div>';

      const chain = CHAINS[chainId];
      const rpc = CHAIN_CONFIGS[chainId]?.rpc || chain.rpcUrls.default.http[0];

      publicClient = createPublicClient({ chain, transport: http(rpc) });

      try {
        const storeAddr = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'STORE' });

        allTiers = await publicClient.readContract({
          address: storeAddr, abi: STORE_ABI, functionName: 'tiersOf',
          args: [hookAddress, [], true, 0n, 100n]
        });

        let totalMinted = 0, totalMaxSupply = 0, floorPrice = 0n;
        const categories = new Set();

        allTiers.forEach(tier => {
          const minted = Number(tier.initialSupply) - Number(tier.remainingSupply);
          totalMinted += minted;
          totalMaxSupply += Number(tier.initialSupply);
          if (tier.category) categories.add(Number(tier.category));
          if (tier.remainingSupply > 0n && (floorPrice === 0n || tier.price < floorPrice)) {
            floorPrice = tier.price;
          }
        });

        document.getElementById('totalTiers').textContent = allTiers.length;
        document.getElementById('totalMinted').textContent = totalMinted.toLocaleString();
        document.getElementById('totalSupply').textContent = totalMaxSupply.toLocaleString();
        document.getElementById('floorPrice').textContent = floorPrice > 0n ? formatEther(floorPrice) + ' ETH' : 'N/A';

        if (categories.size > 0) {
          let categoryHtml = '<div class="category-chip active" onclick="filterCategory(null)">All</div>';
          [...categories].sort((a, b) => a - b).forEach(cat => {
            categoryHtml += `<div class="category-chip" onclick="filterCategory(${cat})">Category ${cat}</div>`;
          });
          document.getElementById('categoryFilter').innerHTML = categoryHtml;
        }

        document.getElementById('statsBar').style.display = 'grid';
        document.getElementById('tabsContainer').style.display = 'flex';
        document.getElementById('filterBar').style.display = 'flex';
        document.getElementById('walletSection').style.display = 'flex';

        renderTiers();
      } catch (error) {
        console.error(error);
        container.innerHTML = `<div class="empty">Error loading collection: ${error.message}</div>`;
      }
    };

    window.connectWallet = async function() {
      if (!window.ethereum) { alert('Please install a web3 wallet'); return; }

      try {
        const [address] = await window.ethereum.request({ method: 'eth_requestAccounts' });
        connectedAddress = address;

        try {
          await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x' + chainId.toString(16) }]
          });
        } catch (e) { console.log('Chain switch failed', e); }

        walletClient = createWalletClient({ chain: CHAINS[chainId], transport: custom(window.ethereum) });

        document.getElementById('walletStatus').textContent = 'Connected:';
        document.getElementById('walletAddress').textContent = truncateAddress(address);
        document.getElementById('connectBtn').textContent = 'Disconnect';
        document.getElementById('connectBtn').onclick = disconnectWallet;

        await loadOwnedNFTs(address);
      } catch (error) {
        console.error(error);
        alert('Failed to connect wallet');
      }
    };

    window.disconnectWallet = function() {
      walletClient = null;
      connectedAddress = null;
      ownedNFTs = [];
      document.getElementById('walletStatus').textContent = 'Not connected';
      document.getElementById('walletAddress').textContent = '';
      document.getElementById('connectBtn').textContent = 'Connect Wallet';
      document.getElementById('connectBtn').onclick = connectWallet;
      if (currentTab === 'owned') switchTab('tiers'); else renderTiers();
    };

    async function loadOwnedNFTs(ownerAddress) {
      try {
        const storeAddr = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'STORE' });
        const balance = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'balanceOf', args: [ownerAddress] });

        ownedNFTs = [];
        for (let i = 0n; i < balance; i++) {
          const tokenId = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'tokenOfOwnerByIndex', args: [ownerAddress, i] });
          const tierId = await publicClient.readContract({ address: storeAddr, abi: STORE_ABI, functionName: 'tierIdOfToken', args: [tokenId] });
          const tier = allTiers.find(t => t.id.toString() === tierId.toString());

          let metadata = {};
          try {
            const uri = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'tokenURI', args: [tokenId] });
            if (uri) {
              const metadataUrl = uri.startsWith('ipfs://') ? `https://ipfs.io/ipfs/${uri.slice(7)}` : uri;
              const response = await fetch(metadataUrl);
              metadata = await response.json();
            }
          } catch (e) { console.log('Failed to load metadata for token', tokenId.toString()); }

          ownedNFTs.push({ tokenId: tokenId.toString(), tierId: tierId.toString(), tier, metadata });
        }

        if (currentTab === 'owned') renderOwnedNFTs(); else renderTiers();
      } catch (error) { console.error('Failed to load owned NFTs:', error); }
    }

    window.switchTab = function(tab) {
      currentTab = tab;
      document.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
      document.querySelector(`.tabs .tab[data-tab="${tab}"]`).classList.add('active');

      if (tab === 'tiers') {
        document.getElementById('filterBar').style.display = 'flex';
        renderTiers();
      } else {
        document.getElementById('filterBar').style.display = 'none';
        renderOwnedNFTs();
      }
    };

    window.filterTiers = function(filter) {
      currentFilter = filter;
      document.querySelectorAll('.filter-bar .tab').forEach(b => b.classList.remove('active'));
      document.querySelector(`.filter-bar .tab[data-filter="${filter}"]`).classList.add('active');
      renderTiers();
    };

    window.filterCategory = function(category) {
      selectedCategory = category;
      document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
      if (category === null) {
        document.querySelector('.category-chip').classList.add('active');
      } else {
        document.querySelectorAll('.category-chip').forEach(c => {
          if (c.textContent === `Category ${category}`) c.classList.add('active');
        });
      }
      renderTiers();
    };

    function renderTiers() {
      const container = document.getElementById('galleryContainer');
      let filteredTiers = [...allTiers];

      if (selectedCategory !== null) filteredTiers = filteredTiers.filter(t => Number(t.category) === selectedCategory);
      if (currentFilter === 'available') filteredTiers = filteredTiers.filter(t => t.remainingSupply > 0n);
      else if (currentFilter === 'sold-out') filteredTiers = filteredTiers.filter(t => t.remainingSupply === 0n);

      if (filteredTiers.length === 0) {
        container.innerHTML = '<div class="empty">No tiers match the current filter</div>';
        return;
      }

      let html = '<div class="gallery-grid">';
      filteredTiers.forEach(tier => {
        const minted = Number(tier.initialSupply) - Number(tier.remainingSupply);
        const soldOut = tier.remainingSupply === 0n;
        const price = formatEther(tier.price);
        const owned = ownedNFTs.filter(nft => nft.tierId === tier.id.toString());

        html += `
          <div class="nft-card" onclick="openTierModal(${tier.id})">
            <div class="nft-image">
              ${tier.resolvedUri ? `<img src="${resolveUri(tier.resolvedUri)}" alt="Tier ${tier.id}" onerror="this.style.display='none';this.parentElement.innerHTML='<div class=\\'placeholder\\'>NFT</div>'">` : '<div class="placeholder">NFT</div>'}
              <div class="tier-badge">Tier ${tier.id}</div>
              <div class="supply-badge ${soldOut ? 'sold-out' : ''}">${minted}/${tier.initialSupply}</div>
              ${owned.length > 0 ? `<div class="owned-badge">Owned: ${owned.length}</div>` : ''}
            </div>
            <div class="nft-info">
              <div class="nft-name">Tier ${tier.id}</div>
              <div class="nft-description">Category ${tier.category || 0}</div>
              <div class="nft-meta">
                <div class="nft-price">${price} ETH</div>
                ${tier.votingUnits > 0 ? `<div class="nft-votes">${tier.votingUnits} votes</div>` : ''}
              </div>
              <button class="mint-btn" ${soldOut ? 'disabled' : ''} onclick="event.stopPropagation(); mintTier(${tier.id}, '${tier.price}')">
                ${soldOut ? 'Sold Out' : 'Mint'}
              </button>
            </div>
          </div>`;
      });
      container.innerHTML = html + '</div>';
    }

    function renderOwnedNFTs() {
      const container = document.getElementById('galleryContainer');
      if (!connectedAddress) {
        container.innerHTML = '<div class="empty">Connect your wallet to view owned NFTs</div>';
        return;
      }
      if (ownedNFTs.length === 0) {
        container.innerHTML = '<div class="empty">You don\'t own any NFTs from this collection</div>';
        return;
      }

      let html = '<div class="gallery-grid">';
      ownedNFTs.forEach(nft => {
        const tier = nft.tier;
        const name = nft.metadata?.name || `Tier ${nft.tierId} #${nft.tokenId}`;
        const image = nft.metadata?.image;

        html += `
          <div class="nft-card" onclick="openNFTModal('${nft.tokenId}')">
            <div class="nft-image">
              ${image ? `<img src="${resolveUri(image)}" alt="${name}" onerror="this.style.display='none';this.parentElement.innerHTML='<div class=\\'placeholder\\'>NFT</div>'">` : '<div class="placeholder">NFT</div>'}
              <div class="tier-badge">Tier ${nft.tierId}</div>
            </div>
            <div class="nft-info">
              <div class="nft-name">${name}</div>
              <div class="nft-description">Token ID: ${nft.tokenId}</div>
              <div class="nft-meta">
                <div class="nft-price">${tier ? formatEther(tier.price) + ' ETH' : '-'}</div>
                ${tier?.votingUnits > 0 ? `<div class="nft-votes">${tier.votingUnits} votes</div>` : ''}
              </div>
            </div>
          </div>`;
      });
      container.innerHTML = html + '</div>';
    }

    window.openTierModal = async function(tierId) {
      const tier = allTiers.find(t => t.id.toString() === tierId.toString());
      if (!tier) return;

      const minted = Number(tier.initialSupply) - Number(tier.remainingSupply);
      const soldOut = tier.remainingSupply === 0n;
      const price = formatEther(tier.price);

      document.getElementById('modalTitle').textContent = `Tier ${tierId}`;
      document.getElementById('modalTokenId').textContent = `Category ${tier.category || 0}`;
      document.getElementById('modalDescription').textContent = tier.resolvedUri ? 'Tier metadata loaded from IPFS' : 'No metadata available';
      document.getElementById('modalImage').innerHTML = tier.resolvedUri
        ? `<img src="${resolveUri(tier.resolvedUri)}" alt="Tier ${tierId}">`
        : '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#444;font-size:64px;">NFT</div>';

      document.getElementById('modalAttributes').innerHTML = `
        <div class="attribute"><div class="attribute-label">Price</div><div class="attribute-value">${price} ETH</div></div>
        <div class="attribute"><div class="attribute-label">Supply</div><div class="attribute-value">${minted} / ${tier.initialSupply}</div></div>
        <div class="attribute"><div class="attribute-label">Remaining</div><div class="attribute-value">${tier.remainingSupply.toString()}</div></div>
        <div class="attribute"><div class="attribute-label">Voting Units</div><div class="attribute-value">${tier.votingUnits || 0}</div></div>
        ${tier.reserveFrequency > 0 ? `<div class="attribute"><div class="attribute-label">Reserve Frequency</div><div class="attribute-value">1 in ${tier.reserveFrequency}</div></div>` : ''}`;

      document.getElementById('modalActions').innerHTML = `
        <button class="action-btn primary" ${soldOut ? 'disabled' : ''} onclick="mintTier(${tierId}, '${tier.price}')">
          ${soldOut ? 'Sold Out' : `Mint for ${price} ETH`}
        </button>`;

      document.getElementById('nftModal').classList.add('visible');
    };

    window.openNFTModal = async function(tokenId) {
      const nft = ownedNFTs.find(n => n.tokenId === tokenId);
      if (!nft) return;

      const name = nft.metadata?.name || `Tier ${nft.tierId} #${tokenId}`;
      const description = nft.metadata?.description || 'No description available';
      const image = nft.metadata?.image;

      document.getElementById('modalTitle').textContent = name;
      document.getElementById('modalTokenId').textContent = `Token #${tokenId}`;
      document.getElementById('modalDescription').textContent = description;
      document.getElementById('modalImage').innerHTML = image
        ? `<img src="${resolveUri(image)}" alt="${name}">`
        : '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#444;font-size:64px;">NFT</div>';

      let attributesHtml = `
        <div class="attribute"><div class="attribute-label">Tier</div><div class="attribute-value">${nft.tierId}</div></div>
        <div class="attribute"><div class="attribute-label">Token ID</div><div class="attribute-value">${tokenId}</div></div>`;

      if (nft.metadata?.attributes) {
        nft.metadata.attributes.forEach(attr => {
          attributesHtml += `<div class="attribute"><div class="attribute-label">${attr.trait_type}</div><div class="attribute-value">${attr.value}</div></div>`;
        });
      }
      document.getElementById('modalAttributes').innerHTML = attributesHtml;

      document.getElementById('modalActions').innerHTML = `
        <button class="action-btn secondary" onclick="transferNFT('${tokenId}')">Transfer</button>
        <button class="action-btn secondary" onclick="cashOutNFT('${tokenId}')">Cash Out</button>`;

      document.getElementById('nftModal').classList.add('visible');
    };

    window.closeModal = function() {
      document.getElementById('nftModal').classList.remove('visible');
    };

    window.mintTier = async function(tierId, price) {
      if (!connectedAddress) { alert('Please connect your wallet first'); return; }
      try {
        const projectId = await publicClient.readContract({ address: hookAddress, abi: HOOK_ABI, functionName: 'PROJECT_ID' });
        alert(`To mint from Tier ${tierId}:\n\n1. Go to the Juicebox app\n2. Pay ${formatEther(BigInt(price))} ETH to Project ${projectId}\n3. The NFT will be minted to your wallet`);
      } catch (error) { console.error(error); alert('Minting failed: ' + error.message); }
    };

    window.transferNFT = async function(tokenId) {
      if (!connectedAddress) { alert('Please connect your wallet first'); return; }
      const recipient = prompt('Enter recipient address:');
      if (!recipient || !isAddress(recipient)) { alert('Invalid address'); return; }

      try {
        const hash = await walletClient.writeContract({
          address: hookAddress, abi: HOOK_ABI, functionName: 'transferFrom',
          args: [connectedAddress, recipient, BigInt(tokenId)], account: connectedAddress
        });
        alert('Transaction submitted: ' + hash);
        await publicClient.waitForTransactionReceipt({ hash });
        alert('Transfer successful!');
        await loadOwnedNFTs(connectedAddress);
        closeModal();
      } catch (error) { console.error(error); alert('Transfer failed: ' + error.message); }
    };

    window.cashOutNFT = function(tokenId) {
      alert(`To cash out NFT #${tokenId}:\n\n1. Go to the Juicebox app\n2. Use the cash out function with this token ID\n3. The NFT will be burned and you'll receive your share of the treasury`);
    };

    function resolveUri(uri) {
      if (!uri) return '';
      if (uri.startsWith('ipfs://')) return `https://ipfs.io/ipfs/${uri.slice(7)}`;
      if (uri.startsWith('data:')) return uri;
      return uri;
    }

    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
    document.getElementById('nftModal').addEventListener('click', (e) => { if (e.target.id === 'nftModal') closeModal(); });
  </script>
</body>
</html>
```

## Key Features

### Tier Browsing
- Grid layout with tier cards
- Supply tracking (minted/total)
- Price display in ETH
- Category filtering
- Availability filtering

### Owned NFTs View
- Wallet connection via viem
- Display owned NFTs with metadata
- Transfer functionality
- Cash out guidance

### Collection Stats
- Total tiers
- Total minted
- Max supply
- Floor price

### NFT Details Modal
- Full metadata display
- Attribute listing
- Action buttons (mint/transfer/cash out)

## Data Sources

The gallery uses on-chain data via:
- `JB721TiersHook` - NFT contract
- `JB721TiersHookStore` - Tier data storage
- Token metadata from IPFS

## Customization Points

1. **Image handling**: Modify `resolveUri()` for different IPFS gateways
2. **Metadata display**: Extend attributes rendering
3. **Minting flow**: Integrate directly with terminal
4. **Styling**: Customize via CSS variables

## Integration Notes

- Works with any V5 721 Hook deployment
- Uses viem for all blockchain interactions
- Shared styles from `/shared/styles.css`
- Chain config from `/shared/wallet-utils.js`
