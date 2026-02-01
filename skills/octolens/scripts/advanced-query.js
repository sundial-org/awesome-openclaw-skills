#!/usr/bin/env node

/**
 * Query mentions with advanced AND/OR filter groups
 * Usage: node advanced-query.js YOUR_API_KEY [limit]
 */

const API_BASE_URL = 'https://app.octolens.com/api/v1';

async function advancedQuery(apiKey, limit = 20) {
  const url = `${API_BASE_URL}/mentions`;
  
  const filters = {
    operator: 'AND',
    groups: [
      {
        operator: 'OR',
        conditions: [
          { source: ['twitter'] },
          { source: ['reddit'] },
        ],
      },
      {
        operator: 'AND',
        conditions: [
          { sentiment: ['positive'] },
          { '!tag': ['spam'] },
        ],
      },
    ],
  };

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
  const limit = args[1] || 20;

  if (!apiKey) {
    console.error('Error: API key required');
    console.error(`Usage: ${process.argv[1]} YOUR_API_KEY [limit]`);
    process.exit(1);
  }

  try {
    console.log('Querying mentions with advanced filters...');
    console.log('Query: (Twitter OR Reddit) AND (Positive sentiment) AND NOT spam');
    const result = await advancedQuery(apiKey, limit);
    console.log(JSON.stringify(result, null, 2));
    console.log('\n✓ Request complete');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
