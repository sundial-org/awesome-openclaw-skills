#!/usr/bin/env node
// Fetch exchange rates from XE.com via Playwright (browserless)
// Usage: node xe-rate.mjs <FROM> <TO> [AMOUNT]
// Example: node xe-rate.mjs USD INR 100

import { chromium } from 'playwright-core';

const CDP_URL = 'ws://localhost:7002?token=ec546a08aed110e96f64cc645bdb58fa8829a63349d6ae53';

const from = (process.argv[2] || 'USD').toUpperCase();
const to = (process.argv[3] || 'INR').toUpperCase();
const amount = parseFloat(process.argv[4] || '1');

if (!from || !to) {
  console.error('Usage: node xe-rate.mjs <FROM> <TO> [AMOUNT]');
  process.exit(1);
}

async function fetchXE() {
  const url = `https://www.xe.com/currencyconverter/convert/?Amount=${amount}&From=${from}&To=${to}`;
  let browser;
  try {
    browser = await chromium.connectOverCDP(CDP_URL);
    const context = browser.contexts()[0] || await browser.newContext();
    const page = await context.newPage();
    await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });

    const result = await page.evaluate((args) => {
      const text = document.body.innerText;
      
      // Extract unit rate: "1.00 USD = 91.67885558 INR"
      const unitMatch = text.match(/1\.00\s+(\w{3})\s*=\s*([\d,.]+)\s+(\w{3})/);
      
      // Extract converted amount from the big display
      // Pattern: the "To" section shows the converted number
      // Look for the amount after "To\n\nTo\n\n"
      const toMatch = text.match(/To\s+To\s+([\d,.]+)\s/);
      
      if (unitMatch) {
        const rate = parseFloat(unitMatch[2].replace(/,/g, ''));
        const converted = toMatch ? parseFloat(toMatch[1].replace(/,/g, '')) : (args.amount * rate);
        return {
          amount: args.amount,
          from: args.from,
          to: args.to,
          rate: rate,
          converted: converted,
          source: 'xe.com (mid-market)',
          timestamp: new Date().toISOString()
        };
      }
      return null;
    }, { amount, from, to });

    await page.close();
    return result;
  } catch (e) {
    return null;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

async function fetchFreeAPI() {
  try {
    const res = await fetch(`https://open.er-api.com/v6/latest/${from}`);
    const data = await res.json();
    if (data.result === 'success' && data.rates[to]) {
      const rate = data.rates[to];
      const converted = parseFloat((amount * rate).toFixed(2));
      return {
        amount,
        from,
        to,
        rate,
        converted,
        source: 'exchangerate-api.com (fallback)',
        timestamp: data.time_last_update_utc
      };
    }
  } catch (e) {}
  return null;
}

(async () => {
  let result = await fetchXE();
  if (!result) result = await fetchFreeAPI();

  if (result) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.error(JSON.stringify({ error: `Could not fetch ${from} to ${to} rate` }));
    process.exit(1);
  }
})();
