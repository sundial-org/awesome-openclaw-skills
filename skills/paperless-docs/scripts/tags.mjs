#!/usr/bin/env node
/**
 * List or create tags in Paperless-ngx
 * Usage: node tags.mjs [--create "name"]
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
  console.log(`Usage: tags.mjs [options]
  
Options:
  -c, --create <name>  Create a new tag
  -h, --help           Show this help`);
  process.exit(0);
}

const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function run() {
  if (values.create) {
    // Create new tag
    const res = await fetch(`${baseUrl}/api/tags/`, {
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
    
    const tag = await res.json();
    console.log(JSON.stringify({ created: true, tag }, null, 2));
  } else {
    // List all tags
    const res = await fetch(`${baseUrl}/api/tags/`, {
      headers: { 'Authorization': `Token ${PAPERLESS_TOKEN}` }
    });
    
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    
    const data = await res.json();
    const tags = data.results.map(t => ({
      id: t.id,
      name: t.name,
      document_count: t.document_count,
      color: t.color
    }));
    
    console.log(JSON.stringify({ count: data.count, tags }, null, 2));
  }
}

run().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
