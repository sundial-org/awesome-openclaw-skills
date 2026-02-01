#!/usr/bin/env node
/**
 * Search documents in Paperless-ngx
 * Usage: node search.mjs "query" [--tag X] [--type X] [--correspondent X] [--limit N]
 */

import { parseArgs } from 'node:util';

const PAPERLESS_URL = process.env.PAPERLESS_URL;
const PAPERLESS_TOKEN = process.env.PAPERLESS_TOKEN;

if (!PAPERLESS_URL || !PAPERLESS_TOKEN) {
  console.error(JSON.stringify({ error: 'PAPERLESS_URL and PAPERLESS_TOKEN must be set' }));
  process.exit(1);
}

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    tag: { type: 'string', short: 't' },
    type: { type: 'string', short: 'T' },
    correspondent: { type: 'string', short: 'c' },
    limit: { type: 'string', short: 'l', default: '20' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help) {
  console.log(`Usage: search.mjs [query] [options]
  
Options:
  -t, --tag <name>           Filter by tag name
  -T, --type <name>          Filter by document type name
  -c, --correspondent <name> Filter by correspondent name
  -l, --limit <n>            Max results (default: 20)
  -h, --help                 Show this help`);
  process.exit(0);
}

const headers = { 'Authorization': `Token ${PAPERLESS_TOKEN}` };
const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function fetchJson(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

async function resolveId(endpoint, name) {
  if (!name) return null;
  const data = await fetchJson(`${baseUrl}/api/${endpoint}/`);
  const match = data.results.find(r => r.name.toLowerCase() === name.toLowerCase());
  return match?.id || null;
}

async function search() {
  const query = positionals[0] || '';
  const limit = parseInt(values.limit) || 20;
  
  // Build query params
  const params = new URLSearchParams();
  params.set('page_size', limit.toString());
  if (query) params.set('query', query);
  
  // Resolve names to IDs
  if (values.tag) {
    const tagId = await resolveId('tags', values.tag);
    if (tagId) params.set('tags__id__in', tagId.toString());
    else console.error(`Warning: Tag "${values.tag}" not found`);
  }
  
  if (values.type) {
    const typeId = await resolveId('document_types', values.type);
    if (typeId) params.set('document_type__id', typeId.toString());
    else console.error(`Warning: Type "${values.type}" not found`);
  }
  
  if (values.correspondent) {
    const corrId = await resolveId('correspondents', values.correspondent);
    if (corrId) params.set('correspondent__id', corrId.toString());
    else console.error(`Warning: Correspondent "${values.correspondent}" not found`);
  }
  
  // Fetch documents
  const data = await fetchJson(`${baseUrl}/api/documents/?${params}`);
  
  // Fetch tag/type/correspondent names for display
  const [tags, types, correspondents] = await Promise.all([
    fetchJson(`${baseUrl}/api/tags/`),
    fetchJson(`${baseUrl}/api/document_types/`),
    fetchJson(`${baseUrl}/api/correspondents/`)
  ]);
  
  const tagMap = Object.fromEntries(tags.results.map(t => [t.id, t.name]));
  const typeMap = Object.fromEntries(types.results.map(t => [t.id, t.name]));
  const corrMap = Object.fromEntries(correspondents.results.map(c => [c.id, c.name]));
  
  // Format results
  const results = data.results.map(doc => ({
    id: doc.id,
    title: doc.title,
    created: doc.created,
    added: doc.added,
    correspondent: doc.correspondent ? corrMap[doc.correspondent] : null,
    document_type: doc.document_type ? typeMap[doc.document_type] : null,
    tags: doc.tags.map(tid => tagMap[tid] || tid),
    archive_serial_number: doc.archive_serial_number
  }));
  
  console.log(JSON.stringify({ count: data.count, results }, null, 2));
}

search().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
