const MintGardenAPI = require('./lib/api');

const api = new MintGardenAPI();

/**
 * Handle MintGarden commands from CLI or Clawdbot
 * @param {string} input - Raw command string
 * @returns {Promise<string>} Formatted output
 */
async function handleCommand(input) {
  input = input.trim().toLowerCase();

  // Strip common prefixes
  input = input.replace(/^(\/mg|\/mintgarden|mg|mintgarden)\s+/, '');

  // Shortcuts - direct IDs
  if (input.startsWith('col1')) {
    return await getCollectionDetails(input);
  }
  if (input.startsWith('nft1')) {
    return await getNFTDetails(input);
  }
  if (input.startsWith('did:chia:')) {
    return await getProfileDetails(input);
  }

  // Parse command
  const parts = input.split(/\s+/);
  const command = parts[0];
  const subcommand = parts[1];
  const args = parts.slice(2);

  switch (command) {
    // SEARCH
    case 'search':
      if (subcommand === 'nfts') {
        return await searchNFTs(args.join(' '));
      }
      if (subcommand === 'collections') {
        return await searchCollections(args.join(' '));
      }
      return await searchAll(parts.slice(1).join(' '));

    // COLLECTIONS
    case 'collections':
      if (subcommand === 'list' || !subcommand) {
        return await listCollections();
      }
      if (subcommand === 'nfts') {
        return await getCollectionNFTs(args[0]);
      }
      return await getCollectionDetails(subcommand);

    case 'collection':
      if (subcommand === 'list') {
        return await listCollections();
      }
      if (subcommand === 'nfts') {
        return await getCollectionNFTs(args[0]);
      }
      if (subcommand === 'stats') {
        return await getCollectionStats(args[0]);
      }
      if (subcommand === 'activity') {
        return await getCollectionActivity(args[0]);
      }
      return await getCollectionDetails(subcommand);

    // NFTs
    case 'nft':
      if (subcommand === 'history') {
        return await getNFTHistory(args[0]);
      }
      if (subcommand === 'offers') {
        return await getNFTOffers(args[0]);
      }
      return await getNFTDetails(subcommand);

    // PROFILES
    case 'profile':
      if (subcommand === 'nfts') {
        return await getProfileNFTs(args[0]);
      }
      if (subcommand === 'activity') {
        return await getProfileActivity(args[0]);
      }
      return await getProfileDetails(subcommand);

    // EVENTS
    case 'events':
      return await getEvents(subcommand);

    // STATS
    case 'stats':
      return await getGlobalStats();

    case 'trending':
      return await getTrending();

    case 'top':
      if (subcommand === 'collectors') {
        return await getTopCollectors();
      }
      if (subcommand === 'traders') {
        return await getTopTraders();
      }
      return '❌ Unknown top command. Try: top collectors, top traders';

    default:
      return `❌ Unknown command: ${command}\n\nTry 'mg help' for usage.`;
  }
}

// === COMMAND IMPLEMENTATIONS ===

async function searchAll(query) {
  if (!query) return '❌ Please provide a search query';
  
  const results = await api.search(query, { limit: 20 });
  
  let output = `🔍 Search results for "${query}":\n\n`;
  
  let hasResults = false;
  
  if (results.collections?.length > 0) {
    hasResults = true;
    output += `📚 COLLECTIONS (${results.collections.length})\n`;
    results.collections.slice(0, 5).forEach(c => {
      output += `  • ${c.name}\n`;
    });
    output += '\n';
  }
  
  if (results.nfts?.length > 0) {
    hasResults = true;
    output += `🖼  NFTs (${results.nfts.length})\n`;
    results.nfts.slice(0, 5).forEach(n => {
      output += `  • ${n.name || 'Unnamed'}\n`;
    });
    output += '\n';
  }
  
  if (results.profiles?.length > 0) {
    hasResults = true;
    output += `👤 PROFILES (${results.profiles.length})\n`;
    results.profiles.slice(0, 5).forEach(p => {
      output += `  • ${p.name || p.username || 'Anonymous'}\n`;
    });
  }
  
  return hasResults ? output : '❌ No results found';
}

async function searchNFTs(query) {
  if (!query) return '❌ Please provide a search query';
  
  const results = await api.searchNFTs(query, { limit: 20 });
  
  let output = `🖼  NFT search results for "${query}":\n\n`;
  
  if (results.nfts?.length > 0) {
    results.nfts.forEach((nft, i) => {
      output += `${i + 1}. ${nft.name || 'Unnamed'}\n`;
      output += `   Collection: ${nft.collection_name || 'Unknown'}\n`;
      if (nft.price) output += `   Price: ${formatXCH(nft.price)}\n`;
      output += `   ID: ${nft.encoded_id}\n\n`;
    });
    return output;
  }
  
  return '❌ No NFTs found';
}

async function searchCollections(query) {
  if (!query) return '❌ Please provide a search query';
  
  const results = await api.searchCollections(query, { limit: 20 });
  
  let output = `📚 Collection search results for "${query}":\n\n`;
  
  if (results.collections?.length > 0) {
    results.collections.forEach((col, i) => {
      output += `${i + 1}. ${col.name}\n`;
      output += `   ID: ${col.id || col.encoded_id}\n\n`;
    });
    return output;
  }
  
  return '❌ No collections found';
}

async function listCollections() {
  const results = await api.getCollections({ limit: 25, sort: 'vol24h' });
  
  let output = `📚 Top Collections by Volume (24h):\n\n`;
  
  if (results.items?.length > 0) {
    results.items.forEach((col, i) => {
      const verified = col.creator?.verification_state ? '✓' : '';
      output += `${i + 1}. ${col.name} ${verified}\n`;
      output += `   ID: ${col.id || col.encoded_id}\n\n`;
    });
    return output;
  }
  
  return '❌ No collections found';
}

async function getCollectionDetails(collectionId) {
  if (!collectionId) return '❌ Please provide a collection ID';
  
  const collection = await api.getCollection(collectionId);
  
  let output = `📚 ${collection.name}\n`;
  const verified = collection.creator?.verification_state ? '✓ Verified' : '';
  if (verified) output += verified + '\n';
  output += '\n';
  
  if (collection.description) {
    output += `${collection.description}\n\n`;
  }
  
  if (collection.creator?.name) {
    output += `Creator: ${collection.creator.name}\n`;
  }
  
  output += `\nID: ${collection.id || collection.encoded_id}\n`;
  
  return output;
}

async function getCollectionNFTs(collectionId) {
  if (!collectionId) return '❌ Please provide a collection ID';
  
  const results = await api.getCollectionNFTs(collectionId, { limit: 20 });
  
  let output = `🖼  NFTs in collection:\n\n`;
  
  if (results.items?.length > 0) {
    results.items.forEach((nft, i) => {
      output += `${i + 1}. ${nft.name || 'Unnamed'}\n`;
      if (nft.price) output += `   Price: ${formatXCH(nft.price)}\n`;
      if (nft.openrarity_rank) output += `   Rarity: #${nft.openrarity_rank}\n`;
      output += `   ID: ${nft.encoded_id}\n\n`;
    });
    return output;
  }
  
  return '❌ No NFTs found in this collection';
}

async function getCollectionStats(collectionId) {
  // Stats are embedded in collection details, not a separate endpoint
  return await getCollectionDetails(collectionId);
}

async function getCollectionActivity(collectionId) {
  // Use events endpoint instead
  return await getEvents(collectionId);
}

async function getNFTDetails(launcherId) {
  if (!launcherId) return '❌ Please provide an NFT launcher ID';
  
  const nft = await api.getNFT(launcherId);
  
  let output = `🖼  ${nft.name || 'Unnamed NFT'}\n\n`;
  
  output += `Collection: ${nft.collection_name || 'Unknown'}\n`;
  if (nft.price) output += `Price: ${formatXCH(nft.price)}\n`;
  
  if (nft.openrarity_rank) {
    output += `Rarity: #${nft.openrarity_rank}\n`;
  }
  
  if (nft.owner_name) {
    output += `Owner: ${nft.owner_name}\n`;
  } else if (nft.owner_encoded_id) {
    output += `Owner: ${nft.owner_encoded_id}\n`;
  }
  
  if (nft.description) {
    output += `\n${nft.description}\n`;
  }
  
  output += `\nID: ${nft.encoded_id}\n`;
  
  return output;
}

async function getNFTHistory(launcherId) {
  // No direct history endpoint - would need to use events
  return '❌ NFT history not available. Try /mg events to see recent activity.';
}

async function getNFTOffers(launcherId) {
  // Check if this is a mint
  try {
    const mint = await api.getMint(launcherId);
    const offers = await api.getMintOffers(launcherId, { limit: 10 });
    
    let output = `💰 Active Offers:\n\n`;
    
    if (offers.items?.length > 0) {
      offers.items.forEach((offer, i) => {
        output += `${i + 1}. Offer details\n\n`;
      });
      return output;
    }
    
    return '❌ No active offers';
  } catch (e) {
    return '❌ No offers found for this NFT';
  }
}

async function getProfileDetails(identifier) {
  if (!identifier) return '❌ Please provide a username or ID';
  
  const profile = await api.getProfile(identifier);
  
  let output = `👤 ${profile.username || profile.name || 'Anonymous'}\n\n`;
  
  if (profile.bio) {
    output += `${profile.bio}\n\n`;
  }
  
  if (profile.encoded_id) {
    output += `ID: ${profile.encoded_id}\n`;
  }
  
  return output;
}

async function getProfileNFTs(identifier) {
  if (!identifier) return '❌ Please provide a username or ID';
  
  const results = await api.getProfileNFTs(identifier, { limit: 20 });
  
  let output = `🖼  NFTs owned by ${identifier}:\n\n`;
  
  if (results.items?.length > 0) {
    results.items.forEach((nft, i) => {
      output += `${i + 1}. ${nft.name || 'Unnamed'}\n`;
      output += `   Collection: ${nft.collection_name || 'Unknown'}\n`;
      if (nft.price) output += `   Value: ${formatXCH(nft.price)}\n`;
      output += '\n';
    });
    return output;
  }
  
  return '❌ No NFTs found';
}

async function getProfileActivity(identifier) {
  // No separate activity endpoint - use events
  return '❌ Profile activity not available. Try /mg events for global activity.';
}

async function getEvents(collectionId) {
  const results = await api.getEvents({ limit: 20 });
  
  let output = `📈 Recent marketplace events:\n\n`;
  
  if (results.items?.length > 0) {
    results.items.forEach((event, i) => {
      output += `${i + 1}. ${event.type || 'Event'}\n`;
      if (event.nft_name) output += `   NFT: ${event.nft_name}\n`;
      if (event.collection_name) output += `   Collection: ${event.collection_name}\n`;
      if (event.price) output += `   ${formatXCH(event.price)}\n`;
      if (event.timestamp) output += `   ${formatTimeAgo(event.timestamp)}\n`;
      output += '\n';
    });
    return output;
  }
  
  return '❌ No recent events';
}

async function getGlobalStats() {
  // No global stats endpoint - use collections instead
  return await listCollections();
}

async function getTrending() {
  // Trending is just sorted collections
  return await listCollections();
}

async function getTopCollectors() {
  return '❌ Top collectors data not available from this API.';
}

async function getTopTraders() {
  return '❌ Top traders data not available from this API.';
}

// === FORMATTING HELPERS ===

function formatXCH(mojos) {
  if (!mojos && mojos !== 0) return 'N/A';
  const xch = mojos / 1_000_000_000_000;
  return `${xch.toFixed(3)} XCH`;
}

function formatTimeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp * 1000;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'Just now';
}

module.exports = { handleCommand };
