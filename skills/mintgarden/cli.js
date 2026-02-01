#!/usr/bin/env node

const MintGardenAPI = require('./lib/api');
const { handleCommand } = require('./index');

const api = new MintGardenAPI();

// CLI interface
(async () => {
  const [,, ...args] = process.argv;
  const input = args.join(' ').trim();

  if (!input || input === 'help' || input === '--help' || input === '-h') {
    console.log(showHelp());
    process.exit(0);
  }

  try {
    const output = await handleCommand(input);
    console.log(output);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
})();

function showHelp() {
  return `🌱 MintGarden API Client

SEARCH
  mg search <query>              Search everything
  mg search nfts "query"         Search NFTs
  mg search collections "query"  Search collections

COLLECTIONS
  mg collections list            List top collections
  mg collection <id>             Get collection details
  mg collection nfts <id>        Get NFTs in collection
  mg collection stats <id>       Get collection statistics
  mg collection activity <id>    Get collection activity

NFTs
  mg nft <launcher_id>           Get NFT details
  mg nft history <launcher_id>   Get NFT trade history
  mg nft offers <launcher_id>    Get active offers

PROFILES
  mg profile <username|did>      Get profile details
  mg profile nfts <username|did> Get profile's NFTs
  mg profile activity <username> Get profile activity

EVENTS
  mg events                      Get recent global events
  mg events <collection_id>      Get collection events

STATS
  mg stats                       Get global stats
  mg trending                    Get trending collections
  mg top collectors              Get top collectors
  mg top traders                 Get top traders

SHORTCUTS
  mg col1abc...                  Get collection by ID
  mg nft1abc...                  Get NFT by launcher ID
  mg did:chia:...                Get profile by DID

Use 'mg help' anytime for this message.`;
}
