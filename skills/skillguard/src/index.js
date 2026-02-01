/**
 * SkillGuard — Agent Security Scanner
 * Main entry point and public API
 */

export { SkillScanner } from './scanner.js';
export { formatTextReport, formatCompactReport, formatMoltbookPost } from './reporter.js';
export { searchSkills, downloadSkillForScan, getSkillInfo } from './clawhub.js';

import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { SkillScanner } from './scanner.js';
import { formatTextReport, formatCompactReport } from './reporter.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * Quick scan — one function to scan a path and get a report
 */
export async function quickScan(skillPath, options = {}) {
  const rulesPath = join(__dirname, '..', 'rules', 'dangerous-patterns.json');
  const rulesData = JSON.parse(await readFile(rulesPath, 'utf-8'));
  const scanner = new SkillScanner(rulesData.rules);
  const report = await scanner.scanDirectory(skillPath);

  if (options.format === 'compact') {
    return { report, text: formatCompactReport(report, options.name) };
  }
  return { report, text: formatTextReport(report) };
}

/**
 * Quick content scan — scan arbitrary text for threats
 */
export function quickContentScan(content, source = 'unknown') {
  // Lazy load rules synchronously for content scanning
  const rulesPath = join(__dirname, '..', 'rules', 'dangerous-patterns.json');
  // We need to use dynamic import for this
  return import('fs').then(async (fs) => {
    const rulesData = JSON.parse(await fs.promises.readFile(rulesPath, 'utf-8'));
    const scanner = new SkillScanner(rulesData.rules);
    return scanner.scanContent(content, source);
  });
}
