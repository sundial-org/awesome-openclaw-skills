#!/usr/bin/env node

/**
 * SkillGuard CLI
 * Usage:
 *   skillguard scan <path>          Scan a local skill directory
 *   skillguard scan-hub <slug>      Download and scan a ClawHub skill
 *   skillguard check <text>         Check text for prompt injection
 */

import { readFile } from 'fs/promises';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { SkillScanner } from './scanner.js';
import { formatTextReport, formatCompactReport } from './reporter.js';
import { downloadSkillForScan } from './clawhub.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function loadRules() {
  const rulesPath = join(__dirname, '..', 'rules', 'dangerous-patterns.json');
  const data = JSON.parse(await readFile(rulesPath, 'utf-8'));
  return data.rules;
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`
SkillGuard v0.1.0 — Agent Security Scanner

Usage:
  skillguard scan <path>          Scan a local skill directory
  skillguard scan-hub <slug>      Download and scan a ClawHub skill
  skillguard check "<text>"       Check text for prompt injection/threats
  skillguard batch <dir>          Scan all subdirectories as skills

Options:
  --json        Output raw JSON report
  --compact     Output compact format (for chat)
  --quiet       Only output score and verdict
    `);
    process.exit(0);
  }

  const flags = {
    json: args.includes('--json'),
    compact: args.includes('--compact'),
    quiet: args.includes('--quiet'),
  };

  const rules = await loadRules();
  const scanner = new SkillScanner(rules);

  switch (command) {
    case 'scan': {
      const targetPath = resolve(args[1] || '.');
      const report = await scanner.scanDirectory(targetPath);

      if (flags.json) {
        console.log(JSON.stringify(report, null, 2));
      } else if (flags.compact) {
        console.log(formatCompactReport(report));
      } else if (flags.quiet) {
        console.log(`${report.score}/100 ${report.risk} — ${report.findings.length} finding(s)`);
      } else {
        console.log(formatTextReport(report));
      }

      // Exit code reflects risk
      process.exit(report.score < 50 ? 1 : 0);
    }

    case 'scan-hub': {
      const slug = args[1];
      if (!slug) {
        console.error('Error: provide a skill slug. Usage: skillguard scan-hub <slug>');
        process.exit(1);
      }

      console.error(`Downloading ${slug} from ClawHub...`);
      let download;
      try {
        download = await downloadSkillForScan(slug);
      } catch (err) {
        console.error(`Failed: ${err.message}`);
        process.exit(1);
      }

      try {
        const report = await scanner.scanDirectory(download.path);
        if (flags.json) {
          console.log(JSON.stringify(report, null, 2));
        } else if (flags.compact) {
          console.log(formatCompactReport(report, slug));
        } else {
          console.log(formatTextReport(report));
        }
        process.exit(report.score < 50 ? 1 : 0);
      } finally {
        await download.cleanup();
      }
    }

    case 'check': {
      const text = args.slice(1).filter(a => !a.startsWith('--')).join(' ');
      if (!text) {
        console.error('Error: provide text to check. Usage: skillguard check "text here"');
        process.exit(1);
      }

      const findings = scanner.scanContent(text, 'input');
      if (findings.length === 0) {
        console.log('✅ No threats detected.');
        process.exit(0);
      }

      console.log(`⚠️ ${findings.length} finding(s):\n`);
      for (const f of findings) {
        console.log(`  ${f.severity.toUpperCase()} [${f.ruleId}] ${f.title}`);
        console.log(`    Match: ${f.match}`);
        console.log('');
      }
      process.exit(1);
    }

    case 'batch': {
      const batchDir = resolve(args[1] || '.');
      const { readdir } = await import('fs/promises');
      const entries = await readdir(batchDir, { withFileTypes: true });
      const dirs = entries.filter(e => e.isDirectory()).map(e => e.name);

      console.log(`Scanning ${dirs.length} skills in ${batchDir}...\n`);

      const results = [];
      for (const dir of dirs) {
        const fullPath = join(batchDir, dir);
        const report = await scanner.scanDirectory(fullPath);
        results.push({ name: dir, score: report.score, risk: report.risk, findings: report.findings.length });
        const icon = report.score >= 80 ? '✅' : report.score >= 50 ? '⚠️' : '🔴';
        console.log(`  ${icon} ${dir.padEnd(30)} ${report.score}/100  ${report.risk.padEnd(8)} ${report.findings.length} finding(s)`);
      }

      console.log(`\n${results.length} skills scanned.`);
      const dangerous = results.filter(r => r.score < 50);
      if (dangerous.length > 0) {
        console.log(`🔴 ${dangerous.length} skill(s) flagged as HIGH/CRITICAL risk.`);
      }
      process.exit(dangerous.length > 0 ? 1 : 0);
    }

    default:
      console.error(`Unknown command: ${command}. Run skillguard --help for usage.`);
      process.exit(1);
  }
}

main().catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
