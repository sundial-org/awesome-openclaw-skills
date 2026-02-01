#!/usr/bin/env bun
/**
 * Create a purchase order AND sign/submit the Base/EVM transaction.
 *
 * Usage:
 *   # Amazon product (by ASIN)
 *   bun run buy_and_sign_base.ts --asin B0CXYZ1234 --email buyer@example.com --wallet 0x1234... --private-key 0xabc... --address "John Doe,123 Main St,New York,NY,10001,US"
 *
 *   # Shopify product (requires URL + variant)
 *   bun run buy_and_sign_base.ts --url "https://store.com/products/item" --variant 41913945718867 --email buyer@example.com --wallet 0x1234... --private-key 0xabc... --address "..."
 *
 * Required packages:
 *   bun add viem
 */

import {
  createWalletClient,
  http,
  parseTransaction,
  type TransactionSerializable,
} from "viem";
import { base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";

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
  rpcUrl: string = "https://mainnet.base.org"
): Promise<{ success: boolean; hash?: string; explorerUrl?: string; error?: string }> {
  // Format private key
  let formattedKey: `0x${string}`;
  try {
    formattedKey = privateKey.startsWith("0x")
      ? (privateKey as `0x${string}`)
      : (`0x${privateKey}` as `0x${string}`);

    if (!/^0x[a-fA-F0-9]{64}$/.test(formattedKey)) {
      return { success: false, error: "Invalid private key format (must be 32 bytes hex)" };
    }
  } catch (e) {
    return { success: false, error: `Invalid private key: ${e}` };
  }

  // Create account
  let account;
  try {
    account = privateKeyToAccount(formattedKey);
  } catch (e) {
    return { success: false, error: `Failed to create account: ${e}` };
  }

  // Parse transaction
  let tx: TransactionSerializable;
  try {
    const formattedTx = serializedTx.startsWith("0x")
      ? (serializedTx as `0x${string}`)
      : (`0x${serializedTx}` as `0x${string}`);
    tx = parseTransaction(formattedTx);
  } catch (e) {
    return { success: false, error: `Invalid transaction: ${e}` };
  }

  // Create wallet client and send
  const client = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl),
  });

  try {
    const hash = await client.sendTransaction({
      to: tx.to,
      data: tx.data,
      value: tx.value,
      gas: tx.gas,
      maxFeePerGas: tx.maxFeePerGas,
      maxPriorityFeePerGas: tx.maxPriorityFeePerGas,
    });

    return {
      success: true,
      hash,
      explorerUrl: `https://basescan.org/tx/${hash}`,
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
Usage: bun run buy_and_sign_base.ts [options]

Options:
  --asin <asin>           Amazon ASIN
  --url <url>             Product URL (Amazon or Shopify)
  --variant <id>          Variant ID (required for Shopify)
  --email <email>         Buyer email (required)
  --wallet <address>      Base/EVM wallet address 0x... (required)
  --private-key <key>     Hex private key 0x... for signing (required)
  --address <addr>        Shipping address (required)
  --rpc-url <url>         Base RPC URL (default: https://mainnet.base.org)
  --json                  Output raw JSON

Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"

Required packages:
  bun add viem
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

  // Validate wallet is EVM format
  if (!/^0x[a-fA-F0-9]{40}$/.test(options.wallet)) {
    console.error("❌ Error: --wallet must be a valid EVM address (0x...)");
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
    console.log("📦 Creating order on Base...");
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
    console.log("🔐 Signing and submitting Base transaction...");
    const txResult = await signAndSendTransaction(
      orderResult.serializedTransaction,
      options.privateKey,
      options.rpcUrl || "https://mainnet.base.org"
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
    console.log(`   Hash:     ${txResult.hash}`);
    console.log(`   Explorer: ${txResult.explorerUrl}`);
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    process.exit(1);
  }
}

main();
