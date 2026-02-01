#!/usr/bin/env node
/**
 * Download document from Paperless-ngx
 * Usage: node download.mjs <id> [--output path] [--original]
 */

import { parseArgs } from 'node:util';
import { writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const PAPERLESS_URL = process.env.PAPERLESS_URL;
const PAPERLESS_TOKEN = process.env.PAPERLESS_TOKEN;

if (!PAPERLESS_URL || !PAPERLESS_TOKEN) {
  console.error(JSON.stringify({ error: 'PAPERLESS_URL and PAPERLESS_TOKEN must be set' }));
  process.exit(1);
}

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    output: { type: 'string', short: 'o' },
    original: { type: 'boolean' },
    help: { type: 'boolean', short: 'h' }
  }
});

if (values.help || positionals.length === 0) {
  console.log(`Usage: download.mjs <document-id> [options]
  
Options:
  -o, --output <path>  Output file path (default: original filename in cwd)
  --original           Download original file instead of archived/OCR'd version
  -h, --help           Show this help`);
  process.exit(values.help ? 0 : 1);
}

const headers = { 'Authorization': `Token ${PAPERLESS_TOKEN}` };
const baseUrl = PAPERLESS_URL.replace(/\/$/, '');

async function download() {
  const docId = positionals[0];
  
  // Get document metadata first
  const metaRes = await fetch(`${baseUrl}/api/documents/${docId}/`, { headers });
  if (!metaRes.ok) throw new Error(`HTTP ${metaRes.status}: ${metaRes.statusText}`);
  const meta = await metaRes.json();
  
  // Determine which file to download
  const endpoint = values.original ? 'original' : 'download';
  const filename = values.original ? meta.original_file_name : (meta.archived_file_name || meta.original_file_name);
  
  // Download the file
  const res = await fetch(`${baseUrl}/api/documents/${docId}/${endpoint}/`, { headers });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  
  const buffer = Buffer.from(await res.arrayBuffer());
  
  // Determine output path
  const outputPath = values.output || join(process.cwd(), filename);
  
  await writeFile(outputPath, buffer);
  
  console.log(JSON.stringify({
    success: true,
    document_id: docId,
    title: meta.title,
    file: outputPath,
    size_bytes: buffer.length
  }, null, 2));
}

download().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
