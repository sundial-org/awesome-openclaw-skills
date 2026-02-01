#!/usr/bin/env node

/**
 * Fetch mentions from Octolens API
 * Usage: node fetch-mentions.js YOUR_API_KEY [limit] [includeAll]
 */

const API_BASE_URL = 'https://app.octolens.com/api/v1';

async function fetchMentions(apiKey, limit = 20, includeAll = false) {
  const url = `${API_BASE_URL}/mentions`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      limit: parseInt(limit),
      includeAll: includeAll === 'true' || includeAll === true,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(`API Error: ${response.status} - ${JSON.stringify(error)}`);
  }

  return await response.json();
}

async function main() {
  const args = process.argv.slice(2);
  const apiKey = args[0];
  const limit = args[1] || 20;
  const includeAll = args[2] || false;

  if (!apiKey) {
    console.error('Error: API key required');
    console.error(`Usage: ${process.argv[1]} YOUR_API_KEY [limit] [includeAll]`);
    process.exit(1);
  }

  try {
    console.log(`Fetching mentions (limit: ${limit}, includeAll: ${includeAll})...`);
    const result = await fetchMentions(apiKey, limit, includeAll);
    console.log(JSON.stringify(result, null, 2));
    console.log('\n✓ Request complete');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
