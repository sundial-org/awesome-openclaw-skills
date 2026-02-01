#!/usr/bin/env node

const { handleCommand } = require('./index');

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
  return `🔍 Spacescan.io API Client

⚠️  Requires API Key: Set SPACESCAN_API_KEY environment variable
   Get your key at: https://www.spacescan.io/apis

BLOCKS
  scan block latest         Get latest block
  scan block <height|hash>  Get specific block
  scan blocks <start> <end> Get block range

TRANSACTIONS
  scan tx <id>              Get transaction details

ADDRESSES
  scan address <addr>       Get address info
  scan address balance <a>  Get address balance
  scan address txs <addr>   Get address transactions

COINS
  scan coin <id>            Get coin details

NETWORK
  scan stats                Network statistics
  scan network              Network info
  scan space                Network space
  scan mempool              Mempool status
  scan price                XCH price

TOKENS
  scan cats                 List CAT tokens
  scan cat <id>             Get CAT details

NFTs
  scan nft <id>             Get NFT details

SEARCH
  scan search <query>       Search by hash/address/block
  scan <hash>               Quick search (long hashes)

Use 'scan help' anytime for this message.`;
}
