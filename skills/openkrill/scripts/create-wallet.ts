#!/usr/bin/env npx ts-node

/**
 * create-wallet.ts
 * 
 * Create or retrieve a server wallet via thirdweb API.
 * The same identifier always returns the same wallet address.
 * 
 * Usage:
 *   npx ts-node create-wallet.ts [identifier]
 * 
 * Environment:
 *   THIRDWEB_SECRET_KEY - Required thirdweb project secret key
 */

interface WalletProfile {
  type: string;
  identifier: string;
}

interface WalletResult {
  success: boolean;
  address?: string;
  userId?: string;
  profiles?: WalletProfile[];
  createdAt?: string;
  error?: string;
}

const THIRDWEB_API_BASE = "https://api.thirdweb.com";
const DEFAULT_IDENTIFIER = "x402-agent-wallet";

async function createWallet(identifier: string = DEFAULT_IDENTIFIER): Promise<WalletResult> {
  const secretKey = process.env.THIRDWEB_SECRET_KEY;
  
  if (!secretKey) {
    return {
      success: false,
      error: "THIRDWEB_SECRET_KEY environment variable is not set"
    };
  }

  try {
    const response = await fetch(`${THIRDWEB_API_BASE}/v1/wallets/server`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-secret-key": secretKey
      },
      body: JSON.stringify({ identifier })
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data?.message || `Failed to create wallet: ${response.status}`
      };
    }

    const result = data.result || data;
    
    return {
      success: true,
      address: result.address,
      userId: result.userId,
      profiles: result.profiles,
      createdAt: result.createdAt
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

async function listWallets(limit: number = 50, page: number = 1): Promise<{
  success: boolean;
  wallets?: Array<{
    address: string;
    profiles: WalletProfile[];
    createdAt: string;
  }>;
  error?: string;
}> {
  const secretKey = process.env.THIRDWEB_SECRET_KEY;
  
  if (!secretKey) {
    return {
      success: false,
      error: "THIRDWEB_SECRET_KEY environment variable is not set"
    };
  }

  try {
    const response = await fetch(
      `${THIRDWEB_API_BASE}/v1/wallets/server?limit=${limit}&page=${page}`,
      {
        method: "GET",
        headers: {
          "x-secret-key": secretKey
        }
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data?.message || `Failed to list wallets: ${response.status}`
      };
    }

    return {
      success: true,
      wallets: data.result?.wallets || []
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
  const command = args[0];

  if (command === "list") {
    console.log("Listing server wallets...\n");
    const result = await listWallets();
    
    if (result.success && result.wallets) {
      if (result.wallets.length === 0) {
        console.log("No wallets found.");
      } else {
        console.log(`Found ${result.wallets.length} wallet(s):\n`);
        result.wallets.forEach((wallet, index) => {
          console.log(`${index + 1}. Address: ${wallet.address}`);
          console.log(`   Created: ${wallet.createdAt}`);
          if (wallet.profiles?.length) {
            const serverProfile = wallet.profiles.find(p => p.type === "server");
            if (serverProfile) {
              console.log(`   Identifier: ${serverProfile.identifier}`);
            }
          }
          console.log();
        });
      }
    } else {
      console.error("Error:", result.error);
      process.exit(1);
    }
    return;
  }

  // Default: create/get wallet
  const identifier = command || DEFAULT_IDENTIFIER;
  
  console.log(`Creating/retrieving wallet with identifier: ${identifier}\n`);
  
  const result = await createWallet(identifier);

  if (result.success) {
    console.log("✓ Wallet ready");
    console.log(`  Address: ${result.address}`);
    console.log(`  User ID: ${result.userId}`);
    console.log(`  Created: ${result.createdAt}`);
    console.log(`\nUse this address with --from parameter in fetch-with-payment.ts`);
  } else {
    console.error("✗ Failed to create wallet");
    console.error("Error:", result.error);
    process.exit(1);
  }
}

// Export for use as a module
export { createWallet, listWallets, WalletResult };

// Run CLI if executed directly
main().catch(console.error);
