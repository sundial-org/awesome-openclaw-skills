#!/usr/bin/env node
/**
 * Upload document to Paperless-ngx
 * Usage: node upload.mjs <file> [--title "..."] [--tags "a,b"] [--type X] [--correspondent X]
 */

import { parseArgs } from 'node:util';
import { createReadStream, statSync } from 'node:fs';
import { basename } from 'node:path';

const PAPERLESS_URL = process.env.PAPERLESS_URL;
const PAPERLESS_TOKEN = process.env.PAPERLESS_TOKEN;

if (!PAPERLESS_URL || !PAPERLESS_TOKEN) {
  console.error(JSON.stringify({ error: 'PAPERLESS_URL and PAPERLESS_TOKEN must be set' }));
  process.exit(1);
}

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    title: { type: 'string', short: 't' },
    tags: { type: 'string', short: 'T' },
    type: { type: 'string' },
    correspondent: { type: 'string', short: 'c' },
    created: { type: 'string', short: 'd' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help || positionals.length === 0) {
  console.log(`Usage: upload.mjs <file> [options]
  
Options:
  -t, --title <title>        Document title
  -T, --tags <a,b,c>         Comma-separated tag names
  --type <name>              Document type name
  -c, --correspondent <name> Correspondent name
  -d, --created <YYYY-MM-DD> Document date
  -h, --help                 Show this help`);
  process.exit(values.help ? 0 : 1);
}

const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { 'Authorization': `Token ${PAPERLESS_TOKEN}`, ...options.headers }
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

async function resolveOrCreateId(endpoint, name) {
  if (!name) return null;
  
  // Try to find existing
  const data = await fetchJson(`${baseUrl}/api/${endpoint}/`);
  const match = data.results.find(r => r.name.toLowerCase() === name.toLowerCase());
  if (match) return match.id;
  
  // Create new
  const created = await fetchJson(`${baseUrl}/api/${endpoint}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  return created.id;
}

async function resolveTagIds(tagString) {
  if (!tagString) return [];
  const tagNames = tagString.split(',').map(t => t.trim()).filter(Boolean);
  const ids = await Promise.all(tagNames.map(name => resolveOrCreateId('tags', name)));
  return ids.filter(Boolean);
}

async function upload() {
  const filePath = positionals[0];
  
  // Verify file exists
  try {
    statSync(filePath);
  } catch {
    throw new Error(`File not found: ${filePath}`);
  }
  
  // Build form data
  const formData = new FormData();
  
  // Read file as blob
  const fileBuffer = await import('node:fs/promises').then(fs => fs.readFile(filePath));
  const blob = new Blob([fileBuffer]);
  formData.append('document', blob, basename(filePath));
  
  if (values.title) {
    formData.append('title', values.title);
  }
  
  if (values.created) {
    formData.append('created', values.created);
  }
  
  // Resolve correspondent and type
  if (values.correspondent) {
    const corrId = await resolveOrCreateId('correspondents', values.correspondent);
    if (corrId) formData.append('correspondent', corrId.toString());
  }
  
  if (values.type) {
    const typeId = await resolveOrCreateId('document_types', values.type);
    if (typeId) formData.append('document_type', typeId.toString());
  }
  
  // Resolve tags
  if (values.tags) {
    const tagIds = await resolveTagIds(values.tags);
    tagIds.forEach(id => formData.append('tags', id.toString()));
  }
  
  // Upload
  const res = await fetch(`${baseUrl}/api/documents/post_document/`, {
    method: 'POST',
    headers: { 'Authorization': `Token ${PAPERLESS_TOKEN}` },
    body: formData
  });
  
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: HTTP ${res.status}: ${text}`);
  }
  
  // The response is just a task ID string
  const taskId = await res.text();
  
  console.log(JSON.stringify({
    success: true,
    message: 'Document queued for processing',
    task_id: taskId.replace(/"/g, ''),
    file: basename(filePath)
  }, null, 2));
}

upload().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
