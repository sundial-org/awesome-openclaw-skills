#!/usr/bin/env node
/**
 * NS Journey Planner
 * Usage: node journey.mjs --from "Station A" --to "Station B"
 */

const API_KEY = process.env.NS_API_KEY;
const BASE_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips';

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

const fromStation = getArg('--from');
const toStation = getArg('--to');
const dateTime = getArg('--time'); // Optional: ISO datetime

if (!fromStation || !toStation) {
  console.log(`
🚆 NS Journey Planner

Usage: node journey.mjs --from "Station" --to "Station" [--time "2026-01-30T08:00:00"]

Examples:
  node journey.mjs --from "Almere Centrum" --to "Amsterdam Zuid"
  node journey.mjs --from "Amsterdam Zuid" --to "Almere Muziekwijk" --time "2026-01-30T17:30:00"
`);
  process.exit(1);
}

async function planJourney() {
  const params = new URLSearchParams({
    fromStation: fromStation,
    toStation: toStation,
    searchForArrival: 'false',
  });
  
  if (dateTime) {
    params.append('dateTime', dateTime);
  }

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
    
    if (!data.trips || data.trips.length === 0) {
      console.log('❌ No trips found for this route.');
      process.exit(0);
    }

    console.log(`\n🚆 ${fromStation} → ${toStation}`);
    console.log('═'.repeat(50));
    
    // Show first 5 options
    data.trips.slice(0, 5).forEach((trip, i) => {
      const legs = trip.legs || [];
      const firstLeg = legs[0];
      const lastLeg = legs[legs.length - 1];
      
      if (!firstLeg || !lastLeg) return;
      
      const departure = new Date(firstLeg.origin?.plannedDateTime);
      const arrival = new Date(lastLeg.destination?.plannedDateTime);
      const duration = trip.plannedDurationInMinutes || Math.round((arrival - departure) / 60000);
      
      const depTime = departure.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
      const arrTime = arrival.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
      
      const transfers = trip.transfers || 0;
      const status = trip.status === 'NORMAL' ? '✅' : '⚠️';
      
      // Check for delays
      const depDelay = firstLeg.origin?.actualDateTime ? 
        Math.round((new Date(firstLeg.origin.actualDateTime) - departure) / 60000) : 0;
      const delayStr = depDelay > 0 ? ` (+${depDelay}min)` : '';
      
      // Platform
      const platform = firstLeg.origin?.plannedTrack || '?';
      
      // Crowdedness
      const crowd = firstLeg.crowdForecast || 'UNKNOWN';
      const crowdEmoji = {
        'LOW': '🟢',
        'MEDIUM': '🟡', 
        'HIGH': '🔴',
        'UNKNOWN': '⚪'
      }[crowd] || '⚪';
      
      console.log(`\n${status} Option ${i + 1}: ${depTime}${delayStr} → ${arrTime}`);
      console.log(`   ⏱️  ${duration} min | 🔄 ${transfers} transfers | 🚏 Platform ${platform}`);
      console.log(`   ${crowdEmoji} Crowdedness: ${crowd.toLowerCase()}`);
      
      // Show legs
      if (legs.length > 1) {
        console.log('   Route:');
        legs.forEach(leg => {
          const type = leg.product?.shortCategoryName || leg.product?.categoryName || '?';
          const dir = leg.direction || '';
          console.log(`     • ${type} ${dir ? '→ ' + dir : ''}`);
        });
      }
      
      // Warnings
      if (trip.messages && trip.messages.length > 0) {
        trip.messages.forEach(msg => {
          if (msg.text) {
            console.log(`   ⚠️  ${msg.text}`);
          }
        });
      }
    });
    
    console.log('\n' + '─'.repeat(50));
    console.log(`⏱️  Checked: ${new Date().toLocaleTimeString('nl-NL')}`);
    
  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

planJourney();
