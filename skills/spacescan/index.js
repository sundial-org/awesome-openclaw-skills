const SpacescanAPI = require('./lib/api');

const api = new SpacescanAPI();

/**
 * Handle Spacescan commands from CLI or Clawdbot
 * @param {string} input - Raw command string
 * @returns {Promise<string>} Formatted output
 */
async function handleCommand(input) {
  input = input.trim().toLowerCase();

  // Strip common prefixes
  input = input.replace(/^(\/scan|\/spacescan|scan|spacescan)\s+/, '');

  // Check API key
  if (!api.hasApiKey()) {
    return '❌ Spacescan API key required.\n\n' +
           'Set environment variable:\n' +
           'export SPACESCAN_API_KEY=your_key_here\n\n' +
           'Get your key at: https://www.spacescan.io/apis';
  }

  const parts = input.split(/\s+/);
  const command = parts[0];
  const subcommand = parts[1];
  const args = parts.slice(2);

  switch (command) {
    // BLOCKS
    case 'block':
      if (subcommand === 'latest') {
        return await getLatestBlock();
      }
      return await getBlock(subcommand);

    case 'blocks':
      return await getBlockRange(subcommand, args[0]);

    // TRANSACTIONS
    case 'tx':
    case 'transaction':
      return await getTransaction(subcommand);

    // ADDRESSES
    case 'address':
    case 'addr':
      if (subcommand === 'balance') {
        return await getAddressBalance(args[0]);
      }
      if (subcommand === 'txs') {
        return await getAddressTransactions(args[0]);
      }
      return await getAddress(subcommand);

    // COINS
    case 'coin':
      return await getCoin(subcommand);

    // STATS
    case 'stats':
      return await getNetworkStats();

    case 'network':
      return await getNetworkInfo();

    case 'space':
      return await getNetworkSpace();

    // MEMPOOL
    case 'mempool':
      return await getMempool();

    // PRICE
    case 'price':
      return await getXCHPrice();

    // SEARCH
    case 'search':
      return await search(parts.slice(1).join(' '));

    // CATS
    case 'cats':
      return await getCATList();

    case 'cat':
      return await getCAT(subcommand);

    // NFT
    case 'nft':
      return await getNFT(subcommand);

    default:
      // Try as search
      if (command && command.length > 10) {
        return await search(input);
      }
      return `❌ Unknown command: ${command}\n\nTry 'scan help' for usage.`;
  }
}

// === COMMAND IMPLEMENTATIONS ===

async function getLatestBlock() {
  const block = await api.getLatestBlock();
  
  let output = `🧱 Latest Block\n\n`;
  output += `Height: ${block.height?.toLocaleString()}\n`;
  output += `Hash: ${block.header_hash}\n`;
  output += `Timestamp: ${new Date(block.timestamp * 1000).toLocaleString()}\n`;
  output += `Transactions: ${block.tx_count || 0}\n`;
  output += `Farmer: ${block.farmer_puzzle_hash?.slice(0, 16)}...\n`;
  
  return output;
}

async function getBlock(heightOrHash) {
  if (!heightOrHash) return '❌ Please provide a block height or hash';
  
  const block = await api.getBlock(heightOrHash);
  
  let output = `🧱 Block ${block.height}\n\n`;
  output += `Hash: ${block.header_hash}\n`;
  output += `Timestamp: ${new Date(block.timestamp * 1000).toLocaleString()}\n`;
  output += `Transactions: ${block.tx_count || 0}\n`;
  output += `Farmer: ${block.farmer_puzzle_hash}\n`;
  
  if (block.prev_hash) {
    output += `Previous: ${block.prev_hash}\n`;
  }
  
  return output;
}

async function getBlockRange(start, end) {
  if (!start || !end) return '❌ Please provide start and end heights';
  
  const blocks = await api.getBlockRange(start, end);
  
  let output = `🧱 Blocks ${start} to ${end}:\n\n`;
  
  if (blocks.length > 0) {
    blocks.forEach(block => {
      output += `${block.height}: ${block.header_hash}\n`;
    });
    return output;
  }
  
  return '❌ No blocks found';
}

async function getTransaction(txId) {
  if (!txId) return '❌ Please provide a transaction ID';
  
  const tx = await api.getTransaction(txId);
  
  let output = `💸 Transaction\n\n`;
  output += `ID: ${tx.id}\n`;
  output += `Block: ${tx.block_height}\n`;
  output += `Timestamp: ${new Date(tx.timestamp * 1000).toLocaleString()}\n`;
  output += `Type: ${tx.type}\n`;
  output += `Fee: ${formatXCH(tx.fee)}\n`;
  
  return output;
}

async function getAddress(address) {
  if (!address) return '❌ Please provide an address';
  
  const addr = await api.getAddress(address);
  
  let output = `👤 Address\n\n`;
  output += `${address}\n\n`;
  output += `Balance: ${formatXCH(addr.balance)}\n`;
  output += `Transactions: ${addr.tx_count || 0}\n`;
  
  return output;
}

async function getAddressBalance(address) {
  if (!address) return '❌ Please provide an address';
  
  const balance = await api.getAddressBalance(address);
  
  let output = `💰 Balance\n\n`;
  output += `${formatXCH(balance.balance)}\n`;
  
  return output;
}

async function getAddressTransactions(address) {
  if (!address) return '❌ Please provide an address';
  
  const result = await api.getAddressTransactions(address, { limit: 20 });
  
  let output = `💸 Recent Transactions:\n\n`;
  
  if (result.transactions?.length > 0) {
    result.transactions.forEach((tx, i) => {
      output += `${i + 1}. ${tx.id}\n`;
      output += `   Block: ${tx.block_height}\n`;
      output += `   Amount: ${formatXCH(tx.amount)}\n\n`;
    });
    return output;
  }
  
  return '❌ No transactions found';
}

async function getCoin(coinId) {
  if (!coinId) return '❌ Please provide a coin ID';
  
  const coin = await api.getCoin(coinId);
  
  let output = `🪙 Coin\n\n`;
  output += `ID: ${coin.coin_name}\n`;
  output += `Amount: ${formatXCH(coin.amount)}\n`;
  output += `Puzzlehash: ${coin.puzzle_hash}\n`;
  output += `Parent: ${coin.parent_coin_info}\n`;
  output += `Spent: ${coin.spent ? 'Yes' : 'No'}\n`;
  
  return output;
}

async function getNetworkStats() {
  const stats = await api.getNetworkStats();
  
  let output = `📊 Network Statistics\n\n`;
  output += `Peak Height: ${stats.peak_height?.toLocaleString()}\n`;
  output += `Network Space: ${formatNetworkSpace(stats.network_space)}\n`;
  output += `Total Supply: ${formatXCH(stats.total_supply)}\n`;
  output += `Block Time: ${stats.block_time}s\n`;
  
  if (stats.total_transactions) {
    output += `Total Transactions: ${stats.total_transactions.toLocaleString()}\n`;
  }
  
  return output;
}

async function getNetworkInfo() {
  const info = await api.getNetworkInfo();
  
  let output = `🌐 Network Info\n\n`;
  output += `Network: ${info.network_name}\n`;
  output += `Version: ${info.version}\n`;
  output += `Peak: ${info.peak_height?.toLocaleString()}\n`;
  
  return output;
}

async function getNetworkSpace() {
  const space = await api.getNetworkSpace();
  
  let output = `💾 Network Space\n\n`;
  output += `${formatNetworkSpace(space.space)}\n`;
  
  return output;
}

async function getMempool() {
  const mempool = await api.getMempool();
  
  let output = `⏳ Mempool\n\n`;
  output += `Pending Transactions: ${mempool.count || 0}\n`;
  output += `Total Fees: ${formatXCH(mempool.total_fees)}\n`;
  
  return output;
}

async function getXCHPrice() {
  const price = await api.getXCHPrice();
  
  let output = `💰 XCH Price\n\n`;
  output += `$${price.usd?.toFixed(2) || 'N/A'}\n`;
  
  if (price.btc) {
    output += `₿${price.btc.toFixed(8)}\n`;
  }
  
  return output;
}

async function search(query) {
  if (!query) return '❌ Please provide a search query';
  
  const result = await api.search(query);
  
  let output = `🔍 Search Results:\n\n`;
  
  if (result.type === 'block') {
    output += `Block: ${result.data.height}\n`;
  } else if (result.type === 'transaction') {
    output += `Transaction: ${result.data.id}\n`;
  } else if (result.type === 'address') {
    output += `Address: ${result.data.address}\n`;
  } else if (result.type === 'coin') {
    output += `Coin: ${result.data.coin_name}\n`;
  } else {
    output += 'No results found\n';
  }
  
  return output;
}

async function getCATList() {
  const result = await api.getCATList({ limit: 30 });
  
  let output = `🪙 CAT Tokens:\n\n`;
  
  if (result.cats?.length > 0) {
    result.cats.forEach((cat, i) => {
      output += `${i + 1}. ${cat.name} (${cat.code})\n`;
      output += `   ID: ${cat.asset_id}\n\n`;
    });
    return output;
  }
  
  return '❌ No CATs found';
}

async function getCAT(assetId) {
  if (!assetId) return '❌ Please provide a CAT asset ID';
  
  const cat = await api.getCAT(assetId);
  
  let output = `🪙 ${cat.name || 'Unknown CAT'}\n\n`;
  output += `Code: ${cat.code}\n`;
  output += `Asset ID: ${cat.asset_id}\n`;
  
  if (cat.description) {
    output += `Description: ${cat.description}\n`;
  }
  
  return output;
}

async function getNFT(nftId) {
  if (!nftId) return '❌ Please provide an NFT ID';
  
  const nft = await api.getNFT(nftId);
  
  let output = `🖼️  ${nft.name || 'Unnamed NFT'}\n\n`;
  output += `ID: ${nft.nft_id}\n`;
  output += `Collection: ${nft.collection_name || 'None'}\n`;
  output += `Owner: ${nft.owner_address}\n`;
  
  return output;
}

// === FORMATTING HELPERS ===

function formatXCH(mojos) {
  if (!mojos && mojos !== 0) return 'N/A';
  const xch = mojos / 1_000_000_000_000;
  return `${xch.toFixed(4)} XCH`;
}

function formatNetworkSpace(bytes) {
  if (!bytes) return 'N/A';
  
  const eb = bytes / (1024 ** 6);
  if (eb >= 1) return `${eb.toFixed(2)} EiB`;
  
  const pb = bytes / (1024 ** 5);
  if (pb >= 1) return `${pb.toFixed(2)} PiB`;
  
  const tb = bytes / (1024 ** 4);
  return `${tb.toFixed(2)} TiB`;
}

module.exports = { handleCommand };
