#!/usr/bin/env node
/**
 * Yahoo Data Fetcher – Stock Quote skill
 * Entry point for Clawdbot
 */

const YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote";

function parseSymbols(argv) {
  if (!argv.length) return [];

  const first = argv[0].trim();

  // JSON input mode
  if (first.startsWith("{") || first.startsWith("[")) {
    const parsed = JSON.parse(first);
    if (Array.isArray(parsed)) return parsed.map(String);
    if (parsed && parsed.symbols) {
      return Array.isArray(parsed.symbols)
        ? parsed.symbols.map(String)
        : [String(parsed.symbols)];
    }
    return [];
  }

  // CLI args mode
  return argv
    .join(" ")
    .split(/[\s,]+/)
    .map(s => s.trim())
    .filter(Boolean);
}

function num(x) {
  return typeof x === "number" && Number.isFinite(x) ? x : null;
}

async function main() {
  const symbols = parseSymbols(process.argv.slice(2));

  if (!symbols.length) {
    console.error(JSON.stringify({
      error: "Missing symbols",
      example: [
        "AAPL",
        "AAPL MSFT TSLA",
        '{ "symbols": ["AAPL", "MSFT"] }'
      ]
    }, null, 2));
    process.exit(2);
  }

  const url = new URL(YAHOO_QUOTE_URL);
  url.searchParams.set("symbols", symbols.join(","));

  const res = await fetch(url.toString(), {
    headers: {
      "User-Agent": "clawdbot-yahoo-data-fetcher/1.0"
    }
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Yahoo request failed (${res.status}): ${body.slice(0, 200)}`);
  }

  const json = await res.json();
  const results = json?.quoteResponse?.result ?? [];

  const output = results.map(q => ({
    symbol: q?.symbol ?? null,
    price: num(q?.regularMarketPrice),
    change: num(q?.regularMarketChange),
    changePercent: num(q?.regularMarketChangePercent),
    currency: q?.currency ?? null,
    marketState: q?.marketState ?? null
  }));

  // Handle symbols Yahoo didn't return
  const seen = new Set(output.map(o => o.symbol));
  for (const s of symbols) {
    if (!seen.has(s)) {
      output.push({
        symbol: s,
        price: null,
        change: null,
        changePercent: null,
        currency: null,
        marketState: null
      });
    }
  }

  process.stdout.write(JSON.stringify(output, null, 2) + "\n");
}

main().catch(err => {
  console.error(JSON.stringify({
    error: err.message || String(err)
  }, null, 2));
  process.exit(1);
});