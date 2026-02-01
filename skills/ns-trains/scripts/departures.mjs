#!/usr/bin/env node
/**
 * NS Station Departures
 * Usage: node departures.mjs --station "Station Name"
 */

const API_KEY = process.env.NS_API_KEY;
const BASE_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures';

if (!API_KEY) {
  console.error('❌ NS_API_KEY not set. Export it first:');
  console.error('   export NS_API_KEY="your-key"');
  process.exit(1);
}

// Parse arguments
const args = process.argv.slice(2);
const getArg = (flag) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
};

const station = getArg('--station') || getArg('-s');
const limit = parseInt(getArg('--limit') || '10');

if (!station) {
  console.log(`
🚉 NS Station Departures

Usage: node departures.mjs --station "Station Name" [--limit 10]

Examples:
  node departures.mjs --station "Almere Centrum"
  node departures.mjs --station "Amsterdam Zuid" --limit 5
  node departures.mjs -s "Utrecht Centraal"
`);
  process.exit(1);
}

async function getDepartures() {
  const params = new URLSearchParams({
    station: station,
    maxJourneys: limit.toString()
  });

  const url = `${BASE_URL}?${params}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Ocp-Apim-Subscription-Key': API_KEY,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌ API Error (${response.status}): ${error}`);
      process.exit(1);
    }

    const data = await response.json();
    const departures = data.payload?.departures || [];
    
    if (departures.length === 0) {
      console.log(`❌ No departures found for "${station}"`);
      process.exit(0);
    }

    console.log(`\n🚉 Departures from ${station}`);
    console.log('═'.repeat(50));
    
    departures.forEach(dep => {
      const planned = new Date(dep.plannedDateTime);
      const actual = dep.actualDateTime ? new Date(dep.actualDateTime) : planned;
      const delay = Math.round((actual - planned) / 60000);
      
      const time = planned.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
      const delayStr = delay > 0 ? ` (+${delay})` : '';
      const status = dep.cancelled ? '❌' : (delay > 0 ? '⚠️' : '✅');
      
      const direction = dep.direction || 'Unknown';
      const platform = dep.plannedTrack || '?';
      const trainType = dep.product?.shortCategoryName || dep.trainCategory || '?';
      
      console.log(`\n${status} ${time}${delayStr} → ${direction}`);
      console.log(`   🚆 ${trainType} | 🚏 Platform ${platform}`);
      
      if (dep.cancelled) {
        console.log(`   ❌ CANCELLED`);
      }
      
      if (dep.messages && dep.messages.length > 0) {
        dep.messages.forEach(msg => {
          console.log(`   ⚠️  ${msg.message || msg.text || ''}`);
        });
      }
      
      // Route stations
      if (dep.routeStations && dep.routeStations.length > 0) {
        const via = dep.routeStations.slice(0, 3).map(s => s.mediumName).join(' → ');
        console.log(`   📍 Via: ${via}`);
      }
    });
    
    console.log('\n' + '─'.repeat(50));
    console.log(`⏱️  Updated: ${new Date().toLocaleTimeString('nl-NL')}`);
    
  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

getDepartures();
