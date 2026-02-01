#!/usr/bin/env bun
/**
 * AI-powered shopping assistant using natural language.
 *
 * Usage:
 *   bun run shop.ts "<message>"
 *
 * Example:
 *   bun run shop.ts "comfortable running shoes under $100"
 *   bun run shop.ts "wireless headphones with good noise cancellation"
 */

const BASE_URL = "https://api.purch.xyz";

function extractVariantId(url: string | undefined): string | null {
  if (!url) return null;
  const match = url.match(/[?&]variant=(\d+)/);
  return match ? match[1] : null;
}

interface Product {
  asin: string;
  title: string;
  price: number;
  currency: string;
  rating?: number;
  reviewCount?: number;
  imageUrl?: string;
  productUrl?: string;
  source: string;
  vendor?: string;
  variantId?: string;
}

interface ShopResponse {
  reply: string;
  products: Product[];
}

interface ShopContext {
  priceRange?: { min?: number; max?: number };
  preferences?: string[];
}

async function shop(message: string, context?: ShopContext): Promise<ShopResponse> {
  const response = await fetch(`${BASE_URL}/shop`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`HTTP ${response.status}: ${error}`);
  }

  return response.json();
}

function parseArgs(args: string[]): {
  message: string;
  priceMin?: number;
  priceMax?: number;
  json?: boolean;
} {
  const result: ReturnType<typeof parseArgs> = { message: "" };
  let i = 0;

  while (i < args.length) {
    const arg = args[i];
    if (arg === "--price-min" && args[i + 1]) {
      result.priceMin = parseFloat(args[++i]);
    } else if (arg === "--price-max" && args[i + 1]) {
      result.priceMax = parseFloat(args[++i]);
    } else if (arg === "--json") {
      result.json = true;
    } else if (!arg.startsWith("--")) {
      result.message = arg;
    }
    i++;
  }

  return result;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
Usage: bun run shop.ts "<message>" [options]

Options:
  --price-min <min>   Minimum price preference
  --price-max <max>   Maximum price preference
  --json              Output raw JSON

Example:
  bun run shop.ts "comfortable running shoes under $100"
    `);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.message) {
    console.error("❌ Error: Message is required");
    process.exit(1);
  }

  // Build context if price preferences provided
  let context: ShopContext | undefined;
  if (options.priceMin !== undefined || options.priceMax !== undefined) {
    context = { priceRange: {} };
    if (options.priceMin !== undefined) context.priceRange!.min = options.priceMin;
    if (options.priceMax !== undefined) context.priceRange!.max = options.priceMax;
  }

  try {
    const result = await shop(options.message, context);

    if (options.json) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    if (result.reply) {
      console.log(`🤖 ${result.reply}`);
      console.log();
    }

    console.log(`📦 Found ${result.products.length} products`);
    console.log("-".repeat(60));

    result.products.forEach((product, i) => {
      const title = product.title.slice(0, 50);
      console.log(`${i + 1}. ${title}`);
      console.log(`   💰 ${product.currency} ${product.price} | ⭐ ${product.rating ?? "N/A"} | 🏷️ ${product.source}`);

      if (product.source === "amazon") {
        console.log(`   🛒 ASIN: ${product.asin}`);
      } else {
        // Shopify
        const variantId = product.variantId || extractVariantId(product.productUrl) || "N/A";
        const cleanUrl = product.productUrl?.split("?")[0] || "N/A";
        console.log(`   🛒 URL: ${cleanUrl}`);
        console.log(`   🔖 Variant ID: ${variantId}`);
      }
      console.log();
    });
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    process.exit(1);
  }
}

main();
