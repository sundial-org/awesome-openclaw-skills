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
  return `💱 Dexie.space API Client

OFFERS
  dex offers               List active offers
  dex offers completed     List completed offers
  dex offer <id>           Get offer details

TOKENS/ASSETS
  dex assets               List top tokens by volume
  dex asset <id|code>      Get token details
  dex search <query>       Search tokens
  dex price <code>         Get token price

PAIRS
  dex pairs                List trading pairs

STATS
  dex stats                Get platform statistics

SHORTCUTS
  dex <token>              Get token price (e.g., dex SBX)

Use 'dex help' anytime for this message.`;
}
