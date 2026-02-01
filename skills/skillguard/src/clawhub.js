/**
 * SkillGuard ClawHub Integration
 * Pull skills from ClawHub registry for scanning
 */

import { execSync } from 'child_process';
import { mkdtemp, rm } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';

/**
 * Search ClawHub for skills
 */
export async function searchSkills(query, limit = 20) {
  try {
    const output = execSync(`clawhub search "${query}" --json 2>/dev/null`, {
      encoding: 'utf-8',
      timeout: 30000,
    });
    return JSON.parse(output);
  } catch {
    // Try without --json flag
    try {
      const output = execSync(`clawhub search "${query}" 2>/dev/null`, {
        encoding: 'utf-8',
        timeout: 30000,
      });
      return parseClawHubTextOutput(output);
    } catch {
      return [];
    }
  }
}

/**
 * Install a skill to a temp directory for scanning
 */
export async function downloadSkillForScan(slug) {
  const tempDir = await mkdtemp(join(tmpdir(), 'skillguard-'));
  try {
    execSync(`clawhub install ${slug} --target "${tempDir}" 2>/dev/null`, {
      encoding: 'utf-8',
      timeout: 60000,
    });
    return { path: tempDir, cleanup: () => rm(tempDir, { recursive: true, force: true }) };
  } catch (err) {
    await rm(tempDir, { recursive: true, force: true });
    throw new Error(`Failed to download skill ${slug}: ${err.message}`);
  }
}

/**
 * Get skill info from ClawHub
 */
export async function getSkillInfo(slug) {
  try {
    const output = execSync(`clawhub info ${slug} 2>/dev/null`, {
      encoding: 'utf-8',
      timeout: 15000,
    });
    return output;
  } catch {
    return null;
  }
}

function parseClawHubTextOutput(text) {
  // Basic parser for clawhub CLI text output
  const skills = [];
  const lines = text.split('\n').filter(l => l.trim());
  for (const line of lines) {
    const match = line.match(/^(\S+)\s+/);
    if (match) {
      skills.push({ slug: match[1], raw: line.trim() });
    }
  }
  return skills;
}
