#!/usr/bin/env npx ts-node

/**
 * fund-wallet.ts
 * 
 * Helper script to guide users through funding their x402 wallet.
 * Provides instructions and links for onramping fiat to crypto.
 * 
 * Usage:
 *   npx ts-node fund-wallet.ts <wallet-address> [--amount <usdc-amount>]
 */

interface OnrampProvider {
  name: string;
  url: string;
  description: string;
  supportedChains: string[];
  minAmount: number;
  fees: string;
}

const ONRAMP_PROVIDERS: OnrampProvider[] = [
  {
    name: "Coinbase",
    url: "https://www.coinbase.com/",
    description: "Major US exchange with direct bank transfers and card payments",
    supportedChains: ["Base", "Ethereum", "Arbitrum"],
    minAmount: 1,
    fees: "1.49% - 3.99% depending on payment method"
  },
  {
    name: "Moonpay",
    url: "https://www.moonpay.com/",
    description: "Fiat onramp with card and bank transfer support",
    supportedChains: ["Base", "Ethereum", "Arbitrum", "Polygon"],
    minAmount: 20,
    fees: "1% - 4.5% depending on payment method"
  },
  {
    name: "Transak",
    url: "https://transak.com/",
    description: "Global fiat onramp with wide payment method support",
    supportedChains: ["Base", "Ethereum", "Arbitrum", "Polygon"],
    minAmount: 15,
    fees: "1% - 5% depending on region"
  },
  {
    name: "thirdweb Pay",
    url: "https://thirdweb.com/pay",
    description: "Integrated crypto purchasing within thirdweb ecosystem",
    supportedChains: ["Base", "Ethereum", "Arbitrum", "170+ EVM chains"],
    minAmount: 1,
    fees: "Varies by provider"
  }
];

const CHAIN_INFO = {
  base: {
    name: "Base",
    chainId: "8453",
    usdc: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    explorer: "https://basescan.org/address/",
    bridge: "https://bridge.base.org/"
  },
  arbitrum: {
    name: "Arbitrum",
    chainId: "42161",
    usdc: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    explorer: "https://arbiscan.io/address/",
    bridge: "https://bridge.arbitrum.io/"
  }
};

function generateFundingInstructions(address: string, amount: number = 10): void {
  console.log("╔════════════════════════════════════════════════════════════════╗");
  console.log("║           x402 Wallet Funding Guide                            ║");
  console.log("╚════════════════════════════════════════════════════════════════╝\n");

  console.log(`Wallet Address: ${address}`);
  console.log(`Recommended Amount: $${amount} USDC + ~$1 ETH for gas\n`);

  console.log("═══════════════════════════════════════════════════════════════════");
  console.log("OPTION 1: Direct USDC Transfer (Fastest)");
  console.log("═══════════════════════════════════════════════════════════════════\n");

  console.log("If you already have USDC, send it directly to your wallet:\n");
  console.log("  Network: Base (Chain ID: 8453)");
  console.log(`  Address: ${address}`);
  console.log(`  Amount:  ${amount} USDC`);
  console.log("\n  Also send ~0.005 ETH for gas fees\n");

  console.log("═══════════════════════════════════════════════════════════════════");
  console.log("OPTION 2: Fiat Onramp (Buy with Card/Bank)");
  console.log("═══════════════════════════════════════════════════════════════════\n");

  ONRAMP_PROVIDERS.forEach((provider, index) => {
    console.log(`${index + 1}. ${provider.name}`);
    console.log(`   ${provider.description}`);
    console.log(`   URL: ${provider.url}`);
    console.log(`   Chains: ${provider.supportedChains.join(", ")}`);
    console.log(`   Min: $${provider.minAmount} | Fees: ${provider.fees}`);
    console.log();
  });

  console.log("Steps:");
  console.log("  1. Visit one of the onramp providers above");
  console.log("  2. Select USDC on Base network");
  console.log(`  3. Enter your wallet address: ${address}`);
  console.log(`  4. Purchase at least $${amount} USDC`);
  console.log("  5. Also purchase ~$5 of ETH for gas fees\n");

  console.log("═══════════════════════════════════════════════════════════════════");
  console.log("OPTION 3: Bridge from Another Chain");
  console.log("═══════════════════════════════════════════════════════════════════\n");

  console.log("If you have USDC on Ethereum or another chain:\n");
  console.log("  Base Bridge: https://bridge.base.org/");
  console.log("  Stargate:    https://stargate.finance/");
  console.log("  Across:      https://across.to/\n");

  console.log("═══════════════════════════════════════════════════════════════════");
  console.log("VERIFICATION");
  console.log("═══════════════════════════════════════════════════════════════════\n");

  console.log("After funding, verify your balance:");
  console.log(`  npx ts-node check-balance.ts ${address}\n`);

  console.log("View on block explorer:");
  console.log(`  ${CHAIN_INFO.base.explorer}${address}\n`);

  console.log("═══════════════════════════════════════════════════════════════════");
  console.log("QUICK LINKS");
  console.log("═══════════════════════════════════════════════════════════════════\n");

  console.log(`Copy address: ${address}`);
  console.log(`Base Explorer: ${CHAIN_INFO.base.explorer}${address}`);
  console.log(`Bridge: ${CHAIN_INFO.base.bridge}`);
  console.log(`thirdweb Pay: https://thirdweb.com/pay\n`);
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  
  const address = args.find(arg => arg.startsWith("0x"));
  const amountIndex = args.indexOf("--amount");
  const amount = amountIndex !== -1 ? parseFloat(args[amountIndex + 1]) : 10;

  if (!address) {
    console.error("Usage: npx ts-node fund-wallet.ts <wallet-address> [--amount <usdc-amount>]");
    console.error("\nOptions:");
    console.error("  --amount  Amount of USDC to recommend (default: 10)");
    console.error("\nExample:");
    console.error("  npx ts-node fund-wallet.ts 0x1234...5678 --amount 50");
    process.exit(1);
  }

  // Validate address format
  if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
    console.error("Error: Invalid Ethereum address format");
    process.exit(1);
  }

  generateFundingInstructions(address, amount);
}

// Export for use as a module
export { ONRAMP_PROVIDERS, CHAIN_INFO, generateFundingInstructions };

// Run CLI if executed directly
main().catch(console.error);
