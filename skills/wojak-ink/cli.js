#!/usr/bin/env node

const WojakAPI = require('./lib/api');
const RarityAnalyzer = require('./lib/rarity');
const PriceHistory = require('./lib/history');
const TraitAnalyzer = require('./lib/traits');
const {
  formatFloorPrice,
  formatCollectionStats,
  formatSearchResults,
  formatListings,
  formatCharacterType
} = require('./lib/format');

const api = new WojakAPI();
const rarityAnalyzer = new RarityAnalyzer();
const priceHistory = new PriceHistory();
const traitAnalyzer = new TraitAnalyzer();

/**
 * Main command handler
 */
async function handleCommand(args) {
  const [command, ...params] = args;

  switch (command) {
    case 'floor':
      return await handleFloor(params);
    case 'search':
      return await handleSearch(params);
    case 'stats':
      return await handleStats();
    case 'listings':
      return await handleListings(params);
    case 'characters':
      return await handleCharacters();
    case 'nft':
      return await handleNFT(params);
    case 'rarity':
      return await handleRarity(params);
    case 'history':
      return await handleHistory(params);
    case 'traits':
      return await handleTraits(params);
    case 'track':
      return await handleTrack(params);
    case 'deals':
      return await handleDeals(params);
    case 'help':
    case '--help':
    case '-h':
      return showHelp();
    default:
      return `❌ Unknown command: ${command}\n\nUse "wojak help" for available commands.`;
  }
}

/**
 * Handle floor price command
 */
async function handleFloor(params) {
  const characterType = params[0] || null;
  
  if (characterType && !isValidCharacterType(characterType)) {
    return `❌ Unknown character type: ${characterType}\n\nUse "wojak characters" to see valid types.`;
  }

  const floor = await api.getFloorPrice(characterType);
  return formatFloorPrice(floor, characterType);
}

/**
 * Handle search command
 */
async function handleSearch(params) {
  const query = params.join(' ');
  
  if (!query) {
    return '❌ Please provide a search term\n\nExample: wojak search "king"';
  }

  const results = await api.searchNFTs(query);
  return formatSearchResults(results);
}

/**
 * Handle stats command
 */
async function handleStats() {
  const stats = await api.fetchCollectionStats();
  return formatCollectionStats(stats);
}

/**
 * Handle listings command
 */
async function handleListings(params) {
  const characterType = params[0] || null;
  
  if (characterType && !isValidCharacterType(characterType)) {
    return `❌ Unknown character type: ${characterType}\n\nUse "wojak characters" to see valid types.`;
  }

  const allListings = await api.fetchListings();
  
  let filtered = allListings;
  if (characterType) {
    const ranges = api.getCharacterRanges();
    const range = ranges[characterType.toLowerCase()];
    if (range) {
      filtered = allListings.filter(l => l.nftId >= range.start && l.nftId <= range.end);
    }
  }

  return formatListings(filtered, null, 20);
}

/**
 * Handle characters command
 */
async function handleCharacters() {
  const ranges = api.getCharacterRanges();
  
  const output = [
    '🎨 Wojak Farmers Plot Character Types:',
    ''
  ];

  for (const [type, range] of Object.entries(ranges)) {
    const count = range.end - range.start + 1;
    output.push(`  ${formatCharacterType(type)}: ${count} NFTs (#${range.start}-#${range.end})`);
  }

  output.push('');
  output.push('Usage: wojak floor <character-type>');
  output.push('Example: wojak floor wojak');

  return output.join('\n');
}

/**
 * Handle NFT lookup command
 */
async function handleNFT(params) {
  const nftId = parseInt(params[0], 10);
  
  if (isNaN(nftId) || nftId < 1 || nftId > 4200) {
    return '❌ Invalid NFT ID. Must be between 1 and 4200.';
  }

  const characterType = api.getCharacterType(nftId);
  const imageUrl = api.getNFTImageUrl(nftId);
  
  const output = [
    `🖼️  Wojak #${String(nftId).padStart(4, '0')}`,
    '',
    `Character: ${formatCharacterType(characterType)}`,
    `Image: ${imageUrl}`,
    ''
  ];

  // Check if listed
  const listings = await api.fetchListings();
  const listing = listings.find(l => l.nftId === nftId);
  
  if (listing) {
    output.push(`Status: 🏷️  Listed for ${listing.priceXch.toFixed(2)} XCH`);
  } else {
    output.push(`Status: Not currently listed`);
  }

  return output.join('\n');
}

/**
 * Handle rarity command
 */
async function handleRarity(params) {
  const nftId = parseInt(params[0], 10);
  
  if (isNaN(nftId) || nftId < 1 || nftId > 4200) {
    return '❌ Invalid NFT ID. Must be between 1 and 4200.';
  }

  const characterType = api.getCharacterType(nftId);
  const estimate = rarityAnalyzer.estimateRank(nftId, characterType);
  
  if (!estimate) {
    return '❌ Could not estimate rarity for this NFT.';
  }

  const { tier, emoji } = estimate.tier;
  
  const output = [
    `${emoji} Rarity Analysis: Wojak #${String(nftId).padStart(4, '0')}`,
    '',
    `Character: ${formatCharacterType(characterType)}`,
    `Rarity Score: ${estimate.estimatedScore.toFixed(2)}`,
    `Rarity Tier: ${tier}`,
    `Estimated Rank: ~#${estimate.estimatedRank} / 4,200`,
    '',
    '⚠️  Note: Estimates based on character type averages.',
    'Full trait data needed for accurate scoring.'
  ];

  return output.join('\n');
}

/**
 * Handle price history command
 */
async function handleHistory(params) {
  const subcommand = params[0] || 'recent';
  const characterType = params[1] || null;

  if (subcommand === 'recent') {
    const sales = priceHistory.getRecentSales(10, characterType);
    
    if (sales.length === 0) {
      return '❌ No sales history recorded yet.';
    }

    const output = [
      `📊 Recent Sales ${characterType ? `(${formatCharacterType(characterType)})` : ''}`,
      ''
    ];

    sales.forEach((sale, i) => {
      const date = new Date(sale.date).toLocaleDateString();
      output.push(`${i + 1}. NFT #${String(sale.nftId).padStart(4, '0')}`);
      output.push(`   ${sale.price.toFixed(2)} XCH - ${date}`);
      output.push('');
    });

    return output.join('\n');
  }

  if (subcommand === 'trend') {
    const hours = parseInt(params[1], 10) || 24;
    const trend = priceHistory.detectTrend(hours, characterType);
    
    const trendEmoji = {
      'rising': '📈',
      'falling': '📉',
      'stable': '➡️',
      'unknown': '❓'
    };

    const output = [
      `${trendEmoji[trend.trend]} Price Trend (${hours}h)`,
      '',
      `Direction: ${trend.trend.toUpperCase()}`,
      `Confidence: ${trend.confidence}%`,
      characterType ? `Character: ${formatCharacterType(characterType)}` : 'Collection-wide',
      '',
      '⚠️  Based on limited data. May not reflect actual market.'
    ];

    return output.join('\n');
  }

  if (subcommand === 'stats') {
    const hours = parseInt(params[1], 10) || 24;
    const stats = priceHistory.getPriceStats(hours, characterType);
    
    if (!stats) {
      return `❌ No price data for the last ${hours} hours.`;
    }

    const changeEmoji = stats.change >= 0 ? '📈' : '📉';
    const changeColor = stats.change >= 0 ? '+' : '';

    const output = [
      `📊 Price Statistics (${hours}h)`,
      '',
      `Current: ${stats.current.toFixed(2)} XCH`,
      `Change: ${changeEmoji} ${changeColor}${stats.changePercent}%`,
      `Min: ${stats.min.toFixed(2)} XCH`,
      `Max: ${stats.max.toFixed(2)} XCH`,
      `Average: ${stats.avg.toFixed(2)} XCH`,
      `Data Points: ${stats.dataPoints}`,
      characterType ? `Character: ${formatCharacterType(characterType)}` : 'Collection-wide'
    ];

    return output.join('\n');
  }

  return '❌ Unknown history subcommand. Use: recent, trend, or stats';
}

/**
 * Handle traits command
 */
async function handleTraits(params) {
  const subcommand = params[0] || 'list';

  if (subcommand === 'list') {
    const output = [
      '🎨 Trait Categories:',
      '',
      ...traitAnalyzer.traitTypes.map(t => `  • ${t}`),
      '',
      'Usage: wojak traits <category>',
      'Example: wojak traits Head'
    ];

    return output.join('\n');
  }

  // If subcommand is a trait type, show distribution
  // (This would need actual NFT data to work properly)
  return [
    `🎨 Trait Analysis: ${subcommand}`,
    '',
    '⚠️  Full trait distribution requires collection data.',
    'Feature available when metadata is loaded.'
  ].join('\n');
}

/**
 * Handle track command (start tracking floor prices)
 */
async function handleTrack(params) {
  const characterType = params[0] || null;
  
  const floor = await api.getFloorPrice(characterType);
  
  if (!floor) {
    return `❌ No listings found to track.`;
  }

  priceHistory.recordFloorPrice(floor.priceXch, characterType);
  
  const output = [
    '✅ Price recorded!',
    '',
    formatFloorPrice(floor, characterType),
    '',
    '💡 Tip: Run this periodically to build price history.'
  ];

  return output.join('\n');
}

/**
 * Handle deals command (find underpriced NFTs)
 */
async function handleDeals(params) {
  const threshold = parseFloat(params[0]) || 10; // Default 10% below average
  
  const listings = await api.fetchListings();
  
  if (listings.length === 0) {
    return '❌ No listings available to analyze.';
  }

  // Calculate average price
  const prices = listings.map(l => l.priceXch).filter(p => p !== null);
  const avgPrice = prices.reduce((sum, p) => sum + p, 0) / prices.length;
  
  // Find deals (below average by threshold %)
  const targetPrice = avgPrice * (1 - threshold / 100);
  const deals = listings.filter(l => l.priceXch && l.priceXch < targetPrice);

  if (deals.length === 0) {
    return `❌ No deals found (< ${threshold}% below avg of ${avgPrice.toFixed(2)} XCH)`;
  }

  const sorted = deals.sort((a, b) => a.priceXch - b.priceXch);
  const limited = sorted.slice(0, 10);

  const output = [
    `💎 Found ${deals.length} Deal${deals.length === 1 ? '' : 's'}!`,
    `(${threshold}% below avg price of ${avgPrice.toFixed(2)} XCH)`,
    ''
  ];

  limited.forEach((listing, i) => {
    const savings = ((1 - listing.priceXch / avgPrice) * 100).toFixed(1);
    output.push(`${i + 1}. ${listing.nftName}`);
    output.push(`   ${listing.priceXch.toFixed(2)} XCH (${savings}% off)`);
    output.push('');
  });

  return output.join('\n');
}

/**
 * Check if character type is valid
 */
function isValidCharacterType(type) {
  const ranges = api.getCharacterRanges();
  return type.toLowerCase() in ranges;
}

/**
 * Show help message
 */
function showHelp() {
  return `
🍊 Wojak Farmers Plot NFT Explorer

USAGE:
  wojak <command> [options]

COMMANDS:
  floor [character]    Show floor price (optionally for specific character)
  search <query>       Search NFTs by name or ID
  listings [character] Show current marketplace listings
  characters           List all character types
  nft <id>             Look up specific NFT by ID
  stats                Show collection statistics
  rarity <id>          Estimate rarity for an NFT
  history <cmd>        Price history (recent/trend/stats)
  traits [category]    View trait categories and distribution
  track [character]    Record current floor price for tracking
  deals [threshold]    Find underpriced NFTs (default 10% below avg)
  help                 Show this help message

EXAMPLES:
  wojak floor                    # Collection floor price
  wojak floor wojak              # Wojak character floor
  wojak search "king"            # Search for NFTs with "king"
  wojak search 42                # Find NFT #42
  wojak listings soyjak          # Show Soyjak listings
  wojak nft 1                    # Info about NFT #0001
  wojak rarity 42                # Rarity estimate for #42
  wojak history recent           # Recent sales
  wojak history trend 24         # 24h price trend
  wojak track wojak              # Track Wojak floor price
  wojak deals 15                 # Find deals 15%+ below avg
  wojak traits                   # List trait categories

CHARACTER TYPES:
  wojak, soyjak, waifu, baddie, papa-tang, monkey-zoo
  bepe-wojak, bepe-soyjak, bepe-waifu, bepe-baddie
  alien-wojak, alien-soyjak, alien-waifu, alien-baddie

COLLECTION:
  Total: 4,200 NFTs
  Collection ID: col10hfq4hml2z0z0wutu3a9hvt60qy9fcq4k4dznsfncey4lu6kpt3su7u9ah
  Website: https://wojak.ink
`;
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(showHelp());
    process.exit(0);
  }

  try {
    const output = await handleCommand(args);
    console.log(output);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Export for use as a module
module.exports = { handleCommand };

// Run if called directly
if (require.main === module) {
  main();
}
