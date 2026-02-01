#!/usr/bin/env bun
/**
 * Create a purchase order AND sign/submit the Solana transaction.
 *
 * Usage:
 *   # Amazon product (by ASIN)
 *   bun run buy_and_sign.ts --asin B0CXYZ1234 --email buyer@example.com --wallet 7xKXtg... --private-key 5abc... --address "John Doe,123 Main St,New York,NY,10001,US"
 *
 *   # Shopify product (requires URL + variant)
 *   bun run buy_and_sign.ts --url "https://store.com/products/item" --variant 41913945718867 --email buyer@example.com --wallet 7xKXtg... --private-key 5abc... --address "..."
 *
 * Required packages:
 *   bun add @solana/web3.js bs58
 */

import { Connection, Keypair, VersionedTransaction, clusterApiUrl } from "@solana/web3.js";
import bs58 from "bs58";

const BASE_URL = "https://api.purch.xyz";

interface ShippingAddress {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  phone?: string;
}

interface OrderResponse {
  orderId: string;
  status: string;
  serializedTransaction: string;
  product: {
    title: string;
    imageUrl?: string;
    price: { amount: string; currency: string };
  };
  totalPrice: { amount: string; currency: string };
  checkoutUrl: string;
}

function parseAddress(addressStr: string): ShippingAddress {
  const parts = addressStr.split(",").map((p) => p.trim());
  if (parts.length < 6) {
    throw new Error("Address must have at least: Name,Line1,City,State,PostalCode,Country");
  }

  const address: ShippingAddress = {
    name: parts[0],
    line1: parts[1],
    city: parts[2],
    state: parts[3],
    postalCode: parts[4],
    country: parts[5],
  };

  if (parts[6]) address.line2 = parts[6];
  if (parts[7]) address.phone = parts[7];

  return address;
}

async function createOrder(params: {
  email: string;
  walletAddress: string;
  shippingAddress: ShippingAddress;
  asin?: string;
  productUrl?: string;
  variantId?: string;
}): Promise<OrderResponse> {
  const response = await fetch(`${BASE_URL}/buy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`HTTP ${response.status}: ${error}`);
  }

  return response.json();
}

async function signAndSendTransaction(
  serializedTx: string,
  privateKey: string,
  rpcUrl: string = clusterApiUrl("mainnet-beta")
): Promise<{ success: boolean; signature?: string; explorerUrl?: string; error?: string }> {
  // Decode private key
  let keypair: Keypair;
  try {
    const keyBytes = bs58.decode(privateKey);
    keypair = Keypair.fromSecretKey(keyBytes);
  } catch (e) {
    return { success: false, error: `Invalid private key: ${e}` };
  }

  // Decode transaction
  let transaction: VersionedTransaction;
  try {
    const txBytes = bs58.decode(serializedTx);
    transaction = VersionedTransaction.deserialize(txBytes);
  } catch (e) {
    return { success: false, error: `Invalid transaction: ${e}` };
  }

  // Sign
  try {
    transaction.sign([keypair]);
  } catch (e) {
    return { success: false, error: `Failed to sign: ${e}` };
  }

  // Send
  const connection = new Connection(rpcUrl, "confirmed");

  try {
    const signature = await connection.sendRawTransaction(transaction.serialize(), {
      skipPreflight: false,
    });
    await connection.confirmTransaction(signature, "confirmed");

    return {
      success: true,
      signature,
      explorerUrl: `https://solscan.io/tx/${signature}`,
    };
  } catch (e) {
    return { success: false, error: `Transaction failed: ${e}` };
  }
}

function parseArgs(args: string[]): {
  asin?: string;
  url?: string;
  variant?: string;
  email?: string;
  wallet?: string;
  privateKey?: string;
  address?: string;
  rpcUrl?: string;
  json?: boolean;
} {
  const result: ReturnType<typeof parseArgs> = {};
  let i = 0;

  while (i < args.length) {
    const arg = args[i];
    if (arg === "--asin" && args[i + 1]) result.asin = args[++i];
    else if (arg === "--url" && args[i + 1]) result.url = args[++i];
    else if (arg === "--variant" && args[i + 1]) result.variant = args[++i];
    else if (arg === "--email" && args[i + 1]) result.email = args[++i];
    else if (arg === "--wallet" && args[i + 1]) result.wallet = args[++i];
    else if (arg === "--private-key" && args[i + 1]) result.privateKey = args[++i];
    else if (arg === "--address" && args[i + 1]) result.address = args[++i];
    else if (arg === "--rpc-url" && args[i + 1]) result.rpcUrl = args[++i];
    else if (arg === "--json") result.json = true;
    i++;
  }

  return result;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
Usage: bun run buy_and_sign.ts [options]

Options:
  --asin <asin>           Amazon ASIN
  --url <url>             Product URL (Amazon or Shopify)
  --variant <id>          Variant ID (required for Shopify)
  --email <email>         Buyer email (required)
  --wallet <address>      Solana wallet address (required)
  --private-key <key>     Base58 private key for signing (required)
  --address <addr>        Shipping address (required)
  --rpc-url <url>         Solana RPC URL (default: mainnet-beta)
  --json                  Output raw JSON

Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"
    `);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.asin && !options.url) {
    console.error("❌ Error: Either --asin or --url is required");
    process.exit(1);
  }
  if (!options.email || !options.wallet || !options.privateKey || !options.address) {
    console.error("❌ Error: --email, --wallet, --private-key, and --address are required");
    process.exit(1);
  }

  let shippingAddress: ShippingAddress;
  try {
    shippingAddress = parseAddress(options.address);
  } catch (e) {
    console.error(`❌ Error: ${e}`);
    process.exit(1);
  }

  try {
    // Step 1: Create order
    console.log("📦 Creating order...");
    const orderResult = await createOrder({
      email: options.email,
      walletAddress: options.wallet,
      shippingAddress,
      asin: options.asin,
      productUrl: options.url,
      variantId: options.variant,
    });

    console.log(`✅ Order created: ${orderResult.orderId}`);
    console.log(`   Product: ${orderResult.product?.title ?? "N/A"}`);
    console.log(`   Total: ${orderResult.totalPrice?.amount ?? "N/A"} ${(orderResult.totalPrice?.currency ?? "USDC").toUpperCase()}`);
    console.log();

    // Step 2: Sign and submit transaction
    console.log("🔐 Signing and submitting transaction...");
    const txResult = await signAndSendTransaction(
      orderResult.serializedTransaction,
      options.privateKey,
      options.rpcUrl || clusterApiUrl("mainnet-beta")
    );

    if (options.json) {
      console.log(JSON.stringify({ order: orderResult, transaction: txResult }, null, 2));
      return;
    }

    if (!txResult.success) {
      console.error(`❌ Transaction failed: ${txResult.error}`);
      console.log();
      console.log(`🌐 You can complete payment via browser: ${orderResult.checkoutUrl}`);
      process.exit(1);
    }

    console.log("✅ Payment complete!");
    console.log(`   Signature: ${txResult.signature}`);
    console.log(`   Explorer:  ${txResult.explorerUrl}`);
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    process.exit(1);
  }
}

main();
