#!/usr/bin/env bun
/**
 * Create a purchase order (without signing the transaction).
 *
 * Usage:
 *   # Amazon product (by ASIN)
 *   bun run buy.ts --asin B0CXYZ1234 --email buyer@example.com --wallet 7xKXtg... --address "John Doe,123 Main St,New York,NY,10001,US"
 *
 *   # Amazon product (by URL)
 *   bun run buy.ts --url "https://amazon.com/dp/B0CXYZ1234" --email buyer@example.com --wallet 7xKXtg... --address "..."
 *
 *   # Shopify product (requires URL + variant)
 *   bun run buy.ts --url "https://store.com/products/item" --variant 41913945718867 --email buyer@example.com --wallet 7xKXtg... --address "..."
 *
 * Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"
 */

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

function parseArgs(args: string[]): {
  asin?: string;
  url?: string;
  variant?: string;
  email?: string;
  wallet?: string;
  address?: string;
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
    else if (arg === "--address" && args[i + 1]) result.address = args[++i];
    else if (arg === "--json") result.json = true;
    i++;
  }

  return result;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
Usage: bun run buy.ts [options]

Options:
  --asin <asin>       Amazon ASIN (for Amazon products)
  --url <url>         Product URL (Amazon or Shopify)
  --variant <id>      Variant ID (required for Shopify)
  --email <email>     Buyer email address (required)
  --wallet <address>  Solana wallet address (required)
  --address <addr>    Shipping address (required)
  --json              Output raw JSON

Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"

Examples:
  # Amazon by ASIN
  bun run buy.ts --asin B0CXYZ1234 --email me@example.com --wallet 7xKXtg... --address "John Doe,123 Main St,NYC,NY,10001,US"

  # Shopify product
  bun run buy.ts --url "https://store.com/products/item" --variant 41913945718867 --email me@example.com --wallet 7xKXtg... --address "..."
    `);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.asin && !options.url) {
    console.error("❌ Error: Either --asin or --url is required");
    process.exit(1);
  }
  if (!options.email || !options.wallet || !options.address) {
    console.error("❌ Error: --email, --wallet, and --address are required");
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
    const result = await createOrder({
      email: options.email,
      walletAddress: options.wallet,
      shippingAddress,
      asin: options.asin,
      productUrl: options.url,
      variantId: options.variant,
    });

    if (options.json) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log("✅ Order created successfully!");
    console.log(`   Order ID: ${result.orderId}`);
    console.log(`   Status: ${result.status}`);
    console.log(`   Product: ${result.product?.title ?? "N/A"}`);
    console.log(`   Total: ${result.totalPrice?.amount ?? "N/A"} ${(result.totalPrice?.currency ?? "USDC").toUpperCase()}`);
    console.log();
    console.log("📝 Next step: Sign the serialized transaction to complete payment");
    console.log(`   Transaction: ${result.serializedTransaction.slice(0, 50)}...`);

    if (result.checkoutUrl) {
      console.log();
      console.log(`🌐 Or pay via browser: ${result.checkoutUrl}`);
    }
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    process.exit(1);
  }
}

main();
