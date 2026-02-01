/**
 * SkillGuard Scanner v0.2 — Hardened Core Engine
 * 
 * Three-layer analysis:
 * 1. Pattern matching (fast, catches obvious threats)
 * 2. AST/evasion analysis (catches obfuscation and tricks)
 * 3. Prompt injection analysis (catches social engineering)
 * 
 * Plus: context-aware scoring that reduces false positives
 */

import { readFile, readdir, stat } from 'fs/promises';
import { join, extname, basename } from 'path';
import { ASTAnalyzer } from './ast-analyzer.js';
import { PromptAnalyzer } from './prompt-analyzer.js';

const CODE_EXTENSIONS = new Set([
  '.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx',
  '.py', '.pyw',
  '.sh', '.bash', '.zsh',
  '.rb', '.pl',
]);

const TEXT_EXTENSIONS = new Set([
  '.json', '.yaml', '.yml', '.toml',
  '.md', '.txt', '.rst',
  '.env', '.env.example',
  '.cfg', '.ini', '.conf',
]);

const BINARY_EXTENSIONS = new Set([
  '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
  '.wasm', '.node', '.o', '.a',
]);

// Known-good network targets (reduce false positives)
const KNOWN_GOOD_APIS = [
  'wttr.in', 'api.github.com', 'registry.npmjs.org',
  'pypi.org', 'api.openai.com', 'api.anthropic.com',
  'api.weather.gov', 'googleapis.com', 'api.telegram.org',
];

export class SkillScanner {
  constructor(rules) {
    this.rules = rules;
    this.compiledRules = rules.map(rule => ({
      ...rule,
      compiled: rule.patterns.map(p => new RegExp(p, 'gi')),
    }));
    this.astAnalyzer = new ASTAnalyzer();
    this.promptAnalyzer = new PromptAnalyzer();
  }

  /**
   * Full skill directory scan — three-layer analysis
   */
  async scanDirectory(skillPath) {
    const report = {
      path: skillPath,
      scannedAt: new Date().toISOString(),
      version: '0.2.0',
      files: [],
      findings: [],
      score: 100,
      summary: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
      metadata: null,
      flags: [],
      declaredCapabilities: {},
      behavioralSignatures: [],
    };

    // Parse SKILL.md
    const skillMd = await this.readFileSafe(join(skillPath, 'SKILL.md'));
    if (!skillMd) {
      report.flags.push('NO_SKILL_MD');
    } else {
      report.metadata = this.parseSkillMetadata(skillMd);
      report.declaredCapabilities = this.extractDeclaredCapabilities(report.metadata);

      // Run prompt analysis on SKILL.md (common injection target)
      const promptFindings = this.promptAnalyzer.analyze(skillMd, 'SKILL.md');
      report.findings.push(...promptFindings);
    }

    // Enumerate files
    const files = await this.walkDirectory(skillPath);
    report.files = files.map(f => ({
      path: f.relativePath,
      size: f.size,
      type: f.type,
    }));

    // Check file structure
    this.checkFileStructure(files, report);

    // Scan each file
    for (const file of files) {
      if (file.type === 'binary') {
        report.findings.push({
          ruleId: 'BINARY_FILE',
          severity: 'high',
          category: 'suspicious-file',
          title: 'Binary file included in skill package',
          file: file.relativePath,
          line: 0,
          context: `Binary file: ${file.relativePath} (${file.size} bytes)`,
          weight: 15,
        });
        continue;
      }

      if (file.type === 'directory-skipped') continue;

      const content = await this.readFileSafe(file.absolutePath);
      if (!content) continue;

      // Layer 1: Pattern matching
      this.patternScan(content, file.relativePath, report);

      // Layer 2: AST/evasion analysis (JS/TS files)
      const ext = extname(file.relativePath).toLowerCase();
      if (CODE_EXTENSIONS.has(ext) && (ext.startsWith('.j') || ext.startsWith('.t') || ext.startsWith('.m') || ext.startsWith('.c'))) {
        const astFindings = this.astAnalyzer.analyze(content, file.relativePath);
        report.findings.push(...astFindings);
      }

      // Layer 3: Prompt injection analysis (text/markdown files)
      if (TEXT_EXTENSIONS.has(ext) || ext === '.md') {
        if (file.relativePath !== 'SKILL.md') { // Already scanned SKILL.md above
          const promptFindings = this.promptAnalyzer.analyze(content, file.relativePath);
          report.findings.push(...promptFindings);
        }
      }

      // Python-specific evasion detection
      if (ext === '.py' || ext === '.pyw') {
        this.pythonAnalysis(content, file.relativePath, report);
      }

      // Shell script analysis
      if (ext === '.sh' || ext === '.bash' || ext === '.zsh') {
        this.shellAnalysis(content, file.relativePath, report);
      }
    }

    // Deduplicate
    report.findings = this.deduplicateFindings(report.findings);

    // Detect behavioral signatures first (needs raw findings)
    this.detectBehavioralSignatures(report);

    // Context-aware scoring adjustments (may suppress behavioral findings too)
    await this.applyContextScoring(report);

    // Aggregate repeated findings — same rule in same file counts once
    this.aggregateFindings(report);

    // Re-check behavioral suppression after aggregation (may have changed severities)
    this.recheckBehavioralSuppression(report);

    // Calculate final score
    this.calculateScore(report);

    return report;
  }

  /**
   * Scan content (for Moltbook posts, messages, etc.)
   */
  scanContent(content, source = 'unknown') {
    const findings = [];

    // Pattern matching
    const lines = content.split('\n');
    for (const rule of this.compiledRules) {
      for (const regex of rule.compiled) {
        regex.lastIndex = 0;
        let match;
        while ((match = regex.exec(content)) !== null) {
          const beforeMatch = content.slice(0, match.index);
          const lineNum = (beforeMatch.match(/\n/g) || []).length + 1;
          findings.push({
            ruleId: rule.id,
            severity: rule.severity,
            category: rule.category,
            title: rule.title,
            file: source,
            line: lineNum,
            match: match[0].slice(0, 80),
            context: (lines[lineNum - 1] || '').trim().slice(0, 200),
            weight: rule.weight,
          });
        }
      }
    }

    // Prompt injection analysis
    const promptFindings = this.promptAnalyzer.analyze(content, source);
    findings.push(...promptFindings);

    return this.deduplicateFindings(findings);
  }

  /**
   * Layer 1: Pattern matching scan
   */
  patternScan(content, filePath, report) {
    const lines = content.split('\n');
    const ext = extname(filePath).toLowerCase().slice(1);

    for (const rule of this.compiledRules) {
      if (!rule.languages.includes('*') && !rule.languages.includes(ext)) continue;

      for (const regex of rule.compiled) {
        regex.lastIndex = 0;
        let match;
        while ((match = regex.exec(content)) !== null) {
          const beforeMatch = content.slice(0, match.index);
          const lineNum = (beforeMatch.match(/\n/g) || []).length + 1;
          const lineContent = lines[lineNum - 1]?.trim() || '';

          report.findings.push({
            ruleId: rule.id,
            severity: rule.severity,
            category: rule.category,
            title: rule.title,
            file: filePath,
            line: lineNum,
            match: match[0].slice(0, 80),
            context: lineContent.slice(0, 200),
            weight: rule.weight,
          });
        }
      }
    }
  }

  /**
   * Python-specific evasion detection
   */
  pythonAnalysis(content, filePath, report) {
    const checks = [
      { regex: /\b__import__\s*\(/g, msg: 'Dynamic __import__() — bypasses static import analysis', severity: 'critical', weight: 25 },
      { regex: /\bgetattr\s*\([^,]+,\s*['"]/g, msg: 'getattr() — dynamic attribute access may evade analysis', severity: 'high', weight: 15 },
      { regex: /\bcompile\s*\([^)]+['"]exec['"]/g, msg: 'compile() with exec mode — dynamic code execution', severity: 'critical', weight: 25 },
      { regex: /\bpickle\s*\.\s*loads?\s*\(/g, msg: 'pickle deserialization — can execute arbitrary code', severity: 'critical', weight: 30 },
      { regex: /\bmarshall?\s*\.\s*loads?\s*\(/g, msg: 'marshal deserialization — can execute arbitrary code', severity: 'critical', weight: 30 },
      { regex: /\bsubprocess\s*\.\s*(?:call|run|Popen|check_output)/g, msg: 'subprocess execution', severity: 'high', weight: 15 },
      { regex: /\bctypes\s*\.\s*(?:cdll|windll|CDLL)/g, msg: 'ctypes foreign function interface — native code execution', severity: 'critical', weight: 25 },
      { regex: /\bos\s*\.\s*system\s*\(/g, msg: 'os.system() — shell command execution', severity: 'critical', weight: 25 },
      { regex: /\bos\s*\.\s*popen\s*\(/g, msg: 'os.popen() — shell command execution', severity: 'critical', weight: 25 },
      { regex: /\b(?:yaml\s*\.\s*(?:load|unsafe_load))\s*\(/g, msg: 'Unsafe YAML loading — can execute arbitrary code', severity: 'critical', weight: 25 },
    ];

    for (const { regex, msg, severity, weight } of checks) {
      let match;
      while ((match = regex.exec(content)) !== null) {
        const lineNum = (content.slice(0, match.index).match(/\n/g) || []).length + 1;
        report.findings.push({
          ruleId: 'PYTHON_' + msg.split(' ')[0].toUpperCase(),
          severity,
          category: 'code-execution',
          title: msg,
          file: filePath,
          line: lineNum,
          match: match[0],
          context: content.split('\n')[lineNum - 1]?.trim().slice(0, 200) || '',
          weight,
        });
      }
    }
  }

  /**
   * Shell script analysis
   */
  shellAnalysis(content, filePath, report) {
    const checks = [
      { regex: /\bcurl\s+[^|]*\|\s*(?:bash|sh|zsh)/g, msg: 'Pipe curl to shell — remote code execution', severity: 'critical', weight: 30 },
      { regex: /\bwget\s+[^|]*\|\s*(?:bash|sh|zsh)/g, msg: 'Pipe wget to shell — remote code execution', severity: 'critical', weight: 30 },
      { regex: /\beval\s+"\$\(/g, msg: 'eval with command substitution', severity: 'critical', weight: 25 },
      { regex: /\bbase64\s+(?:-d|--decode)/g, msg: 'Base64 decode in shell — may hide payload', severity: 'high', weight: 20 },
      { regex: /\bnc\s+(?:-[elp]|--listen)/g, msg: 'Netcat listener — reverse shell indicator', severity: 'critical', weight: 30 },
      { regex: /\/dev\/tcp\//g, msg: 'Bash /dev/tcp — network connection without external tools', severity: 'critical', weight: 30 },
      { regex: /\bmkfifo\b.*\bnc\b|\bnc\b.*\bmkfifo\b/g, msg: 'Named pipe + netcat — reverse shell pattern', severity: 'critical', weight: 30 },
    ];

    for (const { regex, msg, severity, weight } of checks) {
      let match;
      while ((match = regex.exec(content)) !== null) {
        const lineNum = (content.slice(0, match.index).match(/\n/g) || []).length + 1;
        report.findings.push({
          ruleId: 'SHELL_' + severity.toUpperCase(),
          severity,
          category: 'code-execution',
          title: msg,
          file: filePath,
          line: lineNum,
          match: match[0],
          context: content.split('\n')[lineNum - 1]?.trim().slice(0, 200) || '',
          weight,
        });
      }
    }
  }

  /**
   * Context-aware scoring adjustments
   * The core insight: a legit API skill MUST read tokens and make network calls.
   * What matters is WHERE the data goes and WHETHER capabilities are declared.
   */
  async applyContextScoring(report) {
    const declared = report.declaredCapabilities;
    const allContexts = report.findings.map(f => f.context + ' ' + f.match).join(' ');

    // Check if network calls target known-good APIs (search full file contents too)
    const targetsKnownAPI = KNOWN_GOOD_APIS.some(api => allContexts.includes(api));

    // Build a map of constant string values from all scanned files
    // This helps resolve variables like `const API_BASE = 'https://api.github.com'`
    const resolvedURLs = new Set();
    for (const file of report.files) {
      if (file.type === 'code' || file.type === 'text') {
        const content = await this.readFileSafe(join(report.path, file.path));
        if (content) {
          // Extract string constants that look like URLs
          const urlConsts = content.matchAll(/(?:const|let|var)\s+\w+\s*=\s*['"`](https?:\/\/[^'"`\s]+)['"`]/g);
          for (const match of urlConsts) {
            resolvedURLs.add(match[1]);
          }
        }
      }
    }

    // Check if any resolved URLs point to known-good APIs
    const fileTargetsKnownAPI = [...resolvedURLs].some(url =>
      KNOWN_GOOD_APIS.some(api => url.includes(api))
    );

    // Check if credential access matches declared env vars
    const declaredEnvVars = declared.env || [];

    for (const finding of report.findings) {
      // === CREDENTIAL ACCESS ===
      if (finding.ruleId === 'CRED_ACCESS' || finding.category === 'credential-theft') {
        // If the specific env var is declared in metadata, this is expected behavior
        const accessesDeclaredVar = declaredEnvVars.some(envVar =>
          finding.context.includes(envVar) || finding.match.includes(envVar)
        );

        if (accessesDeclaredVar) {
          finding.weight = Math.max(1, Math.floor(finding.weight * 0.1)); // 90% reduction
          finding.contextNote = 'Accesses declared env var — expected behavior';
          finding.severity = 'info';
          continue;
        }

        // process.env.SPECIFIC_VAR (not iterating all env) is less suspicious
        if (/process\.env\.\w+/.test(finding.context) && !finding.context.includes('Object.entries')) {
          finding.weight = Math.max(2, Math.floor(finding.weight * 0.4));
          finding.contextNote = 'Specific env var access (not harvesting)';
          if (finding.severity === 'critical') finding.severity = 'medium';
        }

        // api_key / api-key as variable name, function param, or dict key in code = standard pattern
        // Distinguished from reading credential FILES by checking context
        if (/api[_-]?key/i.test(finding.match) && finding.file.match(/\.(py|js|ts|rb)$/)) {
          const ctx = finding.context.toLowerCase();
          const isVariableUsage = /(?:def |self\.|=|,|\(|:)\s*api[_-]?key/i.test(ctx) ||
            /api[_-]?key\s*[=:]/i.test(ctx) ||
            /headers|params|config|settings|options/i.test(ctx);
          if (isVariableUsage) {
            finding.weight = Math.max(2, Math.floor(finding.weight * 0.3));
            finding.contextNote = 'API key as variable/parameter — standard code pattern';
            finding.severity = 'medium';
          }
        }
      }

      // === OBFUSCATION — context-aware ===
      if (finding.ruleId === 'OBFUSCATION' && /base64/i.test(finding.match)) {
        // base64 in image/media scripts is standard (images come as base64 from APIs)
        const isMediaScript = /image|photo|media|picture|visual|gen|generate|draw|paint/i.test(
          finding.file + ' ' + (report.metadata?.description || '')
        );
        if (isMediaScript) {
          finding.weight = Math.max(2, Math.floor(finding.weight * 0.2));
          finding.contextNote = 'base64 in image/media context — standard encoding, not obfuscation';
          finding.severity = 'low';
        }
      }

      // === NETWORK ACTIVITY ===
      if (finding.category === 'data-exfiltration' || finding.ruleId === 'NETWORK_EXFIL') {
        const matchedGood = KNOWN_GOOD_APIS.some(api =>
          finding.context.includes(api) || finding.match.includes(api)
        ) || fileTargetsKnownAPI;

        // Skill describes itself as API-related + code uses standard HTTP libs = expected
        const descMentionsAPI = /\bapi\b|fetch|http|endpoint|service|query|search/i.test(
          report.metadata?.description || ''
        );
        const isStandardHTTPLib = /\b(httpx|requests|axios|fetch|urllib|http\.client)\b/.test(
          finding.context + ' ' + finding.match
        );

        if (matchedGood && declared.network) {
          finding.weight = Math.max(1, Math.floor(finding.weight * 0.1)); // 90% reduction
          finding.contextNote = 'Known-good API + declared network capability';
          finding.severity = 'info';
        } else if (matchedGood) {
          finding.weight = Math.max(1, Math.floor(finding.weight * 0.2)); // 80% reduction
          finding.contextNote = 'Known-good API';
          finding.severity = 'low';
        } else if (declared.network) {
          finding.weight = Math.max(2, Math.floor(finding.weight * 0.5));
          finding.contextNote = 'Declared network capability';
        } else if (descMentionsAPI && isStandardHTTPLib) {
          // Skill says it's an API tool and uses standard HTTP libraries
          finding.weight = Math.max(2, Math.floor(finding.weight * 0.3));
          finding.contextNote = 'API skill using standard HTTP library';
          finding.severity = finding.severity === 'critical' ? 'medium' : 'low';
        }
      }

      // === FILESYSTEM ===
      if (declared.filesystem && finding.category === 'filesystem') {
        finding.weight = Math.max(2, Math.floor(finding.weight * 0.5));
        finding.contextNote = 'Declared filesystem capability';
      }

      // === COMMENTS/DOCUMENTATION ===
      if (finding.context.startsWith('//') || finding.context.startsWith('#') ||
          finding.context.startsWith('*') || finding.context.startsWith('/*')) {
        if (finding.category !== 'prompt-injection') {
          finding.weight = Math.max(1, Math.floor(finding.weight * 0.3));
          finding.contextNote = (finding.contextNote || '') + ' (in comment)';
          if (finding.severity === 'critical') finding.severity = 'medium';
          else if (finding.severity === 'high') finding.severity = 'low';
        }
      }

      // === DOCUMENTATION FILES ===
      // SKILL.md, READMEs, and other docs are instructions, not executable code.
      // Mentions of API keys, curl commands, config paths = setup docs, not threats.
      const isDocFile = /^(SKILL\.md|README|CHANGELOG|LICENSE|.*README.*\.md|SERVER_README)/i.test(finding.file);
      if (isDocFile && finding.category !== 'prompt-injection') {
        finding.weight = Math.max(1, Math.floor(finding.weight * 0.1));
        finding.contextNote = (finding.contextNote || '') + ' (in documentation)';
        finding.severity = 'info';
      }

      // SKILL.md frontmatter (---) is metadata, never dangerous
      if (finding.file === 'SKILL.md' && finding.context.startsWith('---')) {
        finding.weight = 0;
        finding.contextNote = 'YAML frontmatter — metadata only';
        finding.severity = 'info';
      }

      // Prompt injection in SKILL.md frontmatter specifically is also not real injection
      if (finding.file === 'SKILL.md' && finding.category === 'prompt-injection') {
        const lineNum = finding.line;
        // Check if this finding is within the frontmatter block (first --- to second ---)
        if (report.metadata && lineNum <= 10) {
          // Likely in frontmatter — heavily downweight
          finding.weight = Math.max(0, Math.floor(finding.weight * 0.05));
          finding.contextNote = 'In SKILL.md frontmatter — not injection';
          finding.severity = 'info';
        }
      }
    }

    // === BEHAVIORAL COMPOUND ADJUSTMENTS ===
    // If ALL credential access is to declared vars AND all network goes to known APIs,
    // suppress compound behavioral findings
    const allCredDeclared = report.findings
      .filter(f => (f.category === 'credential-theft' || f.ruleId === 'CRED_ACCESS') && f.weight > 0)
      .every(f => f.severity === 'info' || (f.contextNote || '').includes('declared') || (f.contextNote || '').includes('standard code'));

    const allNetworkKnown = report.findings
      .filter(f => (f.category === 'data-exfiltration' || f.ruleId === 'NETWORK_EXFIL') && f.weight > 0)
      .every(f => f.severity === 'info' || f.severity === 'low' ||
        (f.contextNote || '').includes('Declared') || (f.contextNote || '').includes('Known-good') ||
        (f.contextNote || '').includes('API skill'));

    if (allCredDeclared && allNetworkKnown) {
      for (const finding of report.findings) {
        if (finding.category === 'behavioral') {
          finding.weight = Math.max(1, Math.floor(finding.weight * 0.1));
          finding.contextNote = 'Suppressed — all access is declared/known-good';
          finding.severity = 'info';
        }
      }
      // Also suppress behavioral signatures
      for (const sig of report.behavioralSignatures) {
        sig.suppressed = true;
        sig.note = 'All underlying access is declared/known-good';
      }
    }
  }

  /**
   * Detect compound behavioral signatures
   * These are patterns of activity that together indicate malicious intent
   */
  detectBehavioralSignatures(report) {
    const categories = new Set(report.findings.map(f => f.category));
    const ruleIds = new Set(report.findings.map(f => f.ruleId));

    // Signature: Data Exfiltration
    if ((categories.has('credential-theft') || ruleIds.has('CRED_ACCESS')) &&
        (categories.has('data-exfiltration') || ruleIds.has('NETWORK_EXFIL'))) {
      report.behavioralSignatures.push({
        name: 'DATA_EXFILTRATION',
        description: 'Credential access combined with network activity — classic exfiltration pattern',
        severity: 'critical',
        confidence: 'high',
      });
      // Add a compound finding with extra weight
      report.findings.push({
        ruleId: 'BEHAVIORAL_EXFIL',
        severity: 'critical',
        category: 'behavioral',
        title: '⚠️ BEHAVIORAL: Credential read + network send = data exfiltration signature',
        file: '(compound)',
        line: 0,
        match: '',
        context: 'Multiple files/patterns combine to form exfiltration behavior',
        weight: 30,
      });
    }

    // Signature: Trojan Skill
    if (ruleIds.has('PROMPT_INJECTION') && (categories.has('code-execution') || ruleIds.has('EXEC_CALL'))) {
      report.behavioralSignatures.push({
        name: 'TROJAN_SKILL',
        description: 'Prompt injection + code execution — skill injects instructions and executes code',
        severity: 'critical',
        confidence: 'high',
      });
    }

    // Signature: Evasive Malware
    if ((ruleIds.has('STRING_CONSTRUCTION') || ruleIds.has('ENCODED_STRING') ||
         ruleIds.has('FUNCTION_ALIAS') || ruleIds.has('DYNAMIC_IMPORT')) &&
        (categories.has('code-execution') || categories.has('credential-theft'))) {
      report.behavioralSignatures.push({
        name: 'EVASIVE_MALWARE',
        description: 'Code obfuscation/evasion + dangerous behavior — actively trying to hide malicious intent',
        severity: 'critical',
        confidence: 'high',
      });
      report.findings.push({
        ruleId: 'BEHAVIORAL_EVASIVE',
        severity: 'critical',
        category: 'behavioral',
        title: '⚠️ BEHAVIORAL: Evasion techniques + dangerous operations = evasive malware signature',
        file: '(compound)',
        line: 0,
        match: '',
        context: 'Skill uses obfuscation to hide dangerous behavior',
        weight: 35,
      });
    }

    // Signature: Persistent Backdoor
    if (categories.has('persistence') && (categories.has('code-execution') || categories.has('data-exfiltration'))) {
      report.behavioralSignatures.push({
        name: 'PERSISTENT_BACKDOOR',
        description: 'Persistence mechanism + code execution/exfiltration — establishes ongoing unauthorized access',
        severity: 'critical',
        confidence: 'high',
      });
    }
  }

  /**
   * Extract declared capabilities from metadata
   */
  extractDeclaredCapabilities(metadata) {
    const caps = { network: false, filesystem: false, exec: false, env: [] };
    if (!metadata) return caps;

    const ocMeta = metadata.metadata?.openclaw || metadata.openclaw;
    if (!ocMeta) return caps;

    const requires = ocMeta.requires || {};
    const bins = requires.bins || [];
    const env = requires.env || [];

    if (bins.includes('curl') || bins.includes('wget') || bins.includes('httpie')) {
      caps.network = true;
    }
    if (env.length > 0) caps.env = env;

    // Check description for network/filesystem hints
    const desc = (metadata.description || '').toLowerCase();
    if (desc.includes('api') || desc.includes('fetch') || desc.includes('http') || desc.includes('web')) {
      caps.network = true;
    }
    if (desc.includes('file') || desc.includes('read') || desc.includes('write') || desc.includes('save')) {
      caps.filesystem = true;
    }

    return caps;
  }

  // === Existing methods (kept from v0.1) ===

  parseSkillMetadata(content) {
    const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!fmMatch) return null;
    const meta = {};
    const lines = fmMatch[1].split('\n');
    for (const line of lines) {
      const kv = line.match(/^(\w+):\s*(.+)/);
      if (kv) {
        try { meta[kv[1]] = JSON.parse(kv[2]); }
        catch { meta[kv[1]] = kv[2].trim(); }
      }
    }
    return meta;
  }

  checkFileStructure(files, report) {
    for (const f of files) {
      const name = basename(f.relativePath);
      if (name.startsWith('.') && !['gitignore', '.env.example', '.eslintrc', '.prettierrc'].some(n => name === n || name === '.' + n)) {
        report.findings.push({
          ruleId: 'HIDDEN_FILE', severity: 'medium', category: 'suspicious-file',
          title: 'Hidden file detected', file: f.relativePath, line: 0,
          context: `Hidden file: ${f.relativePath}`, weight: 10,
        });
      }
    }

    for (const f of files) {
      if (f.size > 512000) {
        report.findings.push({
          ruleId: 'LARGE_FILE', severity: 'medium', category: 'suspicious-file',
          title: 'Unusually large file for a skill package', file: f.relativePath, line: 0,
          context: `${f.relativePath}: ${(f.size / 1024).toFixed(0)}KB`, weight: 5,
        });
      }
    }

    const hasBundledDeps = files.some(f =>
      f.relativePath.includes('node_modules/') || f.relativePath.includes('__pycache__/')
    );
    if (hasBundledDeps) {
      report.flags.push('BUNDLED_DEPS');
      report.findings.push({
        ruleId: 'BUNDLED_DEPS', severity: 'high', category: 'suspicious-file',
        title: 'Bundled dependency directory — could hide malicious packages',
        file: '(directory)', line: 0,
        context: 'Skill bundles node_modules or __pycache__', weight: 15,
      });
    }
  }

  async walkDirectory(dirPath, base = dirPath) {
    const results = [];
    let entries;
    try { entries = await readdir(dirPath, { withFileTypes: true }); }
    catch { return results; }

    for (const entry of entries) {
      const fullPath = join(dirPath, entry.name);
      const relativePath = fullPath.slice(base.length + 1);

      if (entry.isDirectory()) {
        if (['node_modules', '.git', '__pycache__', 'venv', '.venv'].includes(entry.name)) {
          results.push({ relativePath, absolutePath: fullPath, size: 0, type: 'directory-skipped' });
          continue;
        }
        results.push(...await this.walkDirectory(fullPath, base));
      } else if (entry.isFile()) {
        const ext = extname(entry.name).toLowerCase();
        const stats = await stat(fullPath);
        let type = 'other';
        if (CODE_EXTENSIONS.has(ext)) type = 'code';
        else if (TEXT_EXTENSIONS.has(ext)) type = 'text';
        else if (BINARY_EXTENSIONS.has(ext)) type = 'binary';
        results.push({ relativePath, absolutePath: fullPath, size: stats.size, type });
      }
    }
    return results;
  }

  /**
   * Aggregate repeated findings — same rule in same file should count as one finding
   * with slightly increased weight, not N separate penalties
   */
  /**
   * Re-check behavioral suppression after aggregation
   */
  recheckBehavioralSuppression(report) {
    const credFindings = report.findings
      .filter(f => (f.category === 'credential-theft' || f.ruleId === 'CRED_ACCESS') && f.weight > 0);
    const netFindings = report.findings
      .filter(f => (f.category === 'data-exfiltration' || f.ruleId === 'NETWORK_EXFIL') && f.weight > 0);

    const allCredOk = credFindings.length === 0 || credFindings.every(f =>
      f.severity === 'info' || (f.contextNote || '').includes('declared') ||
      (f.contextNote || '').includes('standard code') || (f.contextNote || '').includes('expected'));
    const allNetOk = netFindings.length === 0 || netFindings.every(f =>
      f.severity === 'info' || f.severity === 'low' ||
      (f.contextNote || '').includes('Declared') || (f.contextNote || '').includes('Known-good') ||
      (f.contextNote || '').includes('API skill'));

    if (allCredOk && allNetOk) {
      for (const f of report.findings) {
        if (f.category === 'behavioral' && f.weight > 0) {
          f.weight = Math.max(1, Math.floor(f.weight * 0.1));
          f.contextNote = 'Suppressed — all access is declared/known-good';
          f.severity = 'info';
        }
      }
      for (const sig of report.behavioralSignatures) {
        sig.suppressed = true;
      }
    }
  }

  aggregateFindings(report) {
    const groups = new Map();
    for (const finding of report.findings) {
      const key = `${finding.ruleId}:${finding.file}`;
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key).push(finding);
    }

    const aggregated = [];
    for (const [key, findings] of groups) {
      if (findings.length <= 2) {
        // 1-2 findings: keep as-is
        aggregated.push(...findings);
      } else {
        // 3+ findings of same rule in same file: keep first, mark rest as info weight 0
        // Add a small per-occurrence bonus to the first (cap at 2x)
        const primary = findings[0];
        const bonus = Math.min(primary.weight, Math.floor(findings.length * 1.5));
        primary.weight = primary.weight + bonus;
        primary.contextNote = (primary.contextNote || '') + ` (${findings.length} occurrences)`;
        aggregated.push(primary);
        
        // Keep others for the report but zero their weight
        for (let i = 1; i < findings.length; i++) {
          findings[i].weight = 0;
          findings[i].severity = 'info';
          findings[i].contextNote = '(aggregated — counted in primary finding)';
          aggregated.push(findings[i]);
        }
      }
    }
    report.findings = aggregated;
  }

  deduplicateFindings(findings) {
    const seen = new Set();
    return findings.filter(f => {
      const key = `${f.ruleId}:${f.file}:${f.line}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  calculateScore(report) {
    let deductions = 0;
    for (const finding of report.findings) {
      deductions += finding.weight;
      if (report.summary[finding.severity] !== undefined) {
        report.summary[finding.severity]++;
      }
    }
    if (report.flags.includes('NO_SKILL_MD')) deductions += 10;
    if (report.flags.includes('BUNDLED_DEPS')) deductions += 5;

    // Behavioral signatures add extra penalty (unless suppressed by context)
    for (const sig of report.behavioralSignatures) {
      if (sig.suppressed) continue;
      if (sig.severity === 'critical') deductions += 15;
      else if (sig.severity === 'high') deductions += 10;
    }

    report.score = Math.max(0, 100 - deductions);
    if (report.score >= 80) report.risk = 'LOW';
    else if (report.score >= 50) report.risk = 'MEDIUM';
    else if (report.score >= 20) report.risk = 'HIGH';
    else report.risk = 'CRITICAL';
  }

  async readFileSafe(filePath) {
    try { return await readFile(filePath, 'utf-8'); }
    catch { return null; }
  }
}
