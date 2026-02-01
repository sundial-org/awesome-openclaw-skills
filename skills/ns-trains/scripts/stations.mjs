#!/usr/bin/env node
/**
 * NS Station Lookup
 * Usage: node stations.mjs --search "query"
 */

const API_KEY = process.env.NS_API_KEY;
const BASE_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations';

if (!API_KEY) {
  console.error('❌ NS_API_KEY not set');
  process.exit(1);
}

const args = process.argv.slice(2);
const getArg = (flag) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
};

const query = getArg('--search') || getArg('-s') || args[0];
const limit = parseInt(getArg('--limit') || '10');

if (!query) {
  console.log(`
🚉 NS Station Lookup

Usage: node stations.mjs --search "query" [--limit 10]

Examples:
  node stations.mjs --search "amsterdam"
  node stations.mjs -s "almere"
  node stations.mjs utrecht
`);
  process.exit(1);
}

async function searchStations() {
  try {
    const res = await fetch(`${BASE_URL}?q=${encodeURIComponent(query)}&limit=${limit}`, {
      headers: { 'Ocp-Apim-Subscription-Key': API_KEY, 'Accept': 'application/json' }
    });

    if (!res.ok) {
      console.error(`❌ API Error: ${res.status}`);
      process.exit(1);
    }

    const data = await res.json();
    const stations = data.payload || [];

    if (stations.length === 0) {
      console.log(`❌ No stations found for "${query}"`);
      process.exit(0);
    }

    console.log(`\n🚉 Stations matching "${query}"`);
    console.log('═'.repeat(50));

    stations.forEach(s => {
      const name = s.namen?.lang || s.namen?.middel || s.code;
      const code = s.code;
      const type = s.stationType?.replace(/_/g, ' ').toLowerCase() || 'station';
      const country = s.land || 'NL';

      console.log(`\n📍 ${name}`);
      console.log(`   Code: ${code} | Type: ${type} | ${country}`);
      
      if (s.sporen?.length > 0) {
        const tracks = s.sporen.map(sp => sp.spoorNummer).join(', ');
        console.log(`   Tracks: ${tracks}`);
      }
    });

    console.log('\n' + '─'.repeat(50));
    console.log(`Found ${stations.length} station(s)`);

  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

searchStations();
