#!/usr/bin/env bun
/**
 * Search products using the Purch API.
 *
 * Usage:
 *   bun run search.ts <query> [--price-min <min>] [--price-max <max>] [--brand <brand>] [--page <page>]
 *
 * Example:
 *   bun run search.ts "wireless headphones" --price-max 100
 *   bun run search.ts "running shoes" --brand Nike
 */

const BASE_URL = "https://api.purch.xyz";

function extractVariantId(url: string | undefined): string | null {
  if (!url) return null;
  const match = url.match(/[?&]variant=(\d+)/);
  return match ? match[1] : null;
}

interface Product {
  id?: string;
  asin?: string;
  title: string;
  price: number;
  currency: string;
  rating?: number;
  reviewCount?: number;
  imageUrl?: string;
  productUrl?: string;
  source: string;
  variantId?: string;
}

interface SearchResponse {
  products: Product[];
  totalResults: number;
  page: number;
  hasMore: boolean;
}

async function searchProducts(
  query: string,
  options: {
    priceMin?: number;
    priceMax?: number;
    brand?: string;
    page?: number;
  } = {}
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });

  if (options.priceMin !== undefined) params.set("priceMin", String(options.priceMin));
  if (options.priceMax !== undefined) params.set("priceMax", String(options.priceMax));
  if (options.brand) params.set("brand", options.brand);
  if (options.page) params.set("page", String(options.page));

  const response = await fetch(`${BASE_URL}/search?${params}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`HTTP ${response.status}: ${error}`);
  }

  return response.json();
}

function parseArgs(args: string[]): {
  query: string;
  priceMin?: number;
  priceMax?: number;
  brand?: string;
  page?: number;
  json?: boolean;
} {
  const result: ReturnType<typeof parseArgs> = { query: "" };
  let i = 0;

  while (i < args.length) {
    const arg = args[i];
    if (arg === "--price-min" && args[i + 1]) {
      result.priceMin = parseFloat(args[++i]);
    } else if (arg === "--price-max" && args[i + 1]) {
      result.priceMax = parseFloat(args[++i]);
    } else if (arg === "--brand" && args[i + 1]) {
      result.brand = args[++i];
    } else if (arg === "--page" && args[i + 1]) {
      result.page = parseInt(args[++i]);
    } else if (arg === "--json") {
      result.json = true;
    } else if (!arg.startsWith("--")) {
      result.query = arg;
    }
    i++;
  }

  return result;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help") {
    console.log(`
Usage: bun run search.ts <query> [options]

Options:
  --price-min <min>   Minimum price filter
  --price-max <max>   Maximum price filter
  --brand <brand>     Brand filter
  --page <page>       Page number (default: 1)
  --json              Output raw JSON
    `);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.query) {
    console.error("❌ Error: Query is required");
    process.exit(1);
  }

  try {
    const result = await searchProducts(options.query, options);

    if (options.json) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log(`📦 Found ${result.totalResults} products (showing ${result.products.length}, page ${result.page})`);
    console.log("-".repeat(60));

    result.products.forEach((product, i) => {
      const title = product.title.slice(0, 50);
      console.log(`${i + 1}. ${title}`);
      console.log(`   💰 ${product.currency} ${product.price} | ⭐ ${product.rating ?? "N/A"} | 🏷️ ${product.source}`);

      if (product.source === "amazon") {
        console.log(`   🛒 ASIN: ${product.asin || product.id || "N/A"}`);
      } else {
        // Shopify
        const variantId = product.variantId || extractVariantId(product.productUrl) || "N/A";
        const cleanUrl = product.productUrl?.split("?")[0] || "N/A";
        console.log(`   🛒 URL: ${cleanUrl}`);
        console.log(`   🔖 Variant ID: ${variantId}`);
      }
      console.log();
    });

    if (result.hasMore) {
      console.log(`📄 More results available. Use --page ${(options.page || 1) + 1} to see next page.`);
    }
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    process.exit(1);
  }
}

main();
