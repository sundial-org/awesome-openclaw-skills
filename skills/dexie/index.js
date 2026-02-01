const DexieAPI = require('./lib/api');

const api = new DexieAPI();

/**
 * Handle Dexie commands from CLI or Clawdbot
 * @param {string} input - Raw command string
 * @returns {Promise<string>} Formatted output
 */
async function handleCommand(input) {
  input = input.trim().toLowerCase();

  // Strip common prefixes
  input = input.replace(/^(\/dex|\/dexie|dex|dexie)\s+/, '');

  const parts = input.split(/\s+/);
  const command = parts[0];
  const subcommand = parts[1];
  const args = parts.slice(2);

  switch (command) {
    // OFFERS
    case 'offers':
      if (subcommand && !['active', 'completed', 'cancelled'].includes(subcommand)) {
        return await getOfferDetails(subcommand);
      }
      return await listOffers(subcommand);

    case 'offer':
      return await getOfferDetails(subcommand);

    // ASSETS
    case 'assets':
    case 'tokens':
      if (subcommand === 'search') {
        return await searchAssets(args.join(' '));
      }
      return await listAssets();

    case 'asset':
    case 'token':
      return await getAssetDetails(subcommand);

    // PAIRS
    case 'pairs':
      return await listPairs();

    case 'pair':
      return await getPairDetails(subcommand);

    // STATS
    case 'stats':
      return await getStats();

    // SEARCH
    case 'search':
      return await searchAssets(parts.slice(1).join(' '));

    // PRICE
    case 'price':
      return await getAssetPrice(parts.slice(1).join(' '));

    default:
      // Try as asset lookup
      if (command && command.length > 0) {
        return await getAssetPrice(input);
      }
      return `❌ Unknown command: ${command}\n\nTry 'dex help' for usage.`;
  }
}

// === COMMAND IMPLEMENTATIONS ===

async function listOffers(status) {
  const statusCode = status === 'completed' ? 1 : status === 'cancelled' ? 2 : 0;
  const results = await api.getOffers({ page_size: 20, status: statusCode });
  
  let output = `💱 ${status || 'Active'} Offers:\n\n`;
  
  if (results.offers?.length > 0) {
    results.offers.forEach((offer, i) => {
      const offered = offer.offered[0];
      const requested = offer.requested[0];
      
      output += `${i + 1}. ${formatAmount(offered.amount)} ${offered.code} → ${formatAmount(requested.amount)} ${requested.code}\n`;
      output += `   Price: ${offer.price.toFixed(6)}\n`;
      output += `   ID: ${offer.id}\n\n`;
    });
    
    output += `Total: ${results.count?.toLocaleString() || '?'} offers\n`;
    return output;
  }
  
  return '❌ No offers found';
}

async function getOfferDetails(offerId) {
  if (!offerId) return '❌ Please provide an offer ID';
  
  const offer = await api.getOffer(offerId);
  
  let output = `💱 Offer Details\n\n`;
  
  const offered = offer.offered[0];
  const requested = offer.requested[0];
  
  output += `Offering: ${formatAmount(offered.amount)} ${offered.code}\n`;
  output += `Requesting: ${formatAmount(requested.amount)} ${requested.code}\n`;
  output += `Price: ${offer.price.toFixed(6)} ${requested.code}/${offered.code}\n\n`;
  
  const statusMap = { 0: 'Active', 1: 'Completed', 2: 'Cancelled' };
  output += `Status: ${statusMap[offer.status] || 'Unknown'}\n`;
  output += `Fees: ${offer.fees} XCH\n\n`;
  
  output += `Created: ${new Date(offer.date_found).toLocaleString()}\n`;
  if (offer.date_completed) {
    output += `Completed: ${new Date(offer.date_completed).toLocaleString()}\n`;
  }
  
  output += `\nID: ${offer.id}\n`;
  
  return output;
}

async function listAssets() {
  const results = await api.getAssets({ page_size: 30, sort: 'volume' });
  
  let output = `🪙 Top Tokens by Volume (24h):\n\n`;
  
  if (results.assets?.length > 0) {
    results.assets.forEach((asset, i) => {
      output += `${i + 1}. ${asset.code} - ${asset.name}\n`;
      output += `   Price: $${asset.current_avg_price?.toFixed(6) || 'N/A'}\n`;
      if (asset.volume && asset.volume[0]) {
        output += `   Volume: ${formatAmount(asset.volume[0])} XCH\n`;
      }
      if (asset.liquidity && asset.liquidity[0]) {
        output += `   Liquidity: ${formatAmount(asset.liquidity[0])} XCH\n`;
      }
      output += '\n';
    });
    return output;
  }
  
  return '❌ No assets found';
}

async function getAssetDetails(assetId) {
  if (!assetId) return '❌ Please provide an asset ID or code';
  
  try {
    const asset = await api.getAsset(assetId);
    
    let output = `🪙 ${asset.code} - ${asset.name}\n\n`;
    
    if (asset.description) {
      output += `${asset.description}\n\n`;
    }
    
    output += `Current Price: $${asset.current_avg_price?.toFixed(6) || 'N/A'}\n`;
    
    if (asset.volume && asset.volume[0]) {
      output += `Volume (24h): ${formatAmount(asset.volume[0])} XCH ($${formatAmount(asset.volume[1])})\n`;
    }
    
    if (asset.liquidity && asset.liquidity[0]) {
      output += `Liquidity: ${formatAmount(asset.liquidity[0])} XCH ($${formatAmount(asset.liquidity[1])})\n`;
    }
    
    if (asset.website) {
      output += `\nWebsite: ${asset.website}\n`;
    }
    
    output += `\nAsset ID: ${asset.id}\n`;
    
    return output;
  } catch (e) {
    // Try searching by code
    return await searchAssets(assetId);
  }
}

async function searchAssets(query) {
  if (!query) return '❌ Please provide a search query';
  
  // Search through assets list
  const results = await api.getAssets({ page_size: 100 });
  
  const matches = results.assets?.filter(a => 
    a.code.toLowerCase().includes(query.toLowerCase()) ||
    a.name.toLowerCase().includes(query.toLowerCase())
  ) || [];
  
  if (matches.length === 0) {
    return '❌ No matching tokens found';
  }
  
  let output = `🔍 Search results for "${query}":\n\n`;
  
  matches.slice(0, 10).forEach((asset, i) => {
    output += `${i + 1}. ${asset.code} - ${asset.name}\n`;
    output += `   Price: $${asset.current_avg_price?.toFixed(6) || 'N/A'}\n`;
    output += `   ID: ${asset.id}\n\n`;
  });
  
  return output;
}

async function getAssetPrice(query) {
  if (!query) return '❌ Please provide a token code or name';
  
  const results = await api.getAssets({ page_size: 100 });
  
  const match = results.assets?.find(a => 
    a.code.toLowerCase() === query.toLowerCase() ||
    a.name.toLowerCase() === query.toLowerCase()
  );
  
  if (!match) {
    return `❌ Token "${query}" not found. Try: dex search ${query}`;
  }
  
  let output = `💰 ${match.code} Price\n\n`;
  output += `$${match.current_avg_price?.toFixed(6) || 'N/A'}\n`;
  
  if (match.volume && match.volume[0]) {
    output += `Volume (24h): ${formatAmount(match.volume[0])} XCH\n`;
  }
  
  return output;
}

async function listPairs() {
  const results = await api.getPairs();
  
  let output = `📊 Trading Pairs:\n\n`;
  
  if (results.pairs?.length > 0) {
    results.pairs.slice(0, 20).forEach((pair, i) => {
      output += `${i + 1}. ${pair.base.code}/${pair.quote.code}\n`;
    });
    
    output += `\nTotal: ${results.pairs.length} pairs\n`;
    return output;
  }
  
  return '❌ No pairs found';
}

async function getPairDetails(pairId) {
  if (!pairId) return '❌ Please provide a pair ID';
  
  const pair = await api.getPair(pairId);
  
  let output = `📊 ${pair.base.code}/${pair.quote.code}\n\n`;
  output += `Base: ${pair.base.name}\n`;
  output += `Quote: ${pair.quote.name}\n`;
  
  return output;
}

async function getStats() {
  const stats = await api.getStats();
  
  let output = `📈 Dexie Stats\n\n`;
  
  if (stats.total_volume_24h) {
    output += `Volume (24h): ${formatAmount(stats.total_volume_24h)} XCH\n`;
  }
  
  if (stats.total_trades_24h) {
    output += `Trades (24h): ${stats.total_trades_24h.toLocaleString()}\n`;
  }
  
  if (stats.active_offers) {
    output += `Active Offers: ${stats.active_offers.toLocaleString()}\n`;
  }
  
  return output;
}

// === FORMATTING HELPERS ===

function formatAmount(amount) {
  if (!amount && amount !== 0) return 'N/A';
  
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(2)}M`;
  }
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(2)}K`;
  }
  return amount.toFixed(2);
}

module.exports = { handleCommand };
