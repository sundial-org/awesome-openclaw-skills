/**
 * Format XCH amount with proper decimals
 */
function formatXCH(amount) {
  if (amount === null || amount === undefined) return 'N/A';
  return `${amount.toFixed(2)} XCH`;
}

/**
 * Format USD amount
 */
function formatUSD(amount) {
  if (amount === null || amount === undefined) return 'N/A';
  return `$${amount.toFixed(2)}`;
}

/**
 * Format NFT ID with padding
 */
function formatNFTId(id) {
  return `#${String(id).padStart(4, '0')}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Format character type name
 */
function formatCharacterType(type) {
  const names = {
    'wojak': 'Wojak',
    'soyjak': 'Soyjak',
    'waifu': 'Waifu',
    'baddie': 'Baddie',
    'papa-tang': 'Papa Tang',
    'monkey-zoo': 'Monkey Zoo',
    'bepe-wojak': 'Bepe Wojak',
    'bepe-soyjak': 'Bepe Soyjak',
    'bepe-waifu': 'Bepe Waifu',
    'bepe-baddie': 'Bepe Baddie',
    'alien-wojak': 'Alien Wojak',
    'alien-soyjak': 'Alien Soyjak',
    'alien-waifu': 'Alien Waifu',
    'alien-baddie': 'Alien Baddie'
  };
  return names[type] || type;
}

/**
 * Format listing output
 */
function formatListing(listing, xchPrice = null) {
  const lines = [
    `${listing.nftName} (${formatNFTId(listing.nftId)})`,
    `  Price: ${formatXCH(listing.priceXch)}`
  ];

  if (xchPrice && listing.priceXch) {
    const usdPrice = listing.priceXch * xchPrice;
    lines.push(`         ${formatUSD(usdPrice)}`);
  }

  if (listing.dateCreated) {
    lines.push(`  Listed: ${formatDate(listing.dateCreated)}`);
  }

  return lines.join('\n');
}

/**
 * Format multiple listings as a list
 */
function formatListings(listings, xchPrice = null, limit = 10) {
  if (!listings || listings.length === 0) {
    return '❌ No listings found';
  }

  const sorted = [...listings].sort((a, b) => (a.priceXch || 0) - (b.priceXch || 0));
  const limited = sorted.slice(0, limit);

  const output = [
    `📊 Found ${listings.length} listing${listings.length === 1 ? '' : 's'}`,
    `${limit < listings.length ? `(showing top ${limit})` : ''}`,
    ''
  ];

  limited.forEach((listing, index) => {
    output.push(`${index + 1}. ${formatListing(listing, xchPrice)}`);
    output.push('');
  });

  return output.join('\n');
}

/**
 * Format floor price summary
 */
function formatFloorPrice(floor, characterType = null, xchPrice = null) {
  if (!floor) {
    const typeStr = characterType ? ` for ${formatCharacterType(characterType)}` : '';
    return `❌ No listings found${typeStr}`;
  }

  const output = [
    characterType ? `🏆 ${formatCharacterType(characterType)} Floor:` : '🏆 Collection Floor:',
    ``,
    formatListing(floor, xchPrice)
  ];

  return output.join('\n');
}

/**
 * Format collection stats
 */
function formatCollectionStats(stats) {
  if (!stats) {
    return '❌ Failed to fetch collection stats';
  }

  const output = [
    '📊 Wojak Farmers Plot Collection Stats',
    '',
    `Total NFTs: 4,200`,
    `Floor Price: ${formatXCH(stats.floor_price || 0)}`,
    `Total Volume: ${formatXCH(stats.total_volume || 0)}`,
    `Listed: ${stats.listed_count || 'N/A'}`
  ];

  return output.join('\n');
}

/**
 * Format search results
 */
function formatSearchResults(results, xchPrice = null) {
  if (!results || results.length === 0) {
    return '❌ No results found';
  }

  return formatListings(results, xchPrice, 20);
}

module.exports = {
  formatXCH,
  formatUSD,
  formatNFTId,
  formatDate,
  formatCharacterType,
  formatListing,
  formatListings,
  formatFloorPrice,
  formatCollectionStats,
  formatSearchResults
};
