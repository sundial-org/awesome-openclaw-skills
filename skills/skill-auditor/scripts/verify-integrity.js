#!/usr/bin/env node
/**
 * Skill Integrity Verifier
 * Compares local installed skill against its original source (GitHub)
 * Generates SHA-256 hashes for each file and compares
 * 
 * Usage:
 *   Verify:   node verify-integrity.js <local-skill-path> <github-url>
 *   Generate: node verify-integrity.js <local-skill-path> --generate
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');

// ─── HTTP ──────────────────────────────────────────────────────────

function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'skill-auditor/1.0' } }, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpGet(res.headers.location).then(resolve).catch(reject);
      }
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({ status: res.statusCode, data: Buffer.concat(chunks) }));
    }).on('error', reject);
  });
}

// ─── File Discovery ────────────────────────────────────────────────

function discoverFiles(dir) {
  const files = [];
  function walk(d) {
    let entries;
    try { entries = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const entry of entries) {
      const full = path.join(d, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === '__pycache__' || entry.name === '.DS_Store') continue;
        walk(full);
      } else {
        files.push(full);
      }
    }
  }
  walk(dir);
  return files;
}

function hashFile(filePath) {
  const content = fs.readFileSync(filePath);
  return crypto.createHash('sha256').update(content).digest('hex');
}

function hashContent(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

// ─── GitHub URL parsing ────────────────────────────────────────────

function parseGithubUrl(url) {
  const m = url.match(/github\.com\/([^/]+)\/([^/]+)\/(?:tree|blob)\/([^/]+)\/(.+)/);
  if (m) return { owner: m[1], repo: m[2], branch: m[3], path: m[4] };
  const m2 = url.match(/github\.com\/([^/]+)\/([^/]+)\/?$/);
  if (m2) return { owner: m2[1], repo: m2[2], branch: 'main', path: '' };
  return null;
}

async function listGithubFiles(gh, dirPath) {
  const apiUrl = `https://api.github.com/repos/${gh.owner}/${gh.repo}/contents/${dirPath}?ref=${gh.branch}`;
  const res = await httpGet(apiUrl);
  if (res.status !== 200) return [];
  const entries = JSON.parse(res.data.toString());
  let allFiles = [];
  for (const entry of entries) {
    if (entry.type === 'file') allFiles.push(entry);
    else if (entry.type === 'dir') {
      const sub = await listGithubFiles(gh, entry.path);
      allFiles.push(...sub);
    }
  }
  return allFiles;
}

// ─── Generate manifest ────────────────────────────────────────────

function generateManifest(skillDir) {
  const files = discoverFiles(skillDir);
  const manifest = {};
  for (const file of files) {
    const rel = path.relative(skillDir, file).replace(/\\/g, '/');
    manifest[rel] = hashFile(file);
  }
  return manifest;
}

// ─── Verify against GitHub ─────────────────────────────────────────

async function verifyAgainstGithub(skillDir, githubUrl) {
  const gh = parseGithubUrl(githubUrl);
  if (!gh) { console.error('Invalid GitHub URL'); process.exit(2); }

  process.stderr.write('Fetching source files...\n');
  const remoteFiles = await listGithubFiles(gh, gh.path);
  const basePath = gh.path ? gh.path + '/' : '';

  // Hash local files
  const localFiles = discoverFiles(skillDir);
  const localHashes = {};
  for (const file of localFiles) {
    const rel = path.relative(skillDir, file).replace(/\\/g, '/');
    localHashes[rel] = hashFile(file);
  }

  // Hash remote files
  const remoteHashes = {};
  for (const f of remoteFiles) {
    const rel = f.path.startsWith(basePath) ? f.path.slice(basePath.length) : f.name;
    const res = await httpGet(f.download_url);
    if (res.status === 200) {
      remoteHashes[rel] = hashContent(res.data);
    }
  }

  // Compare
  const results = { matched: [], modified: [], localOnly: [], remoteOnly: [] };

  const allKeys = new Set([...Object.keys(localHashes), ...Object.keys(remoteHashes)]);
  for (const key of allKeys) {
    const local = localHashes[key];
    const remote = remoteHashes[key];
    if (local && remote) {
      if (local === remote) results.matched.push(key);
      else results.modified.push(key);
    } else if (local && !remote) {
      results.localOnly.push(key);
    } else {
      results.remoteOnly.push(key);
    }
  }

  return results;
}

// ─── Format Report ─────────────────────────────────────────────────

function formatVerifyReport(results, skillName, sourceUrl) {
  const lines = [];
  const total = results.matched.length + results.modified.length + results.localOnly.length + results.remoteOnly.length;
  const tampered = results.modified.length > 0 || results.localOnly.length > 0 || results.remoteOnly.length > 0;

  if (!tampered) {
    lines.push(`🔒 VERIFIED — "${skillName}"`);
    lines.push('');
    lines.push(`Integrity: 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%`);
    lines.push(`Files: ${total} checked | All match source`);
    lines.push('');
    lines.push(`✅ Every file matches the original source exactly.`);
    lines.push(`Source: ${sourceUrl}`);
  } else {
    const matchPct = Math.round((results.matched.length / total) * 100);
    const fill = Math.round(matchPct / 10);
    const bar = '🟩'.repeat(fill) + '🔴'.repeat(10 - fill);

    lines.push(`⚠️ TAMPERED — "${skillName}"`);
    lines.push('');
    lines.push(`Integrity: ${bar} ${matchPct}%`);
    lines.push(`Files: ${total} checked | ${results.matched.length} match, ${results.modified.length} modified, ${results.localOnly.length} added, ${results.remoteOnly.length} missing`);
    lines.push('');

    if (results.modified.length > 0) {
      lines.push('🔴 Modified (different from source):');
      for (const f of results.modified) lines.push(`  → ${f}`);
      lines.push('');
    }

    if (results.localOnly.length > 0) {
      lines.push('⚠️ Added (not in source):');
      for (const f of results.localOnly) lines.push(`  → ${f}`);
      lines.push('');
    }

    if (results.remoteOnly.length > 0) {
      lines.push('❌ Missing (in source but not installed):');
      for (const f of results.remoteOnly) lines.push(`  → ${f}`);
      lines.push('');
    }

    lines.push(`Source: ${sourceUrl}`);
    lines.push('');
    lines.push('→ This skill has been altered from its original source. Proceed with caution.');
  }

  return lines.join('\n');
}

// ─── Manifest Format ───────────────────────────────────────────────

function formatManifest(manifest, skillName) {
  const lines = [];
  lines.push(`# Integrity Manifest — ${skillName}`);
  lines.push(`# Generated: ${new Date().toISOString()}`);
  lines.push(`# SHA-256 hashes for each file`);
  lines.push('');
  const sorted = Object.entries(manifest).sort((a, b) => a[0].localeCompare(b[0]));
  for (const [file, hash] of sorted) {
    lines.push(`${hash}  ${file}`);
  }
  return lines.join('\n');
}

// ─── Main ──────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage:');
    console.error('  Verify:   node verify-integrity.js <skill-path> <github-url>');
    console.error('  Manifest: node verify-integrity.js <skill-path> --generate');
    process.exit(2);
  }

  const skillDir = path.resolve(args[0]);
  if (!fs.existsSync(skillDir)) { console.error(`Not found: ${skillDir}`); process.exit(2); }

  // Get skill name from SKILL.md
  let skillName = path.basename(skillDir);
  const skillMd = path.join(skillDir, 'SKILL.md');
  if (fs.existsSync(skillMd)) {
    const content = fs.readFileSync(skillMd, 'utf-8');
    const nm = content.match(/^name:\s*(.+)$/m);
    if (nm) skillName = nm[1].trim();
  }

  if (args[1] === '--generate') {
    const manifest = generateManifest(skillDir);
    const output = formatManifest(manifest, skillName);
    const outPath = path.join(skillDir, 'INTEGRITY.md');
    fs.writeFileSync(outPath, output);
    console.log(`Manifest saved to: ${outPath}`);
    console.log(`${Object.keys(manifest).length} files hashed`);
  } else {
    const results = await verifyAgainstGithub(skillDir, args[1]);
    console.log(formatVerifyReport(results, skillName, args[1]));
  }
}

main().catch(e => { console.error(e); process.exit(2); });
