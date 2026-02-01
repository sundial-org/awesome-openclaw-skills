#!/usr/bin/env node
/**
 * List or create correspondents in Paperless-ngx
 * Usage: node correspondents.mjs [--create "name"]
 */

import { parseArgs } from 'node:util';

const PAPERLESS_URL = process.env.PAPERLESS_URL;
const PAPERLESS_TOKEN = process.env.PAPERLESS_TOKEN;

if (!PAPERLESS_URL || !PAPERLESS_TOKEN) {
  console.error(JSON.stringify({ error: 'PAPERLESS_URL and PAPERLESS_TOKEN must be set' }));
  process.exit(1);
}

const { values } = parseArgs({
  options: {
    create: { type: 'string', short: 'c' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help) {
  console.log(`Usage: correspondents.mjs [options]
  
Options:
  -c, --create <name>  Create a new correspondent
  -h, --help           Show this help`);
  process.exit(0);
}

const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function run() {
  if (values.create) {
    const res = await fetch(`${baseUrl}/api/correspondents/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${PAPERLESS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: values.create })
    });
    
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    
    const correspondent = await res.json();
    console.log(JSON.stringify({ created: true, correspondent }, null, 2));
  } else {
    const res = await fetch(`${baseUrl}/api/correspondents/`, {
      headers: { 'Authorization': `Token ${PAPERLESS_TOKEN}` }
    });
    
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    
    const data = await res.json();
    const correspondents = data.results.map(c => ({
      id: c.id,
      name: c.name,
      document_count: c.document_count
    }));
    
    console.log(JSON.stringify({ count: data.count, correspondents }, null, 2));
  }
}

run().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
