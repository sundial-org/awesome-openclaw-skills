#!/usr/bin/env node
/**
 * Skill Auditor — Static security scanner for Moltbot skills
 * Usage: node scan-skill.js <skill-directory> [--json <output-path>]
 * Exit codes: 0 = clean, 1 = findings, 2 = error
 */

const fs = require('fs');
const path = require('path');

// ─── Threat Patterns ───────────────────────────────────────────────

const PATTERNS = [
  // === FILE ACCESS ===
  {
    id: 'path-traversal',
    category: 'File Access',
    severity: 'high',
    regex: /\.\.[\/\\]|['"]\.\.['"]\s*,\s*['"]\.\.['"]/g,
    description: 'Path traversal — attempts to access files outside skill directory'
  },
  {
    id: 'absolute-path-windows',
    category: 'File Access',
    severity: 'medium',
    regex: /[A-Z]:\\(?:Users|Windows|Program\s*Files|ProgramData|System32)[\w\\\s]/gi,
    description: 'Absolute Windows path to sensitive directory',
    contextNote: 'Lower severity in reference docs — may be legitimate documentation'
  },
  {
    id: 'absolute-path-unix',
    category: 'File Access',
    severity: 'high',
    regex: /(?<!#!.*)(?<!file:\/\/)(?:^|[^.a-z])\/(etc|home|root|var)\/\S+/gm,
    description: 'Absolute Unix path — accesses system directories'
  },
  {
    id: 'homedir-access',
    category: 'File Access',
    severity: 'high',
    regex: /(?:os\.homedir\(\)|process\.env\.(?:HOME|USERPROFILE)\b)/g,
    description: 'Home directory access in code — may reach user files outside workspace'
  },
  {
    id: 'memory-file-access',
    category: 'Sensitive File Access',
    severity: 'critical',
    regex: /(?:readFile|writeFile|openSync|readFileSync|writeFileSync|fs\.\w+|open\(|cat\s+|type\s+|Get-Content|Set-Content).*(?:MEMORY\.md|TOOLS\.md|SOUL\.md|USER\.md|AGENTS\.md|HEARTBEAT\.md|moltbot\.json|clawdbot\.json)|(?:MEMORY\.md|TOOLS\.md|SOUL\.md|USER\.md|AGENTS\.md|HEARTBEAT\.md|moltbot\.json|clawdbot\.json).*(?:readFile|writeFile|open|read|write|fs\.\w+)/gi,
    description: 'Code that reads/writes Moltbot core files — could access agent memory or config'
  },
  {
    id: 'credential-file-access',
    category: 'Sensitive File Access',
    severity: 'critical',
    regex: /(?:\.ssh[\/\\]|[\/\\]\.env\b|\.aws[\/\\]credentials|[\/\\]id_rsa\b|[\/\\]id_ed25519\b|\.gnupg[\/\\]|[\/\\]\.npmrc\b|[\/\\]\.pypirc\b)/g,
    description: 'Access to credential/key files'
  },

  {
    id: 'env-sensitive-access',
    category: 'Sensitive File Access',
    severity: 'high',
    regex: /(?:os\.environ(?:\.get)?\s*[\[(]|process\.env\s*[\[.]|getenv\s*\()\s*['"]?(?:API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIALS|AWS_|GITHUB_TOKEN|OPENAI|ANTHROPIC)/gi,
    description: 'Reads sensitive environment variables — could harvest API keys or secrets'
  },

  // === NETWORK ===
  {
    id: 'http-url',
    category: 'Network',
    severity: 'medium',
    regex: /https?:\/\/(?!(?:example\.com|localhost|127\.0\.0\.1|your[\w-]*\.example))[^\s"'`)>\]]+/g,
    description: 'HTTP URL — skill makes or references external network calls',
    extractMatch: true
  },
  {
    id: 'fetch-call',
    category: 'Network',
    severity: 'high',
    regex: /\b(?:axios|needle|superagent|XMLHttpRequest|urllib|requests\.(?:get|post|put|delete))\s*\(|(?:^|[^.\w])fetch\s*\(\s*['"`h]/gm,
    description: 'HTTP library call — makes outbound network requests'
  },
  {
    id: 'curl-wget',
    category: 'Network',
    severity: 'high',
    regex: /\b(?:curl|wget|Invoke-WebRequest|Invoke-RestMethod)\s+['"`\-h$]/g,
    description: 'CLI HTTP tool — makes outbound network requests'
  },
  {
    id: 'webhook-exfil',
    category: 'Data Exfiltration',
    severity: 'critical',
    regex: /(?:webhook\.site|requestbin|pipedream|ngrok|burpcollaborator|interact\.sh|oastify)/gi,
    description: 'Known data capture service — likely exfiltration endpoint'
  },
  {
    id: 'dns-exfil',
    category: 'Data Exfiltration',
    severity: 'high',
    regex: /\b(?:nslookup|dig|host)\s+.*\$|dns.*exfil/gi,
    description: 'Possible DNS exfiltration technique'
  },

  // === SHELL EXECUTION ===
  {
    id: 'shell-exec-node',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\brequire\s*\(\s*['"]child_process['"]\s*\)|(?:^|[^.])(?:execSync|spawnSync|execFile|execFileSync)\s*\(/gm,
    description: 'Node.js shell execution — can run arbitrary system commands'
  },
  {
    id: 'shell-exec-python',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\b(?:os\.system\s*\(|os\.popen\s*\(|subprocess\.(?:run|call|Popen|check_output)\s*\(|__import__\s*\(\s*['"](?:subprocess|os|shutil)['"]\s*\))/g,
    description: 'Python shell execution — can run arbitrary system commands'
  },
  {
    id: 'shell-exec-generic',
    category: 'Shell Execution',
    severity: 'high',
    regex: /(?:^|[^.\w])eval\s*\(\s*[^)]+\)|new\s+Function\s*\(/gm,
    description: 'Dynamic code evaluation — could execute arbitrary code'
  },
  {
    id: 'powershell-invoke',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\b(?:Invoke-Expression|iex|Start-Process|\.Invoke)\b/gi,
    description: 'PowerShell execution — can run arbitrary commands'
  },

  // === OBFUSCATION ===
  {
    id: 'base64-encode',
    category: 'Obfuscation',
    severity: 'high',
    regex: /(?:btoa|atob|Buffer\.from\([^)]+,\s*['"]base64['"]\)|base64\.(?:b64encode|b64decode|encode|decode)|Convert\]::(?:ToBase64|FromBase64))/g,
    description: 'Base64 encoding/decoding — may hide malicious payloads'
  },
  {
    id: 'base64-string',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?<![\w:\/\-.])(?![0-9a-f]{40,})[A-Za-z0-9+\/]{80,}={0,2}(?![\w\-])/g,
    description: 'Long base64-like string — could be an encoded payload',
    maxMatches: 3
  },
  {
    id: 'hex-string',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?:\\x[0-9a-fA-F]{2}){4,}/g,
    description: 'Hex-encoded string — may hide file paths or URLs'
  },
  {
    id: 'unicode-escape',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?:\\u[0-9a-fA-F]{4}){3,}/g,
    description: 'Unicode escape sequence — may hide instructions or paths'
  },
  {
    id: 'string-concat-obfuscation',
    category: 'Obfuscation',
    severity: 'high',
    regex: /["'][A-Z]{1,4}["']\s*\+\s*["'][A-Z]{1,4}["']/g,
    description: 'String concatenation of short uppercase fragments — may be building sensitive names'
  },
  {
    id: 'zero-width-chars',
    category: 'Obfuscation',
    severity: 'critical',
    regex: /[\u200B\u200C\u200D\uFEFF\u00AD\u2060\u180E]/g,
    description: 'Zero-width/invisible characters — hidden content that renders invisible'
  },
  {
    id: 'html-comment-instructions',
    category: 'Obfuscation',
    severity: 'high',
    regex: /<!--[\s\S]*?(?:ignore|disregard|instruction|important|system|read|send|fetch|execute|include|also|override)[\s\S]*?-->/gi,
    description: 'HTML comment with suspicious instructions — hidden directives'
  },

  // === PROMPT INJECTION ===
  {
    id: 'prompt-injection-ignore',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?|context)/gi,
    description: 'Prompt injection — attempts to override agent instructions'
  },
  {
    id: 'prompt-injection-new-instructions',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:new|updated|revised|real|actual|true)\s+(?:instructions?|system\s*prompt|directives?|rules?)\s*:/gi,
    description: 'Prompt injection — attempts to inject new instructions'
  },
  {
    id: 'prompt-injection-role',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:you\s+are\s+now|act\s+as|pretend\s+(?:to\s+be|you\s+are)|your\s+new\s+role|from\s+now\s+on\s+you)/gi,
    description: 'Prompt injection — attempts to change agent identity/role'
  },
  {
    id: 'prompt-injection-system',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:^|\s)(?:\[SYSTEM\]|SYSTEM:|<\|system\|>|<system>)/gm,
    description: 'Prompt injection — fake system message delimiter'
  },
  {
    id: 'prompt-injection-delimiter',
    category: 'Prompt Injection',
    severity: 'high',
    regex: /(?:```system|<\|im_start\|>|<\|endoftext\|>|<\|separator\|>|\[INST\]|\[\/INST\])/g,
    description: 'Prompt injection — LLM delimiter manipulation'
  },

  // === DATA EXFILTRATION TECHNIQUES ===
  {
    id: 'markdown-image-exfil',
    category: 'Data Exfiltration',
    severity: 'critical',
    regex: /!\[.*?\]\(https?:\/\/.*?[?&].*?(?:data|token|key|secret|content|payload|q)=/gi,
    description: 'Markdown image with query parameters — possible data exfiltration via image URL'
  },
  {
    id: 'message-tool-abuse',
    category: 'Data Exfiltration',
    severity: 'high',
    regex: /\b(?:sessions_send|sessions_spawn)\b.*(?:send|target|to)\b/gi,
    description: 'References Moltbot session tools — could exfiltrate data via messaging'
  },

  // === PERSISTENCE ===
  {
    id: 'memory-write',
    category: 'Persistence',
    severity: 'critical',
    regex: /(?:writeFile|appendFile|fs\.write|Set-Content|Out-File|>>?\s*).*(?:MEMORY\.md|HEARTBEAT\.md|AGENTS\.md|SOUL\.md|memory\/)|(?:MEMORY\.md|HEARTBEAT\.md|AGENTS\.md|SOUL\.md|memory\/).*(?:writeFile|appendFile|write|>)/gi,
    description: 'Writes to agent memory/config files — persistence attack vector'
  },
  {
    id: 'cron-manipulation',
    category: 'Persistence',
    severity: 'critical',
    regex: /\b(?:schtasks\s+\/create|crontab\s+-[ew]|cron\.add|cron\.update)\b/gi,
    description: 'Creates scheduled tasks — could establish persistent execution'
  },
  {
    id: 'startup-persistence',
    category: 'Persistence',
    severity: 'critical',
    regex: /(?:autorun|HKLM\\|HKCU\\|\\Run\\|init\.d\/|systemd\s+enable|launchctl\s+load|\.plist\b|schtasks\s+\/create)/gi,
    description: 'System startup/persistence mechanism'
  },

  // === PRIVILEGE ESCALATION ===
  {
    id: 'browser-tool',
    category: 'Privilege Escalation',
    severity: 'high',
    regex: /\brequire\s*\(\s*['"](?:puppeteer|playwright|selenium)['"]\s*\)|\.(?:newPage|goto|navigate)\s*\(/g,
    description: 'Browser automation — could access authenticated sessions'
  },
  {
    id: 'node-control',
    category: 'Privilege Escalation',
    severity: 'high',
    regex: /\b(?:camera_snap|screen_record|location_get)\s*\(|nodes\s*\.\s*(?:run|camera|screen|location)/g,
    description: 'Calls Moltbot node control — accesses paired devices'
  },
  {
    id: 'config-modification',
    category: 'Privilege Escalation',
    severity: 'critical',
    regex: /\b(?:config\.apply|config\.patch|gateway\.restart)\s*\(/g,
    description: 'Calls Moltbot gateway config — could modify system configuration'
  }
];

// ─── Binary Detection ──────────────────────────────────────────────

const BINARY_EXTENSIONS = new Set([
  '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.svg',
  '.mp3', '.mp4', '.wav', '.ogg', '.webm', '.avi',
  '.zip', '.tar', '.gz', '.7z', '.rar', '.skill',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.woff', '.woff2', '.ttf', '.otf', '.eot'
]);

function isBinary(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (BINARY_EXTENSIONS.has(ext)) return true;
  try {
    const buf = Buffer.alloc(512);
    const fd = fs.openSync(filePath, 'r');
    const bytesRead = fs.readSync(fd, buf, 0, 512, 0);
    fs.closeSync(fd);
    for (let i = 0; i < bytesRead; i++) {
      if (buf[i] === 0) return true;
    }
  } catch { }
  return false;
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
        if (entry.name === 'node_modules' || entry.name === '.git') continue;
        walk(full);
      } else {
        files.push(full);
      }
    }
  }
  walk(dir);
  return files;
}

// ─── Scanner ───────────────────────────────────────────────────────

// Files that are documentation, not executable code
const DOC_EXTENSIONS = new Set(['.md', '.txt', '.rst', '.html', '.css', '.json', '.yaml', '.yml', '.toml', '.xml', '.xsd', '.xsl', '.dtd', '.svg', '.csv']);

function isDocFile(filePath) {
  return DOC_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

// Downgrade severity for findings in documentation files
function adjustSeverityForContext(severity, filePath) {
  if (!isDocFile(filePath)) return severity;
  // Doc files get one level downgrade (patterns in docs are less dangerous than in scripts)
  const downgrade = { critical: 'high', high: 'medium', medium: 'low', low: 'low' };
  return downgrade[severity] || severity;
}

function scanFile(filePath, skillDir) {
  const findings = [];
  const relativePath = path.relative(skillDir, filePath);

  if (isBinary(filePath)) {
    findings.push({
      id: 'binary-file',
      category: 'Binary File',
      severity: 'medium',
      file: relativePath,
      line: 0,
      snippet: `[Binary file: ${path.basename(filePath)}]`,
      explanation: `Binary file detected — cannot be statically analyzed. Review manually.`
    });
    return findings;
  }

  let content;
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    findings.push({
      id: 'read-error',
      category: 'Error',
      severity: 'medium',
      file: relativePath,
      line: 0,
      snippet: '',
      explanation: `Could not read file: ${e.message}`
    });
    return findings;
  }

  const lines = content.split('\n');

  for (const pattern of PATTERNS) {
    let matchCount = 0;
    const maxMatches = pattern.maxMatches || 5;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      // Reset regex lastIndex for global patterns
      pattern.regex.lastIndex = 0;
      let match;
      while ((match = pattern.regex.exec(line)) !== null) {
        matchCount++;
        if (matchCount > maxMatches) break;

        const snippet = line.trim().substring(0, 200);
        const adjustedSeverity = adjustSeverityForContext(pattern.severity, filePath);
        findings.push({
          id: pattern.id,
          category: pattern.category,
          severity: adjustedSeverity,
          originalSeverity: pattern.severity !== adjustedSeverity ? pattern.severity : undefined,
          file: relativePath,
          line: i + 1,
          snippet: snippet,
          explanation: pattern.description + (pattern.severity !== adjustedSeverity ? ' (downgraded — in documentation file)' : ''),
          match: pattern.extractMatch ? match[0] : undefined
        });

        // Avoid infinite loops on zero-length matches
        if (match.index === pattern.regex.lastIndex) {
          pattern.regex.lastIndex++;
        }
      }
      if (matchCount > maxMatches) break;
    }
  }

  return findings;
}

// ─── Declared Purpose Analysis ─────────────────────────────────────

function parseSkillMd(skillDir) {
  const skillMdPath = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(skillMdPath)) {
    return { name: 'unknown', description: 'No SKILL.md found', hasSkillMd: false };
  }

  const content = fs.readFileSync(skillMdPath, 'utf-8');
  const fmMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!fmMatch) {
    return { name: 'unknown', description: 'No frontmatter', hasSkillMd: true };
  }

  const fm = fmMatch[1];
  const nameMatch = fm.match(/^name:\s*(.+)$/m);
  const descMatch = fm.match(/^description:\s*(.+)$/m);

  return {
    name: nameMatch ? nameMatch[1].trim() : 'unknown',
    description: descMatch ? descMatch[1].trim() : 'No description',
    hasSkillMd: true
  };
}

// ─── Risk Scoring ──────────────────────────────────────────────────

function calculateRisk(findings) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  const categories = new Set();

  for (const f of findings) {
    counts[f.severity] = (counts[f.severity] || 0) + 1;
    categories.add(f.category);
  }

  // Check for obfuscation + data access combo (auto-critical)
  const hasObfuscation = categories.has('Obfuscation');
  const hasDataAccess = categories.has('Sensitive File Access') || categories.has('Data Exfiltration');
  const hasPromptInjection = categories.has('Prompt Injection');

  if (hasPromptInjection || (hasObfuscation && hasDataAccess)) {
    return 'CRITICAL';
  }
  if (counts.critical > 0) return 'CRITICAL';
  if (counts.high > 0) return 'HIGH';
  if (counts.medium >= 3 || (counts.medium >= 1 && counts.low >= 2)) return 'MEDIUM';
  if (counts.medium > 0 || counts.low > 2) return 'LOW';
  return 'CLEAN';
}

// ─── Capability Summary ────────────────────────────────────────────

function summarizeCapabilities(findings) {
  const caps = new Set();
  for (const f of findings) {
    if (f.category === 'Network' || f.id === 'fetch-call' || f.id === 'curl-wget') caps.add('Makes network requests');
    if (f.category === 'File Access' || f.category === 'Sensitive File Access') caps.add('Accesses files outside skill directory');
    if (f.category === 'Shell Execution') caps.add('Executes shell commands');
    if (f.category === 'Obfuscation') caps.add('Uses obfuscation techniques');
    if (f.category === 'Prompt Injection') caps.add('Contains prompt injection attempts');
    if (f.category === 'Data Exfiltration') caps.add('Potential data exfiltration');
    if (f.category === 'Persistence') caps.add('Attempts persistence mechanisms');
    if (f.category === 'Privilege Escalation') caps.add('Attempts privilege escalation');
  }
  return Array.from(caps);
}

// ─── Description Accuracy Score ────────────────────────────────────

// Keywords that suggest a skill mentions certain capabilities in its description
const DESC_CAPABILITY_KEYWORDS = {
  'Makes network requests': [
    /\b(?:fetch|download|upload|sync|cloud|api|web|url|http|online|remote|server|connect|request|send|receive|internet)\b/i
  ],
  'Accesses files outside skill directory': [
    /\b(?:system\s*files?|user\s*files?|documents?|config|settings?|memory|workspace|home\s*dir|browse\s*files?)\b/i
  ],
  'Executes shell commands': [
    /\b(?:shell|command|terminal|exec|run\s*(?:program|process|command)|cli|system\s*command|script)\b/i
  ],
  'Uses obfuscation techniques': [],  // Should never be described — always undisclosed
  'Contains prompt injection attempts': [],  // Should never be described
  'Potential data exfiltration': [],  // Should never be described
  'Attempts persistence mechanisms': [
    /\b(?:schedul|cron|autostart|background|persist|always.?on|daemon|service)\b/i
  ],
  'Attempts privilege escalation': [
    /\b(?:browser|device|camera|screen|node|control|automat)/i
  ]
};

// Capabilities that are always suspicious if undisclosed
const ALWAYS_SUSPICIOUS = new Set([
  'Uses obfuscation techniques',
  'Contains prompt injection attempts',
  'Potential data exfiltration'
]);

function calculateAccuracyScore(description, actualCapabilities) {
  if (!description || description === 'No SKILL.md found' || description === 'No frontmatter' || description === 'No description') {
    return { score: 1, disclosed: [], undisclosed: actualCapabilities, reason: 'No description provided — impossible to verify intent' };
  }

  if (actualCapabilities.length === 0) {
    return { score: 10, disclosed: [], undisclosed: [], reason: 'Skill does what it says and nothing more' };
  }

  const disclosed = [];
  const undisclosed = [];

  for (const cap of actualCapabilities) {
    // Always-suspicious capabilities are never "disclosed" — they're inherently deceptive
    if (ALWAYS_SUSPICIOUS.has(cap)) {
      undisclosed.push(cap);
      continue;
    }

    const keywords = DESC_CAPABILITY_KEYWORDS[cap] || [];
    const mentioned = keywords.some(regex => regex.test(description));
    if (mentioned) {
      disclosed.push(cap);
    } else {
      undisclosed.push(cap);
    }
  }

  // Score calculation:
  // Start at 10
  // Each undisclosed capability deducts points based on severity
  const DEDUCTIONS = {
    'Uses obfuscation techniques': 4,
    'Contains prompt injection attempts': 5,
    'Potential data exfiltration': 5,
    'Makes network requests': 1.5,
    'Accesses files outside skill directory': 2,
    'Executes shell commands': 2,
    'Attempts persistence mechanisms': 3,
    'Attempts privilege escalation': 2
  };

  let score = 10;
  for (const cap of undisclosed) {
    score -= (DEDUCTIONS[cap] || 1);
  }

  // Bonus: if capabilities ARE disclosed, slight boost for honesty
  score += disclosed.length * 0.25;

  score = Math.max(1, Math.min(10, Math.round(score)));

  let reason;
  if (score >= 8) {
    reason = 'Description accurately reflects what the skill does';
  } else if (score >= 5) {
    reason = 'Some capabilities are not mentioned in the description';
  } else if (score >= 3) {
    reason = 'Significant undisclosed capabilities — description is misleading';
  } else {
    reason = 'Description does not match actual behavior — skill is deceptive';
  }

  return { score, disclosed, undisclosed, reason };
}

// ─── Deduplicate Findings ──────────────────────────────────────────

function deduplicateFindings(findings) {
  const seen = new Set();
  return findings.filter(f => {
    const key = `${f.id}:${f.file}:${f.line}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// ─── Main ──────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  let skillDir = null;
  let jsonOutput = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json' && args[i + 1]) {
      jsonOutput = args[++i];
    } else if (!skillDir) {
      skillDir = args[i];
    }
  }

  if (!skillDir) {
    console.error('Usage: node scan-skill.js <skill-directory> [--json <output-path>]');
    process.exit(2);
  }

  skillDir = path.resolve(skillDir);

  if (!fs.existsSync(skillDir)) {
    console.error(`Error: Directory not found: ${skillDir}`);
    process.exit(2);
  }

  // Parse skill metadata
  const skillMeta = parseSkillMd(skillDir);

  // Discover and scan files
  const files = discoverFiles(skillDir);
  let allFindings = [];

  for (const file of files) {
    const findings = scanFile(file, skillDir);
    allFindings.push(...findings);
  }

  allFindings = deduplicateFindings(allFindings);

  // Calculate risk
  const riskLevel = calculateRisk(allFindings);
  const capabilities = summarizeCapabilities(allFindings);

  // URLs found
  const urls = allFindings
    .filter(f => f.id === 'http-url' && f.match)
    .map(f => f.match);
  const uniqueUrls = [...new Set(urls)];

  // Build report
  const report = {
    skill: {
      name: skillMeta.name,
      description: skillMeta.description,
      hasSkillMd: skillMeta.hasSkillMd,
      directory: skillDir
    },
    scan: {
      timestamp: new Date().toISOString(),
      filesScanned: files.map(f => path.relative(skillDir, f)),
      fileCount: files.length
    },
    riskLevel,
    reputation: { publisher: 'Local install', tier: 'local', note: 'Installed from local source', warning: 'No publisher info available — verify source yourself.' },
    accuracyScore: calculateAccuracyScore(skillMeta.description, capabilities),
    findings: allFindings,
    findingCount: allFindings.length,
    summary: {
      declaredPurpose: skillMeta.description,
      actualCapabilities: capabilities,
      externalUrls: uniqueUrls,
      severityCounts: {
        critical: allFindings.filter(f => f.severity === 'critical').length,
        high: allFindings.filter(f => f.severity === 'high').length,
        medium: allFindings.filter(f => f.severity === 'medium').length,
        low: allFindings.filter(f => f.severity === 'low').length
      }
    }
  };

  // Output
  const json = JSON.stringify(report, null, 2);

  if (jsonOutput) {
    fs.writeFileSync(jsonOutput, json);
    console.log(`Report saved to: ${jsonOutput}`);
  } else {
    console.log(json);
  }

  // Exit code
  process.exit(allFindings.length > 0 ? 1 : 0);
}

main();
