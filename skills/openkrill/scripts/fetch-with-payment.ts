#!/usr/bin/env npx ts-node

/**
 * fetch-with-payment.ts
 * 
 * Core x402 fetch wrapper that automatically handles payment flows
 * when APIs return 402 Payment Required responses.
 * 
 * Usage:
 *   npx ts-node fetch-with-payment.ts --url <target-url> --method <HTTP-method> [--body <json-body>] [--from <wallet-address>]
 * 
 * Environment:
 *   THIRDWEB_SECRET_KEY - Required thirdweb project secret key
 */

interface FetchWithPaymentOptions {
  url: string;
  method: string;
  body?: Record<string, unknown>;
  from?: string;
  maxValue?: string;
  asset?: string;
  chainId?: string;
}

interface FetchWithPaymentResult {
  success: boolean;
  status: number;
  data?: unknown;
  error?: string;
}

const THIRDWEB_API_BASE = "https://api.thirdweb.com";

async function fetchWithPayment(options: FetchWithPaymentOptions): Promise<FetchWithPaymentResult> {
  const secretKey = process.env.THIRDWEB_SECRET_KEY;
  
  if (!secretKey) {
    return {
      success: false,
      status: 401,
      error: "THIRDWEB_SECRET_KEY environment variable is not set"
    };
  }

  // Build query parameters
  const params = new URLSearchParams();
  params.set("url", options.url);
  params.set("method", options.method);
  
  if (options.from) {
    params.set("from", options.from);
  }
  if (options.maxValue) {
    params.set("maxValue", options.maxValue);
  }
  if (options.asset) {
    params.set("asset", options.asset);
  }
  if (options.chainId) {
    params.set("chainId", options.chainId);
  }

  const fetchUrl = `${THIRDWEB_API_BASE}/v1/payments/x402/fetch?${params.toString()}`;

  try {
    const response = await fetch(fetchUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-secret-key": secretKey
      },
      body: options.body ? JSON.stringify(options.body) : undefined
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error: data?.message || `Request failed with status ${response.status}`,
        data
      };
    }

    return {
      success: true,
      status: response.status,
      data
    };
  } catch (error) {
    return {
      success: false,
      status: 500,
      error: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
}

// CLI execution
async function main() {
  const args = process.argv.slice(2);
  
  const getArg = (name: string): string | undefined => {
    const index = args.indexOf(`--${name}`);
    return index !== -1 ? args[index + 1] : undefined;
  };

  const url = getArg("url");
  const method = getArg("method") || "GET";
  const bodyStr = getArg("body");
  const from = getArg("from");
  const maxValue = getArg("maxValue");
  const asset = getArg("asset");
  const chainId = getArg("chainId");

  if (!url) {
    console.error("Usage: npx ts-node fetch-with-payment.ts --url <target-url> --method <HTTP-method> [--body <json>] [--from <wallet>]");
    console.error("\nRequired:");
    console.error("  --url      Target API URL to call");
    console.error("\nOptional:");
    console.error("  --method   HTTP method (default: GET)");
    console.error("  --body     JSON body to send");
    console.error("  --from     Wallet address for payment");
    console.error("  --maxValue Maximum payment in wei");
    console.error("  --asset    Payment token address");
    console.error("  --chainId  Chain ID (e.g., eip155:8453)");
    process.exit(1);
  }

  let body: Record<string, unknown> | undefined;
  if (bodyStr) {
    try {
      body = JSON.parse(bodyStr);
    } catch {
      console.error("Error: Invalid JSON body");
      process.exit(1);
    }
  }

  console.log(`Making x402 payment request to: ${url}`);
  console.log(`Method: ${method}`);
  if (from) console.log(`From wallet: ${from}`);
  
  const result = await fetchWithPayment({
    url,
    method,
    body,
    from,
    maxValue,
    asset,
    chainId
  });

  if (result.success) {
    console.log("\n✓ Request successful");
    console.log("Response:", JSON.stringify(result.data, null, 2));
  } else {
    console.error(`\n✗ Request failed (${result.status})`);
    console.error("Error:", result.error);
    if (result.data) {
      console.error("Details:", JSON.stringify(result.data, null, 2));
    }
    process.exit(1);
  }
}

// Export for use as a module
export { fetchWithPayment, FetchWithPaymentOptions, FetchWithPaymentResult };

// Run CLI if executed directly
main().catch(console.error);
