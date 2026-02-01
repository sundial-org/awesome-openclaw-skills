#!/usr/bin/env node

/**
 * List all keywords from Octolens API
 * Usage: node list-keywords.js YOUR_API_KEY
 */

const API_BASE_URL = 'https://app.octolens.com/api/v1';

async function listKeywords(apiKey) {
  const url = `${API_BASE_URL}/keywords`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
    },
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

  if (!apiKey) {
    console.error('Error: API key required');
    console.error(`Usage: ${process.argv[1]} YOUR_API_KEY`);
    process.exit(1);
  }

  try {
    console.log('Fetching keywords...');
    const result = await listKeywords(apiKey);
    console.log(JSON.stringify(result, null, 2));
    console.log('\n✓ Request complete');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
