#!/usr/bin/env node
/**
 * Get document details from Paperless-ngx
 * Usage: node get.mjs <id> [--content] [--full]
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
    content: { type: 'boolean', short: 'c' },
    full: { type: 'boolean', short: 'f' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help || positionals.length === 0) {
  console.log(`Usage: get.mjs <document-id> [options]
  
Options:
  -c, --content  Include OCR text content
  -f, --full     Don't truncate content (default: 2000 chars)
  -h, --help     Show this help`);
  process.exit(values.help ? 0 : 1);
}

const headers = { 'Authorization': `Token ${PAPERLESS_TOKEN}` };
const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function fetchJson(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

async function get() {
  const docId = positionals[0];
  
  const doc = await fetchJson(`${baseUrl}/api/documents/${docId}/`);
  
  // Fetch metadata for names
  const [tags, types, correspondents] = await Promise.all([
    fetchJson(`${baseUrl}/api/tags/`),
    fetchJson(`${baseUrl}/api/document_types/`),
    fetchJson(`${baseUrl}/api/correspondents/`)
  ]);
  
  const tagMap = Object.fromEntries(tags.results.map(t => [t.id, t.name]));
  const typeMap = Object.fromEntries(types.results.map(t => [t.id, t.name]));
  const corrMap = Object.fromEntries(correspondents.results.map(c => [c.id, c.name]));
  
  const result = {
    id: doc.id,
    title: doc.title,
    created: doc.created,
    added: doc.added,
    modified: doc.modified,
    correspondent: doc.correspondent ? corrMap[doc.correspondent] : null,
    document_type: doc.document_type ? typeMap[doc.document_type] : null,
    tags: doc.tags.map(tid => tagMap[tid] || tid),
    archive_serial_number: doc.archive_serial_number,
    original_file_name: doc.original_file_name,
    archived_file_name: doc.archived_file_name
  };
  
  if (values.content) {
    let content = doc.content || '';
    if (!values.full && content.length > 2000) {
      content = content.substring(0, 2000) + '\n... [truncated, use --full for complete content]';
    }
    result.content = content;
  }
  
  console.log(JSON.stringify(result, null, 2));
}

get().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
