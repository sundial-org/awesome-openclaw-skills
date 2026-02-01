#!/usr/bin/env npx ts-node

/**
 * list-services.ts
 * 
 * List x402-compatible services that support micropayments.
 * 
 * Usage:
 *   npx ts-node list-services.ts [--fetch]
 * 
 * Environment:
 *   THIRDWEB_SECRET_KEY - Required for --fetch option to query live services
 */

interface X402Service {
  name: string;
  description: string;
  endpoint: string;
  methods: string[];
  pricing: string;
  documentation: string;
  example?: {
    method: string;
    body?: Record<string, unknown>;
  };
}

// Known x402-compatible services
const KNOWN_SERVICES: X402Service[] = [
  {
    name: "Browserbase",
    description: "Cloud browser automation platform. Spin up headless browsers for web scraping, testing, and automation.",
    endpoint: "https://api.browserbase.com/v1/sessions",
    methods: ["POST", "GET", "DELETE"],
    pricing: "Pay-per-session, typically $0.01-0.05 per session",
    documentation: "https://docs.browserbase.com/integrations/x402/introduction",
    example: {
      method: "POST",
      body: {
        browserSettings: {
          viewport: { width: 1920, height: 1080 }
        }
      }
    }
  },
  {
    name: "Firecrawl",
    description: "Web scraping and search API. Extract structured data from websites with pay-per-search pricing.",
    endpoint: "https://api.firecrawl.dev/v1/search",
    methods: ["POST"],
    pricing: "Pay-per-search, pricing varies by query complexity",
    documentation: "https://docs.firecrawl.dev/x402/search",
    example: {
      method: "POST",
      body: {
        query: "AI agent frameworks",
        limit: 10
      }
    }
  },
  {
    name: "Firecrawl Scrape",
    description: "Single page scraping endpoint for extracting content from a specific URL.",
    endpoint: "https://api.firecrawl.dev/v1/scrape",
    methods: ["POST"],
    pricing: "Pay-per-scrape",
    documentation: "https://docs.firecrawl.dev/x402/scrape",
    example: {
      method: "POST",
      body: {
        url: "https://example.com",
        formats: ["markdown", "html"]
      }
    }
  }
];

async function fetchLiveServices(): Promise<X402Service[] | null> {
  const secretKey = process.env.THIRDWEB_SECRET_KEY;
  
  if (!secretKey) {
    console.warn("Warning: THIRDWEB_SECRET_KEY not set, cannot fetch live services");
    return null;
  }

  try {
    // Use thirdweb MCP to list payable services if available
    const response = await fetch(
      "https://api.thirdweb.com/mcp?tools=listPayableServices",
      {
        method: "GET",
        headers: {
          "x-secret-key": secretKey
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      // Parse MCP response if available
      return data.services || null;
    }
  } catch {
    // Fall back to static list
  }

  return null;
}

function printService(service: X402Service, index: number): void {
  console.log(`\n${index + 1}. ${service.name}`);
  console.log(`   ${service.description}`);
  console.log(`   Endpoint: ${service.endpoint}`);
  console.log(`   Methods:  ${service.methods.join(", ")}`);
  console.log(`   Pricing:  ${service.pricing}`);
  console.log(`   Docs:     ${service.documentation}`);
  
  if (service.example) {
    console.log(`   Example:`);
    console.log(`     npx ts-node fetch-with-payment.ts \\`);
    console.log(`       --url "${service.endpoint}" \\`);
    console.log(`       --method "${service.example.method}" \\`);
    if (service.example.body) {
      console.log(`       --body '${JSON.stringify(service.example.body)}'`);
    }
  }
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  const shouldFetch = args.includes("--fetch");

  console.log("x402-Compatible Services");
  console.log("========================");
  console.log("\nThese services accept micropayments via the x402 protocol.");
  console.log("Use fetch-with-payment.ts to make paid API calls.\n");

  let services = KNOWN_SERVICES;

  if (shouldFetch) {
    console.log("Fetching live service list...");
    const liveServices = await fetchLiveServices();
    if (liveServices && liveServices.length > 0) {
      services = liveServices;
      console.log("Using live service data.\n");
    } else {
      console.log("Using cached service list.\n");
    }
  }

  services.forEach((service, index) => printService(service, index));

  console.log("\n---");
  console.log("To make a payment request:");
  console.log("  1. Ensure wallet is funded (check-balance.ts)");
  console.log("  2. Use fetch-with-payment.ts with the service endpoint");
  console.log("  3. The x402 protocol handles payment automatically");
  console.log("\nMore services: https://x402.org");
}

// Export for use as a module
export { KNOWN_SERVICES, X402Service, fetchLiveServices };

// Run CLI if executed directly
main().catch(console.error);
