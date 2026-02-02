#!/usr/bin/env npx tsx
/**
 * Bulk upload OpenClaw skills to Supabase
 *
 * Usage:
 *   npx tsx bulk-upload.ts --test <slug>     # Test with one skill
 *   npx tsx bulk-upload.ts --all             # Upload all skills
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import { execSync } from 'child_process';

const SKILLS_CLI_ENV = '/Users/turboblitz/code/my-code/skills/cli/.env';
const METADATA_FILE = './skills_metadata.json';
const README_FILE = './README.md';
const ZIPS_DIR = './zips';

function loadEnv(): { url: string; serviceKey: string } {
  if (!fs.existsSync(SKILLS_CLI_ENV)) {
    console.error(`Error: Could not find ${SKILLS_CLI_ENV}`);
    process.exit(1);
  }
  const content = fs.readFileSync(SKILLS_CLI_ENV, 'utf-8');
  const url = content.match(/SUPABASE_URL=(.+)/)?.[1]?.trim();
  const serviceKey = content.match(/SUPABASE_SERVICE_ROLE_KEY=(.+)/)?.[1]?.trim();
  if (!url || !serviceKey) {
    console.error('Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
    process.exit(1);
  }
  return { url, serviceKey };
}

interface SkillMetadata {
  slug: string;
  displayName: string;
  summary: string;
  stats: { downloads: number };
  download_url: string;
}

interface MetadataFile {
  skills: SkillMetadata[];
}

function loadMetadata(): Map<string, SkillMetadata> {
  const content = fs.readFileSync(METADATA_FILE, 'utf-8');
  const data: MetadataFile = JSON.parse(content);
  const map = new Map<string, SkillMetadata>();
  for (const skill of data.skills) {
    map.set(skill.slug, skill);
  }
  return map;
}

function parseOwnersFromReadme(): Map<string, string> {
  const content = fs.readFileSync(README_FILE, 'utf-8');
  const map = new Map<string, string>();
  // Pattern: https://www.clawhub.com/<owner>/<slug>
  const regex = /clawhub\.com\/([^\/]+)\/([^\)]+)/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const owner = match[1];
    const slug = match[2];
    map.set(slug, owner);
  }
  return map;
}

async function uploadZip(url: string, serviceKey: string, skillName: string, zipBuffer: Buffer): Promise<string> {
  const zipPath = `${skillName}.zip`;
  const res = await fetch(`${url}/storage/v1/object/skill-zips/${zipPath}`, {
    method: 'PUT',
    headers: {
      'apikey': serviceKey,
      'Authorization': `Bearer ${serviceKey}`,
      'Content-Type': 'application/zip',
      'x-upsert': 'true',
    },
    body: zipBuffer,
  });
  if (!res.ok) {
    throw new Error(`Upload failed: ${await res.text()}`);
  }
  return zipPath;
}

/**
 * Repackage a zip to have a wrapper folder.
 * OpenClaw zips have files at root, but CLI expects skill-name/SKILL.md structure.
 */
function repackageZip(originalZipPath: string, slug: string): Buffer {
  const tempDir = path.join(os.tmpdir(), `repackage-${Date.now()}`);
  const extractDir = path.join(tempDir, 'extract');
  const wrapperDir = path.join(tempDir, slug);
  const newZipPath = path.join(tempDir, `${slug}.zip`);

  try {
    fs.mkdirSync(extractDir, { recursive: true });

    // Extract original zip
    execSync(`unzip -q "${originalZipPath}" -d "${extractDir}"`, { stdio: 'pipe' });

    // Move contents into wrapper folder
    fs.renameSync(extractDir, wrapperDir);

    // Create new zip with wrapper
    execSync(`zip -rq "${newZipPath}" "${slug}"`, { cwd: tempDir, stdio: 'pipe' });

    return fs.readFileSync(newZipPath);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

interface SkillRecord {
  name: string;
  display_name: string;
  description: string;
  category: string;
  author: string;
  github_url: string;
  degit_path: string;
  zip_path: string;
  download_count: number;
  visibility: 'public' | 'private';
}

async function upsertSkill(url: string, serviceKey: string, skill: SkillRecord): Promise<void> {
  // Try insert first
  const insertRes = await fetch(`${url}/rest/v1/skills`, {
    method: 'POST',
    headers: {
      'apikey': serviceKey,
      'Authorization': `Bearer ${serviceKey}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal',
    },
    body: JSON.stringify(skill),
  });

  if (insertRes.ok) return;

  const error = await insertRes.text();
  if (!error.includes('duplicate key')) {
    throw new Error(`Insert failed: ${error}`);
  }

  // Skill exists, update it
  const { name, ...updateFields } = skill;
  const updateRes = await fetch(`${url}/rest/v1/skills?name=eq.${encodeURIComponent(name)}`, {
    method: 'PATCH',
    headers: {
      'apikey': serviceKey,
      'Authorization': `Bearer ${serviceKey}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal',
    },
    body: JSON.stringify(updateFields),
  });

  if (!updateRes.ok) {
    throw new Error(`Update failed: ${await updateRes.text()}`);
  }
}

async function uploadSkill(
  url: string,
  serviceKey: string,
  slug: string,
  metadata: SkillMetadata,
  owner: string
): Promise<void> {
  // Try slug.zip first, then check download_url for original name
  let zipFile = path.join(ZIPS_DIR, `${slug}.zip`);

  if (!fs.existsSync(zipFile)) {
    // Extract original slug from download_url (e.g., ?slug=hippocampus-memory)
    const match = metadata.download_url?.match(/[?&]slug=([^&]+)/);
    if (match) {
      const originalSlug = match[1];
      zipFile = path.join(ZIPS_DIR, `${originalSlug}.zip`);
    }
  }

  if (!fs.existsSync(zipFile)) {
    console.log(`  ⚠️  Zip not found for ${slug}, skipping`);
    return;
  }

  console.log(`  📦 Uploading ${slug}...`);

  // Repackage zip with wrapper folder (OpenClaw zips have files at root)
  const zipBuffer = repackageZip(zipFile, slug);
  const sizeMb = (zipBuffer.length / 1024 / 1024).toFixed(2);
  console.log(`     Zip size: ${sizeMb} MB (repackaged)`);

  const zipPath = await uploadZip(url, serviceKey, slug, zipBuffer);

  // Upsert skill record
  const record: SkillRecord = {
    name: slug,
    display_name: metadata.displayName,
    description: metadata.summary || `${metadata.displayName} skill`,
    category: 'Openclaw',
    author: owner,
    github_url: `https://github.com/sundial-org/awesome-openclaw-skills/blob/main/skills/${slug}/SKILL.md`,
    degit_path: `sundial-org/awesome-openclaw-skills/skills/${slug}#main`,
    zip_path: zipPath,
    download_count: metadata.stats.downloads,
    visibility: 'private',
  };

  await upsertSkill(url, serviceKey, record);
  console.log(`  ✅ ${slug} uploaded (${metadata.stats.downloads} downloads)`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
Bulk Upload OpenClaw Skills

Usage:
  npx tsx bulk-upload.ts --test <slug>     Test with one skill
  npx tsx bulk-upload.ts --all             Upload all skills
  npx tsx bulk-upload.ts --dry-run         Show what would be uploaded
`);
    return;
  }

  const { url, serviceKey } = loadEnv();
  console.log('📂 Loading metadata...');
  const metadata = loadMetadata();
  console.log(`   Found ${metadata.size} skills in metadata`);

  console.log('📂 Parsing owners from README...');
  const owners = parseOwnersFromReadme();
  console.log(`   Found ${owners.size} owner mappings`);

  if (args[0] === '--test' && args[1]) {
    const slug = args[1];
    const skillMeta = metadata.get(slug);
    const owner = owners.get(slug) || 'unknown';

    if (!skillMeta) {
      console.error(`Skill not found in metadata: ${slug}`);
      process.exit(1);
    }

    console.log(`\n🧪 Testing upload for: ${slug}`);
    console.log(`   Display Name: ${skillMeta.displayName}`);
    console.log(`   Owner: ${owner}`);
    console.log(`   Downloads: ${skillMeta.stats.downloads}`);

    await uploadSkill(url, serviceKey, slug, skillMeta, owner);

  } else if (args[0] === '--all' || args[0] === '--batch') {
    const limit = args[0] === '--batch' ? parseInt(args[1] || '10', 10) : Infinity;
    const skip = args[0] === '--batch' && args[2] ? parseInt(args[2], 10) : 0;

    // Only upload skills that have owner mappings in README
    const skillsToUpload = Array.from(metadata.entries())
      .filter(([slug]) => owners.has(slug))
      .slice(skip, skip + limit);

    console.log(`\n🚀 Uploading ${skillsToUpload.length} skills (skip=${skip}, limit=${limit})...\n`);
    let success = 0;
    let failed = 0;

    for (const [slug, skillMeta] of skillsToUpload) {
      const owner = owners.get(slug)!;
      try {
        await uploadSkill(url, serviceKey, slug, skillMeta, owner);
        success++;
      } catch (err) {
        console.error(`  ❌ Failed: ${slug} - ${err}`);
        failed++;
      }
    }

    console.log(`\n✅ Done! Success: ${success}, Failed: ${failed}`);

  } else if (args[0] === '--dry-run') {
    console.log('\n📋 Dry run - showing first 10 skills:\n');
    let count = 0;
    for (const [slug, skillMeta] of metadata) {
      if (count >= 10) break;
      const owner = owners.get(slug) || 'unknown';
      const zipExists = fs.existsSync(path.join(ZIPS_DIR, `${slug}.zip`));
      console.log(`  ${zipExists ? '✓' : '✗'} ${slug} | ${owner} | ${skillMeta.stats.downloads} downloads`);
      count++;
    }
  }
}

main().catch(console.error);
