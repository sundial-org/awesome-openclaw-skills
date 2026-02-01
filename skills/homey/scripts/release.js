#!/usr/bin/env node

const { execSync } = require('node:child_process');
const fs = require('node:fs');

function run(cmd, opts = {}) {
  return execSync(cmd, { stdio: 'pipe', encoding: 'utf8', ...opts }).trim();
}

function readPkgVersion() {
  const raw = fs.readFileSync('package.json', 'utf8');
  const pkg = JSON.parse(raw);
  return String(pkg.version || '').trim();
}

function runInherit(cmd) {
  execSync(cmd, { stdio: 'inherit' });
}

function fail(msg) {
  console.error(`error: ${msg}`);
  process.exit(1);
}

const bump = process.argv[2];
if (!bump) {
  fail('usage: node scripts/release.js <patch|minor|major|prerelease|x.y.z>');
}

const allowed = new Set(['patch', 'minor', 'major', 'prerelease']);
const isExplicit = /^\d+\.\d+\.\d+.*$/.test(bump);
if (!allowed.has(bump) && !isExplicit) {
  fail('bump must be patch|minor|major|prerelease or an explicit semver like 1.2.3');
}

// Ensure we’re on a branch and working tree is clean.
try {
  const status = run('git status --porcelain');
  if (status) {
    fail('working tree is not clean. Commit or stash changes first.');
  }
} catch (e) {
  fail(`git not available? ${e.message}`);
}

let current;
try {
  current = readPkgVersion();
} catch (e) {
  fail(`failed to read package.json version: ${e.message}`);
}

console.log(`Current version: ${current}`);

// npm version creates a commit + tag (unless --no-git-tag-version, which we do not use).
// It also updates package-lock.json.
try {
  runInherit(`npm version ${bump} -m "Release %s"`);
} catch (e) {
  fail(`npm version failed: ${e.message}`);
}

const next = readPkgVersion();
console.log(`\nVersion bumped: ${current} -> ${next}`);

console.log('\nNext steps:');
console.log('  1) Update CHANGELOG.md (optional but recommended)');
console.log('  2) Push commit + tag:');
console.log('     git push origin HEAD --follow-tags');
console.log('\nTag push triggers the publish-clawdhub workflow.');
