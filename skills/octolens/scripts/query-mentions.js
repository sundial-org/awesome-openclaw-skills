#!/usr/bin/env node

/**
 * Query mentions with custom filters
 * Usage: node query-mentions.js YOUR_API_KEY '{"source": ["twitter"], "sentiment": ["positive"]}'
 */

const API_BASE_URL = 'https://app.octolens.com/api/v1';

async function queryMentions(apiKey, filters, limit = 20) {
  const url = `${API_BASE_URL}/mentions`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      limit: parseInt(limit),
      filters: filters,
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
  const filtersJson = args[1];
  const limit = args[2] || 20;

  if (!apiKey || !filtersJson) {
    console.error('Error: API key and filters required');
    console.error(`Usage: ${process.argv[1]} YOUR_API_KEY '{"source": ["twitter"]}'`);
    console.error('');
    console.error('Example filters:');
    console.error('  Simple: \'{"source": ["twitter"], "sentiment": ["positive"]}\'');
    console.error('  With exclusion: \'{"source": ["twitter"], "!tag": ["spam"]}\'');
    console.error('  Date range: \'{"startDate": "2024-01-01T00:00:00Z", "endDate": "2024-01-31T23:59:59Z"}\'');
    process.exit(1);
  }

  let filters;
  try {
    filters = JSON.parse(filtersJson);
  } catch (error) {
    console.error('Error: Invalid JSON in filters argument');
    console.error(error.message);
    process.exit(1);
  }

  try {
    console.log('Querying mentions with custom filters...');
    const result = await queryMentions(apiKey, filters, limit);
    console.log(JSON.stringify(result, null, 2));
    console.log('\n✓ Request complete');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
