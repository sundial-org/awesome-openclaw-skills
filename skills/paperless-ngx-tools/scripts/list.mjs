#!/usr/bin/env node
/**
 * List recent documents in Paperless-ngx
 * Usage: node list.mjs [--limit N] [--ordering field]
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
    limit: { type: 'string', short: 'l', default: '10' },
    ordering: { type: 'string', short: 'o', default: '-added' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help) {
  console.log(`Usage: list.mjs [options]
  
Options:
  -l, --limit <n>       Max results (default: 10)
  -o, --ordering <field> Sort field (default: -added, use - prefix for descending)
                        Fields: added, created, title, correspondent, document_type
  -h, --help            Show this help`);
  process.exit(0);
}

const headers = { 'Authorization': `Token ${PAPERLESS_TOKEN}` };
const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function fetchJson(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

async function list() {
  const limit = parseInt(values.limit) || 10;
  const ordering = values.ordering;
  
  const params = new URLSearchParams();
  params.set('page_size', limit.toString());
  params.set('ordering', ordering);
  
  const data = await fetchJson(`${baseUrl}/api/documents/?${params}`);
  
  // Fetch metadata for names
  const [tags, types, correspondents] = await Promise.all([
    fetchJson(`${baseUrl}/api/tags/`),
    fetchJson(`${baseUrl}/api/document_types/`),
    fetchJson(`${baseUrl}/api/correspondents/`)
  ]);
  
  const tagMap = Object.fromEntries(tags.results.map(t => [t.id, t.name]));
  const typeMap = Object.fromEntries(types.results.map(t => [t.id, t.name]));
  const corrMap = Object.fromEntries(correspondents.results.map(c => [c.id, c.name]));
  
  const results = data.results.map(doc => ({
    id: doc.id,
    title: doc.title,
    created: doc.created,
    added: doc.added,
    correspondent: doc.correspondent ? corrMap[doc.correspondent] : null,
    document_type: doc.document_type ? typeMap[doc.document_type] : null,
    tags: doc.tags.map(tid => tagMap[tid] || tid)
  }));
  
  console.log(JSON.stringify({ count: data.count, results }, null, 2));
}

list().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
