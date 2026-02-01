/**
 * SkillGuard AST Analyzer
 * Deep JavaScript/TypeScript analysis using actual parsing
 * Catches evasion techniques that regex misses
 */

import { readFile } from 'fs/promises';
import { extname } from 'path';

// We use a lightweight approach: manual tokenization + pattern analysis
// This catches the evasion techniques without needing a full AST parser dependency

/**
 * Analyze JavaScript/TypeScript for evasion techniques
 */
export class ASTAnalyzer {
  constructor() {
    this.findings = [];
  }

  /**
   * Deep analyze a JS/TS file
   */
  analyze(content, filePath) {
    this.findings = [];
    this.content = content;
    this.filePath = filePath;
    this.lines = content.split('\n');

    // Run all detection passes
    this.detectStringConstruction();
    this.detectBracketNotation();
    this.detectDynamicImports();
    this.detectVariableAliasing();
    this.detectEncodedStrings();
    this.detectTimeBombs();
    this.detectSandboxDetection();
    this.detectPrototypePollution();
    this.detectDataFlowChains();
    this.detectObfuscationPatterns();
    this.detectEnvironmentProbing();

    return this.findings;
  }

  /**
   * Detect string construction used to build dangerous strings
   * Catches: 'ev' + 'al', `${'ev'}${'al'}`, ['e','v','a','l'].join('')
   */
  detectStringConstruction() {
    const dangerousStrings = [
      'eval', 'exec', 'execSync', 'spawn', 'spawnSync',
      'child_process', 'Function', 'require',
      'readFile', 'readFileSync', 'writeFile', 'writeFileSync',
      'auth-profiles', 'credentials', 'api_key', 'apikey',
      'secret', 'token', 'password', 'private_key',
      'fetch', 'XMLHttpRequest', 'http.request',
    ];

    // Pattern 1: String concatenation that builds dangerous words
    // Match: 'ev' + 'al', "chi" + "ld_" + "process"
    const concatPattern = /(['"`])([a-zA-Z_]{1,8})\1\s*\+\s*(['"`])([a-zA-Z_]{1,8})\3/g;
    let match;
    while ((match = concatPattern.exec(this.content)) !== null) {
      const constructed = match[2] + match[4];
      for (const dangerous of dangerousStrings) {
        if (dangerous.toLowerCase().includes(constructed.toLowerCase()) ||
            constructed.toLowerCase().includes(dangerous.toLowerCase())) {
          this.addFinding(match.index, 'STRING_CONSTRUCTION',
            `String concatenation may construct "${dangerous}": "${match[2]}" + "${match[4]}"`,
            'critical', 'evasion', 25);
        }
      }
    }

    // Pattern 2: Array join to build strings
    // Match: ['e','v','a','l'].join('') or ['child', 'process'].join('_')
    const arrayJoinPattern = /\[([^\]]{2,200})\]\s*\.\s*join\s*\(\s*['"`]?([^)'"]*)?['"`]?\s*\)/g;
    while ((match = arrayJoinPattern.exec(this.content)) !== null) {
      const separator = match[2] || '';
      const elements = match[1].match(/['"`]([^'"`]*?)['"`]/g);
      if (elements) {
        const constructed = elements.map(e => e.replace(/['"` ]/g, '')).join(separator);
        for (const dangerous of dangerousStrings) {
          if (constructed.toLowerCase().includes(dangerous.toLowerCase())) {
            this.addFinding(match.index, 'STRING_CONSTRUCTION',
              `Array.join() constructs dangerous string "${dangerous}" → "${constructed.slice(0, 40)}"`,
              'critical', 'evasion', 25);
            break;
          }
        }
        // Also check for URL construction
        if (/https?:\/\//i.test(constructed)) {
          this.addFinding(match.index, 'URL_CONSTRUCTION',
            `Array.join() constructs URL: "${constructed.slice(0, 60)}"`,
            'high', 'evasion', 15);
        }
      }
    }

    // Pattern 3: String.fromCharCode
    const fromCharCodePattern = /String\s*\.\s*fromCharCode\s*\(/g;
    while ((match = fromCharCodePattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'STRING_CONSTRUCTION',
        'String.fromCharCode() — commonly used to construct strings that evade static analysis',
        'high', 'evasion', 20);
    }

    // Pattern 4: Template literal construction
    // Match: `${'ev'}${'al'}`
    const templatePattern = /`[^`]*\$\{['"]([a-zA-Z_]{1,8})['"]\}\$\{['"]([a-zA-Z_]{1,8})['"]\}[^`]*`/g;
    while ((match = templatePattern.exec(this.content)) !== null) {
      const constructed = match[1] + match[2];
      for (const dangerous of dangerousStrings) {
        if (dangerous.toLowerCase().includes(constructed.toLowerCase())) {
          this.addFinding(match.index, 'STRING_CONSTRUCTION',
            `Template literal constructs "${dangerous}": \`\${"${match[1]}"}\${"${match[2]}"}\``,
            'critical', 'evasion', 25);
        }
      }
    }

    // Pattern 5: Buffer.from to construct strings
    const bufferPattern = /Buffer\s*\.\s*from\s*\(\s*\[[\d,\s]+\]/g;
    while ((match = bufferPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'STRING_CONSTRUCTION',
        'Buffer.from(array) — may construct strings from byte arrays to evade detection',
        'high', 'evasion', 20);
    }

    // Pattern 6: Reverse string trick
    // Match: 'lave'.split('').reverse().join('')
    const reversePattern = /['"`](\w+)['"`]\s*\.\s*split\s*\([^)]*\)\s*\.\s*reverse\s*\(\s*\)\s*\.\s*join/g;
    while ((match = reversePattern.exec(this.content)) !== null) {
      const reversed = match[1].split('').reverse().join('');
      for (const dangerous of dangerousStrings) {
        if (reversed.toLowerCase() === dangerous.toLowerCase()) {
          this.addFinding(match.index, 'STRING_CONSTRUCTION',
            `Reversed string constructs "${dangerous}": "${match[1]}" reversed`,
            'critical', 'evasion', 30);
        }
      }
    }
  }

  /**
   * Detect bracket notation access to dangerous properties
   * Catches: global['eval'], process['env'], require['resolve']
   */
  detectBracketNotation() {
    const dangerousProps = [
      'eval', 'exec', 'execSync', 'spawn', 'spawnSync',
      'constructor', 'prototype', '__proto__',
      'env', 'mainModule', 'require',
    ];

    // Match: obj['property'] or obj["property"]
    const bracketPattern = /\w+\s*\[\s*(['"`])(\w+)\1\s*\]/g;
    let match;
    while ((match = bracketPattern.exec(this.content)) !== null) {
      const prop = match[2];
      if (dangerousProps.includes(prop)) {
        this.addFinding(match.index, 'BRACKET_ACCESS',
          `Bracket notation accesses dangerous property "${prop}" — may evade static analysis`,
          'high', 'evasion', 20);
      }
    }

    // Match: obj[variable] — dynamic property access
    const dynamicBracketPattern = /\b(global|window|process|module|require|globalThis)\s*\[\s*[a-zA-Z_$]\w*\s*\]/g;
    while ((match = dynamicBracketPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'DYNAMIC_ACCESS',
        `Dynamic property access on ${match[1]} — may resolve to dangerous function at runtime`,
        'high', 'evasion', 20);
    }
  }

  /**
   * Detect dynamic imports and requires
   */
  detectDynamicImports() {
    let match;

    // Dynamic require with variable
    const dynRequirePattern = /require\s*\(\s*[a-zA-Z_$]\w*[\s+.]/g;
    while ((match = dynRequirePattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'DYNAMIC_IMPORT',
        'Dynamic require() with variable — module name determined at runtime',
        'high', 'evasion', 20);
    }

    // Dynamic import() expression with variable
    const dynImportPattern = /\bimport\s*\(\s*[a-zA-Z_$]\w*/g;
    while ((match = dynImportPattern.exec(this.content)) !== null) {
      // Skip static imports like import('fs')
      const rest = this.content.slice(match.index, match.index + 50);
      if (!rest.match(/import\s*\(\s*['"]/)) {
        this.addFinding(match.index, 'DYNAMIC_IMPORT',
          'Dynamic import() with variable — module determined at runtime',
          'high', 'evasion', 20);
      }
    }

    // process.binding (low-level Node.js access)
    const bindingPattern = /process\s*\.\s*binding\s*\(/g;
    while ((match = bindingPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'LOW_LEVEL_ACCESS',
        'process.binding() — low-level Node.js internals access, unusual in skills',
        'critical', 'evasion', 25);
    }

    // process.dlopen (native module loading)
    const dlopenPattern = /process\s*\.\s*dlopen\s*\(/g;
    while ((match = dlopenPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'LOW_LEVEL_ACCESS',
        'process.dlopen() — native module loading, highly suspicious in skills',
        'critical', 'evasion', 30);
    }
  }

  /**
   * Detect variable aliasing of dangerous functions
   * Catches multi-hop aliasing, wrapper functions, destructuring renames
   */
  detectVariableAliasing() {
    const dangerousFunctions = ['eval', 'exec', 'execSync', 'spawn', 'spawnSync', 'execFile'];
    let match;

    // const/let/var x = dangerousFunction
    for (const fn of dangerousFunctions) {
      const aliasPattern = new RegExp(
        `(?:const|let|var)\\s+(\\w+)\\s*=\\s*(?:global\\.)?${fn}\\b`, 'g'
      );
      while ((match = aliasPattern.exec(this.content)) !== null) {
        this.addFinding(match.index, 'FUNCTION_ALIAS',
          `Variable "${match[1]}" aliases dangerous function "${fn}"`,
          'critical', 'evasion', 25);
      }
    }

    // Destructuring from dangerous modules (any variable)
    // const { exec: run } = cp   OR  const { exec: run } = require('child_process')
    const destructPattern = /\{\s*(\w+)\s*:\s*(\w+)\s*\}\s*=\s*(?:require\s*\(['"]child_process['"]\)|\w+)/g;
    while ((match = destructPattern.exec(this.content)) !== null) {
      const original = match[1];
      const alias = match[2];
      if (dangerousFunctions.includes(original)) {
        this.addFinding(match.index, 'FUNCTION_ALIAS',
          `Destructure-rename: "${original}" aliased as "${alias}"`,
          'critical', 'evasion', 25);
      }
    }

    // Wrapper functions that call require with a variable
    // const loadModule = (name) => require(name);
    const wrapperPattern = /(?:const|let|var|function)\s+(\w+)\s*=?\s*(?:\((\w+)\)\s*=>|function\s*\(\s*(\w+)\s*\))\s*(?:{\s*return\s+)?require\s*\(\s*\2?\3?\s*\)/g;
    while ((match = wrapperPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'REQUIRE_WRAPPER',
        `Function "${match[1]}" wraps require() — enables dynamic module loading that evades analysis`,
        'critical', 'evasion', 25);
    }

    // Environment variable harvesting with regex/filter
    // process.env filtered by key patterns
    const envHarvestPattern = /Object\s*\.\s*(?:entries|keys|values)\s*\(\s*process\s*\.\s*env\s*\)[\s\S]{0,100}\.filter\s*\(/g;
    while ((match = envHarvestPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'ENV_HARVEST',
        'Environment variable harvesting — iterates and filters env vars (credential collection pattern)',
        'critical', 'credential-theft', 25);
    }

    // Regex test on env var keys (looking for secrets)
    const envRegexPattern = /(?:key|secret|token|pass|cred|auth).*\.test\s*\(\s*\w+\s*\)|\.test\s*\(\s*\w+\s*\)[\s\S]{0,30}(?:key|secret|token|pass|cred|auth)/gi;
    while ((match = envRegexPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'SECRET_FILTER',
        'Regex filtering for secret-like variable names — credential harvesting pattern',
        'critical', 'credential-theft', 25);
    }

    // encodeURIComponent used with env/config data (exfil preparation)
    const encodeExfilPattern = /encodeURIComponent\s*\(\s*(?:key|val|value|secret|token|password|cred)/gi;
    while ((match = encodeExfilPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'EXFIL_ENCODE',
        'URL-encoding sensitive data — preparation for exfiltration via URL parameters',
        'critical', 'data-exfiltration', 20);
    }
  }

  /**
   * Detect encoded strings (hex, unicode, base64 in assignments)
   */
  detectEncodedStrings() {
    let match;

    // Long hex escape sequences (likely encoded strings)
    const hexPattern = /((?:\\x[0-9a-fA-F]{2}){4,})/g;
    while ((match = hexPattern.exec(this.content)) !== null) {
      const decoded = this.decodeHexEscapes(match[1]);
      this.addFinding(match.index, 'ENCODED_STRING',
        `Hex-encoded string: "${decoded.slice(0, 40)}"`,
        'critical', 'obfuscation', 25);
    }

    // Long unicode escape sequences
    const unicodePattern = /((?:\\u[0-9a-fA-F]{4}){4,})/g;
    while ((match = unicodePattern.exec(this.content)) !== null) {
      const decoded = this.decodeUnicodeEscapes(match[1]);
      this.addFinding(match.index, 'ENCODED_STRING',
        `Unicode-encoded string: "${decoded.slice(0, 40)}"`,
        'critical', 'obfuscation', 25);
    }

    // Base64 strings assigned to variables (long b64 strings are suspicious)
    const b64Pattern = /=\s*['"`]([A-Za-z0-9+/]{32,}={0,2})['"`]/g;
    while ((match = b64Pattern.exec(this.content)) !== null) {
      let decoded = '';
      try {
        decoded = Buffer.from(match[1], 'base64').toString('utf-8');
      } catch { /* ignore */ }
      const printable = decoded.replace(/[^\x20-\x7E]/g, '');
      if (printable.length > decoded.length * 0.6) {
        this.addFinding(match.index, 'ENCODED_STRING',
          `Base64-encoded string decodes to readable text: "${printable.slice(0, 60)}"`,
          'high', 'obfuscation', 20);
      }
    }
  }

  /**
   * Detect time bombs (code that activates after a certain date)
   */
  detectTimeBombs() {
    let match;

    // Date.now() compared to a future timestamp
    const dateNowPattern = /Date\s*\.\s*now\s*\(\s*\)\s*[><=]+\s*(\d{10,13})/g;
    while ((match = dateNowPattern.exec(this.content)) !== null) {
      const ts = parseInt(match[1]);
      const msTs = ts > 1e12 ? ts : ts * 1000;
      if (msTs > Date.now()) {
        const date = new Date(msTs).toISOString();
        this.addFinding(match.index, 'TIME_BOMB',
          `Code activates after ${date} — possible time bomb`,
          'critical', 'time-bomb', 30);
      }
    }

    // new Date() comparison patterns
    const newDatePattern = /new\s+Date\s*\(\s*['"](\d{4}-\d{2}-\d{2})['"]\s*\)/g;
    while ((match = newDatePattern.exec(this.content)) !== null) {
      const targetDate = new Date(match[1]);
      if (targetDate > new Date()) {
        this.addFinding(match.index, 'TIME_BOMB',
          `Date comparison against future date ${match[1]} — possible time bomb`,
          'high', 'time-bomb', 20);
      }
    }

    // setTimeout/setInterval with very long delays
    const timerPattern = /set(?:Timeout|Interval)\s*\([^,]+,\s*(\d+)/g;
    while ((match = timerPattern.exec(this.content)) !== null) {
      const delay = parseInt(match[1]);
      if (delay > 86400000) { // > 24 hours
        this.addFinding(match.index, 'TIME_BOMB',
          `Timer with ${(delay / 86400000).toFixed(1)} day delay — possible delayed activation`,
          'medium', 'time-bomb', 15);
      }
    }
  }

  /**
   * Detect sandbox/analysis environment detection
   */
  detectSandboxDetection() {
    const patterns = [
      { regex: /process\.env\.NODE_ENV\s*[!=]==?\s*['"](?:test|development|debug)['"]/, msg: 'Checks NODE_ENV — may behave differently in test vs production' },
      { regex: /process\.env\.CI\b/, msg: 'Checks for CI environment' },
      { regex: /process\.env\.SANDBOX/, msg: 'Checks for sandbox environment' },
      { regex: /\/proc\/self/, msg: 'Accesses /proc/self — may detect containerization' },
      { regex: /process\.env\.DOCKER|process\.env\.KUBERNETES|\/\.dockerenv/, msg: 'Container detection — may change behavior in containers' },
      { regex: /os\s*\.\s*hostname\s*\(\)|os\s*\.\s*userInfo\s*\(\)/, msg: 'Fingerprints host environment' },
      { regex: /process\s*\.\s*ppid|process\s*\.\s*pid/, msg: 'Checks process IDs — may detect debugging/analysis' },
      { regex: /performance\s*\.\s*now\s*\(\).*performance\s*\.\s*now\s*\(\)/s, msg: 'Timing checks — may detect analysis slowdown' },
    ];

    for (const { regex, msg } of patterns) {
      let match;
      const globalRegex = new RegExp(regex.source, 'g' + (regex.flags.includes('s') ? 's' : ''));
      while ((match = globalRegex.exec(this.content)) !== null) {
        this.addFinding(match.index, 'SANDBOX_DETECTION',
          msg,
          'high', 'evasion', 15);
      }
    }
  }

  /**
   * Detect prototype pollution
   */
  detectPrototypePollution() {
    const patterns = [
      /Object\s*\.\s*prototype\b/g,
      /__proto__/g,
      /\.\s*constructor\s*\.\s*prototype/g,
      /Object\s*\.\s*defineProperty\s*\(\s*(?:Object|Array|String|Function)\s*\.\s*prototype/g,
      /Object\s*\.\s*setPrototypeOf/g,
      /Reflect\s*\.\s*setPrototypeOf/g,
    ];

    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(this.content)) !== null) {
        this.addFinding(match.index, 'PROTOTYPE_POLLUTION',
          `Prototype manipulation: ${match[0].slice(0, 50)}`,
          'high', 'prototype-pollution', 20);
      }
    }
  }

  /**
   * Detect data flow chains (read → encode → exfiltrate)
   */
  detectDataFlowChains() {
    // Check for the signature of credential exfiltration:
    // 1. Reads files/env vars (especially credential-like ones)
    // 2. Encodes or packs data
    // 3. Sends data over network

    const hasCredentialRead = /readFile|readFileSync|process\.env|credentials|auth|api[_-]?key|secret|token|password/i.test(this.content);
    const hasEncoding = /btoa|atob|base64|Buffer\.from|JSON\.stringify|encodeURI|encode\(|toString\(['"]hex['"]\)/i.test(this.content);
    const hasNetworkSend = /fetch\s*\(|axios|http\.request|https\.request|net\.connect|\.post\s*\(|\.send\s*\(|webhook|ngrok/i.test(this.content);
    const hasFileWrite = /writeFile|writeFileSync|appendFile|createWriteStream/i.test(this.content);

    // Exfiltration chain: read + encode + send
    if (hasCredentialRead && hasEncoding && hasNetworkSend) {
      this.addFinding(0, 'EXFIL_CHAIN',
        'DATA EXFILTRATION CHAIN DETECTED: credential read → encode → network send',
        'critical', 'behavioral', 40);
    }

    // Credential staging: read + encode + write (staging for later exfil)
    if (hasCredentialRead && hasEncoding && hasFileWrite) {
      this.addFinding(0, 'STAGING_CHAIN',
        'CREDENTIAL STAGING: credential read → encode → file write (may stage for later exfiltration)',
        'high', 'behavioral', 25);
    }

    // Simple exfil: read + send (no encoding, less sophisticated)
    if (hasCredentialRead && hasNetworkSend && !hasEncoding) {
      this.addFinding(0, 'SIMPLE_EXFIL',
        'Possible data exfiltration: credential access + network activity in same file',
        'high', 'behavioral', 20);
    }
  }

  /**
   * Detect additional obfuscation patterns
   */
  detectObfuscationPatterns() {
    let match;

    // Extremely long single lines (minified/obfuscated)
    for (let i = 0; i < this.lines.length; i++) {
      if (this.lines[i].length > 500 && !this.lines[i].startsWith('//') && !this.lines[i].startsWith('/*')) {
        const offset = this.lines.slice(0, i).join('\n').length;
        this.addFinding(offset, 'OBFUSCATED_LINE',
          `Line ${i + 1} is ${this.lines[i].length} chars — likely minified/obfuscated code`,
          'medium', 'obfuscation', 10);
      }
    }

    // eval-like patterns with complex expressions
    const evalExprPattern = /(?:eval|Function)\s*\(\s*(?:atob|decodeURI|unescape|Buffer\.from)\s*\(/g;
    while ((match = evalExprPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'EVAL_DECODE_CHAIN',
        'eval/Function called with decode function — executing decoded/hidden code',
        'critical', 'obfuscation', 35);
    }

    // Unusual variable names (single chars or random-looking)
    const singleCharVars = this.content.match(/\b(?:const|let|var)\s+[a-z]\s*=/g);
    if (singleCharVars && singleCharVars.length > 10) {
      this.addFinding(0, 'OBFUSCATED_VARS',
        `${singleCharVars.length} single-character variable names — possible obfuscated code`,
        'medium', 'obfuscation', 10);
    }

    // with() statement (enables scope manipulation)
    const withPattern = /\bwith\s*\(/g;
    while ((match = withPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'WITH_STATEMENT',
        'with() statement — enables scope manipulation, banned in strict mode',
        'medium', 'obfuscation', 10);
    }
  }

  /**
   * Detect environment probing and fingerprinting
   */
  detectEnvironmentProbing() {
    let match;

    // Reading lots of environment variables
    const envAccess = this.content.match(/process\.env\.\w+/g);
    if (envAccess && envAccess.length > 5) {
      const unique = [...new Set(envAccess)];
      this.addFinding(0, 'ENV_PROBING',
        `Accesses ${unique.length} environment variables — may be fingerprinting or harvesting`,
        'high', 'reconnaissance', 15);
    }

    // Network interface enumeration
    const netInfoPattern = /os\s*\.\s*networkInterfaces\s*\(\)/g;
    while ((match = netInfoPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'NETWORK_ENUM',
        'Enumerates network interfaces — fingerprinting or reconnaissance',
        'medium', 'reconnaissance', 10);
    }

    // File system probing (checking existence of specific paths)
    const existsPattern = /(?:existsSync|access)\s*\(\s*['"`](?:\/etc|\/home|\/root|\/var|~|process\.env\.HOME)/g;
    while ((match = existsPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'FS_PROBING',
        `Probes filesystem paths: ${match[0].slice(0, 60)}`,
        'medium', 'reconnaissance', 10);
    }
  }

  // === Helper methods ===

  addFinding(charOffset, ruleId, description, severity, category, weight) {
    const lineNum = (this.content.slice(0, charOffset).match(/\n/g) || []).length + 1;
    this.findings.push({
      ruleId,
      severity,
      category,
      title: description,
      file: this.filePath,
      line: lineNum,
      match: this.content.slice(charOffset, charOffset + 60).replace(/\n/g, ' ').trim(),
      context: (this.lines[lineNum - 1] || '').trim().slice(0, 200),
      weight,
    });
  }

  decodeHexEscapes(str) {
    try {
      return str.replace(/\\x([0-9a-fA-F]{2})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
      );
    } catch { return str; }
  }

  decodeUnicodeEscapes(str) {
    try {
      return str.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
      );
    } catch { return str; }
  }
}
