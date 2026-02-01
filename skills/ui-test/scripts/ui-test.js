#!/usr/bin/env node
/**
 * UI Test — Plain English E2E test manager
 * 
 * Stores test definitions as JSON. The agent executes them
 * via the browser tool, interpreting plain English steps.
 */

const fs = require('fs');
const path = require('path');

const TESTS_DIR = path.join(process.env.HOME, '.ui-tests');
const RUNS_DIR = path.join(TESTS_DIR, 'runs');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}
ensureDir(TESTS_DIR);
ensureDir(RUNS_DIR);

// ── Helpers ──

function slugify(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function testPath(name) {
  return path.join(TESTS_DIR, `${slugify(name)}.json`);
}

function loadTest(name) {
  const p = testPath(name);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function saveTest(test) {
  const p = testPath(test.name);
  fs.writeFileSync(p, JSON.stringify(test, null, 2));
  return p;
}

// ── Commands ──

function create(name, url, steps) {
  if (!name) { console.error('Usage: ui-test.js create <name> <url> <steps...>'); process.exit(1); }
  
  const existing = loadTest(name);
  if (existing) {
    console.error(`❌ Test "${name}" already exists. Use 'update' to modify.`);
    process.exit(1);
  }

  const test = {
    name,
    slug: slugify(name),
    url: url || '',
    steps: steps || [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    lastRun: null
  };

  const p = saveTest(test);
  console.log(`✅ Created test: "${name}"`);
  console.log(`   URL: ${url || '(not set)'}`);
  console.log(`   Steps: ${test.steps.length}`);
  console.log(`   File: ${p}`);
  return test;
}

function update(name, data) {
  const test = loadTest(name);
  if (!test) { console.error(`❌ Test "${name}" not found`); process.exit(1); }

  if (data.url) test.url = data.url;
  if (data.steps) test.steps = data.steps;
  if (data.addStep) test.steps.push(data.addStep);
  test.updatedAt = new Date().toISOString();

  saveTest(test);
  console.log(`✅ Updated test: "${name}"`);
  console.log(`   URL: ${test.url}`);
  console.log(`   Steps: ${test.steps.length}`);
  for (let i = 0; i < test.steps.length; i++) {
    console.log(`   ${i + 1}. ${test.steps[i]}`);
  }
}

function get(name) {
  const test = loadTest(name);
  if (!test) { console.error(`❌ Test "${name}" not found`); process.exit(1); }
  console.log(JSON.stringify(test, null, 2));
}

function list() {
  ensureDir(TESTS_DIR);
  const files = fs.readdirSync(TESTS_DIR).filter(f => f.endsWith('.json') && f !== 'config.json');
  
  if (files.length === 0) {
    console.log('📋 No tests defined yet.');
    console.log('Create one: ui-test.js create "my test" https://myapp.com');
    return;
  }

  console.log(`📋 UI Tests (${files.length})`);
  console.log('='.repeat(50));
  
  for (const f of files) {
    const test = JSON.parse(fs.readFileSync(path.join(TESTS_DIR, f), 'utf8'));
    const status = test.lastRun 
      ? (test.lastRun.passed ? '✅' : '❌') + ` (${test.lastRun.date})`
      : '⏸ never run';
    console.log(`\n  ${test.name}`);
    console.log(`  URL: ${test.url || '(none)'}`);
    console.log(`  Steps: ${test.steps.length} | Status: ${status}`);
    for (let i = 0; i < test.steps.length; i++) {
      console.log(`    ${i + 1}. ${test.steps[i]}`);
    }
  }
}

function remove(name) {
  if (!name) { console.error('Usage: ui-test.js remove <name>'); process.exit(1); }
  const p = testPath(name);
  if (!fs.existsSync(p)) { console.error(`❌ Test "${name}" not found`); process.exit(1); }
  fs.unlinkSync(p);
  console.log(`🗑 Deleted test: "${name}"`);
}

function saveRun(name, result) {
  const test = loadTest(name);
  if (!test) { console.error(`❌ Test "${name}" not found`); process.exit(1); }

  const run = {
    testName: name,
    date: new Date().toISOString(),
    passed: result.passed === 'true' || result.passed === true,
    duration: result.duration || null,
    stepResults: result.stepResults ? JSON.parse(result.stepResults) : [],
    screenshots: result.screenshots ? JSON.parse(result.screenshots) : [],
    error: result.error || null
  };

  // Save run
  const runFile = path.join(RUNS_DIR, `${slugify(name)}-${Date.now()}.json`);
  fs.writeFileSync(runFile, JSON.stringify(run, null, 2));

  // Update test's lastRun
  test.lastRun = { date: run.date, passed: run.passed };
  saveTest(test);

  console.log(`${run.passed ? '✅' : '❌'} Run saved: ${name}`);
  console.log(`   Date: ${run.date}`);
  console.log(`   Passed: ${run.passed}`);
  if (run.error) console.log(`   Error: ${run.error}`);
  console.log(`   File: ${runFile}`);
}

function runs(name) {
  ensureDir(RUNS_DIR);
  const prefix = name ? slugify(name) : '';
  const files = fs.readdirSync(RUNS_DIR)
    .filter(f => f.endsWith('.json') && (!prefix || f.startsWith(prefix)))
    .sort()
    .reverse();

  if (files.length === 0) {
    console.log(`📊 No runs found${name ? ` for "${name}"` : ''}.`);
    return;
  }

  console.log(`📊 Test Runs${name ? ` — ${name}` : ''} (${files.length})`);
  console.log('='.repeat(50));

  for (const f of files.slice(0, 20)) {
    const run = JSON.parse(fs.readFileSync(path.join(RUNS_DIR, f), 'utf8'));
    const icon = run.passed ? '✅' : '❌';
    const steps = run.stepResults || [];
    const passCount = steps.filter(s => s.passed).length;
    console.log(`${icon} ${run.date} — ${run.testName} (${passCount}/${steps.length} steps)`);
    if (run.error) console.log(`   Error: ${run.error}`);
  }
}

// ── Playwright Export ──

function exportPlaywright(name, outFile) {
  const test = loadTest(name);
  if (!test) { console.error(`❌ Test "${name}" not found`); process.exit(1); }
  if (test.steps.length === 0) { console.error(`❌ Test "${name}" has no steps`); process.exit(1); }

  // Find latest successful run for selector hints
  const runFiles = fs.readdirSync(RUNS_DIR)
    .filter(f => f.startsWith(test.slug) && f.endsWith('.json'))
    .sort().reverse();

  let runData = null;
  for (const rf of runFiles) {
    const r = JSON.parse(fs.readFileSync(path.join(RUNS_DIR, rf), 'utf8'));
    if (r.passed) { runData = r; break; }
  }

  const lines = [];
  lines.push(`import { test, expect } from '@playwright/test';`);
  lines.push('');
  lines.push(`test.describe('${test.name}', () => {`);
  if (test.url) {
    lines.push(`  test.beforeEach(async ({ page }) => {`);
    lines.push(`    await page.goto('${test.url}');`);
    lines.push(`  });`);
    lines.push('');
  }
  lines.push(`  test('${test.name}', async ({ page }) => {`);

  for (let i = 0; i < test.steps.length; i++) {
    const step = test.steps[i];
    const stepResult = runData?.stepResults?.[i];
    lines.push(`    // Step ${i + 1}: ${step}`);
    lines.push(`    ${stepToPlaywright(step, stepResult)}`);
    lines.push('');
  }

  lines.push(`  });`);
  lines.push(`});`);
  lines.push('');

  const code = lines.join('\n');
  const output = outFile || path.join(process.cwd(), 'tests', `${test.slug}.spec.ts`);

  ensureDir(path.dirname(output));
  fs.writeFileSync(output, code);
  console.log(`✅ Exported Playwright script: ${output}`);
  console.log('');
  console.log(code);
}

function stepToPlaywright(step, stepResult) {
  const s = step.toLowerCase();

  // Use selector from run data if available
  const selector = stepResult?.selector || null;
  const ref = stepResult?.ref || null;

  // Click
  if (s.match(/^click\s+(the\s+)?/i)) {
    const target = step.replace(/^click\s+(the\s+)?/i, '').trim().replace(/["']/g, '');
    if (selector) return `await page.locator('${selector}').click();`;
    if (s.includes('button')) {
      const btnName = target.replace(/\s*button\s*/i, '').trim();
      return `await page.getByRole('button', { name: '${btnName}' }).click();`;
    }
    if (s.includes('link')) {
      const linkName = target.replace(/\s*link\s*/i, '').trim();
      return `await page.getByRole('link', { name: '${linkName}' }).click();`;
    }
    return `await page.getByText('${target}').click();`;
  }

  // Type / fill
  if (s.match(/^(type|enter|fill|input)\s+/i)) {
    const match = step.match(/(?:type|enter|fill|input)\s+["']?(.+?)["']?\s+(?:in|into|in the|into the)\s+(?:the\s+)?(.+)/i);
    if (match) {
      const value = match[1].trim();
      const field = match[2].trim().replace(/\s*field\s*/i, '').replace(/["']/g, '');
      if (selector) return `await page.locator('${selector}').fill('${value}');`;
      return `await page.getByLabel('${field}').fill('${value}');`;
    }
    return `// TODO: parse step — ${step}`;
  }

  // Verify / assert / expect / check / should
  if (s.match(/^(verify|assert|expect|check|should|confirm|see)\s+/i)) {
    // URL check
    if (s.includes('url') && s.includes('contain')) {
      const urlMatch = step.match(/contains?\s+["']?([^\s"']+)["']?/i);
      if (urlMatch) return `await expect(page).toHaveURL(/${urlMatch[1].replace(/\//g, '\\/')}/);`;
    }
    // Text visible
    const textMatch = step.match(/(?:shows?|contains?|displays?|has|see|visible)\s+["']?(.+?)["']?\s*$/i);
    if (textMatch) {
      const text = textMatch[1].replace(/["']/g, '');
      return `await expect(page.getByText('${text}')).toBeVisible();`;
    }
    return `// TODO: parse assertion — ${step}`;
  }

  // Wait
  if (s.match(/^wait\s+/i)) {
    if (s.includes('load')) return `await page.waitForLoadState('networkidle');`;
    const timeMatch = s.match(/(\d+)\s*(?:s|sec|seconds)/);
    if (timeMatch) return `await page.waitForTimeout(${parseInt(timeMatch[1]) * 1000});`;
    return `await page.waitForLoadState('networkidle');`;
  }

  // Scroll
  if (s.includes('scroll')) {
    if (s.includes('down')) return `await page.evaluate(() => window.scrollBy(0, 500));`;
    if (s.includes('up')) return `await page.evaluate(() => window.scrollBy(0, -500));`;
    if (s.includes('bottom')) return `await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));`;
    return `await page.evaluate(() => window.scrollBy(0, 500));`;
  }

  // Screenshot
  if (s.includes('screenshot')) {
    return `await page.screenshot({ path: 'step-screenshot.png' });`;
  }

  // Select / dropdown
  if (s.match(/^select\s+/i)) {
    const selMatch = step.match(/select\s+["']?(.+?)["']?\s+(?:from|in)\s+(?:the\s+)?(.+)/i);
    if (selMatch) {
      return `await page.getByLabel('${selMatch[2].trim()}').selectOption('${selMatch[1].trim()}');`;
    }
  }

  // Check checkbox
  if (s.match(/^(check|toggle)\s+/i)) {
    const target = step.replace(/^(check|toggle)\s+(the\s+)?/i, '').trim();
    return `await page.getByLabel('${target}').check();`;
  }

  // Navigate / go to
  if (s.match(/^(navigate|go|open|visit)\s+/i)) {
    const urlMatch = step.match(/(?:to|at)\s+(\S+)/i);
    if (urlMatch) return `await page.goto('${urlMatch[1]}');`;
  }

  // Fallback
  return `// TODO: manually implement — ${step}`;
}

// ── Main ──

const args = process.argv.slice(2);
const command = args[0] || 'help';

switch (command) {
  case 'create': {
    const name = args[1];
    const url = args[2] || '';
    const steps = args.slice(3);
    create(name, url, steps);
    break;
  }
  case 'update': {
    const name = args[1];
    const dataStr = args.slice(2).join(' ');
    try {
      const data = JSON.parse(dataStr);
      update(name, data);
    } catch {
      // Treat as adding a step
      update(name, { addStep: dataStr });
    }
    break;
  }
  case 'set-url': {
    const name = args[1];
    const url = args[2];
    if (!name || !url) { console.error('Usage: ui-test.js set-url <name> <url>'); process.exit(1); }
    update(name, { url });
    break;
  }
  case 'add-step': {
    const name = args[1];
    const step = args.slice(2).join(' ');
    if (!name || !step) { console.error('Usage: ui-test.js add-step <name> <step>'); process.exit(1); }
    update(name, { addStep: step });
    break;
  }
  case 'set-steps': {
    const name = args[1];
    const stepsJson = args.slice(2).join(' ');
    try {
      const steps = JSON.parse(stepsJson);
      update(name, { steps });
    } catch (e) {
      console.error('Steps must be a JSON array: ["step1", "step2", ...]');
      process.exit(1);
    }
    break;
  }
  case 'get':
    get(args[1]);
    break;
  case 'list':
    list();
    break;
  case 'remove':
  case 'delete':
    remove(args[1]);
    break;
  case 'save-run': {
    const name = args[1];
    const result = {};
    for (let i = 2; i < args.length; i++) {
      const [k, ...v] = args[i].split('=');
      result[k] = v.join('=');
    }
    saveRun(name, result);
    break;
  }
  case 'runs':
    runs(args[1]);
    break;
  case 'export': {
    const name = args[1];
    const outFile = args[2] || null;
    exportPlaywright(name, outFile);
    break;
  }
  case 'help':
  default:
    console.log(`
🧪 UI Test — Plain English E2E Testing

Commands:
  create <name> [url] [steps...]   Create a new test
  set-url <name> <url>             Set/update the test URL
  add-step <name> <step>           Add a step (plain English)
  set-steps <name> <json-array>    Replace all steps
  get <name>                       Show test definition (JSON)
  list                             List all tests
  remove <name>                    Delete a test
  save-run <name> key=val...       Save a test run result
  runs [name]                      Show run history

Tests stored in: ~/.ui-tests/
Run history in: ~/.ui-tests/runs/

Workflow:
  1. Create a test:  ui-test.js create "login flow" https://myapp.com
  2. Add steps:      ui-test.js add-step "login flow" "click the Sign In button"
  3. Agent executes via browser tool, interpreting each step
  4. Results saved:  ui-test.js save-run "login flow" passed=true ...
`);
}
