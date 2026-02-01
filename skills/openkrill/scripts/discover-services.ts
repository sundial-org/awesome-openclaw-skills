#!/usr/bin/env npx ts-node

/**
 * discover-services.ts
 * 
 * Query the x402 Bazaar discovery endpoint to find x402-compatible services
 * that agents can use for micropayments.
 * 
 * The Bazaar is a machine-readable catalog that helps developers and AI agents
 * find and integrate with x402-compatible API endpoints.
 * 
 * Usage:
 *   npx ts-node discover-services.ts [options]
 * 
 * Options:
 *   --limit <number>    Number of results to return (default: 20, max: 100)
 *   --offset <number>   Pagination offset (default: 0)
 *   --type <string>     Filter by resource type (default: "http")
 *   --facilitator <url> Custom facilitator URL (default: x402.org/facilitator)
 *   --json              Output raw JSON instead of formatted text
 *   --verbose           Show detailed information including schemas
 */

interface PaymentOption {
  scheme: string;
  network: string;
  amount: string;
  asset: string;
  payTo: string;
}

interface DiscoveredResource {
  resource: string;
  type: string;
  x402Version: number;
  accepts: PaymentOption[];
  lastUpdated: string;
  metadata?: {
    description?: string;
    mimeType?: string;
    input?: unknown;
    output?: unknown;
  };
}

interface DiscoveryResponse {
  x402Version: number;
  items: DiscoveredResource[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
  };
}

interface DiscoverOptions {
  limit?: number;
  offset?: number;
  type?: string;
  facilitatorUrl?: string;
}

const DEFAULT_FACILITATOR = "https://x402.org/facilitator";
const CDP_FACILITATOR = "https://api.cdp.coinbase.com/platform/v2/x402";

/**
 * Query the x402 Bazaar discovery endpoint
 */
async function discoverServices(options: DiscoverOptions = {}): Promise<DiscoveryResponse | null> {
  const {
    limit = 20,
    offset = 0,
    type = "http",
    facilitatorUrl = DEFAULT_FACILITATOR
  } = options;

  const params = new URLSearchParams();
  params.set("limit", limit.toString());
  params.set("offset", offset.toString());
  if (type) {
    params.set("type", type);
  }

  const url = `${facilitatorUrl}/discovery/resources?${params.toString()}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      console.error(`Discovery request failed with status ${response.status}`);
      return null;
    }

    const data = await response.json();
    return data as DiscoveryResponse;
  } catch (error) {
    console.error("Error querying discovery endpoint:", error instanceof Error ? error.message : error);
    return null;
  }
}

/**
 * Format payment amount for display
 */
function formatPayment(accept: PaymentOption): string {
  // Convert amount to human-readable format (assuming 6 decimals for USDC)
  const amount = parseInt(accept.amount, 10);
  const usdcAmount = amount / 1_000_000;
  
  // Determine network name
  const networkNames: Record<string, string> = {
    "eip155:8453": "Base",
    "eip155:84532": "Base Sepolia",
    "eip155:1": "Ethereum",
    "eip155:42161": "Arbitrum"
  };
  const networkName = networkNames[accept.network] || accept.network;
  
  return `$${usdcAmount.toFixed(4)} USDC on ${networkName}`;
}

/**
 * Print a discovered resource in human-readable format
 */
function printResource(resource: DiscoveredResource, index: number, verbose: boolean): void {
  console.log(`\n${index + 1}. ${resource.resource}`);
  console.log(`   Type: ${resource.type}`);
  console.log(`   x402 Version: ${resource.x402Version}`);
  console.log(`   Last Updated: ${new Date(resource.lastUpdated).toLocaleDateString()}`);
  
  if (resource.accepts.length > 0) {
    console.log(`   Payment Options:`);
    resource.accepts.forEach((accept, i) => {
      console.log(`     ${i + 1}. ${formatPayment(accept)}`);
      if (verbose) {
        console.log(`        Scheme: ${accept.scheme}`);
        console.log(`        Pay To: ${accept.payTo}`);
        console.log(`        Asset:  ${accept.asset}`);
      }
    });
  }
  
  if (resource.metadata) {
    if (resource.metadata.description) {
      console.log(`   Description: ${resource.metadata.description}`);
    }
    if (resource.metadata.mimeType) {
      console.log(`   MIME Type: ${resource.metadata.mimeType}`);
    }
    if (verbose && resource.metadata.input) {
      console.log(`   Input Schema: ${JSON.stringify(resource.metadata.input, null, 2)}`);
    }
    if (verbose && resource.metadata.output) {
      console.log(`   Output Schema: ${JSON.stringify(resource.metadata.output, null, 2)}`);
    }
  }
}

/**
 * Generate example fetch command for a resource
 */
function generateExample(resource: DiscoveredResource): string {
  // Extract method from metadata if available, default to GET
  const method = "GET";
  
  return `npx ts-node fetch-with-payment.ts \\
    --url "${resource.resource}" \\
    --method "${method}"`;
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  
  const getArg = (name: string): string | undefined => {
    const index = args.indexOf(`--${name}`);
    return index !== -1 ? args[index + 1] : undefined;
  };

  const hasFlag = (name: string): boolean => args.includes(`--${name}`);

  const limit = parseInt(getArg("limit") || "20", 10);
  const offset = parseInt(getArg("offset") || "0", 10);
  const type = getArg("type") || "http";
  const facilitatorUrl = getArg("facilitator") || DEFAULT_FACILITATOR;
  const jsonOutput = hasFlag("json");
  const verbose = hasFlag("verbose");

  if (hasFlag("help") || hasFlag("h")) {
    console.log(`
x402 Bazaar Service Discovery
==============================

Query the x402 Bazaar to discover x402-compatible API endpoints.

Usage:
  npx ts-node discover-services.ts [options]

Options:
  --limit <number>       Number of results (default: 20, max: 100)
  --offset <number>      Pagination offset (default: 0)
  --type <string>        Resource type filter (default: "http")
  --facilitator <url>    Facilitator URL (default: ${DEFAULT_FACILITATOR})
  --json                 Output raw JSON
  --verbose              Show detailed schemas
  --help                 Show this help message

Facilitators:
  Default:  ${DEFAULT_FACILITATOR}
  CDP:      ${CDP_FACILITATOR}

Examples:
  # Discover first 20 services
  npx ts-node discover-services.ts

  # Get more results with pagination
  npx ts-node discover-services.ts --limit 50 --offset 0

  # Use CDP facilitator
  npx ts-node discover-services.ts --facilitator "${CDP_FACILITATOR}"

  # Output as JSON for programmatic use
  npx ts-node discover-services.ts --json
`);
    return;
  }

  if (!jsonOutput) {
    console.log("x402 Bazaar Service Discovery");
    console.log("==============================");
    console.log(`\nQuerying: ${facilitatorUrl}/discovery/resources`);
    console.log(`Filters: type=${type}, limit=${limit}, offset=${offset}\n`);
  }

  const result = await discoverServices({
    limit,
    offset,
    type,
    facilitatorUrl
  });

  if (!result) {
    console.error("\nFailed to query discovery endpoint.");
    console.error("Try using a different facilitator:");
    console.error(`  --facilitator "${CDP_FACILITATOR}"`);
    process.exit(1);
  }

  if (jsonOutput) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const { items, pagination } = result;

  if (items.length === 0) {
    console.log("No services found matching your criteria.");
    return;
  }

  console.log(`Found ${pagination.total} total services (showing ${items.length}):`);

  items.forEach((resource, index) => {
    printResource(resource, offset + index, verbose);
  });

  // Pagination info
  console.log("\n---");
  console.log(`Page: ${Math.floor(offset / limit) + 1} of ${Math.ceil(pagination.total / limit)}`);
  
  if (offset + limit < pagination.total) {
    console.log(`\nNext page: npx ts-node discover-services.ts --offset ${offset + limit} --limit ${limit}`);
  }

  // Example usage
  if (items.length > 0) {
    console.log("\nTo use a discovered service:");
    console.log("  1. Check wallet balance: npx ts-node check-balance.ts");
    console.log("  2. Fund wallet if needed: npx ts-node fund-wallet.ts");
    console.log(`  3. Call the service:\n     ${generateExample(items[0])}`);
  }

  console.log("\nMore info: https://docs.cdp.coinbase.com/x402/bazaar");
}

// Export for use as a module
export { discoverServices, DiscoverOptions, DiscoveryResponse, DiscoveredResource, PaymentOption };

// Run CLI if executed directly
main().catch(console.error);
