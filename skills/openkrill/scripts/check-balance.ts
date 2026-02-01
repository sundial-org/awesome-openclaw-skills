#!/usr/bin/env npx ts-node

/**
 * check-balance.ts
 * 
 * Check USDC and ETH balance for a wallet address on Base chain.
 * 
 * Usage:
 *   npx ts-node check-balance.ts <wallet-address> [--chain <chain-id>]
 * 
 * Environment:
 *   THIRDWEB_SECRET_KEY - Required thirdweb project secret key
 */

// Common token addresses
const TOKENS = {
  // Base Mainnet (Chain ID: 8453)
  "8453": {
    USDC: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    name: "Base"
  },
  // Base Sepolia Testnet (Chain ID: 84532)
  "84532": {
    USDC: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    name: "Base Sepolia"
  },
  // Arbitrum One (Chain ID: 42161)
  "42161": {
    USDC: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    name: "Arbitrum"
  }
};

const DEFAULT_CHAIN_ID = "8453"; // Base Mainnet

interface BalanceResult {
  success: boolean;
  address?: string;
  chain?: string;
  chainId?: string;
  balances?: {
    eth: string;
    usdc: string;
    usdcRaw: string;
  };
  funded?: boolean;
  error?: string;
}

async function getEthBalance(address: string, chainId: string, secretKey: string): Promise<string> {
  // Using thirdweb RPC or a public RPC
  const rpcUrls: Record<string, string> = {
    "8453": "https://mainnet.base.org",
    "84532": "https://sepolia.base.org",
    "42161": "https://arb1.arbitrum.io/rpc"
  };

  const rpcUrl = rpcUrls[chainId] || rpcUrls[DEFAULT_CHAIN_ID];

  try {
    const response = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_getBalance",
        params: [address, "latest"],
        id: 1
      })
    });

    const data = await response.json();
    const balanceWei = BigInt(data.result || "0");
    const balanceEth = Number(balanceWei) / 1e18;
    return balanceEth.toFixed(6);
  } catch {
    return "0.000000";
  }
}

async function getUsdcBalance(address: string, chainId: string, secretKey: string): Promise<{ formatted: string; raw: string }> {
  const tokenConfig = TOKENS[chainId as keyof typeof TOKENS] || TOKENS[DEFAULT_CHAIN_ID];
  const usdcAddress = tokenConfig.USDC;

  const rpcUrls: Record<string, string> = {
    "8453": "https://mainnet.base.org",
    "84532": "https://sepolia.base.org",
    "42161": "https://arb1.arbitrum.io/rpc"
  };

  const rpcUrl = rpcUrls[chainId] || rpcUrls[DEFAULT_CHAIN_ID];

  // ERC20 balanceOf(address) selector: 0x70a08231
  const data = `0x70a08231000000000000000000000000${address.slice(2).toLowerCase()}`;

  try {
    const response = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_call",
        params: [{ to: usdcAddress, data }, "latest"],
        id: 1
      })
    });

    const result = await response.json();
    const balanceRaw = BigInt(result.result || "0");
    // USDC has 6 decimals
    const balanceFormatted = Number(balanceRaw) / 1e6;
    return {
      formatted: balanceFormatted.toFixed(2),
      raw: balanceRaw.toString()
    };
  } catch {
    return { formatted: "0.00", raw: "0" };
  }
}

async function checkBalance(address: string, chainId: string = DEFAULT_CHAIN_ID): Promise<BalanceResult> {
  const secretKey = process.env.THIRDWEB_SECRET_KEY;
  
  if (!secretKey) {
    return {
      success: false,
      error: "THIRDWEB_SECRET_KEY environment variable is not set"
    };
  }

  // Validate address format
  if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
    return {
      success: false,
      error: "Invalid Ethereum address format"
    };
  }

  const tokenConfig = TOKENS[chainId as keyof typeof TOKENS] || TOKENS[DEFAULT_CHAIN_ID];

  try {
    const [ethBalance, usdcBalance] = await Promise.all([
      getEthBalance(address, chainId, secretKey),
      getUsdcBalance(address, chainId, secretKey)
    ]);

    const ethNum = parseFloat(ethBalance);
    const usdcNum = parseFloat(usdcBalance.formatted);

    // Consider wallet "funded" if it has at least 0.001 ETH for gas and $1 USDC
    const funded = ethNum >= 0.001 && usdcNum >= 1;

    return {
      success: true,
      address,
      chain: tokenConfig.name,
      chainId,
      balances: {
        eth: ethBalance,
        usdc: usdcBalance.formatted,
        usdcRaw: usdcBalance.raw
      },
      funded
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  
  const address = args.find(arg => arg.startsWith("0x"));
  const chainIndex = args.indexOf("--chain");
  const chainId = chainIndex !== -1 ? args[chainIndex + 1] : DEFAULT_CHAIN_ID;

  if (!address) {
    console.error("Usage: npx ts-node check-balance.ts <wallet-address> [--chain <chain-id>]");
    console.error("\nSupported chains:");
    Object.entries(TOKENS).forEach(([id, config]) => {
      console.error(`  ${id}: ${config.name}`);
    });
    process.exit(1);
  }

  console.log(`Checking balance for: ${address}`);
  console.log(`Chain: ${TOKENS[chainId as keyof typeof TOKENS]?.name || "Unknown"} (${chainId})\n`);

  const result = await checkBalance(address, chainId);

  if (result.success && result.balances) {
    console.log("Balances:");
    console.log(`  ETH:  ${result.balances.eth} ETH`);
    console.log(`  USDC: $${result.balances.usdc}`);
    console.log();
    
    if (result.funded) {
      console.log("✓ Wallet is funded and ready for x402 payments");
    } else {
      console.log("⚠ Wallet needs funding:");
      if (parseFloat(result.balances.eth) < 0.001) {
        console.log("  - Add ETH for gas fees (minimum 0.001 ETH recommended)");
      }
      if (parseFloat(result.balances.usdc) < 1) {
        console.log("  - Add USDC for payments (minimum $1 recommended)");
      }
      console.log(`\nFund this address on ${result.chain}:`);
      console.log(`  ${address}`);
    }
  } else {
    console.error("✗ Failed to check balance");
    console.error("Error:", result.error);
    process.exit(1);
  }
}

// Export for use as a module
export { checkBalance, BalanceResult };

// Run CLI if executed directly
main().catch(console.error);
