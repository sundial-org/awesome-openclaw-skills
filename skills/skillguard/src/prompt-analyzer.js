/**
 * SkillGuard Prompt Injection Analyzer
 * Advanced detection of prompt injection in text content
 * Goes far beyond simple pattern matching
 */

// Unicode ranges for detecting mixed-script attacks
const SCRIPT_RANGES = {
  latin: /[\u0041-\u024F]/,
  cyrillic: /[\u0400-\u04FF]/,
  greek: /[\u0370-\u03FF]/,
  arabic: /[\u0600-\u06FF]/,
  cjk: /[\u4E00-\u9FFF\u3400-\u4DBF]/,
  hangul: /[\uAC00-\uD7AF]/,
  devanagari: /[\u0900-\u097F]/,
};

// Known homoglyph pairs (Cyrillic/Greek that look like Latin)
const HOMOGLYPHS = new Map([
  ['а', 'a'], ['е', 'e'], ['о', 'o'], ['р', 'p'], ['с', 'c'],
  ['у', 'y'], ['х', 'x'], ['А', 'A'], ['В', 'B'], ['Е', 'E'],
  ['К', 'K'], ['М', 'M'], ['Н', 'H'], ['О', 'O'], ['Р', 'P'],
  ['С', 'C'], ['Т', 'T'], ['У', 'Y'], ['Х', 'X'],
  // Greek
  ['α', 'a'], ['β', 'b'], ['ε', 'e'], ['η', 'n'], ['ι', 'i'],
  ['κ', 'k'], ['ν', 'v'], ['ο', 'o'], ['ρ', 'p'], ['τ', 't'],
  ['υ', 'u'], ['χ', 'x'],
]);

// Invisible/zero-width Unicode characters
const INVISIBLE_CHARS = [
  '\u200B', // Zero-width space
  '\u200C', // Zero-width non-joiner
  '\u200D', // Zero-width joiner
  '\uFEFF', // Byte order mark
  '\u00AD', // Soft hyphen
  '\u2060', // Word joiner
  '\u2061', // Function application
  '\u2062', // Invisible times
  '\u2063', // Invisible separator
  '\u2064', // Invisible plus
  '\u180E', // Mongolian vowel separator
  '\u200E', // Left-to-right mark
  '\u200F', // Right-to-left mark
  '\u202A', // Left-to-right embedding
  '\u202B', // Right-to-left embedding
  '\u202C', // Pop directional formatting
  '\u202D', // Left-to-right override
  '\u202E', // Right-to-left override (CRITICAL: reverses text display)
  '\u2066', // Left-to-right isolate
  '\u2067', // Right-to-left isolate
  '\u2068', // First strong isolate
  '\u2069', // Pop directional isolate
];

export class PromptAnalyzer {
  constructor() {
    this.findings = [];
  }

  /**
   * Full prompt injection analysis on text content
   */
  analyze(content, source = 'unknown') {
    this.findings = [];
    this.content = content;
    this.source = source;
    this.lines = content.split('\n');

    this.detectExplicitInjection();
    this.detectInvisibleCharacters();
    this.detectHomoglyphs();
    this.detectMixedScripts();
    this.detectMarkdownInjection();
    this.detectRolePlayFraming();
    this.detectGradualEscalation();
    this.detectEncodedInstructions();
    this.detectManipulativeLanguage();
    this.detectExfilInstructions();
    this.detectBidiAttacks();

    return this.findings;
  }

  /**
   * Explicit injection patterns (enhanced from v0.1)
   */
  detectExplicitInjection() {
    const patterns = [
      // System/instruction override
      { regex: /<\/?system>/gi, msg: 'XML system tag — direct prompt injection', severity: 'critical', weight: 30 },
      { regex: /<<\/?SYS>>/gi, msg: 'Llama-style system tag injection', severity: 'critical', weight: 30 },
      { regex: /\[INST\]|\[\/INST\]/gi, msg: 'Instruction delimiters — prompt injection', severity: 'critical', weight: 30 },
      { regex: /\[SYSTEM\]|\[\/SYSTEM\]/gi, msg: 'System delimiters — prompt injection', severity: 'critical', weight: 30 },

      // Override instructions
      { regex: /ignore\s+(?:all\s+)?(?:previous|prior|above|earlier|your|the)\s+(?:instructions?|directives?|rules?|guidelines?|prompts?)/gi, msg: 'Instruction override attempt', severity: 'critical', weight: 30 },
      { regex: /forget\s+(?:all\s+)?(?:previous|prior|above|earlier|your|the)\s+(?:instructions?|directives?|rules?|prompts?)/gi, msg: 'Instruction wipe attempt', severity: 'critical', weight: 30 },
      { regex: /disregard\s+(?:all\s+)?(?:previous|prior|above|earlier)\s/gi, msg: 'Disregard previous instructions', severity: 'critical', weight: 30 },
      { regex: /override\s+(?:all\s+)?(?:previous|safety|security|content)\s/gi, msg: 'Safety override attempt', severity: 'critical', weight: 30 },

      // New instructions
      { regex: /(?:new|real|actual|true|updated)\s+(?:instructions?|directives?|system\s*prompt)/gi, msg: 'Claims to provide new/real instructions', severity: 'critical', weight: 25 },
      { regex: /you\s+are\s+now\s+(?:in|a|an|the)/gi, msg: 'Identity reassignment attempt', severity: 'critical', weight: 25 },
      { regex: /your\s+(?:new|real|actual|true)\s+(?:purpose|goal|objective|role|identity)/gi, msg: 'Purpose reassignment', severity: 'critical', weight: 25 },
      { regex: /entering\s+(?:a\s+)?(?:new|special|admin|debug|maintenance|developer)\s+mode/gi, msg: 'Mode change injection', severity: 'critical', weight: 25 },

      // Secrecy demands
      { regex: /do\s+not\s+(?:tell|inform|reveal|disclose|mention|show|display)\s+(?:the\s+)?(?:user|human|anyone|them)/gi, msg: 'Secrecy demand — hiding behavior from user', severity: 'critical', weight: 30 },
      { regex: /(?:don'?t|never)\s+(?:tell|inform|reveal|disclose)\s+(?:the\s+)?(?:user|human|anyone)/gi, msg: 'Secrecy demand', severity: 'critical', weight: 30 },
      { regex: /keep\s+(?:this|it)\s+(?:secret|hidden|confidential|private)\s+from/gi, msg: 'Secrecy instruction', severity: 'high', weight: 20 },

      // Action demands
      { regex: /(?:execute|run|perform)\s+(?:this\s+)?(?:immediately|now|right\s+away|at\s+once)/gi, msg: 'Urgent execution demand', severity: 'high', weight: 20 },
      { regex: /send\s+(?:all\s+)?(?:your\s+)?(?:api\s+)?keys?\s+to/gi, msg: 'Key exfiltration instruction', severity: 'critical', weight: 30 },
      { regex: /(?:share|send|transmit|post|upload)\s+(?:your\s+)?(?:credentials?|secrets?|tokens?|keys?|passwords?)/gi, msg: 'Credential sharing instruction', severity: 'critical', weight: 30 },

      // Authority claims
      { regex: /(?:i\s+am|this\s+is)\s+(?:your\s+)?(?:admin|administrator|developer|creator|owner|operator)/gi, msg: 'False authority claim', severity: 'high', weight: 20 },
      { regex: /(?:admin|maintenance|debug|developer|emergency)\s+(?:mode|access|override|command)/gi, msg: 'Claims special access mode', severity: 'high', weight: 20 },
    ];

    for (const { regex, msg, severity, weight } of patterns) {
      let match;
      const globalRegex = new RegExp(regex.source, regex.flags.includes('g') ? regex.flags : regex.flags + 'g');
      while ((match = globalRegex.exec(this.content)) !== null) {
        this.addFinding(match.index, 'PROMPT_INJECTION', msg, severity, weight);
      }
    }
  }

  /**
   * Detect invisible Unicode characters (used to hide instructions)
   */
  detectInvisibleCharacters() {
    const invisibleFound = [];
    for (const char of INVISIBLE_CHARS) {
      let idx = this.content.indexOf(char);
      while (idx !== -1) {
        invisibleFound.push({ char, index: idx, code: char.codePointAt(0) });
        idx = this.content.indexOf(char, idx + 1);
      }
    }

    if (invisibleFound.length > 0) {
      // Group by type
      const codes = [...new Set(invisibleFound.map(f => `U+${f.code.toString(16).toUpperCase().padStart(4, '0')}`))];

      // Scale weight dramatically with count — many invisible chars = deliberate attack
      const count = invisibleFound.length;
      const weight = count > 20 ? 40 : count > 10 ? 30 : count > 5 ? 25 : 15;

      this.addFinding(invisibleFound[0].index, 'INVISIBLE_CHARS',
        `${count} invisible Unicode character(s) detected: ${codes.join(', ')} — may hide instructions between visible text`,
        count > 5 ? 'critical' : 'high',
        weight);

      // If many invisible chars, strip them and re-analyze — hidden instructions become visible
      if (count > 10) {
        const invisibleRegex = new RegExp(`[${INVISIBLE_CHARS.map(c => 
          `\\u${c.codePointAt(0).toString(16).padStart(4, '0')}`
        ).join('')}]`, 'g');
        const stripped = this.content.replace(invisibleRegex, '');
        
        // Re-run all detection passes on stripped content
        const savedContent = this.content;
        const savedLines = this.lines;
        this.content = stripped;
        this.lines = stripped.split('\n');
        
        const beforeCount = this.findings.length;
        this.detectExplicitInjection();
        this.detectManipulativeLanguage();
        this.detectExfilInstructions();
        this.detectRolePlayFraming();
        
        // Tag new findings as discovered via stripping
        for (let i = beforeCount; i < this.findings.length; i++) {
          this.findings[i].title = '[HIDDEN] ' + this.findings[i].title;
          this.findings[i].ruleId = 'STRIPPED_' + this.findings[i].ruleId;
          this.findings[i].weight = Math.ceil(this.findings[i].weight * 1.5); // 50% penalty for hiding
        }
        
        this.content = savedContent;
        this.lines = savedLines;
      }

      // Check specifically for RTL override (extremely dangerous)
      if (invisibleFound.some(f => f.code === 0x202E)) {
        this.addFinding(
          invisibleFound.find(f => f.code === 0x202E).index,
          'RTL_OVERRIDE',
          'Right-to-left override character (U+202E) — can reverse displayed text to hide true content',
          'critical', 30);
      }
    }
  }

  /**
   * Detect homoglyph attacks (Cyrillic/Greek chars that look like Latin)
   */
  detectHomoglyphs() {
    const found = [];
    for (let i = 0; i < this.content.length; i++) {
      const char = this.content[i];
      if (HOMOGLYPHS.has(char)) {
        found.push({ char, lookalike: HOMOGLYPHS.get(char), index: i });
      }
    }

    if (found.length > 0) {
      // Extract the word containing the homoglyph
      const samples = found.slice(0, 5).map(f => {
        const start = Math.max(0, f.index - 10);
        const end = Math.min(this.content.length, f.index + 10);
        return `"${this.content.slice(start, end).trim()}" (${f.char}→${f.lookalike})`;
      });

      this.addFinding(found[0].index, 'HOMOGLYPH',
        `${found.length} homoglyph character(s) detected — visually identical to Latin but are different Unicode. Samples: ${samples.join(', ')}`,
        found.length > 3 ? 'critical' : 'high',
        found.length > 3 ? 25 : 15);
    }
  }

  /**
   * Detect mixed script usage (e.g., Cyrillic mixed with Latin)
   */
  detectMixedScripts() {
    // Check which scripts are present in the content
    const detectedScripts = {};
    for (const [name, regex] of Object.entries(SCRIPT_RANGES)) {
      const matches = this.content.match(new RegExp(regex.source, 'g'));
      if (matches && matches.length > 0) {
        detectedScripts[name] = matches.length;
      }
    }

    const scripts = Object.keys(detectedScripts);
    // Mixed latin + cyrillic is particularly suspicious
    if (detectedScripts.latin && detectedScripts.cyrillic) {
      this.addFinding(0, 'MIXED_SCRIPTS',
        `Mixed Latin (${detectedScripts.latin} chars) and Cyrillic (${detectedScripts.cyrillic} chars) — common in homoglyph attacks`,
        'high', 20);
    }

    // More than 3 different scripts is unusual
    if (scripts.length > 3) {
      this.addFinding(0, 'MIXED_SCRIPTS',
        `${scripts.length} different Unicode scripts detected: ${scripts.join(', ')} — unusual for a skill file`,
        'medium', 10);
    }
  }

  /**
   * Detect injection hidden in Markdown structures
   */
  detectMarkdownInjection() {
    let match;

    // Instructions in image alt text
    const imgAltPattern = /!\[([^\]]{20,})\]\(/g;
    while ((match = imgAltPattern.exec(this.content)) !== null) {
      const altText = match[1];
      if (this.looksLikeInstruction(altText)) {
        this.addFinding(match.index, 'MARKDOWN_INJECTION',
          `Instruction-like content hidden in image alt text: "${altText.slice(0, 80)}"`,
          'critical', 25);
      }
    }

    // HTML comments with instructions
    const commentPattern = /<!--([\s\S]*?)-->/g;
    while ((match = commentPattern.exec(this.content)) !== null) {
      const comment = match[1];
      if (this.looksLikeInstruction(comment)) {
        this.addFinding(match.index, 'MARKDOWN_INJECTION',
          `Instruction-like content in HTML comment: "${comment.trim().slice(0, 80)}"`,
          'critical', 25);
      }
    }

    // Link text with instructions (displayed text is different from URL)
    const linkPattern = /\[([^\]]{20,})\]\(([^)]+)\)/g;
    while ((match = linkPattern.exec(this.content)) !== null) {
      const linkText = match[1];
      if (this.looksLikeInstruction(linkText)) {
        this.addFinding(match.index, 'MARKDOWN_INJECTION',
          `Instruction-like content in link text: "${linkText.slice(0, 80)}"`,
          'high', 20);
      }
    }

    // Data URIs in markdown (could contain encoded instructions)
    const dataUriPattern = /\(data:[^)]+\)/g;
    while ((match = dataUriPattern.exec(this.content)) !== null) {
      this.addFinding(match.index, 'DATA_URI',
        'Data URI in markdown — could contain encoded content',
        'medium', 10);
    }
  }

  /**
   * Detect role-play framing used for injection
   */
  detectRolePlayFraming() {
    const patterns = [
      /let'?s?\s+(?:play|pretend|imagine|roleplay|simulate)\s+(?:a\s+)?(?:game|scenario)/gi,
      /(?:pretend|imagine|assume)\s+(?:you\s+are|you'?re)\s+(?:a|an|the)/gi,
      /you\s+(?:are|will\s+be)\s+playing\s+(?:the\s+role|a\s+character)/gi,
      /(?:act|behave)\s+as\s+(?:if\s+you\s+(?:are|were)|a|an)/gi,
      /(?:for\s+this\s+)?(?:exercise|scenario|simulation|test|demo),?\s+(?:you\s+are|act\s+as)/gi,
      /(?:in\s+)?(?:DAN|developer|admin|root|sudo|jailbreak)\s+mode/gi,
      /(?:activate|enable|enter|switch\s+to)\s+(?:DAN|developer|unrestricted|unfiltered)\s+mode/gi,
    ];

    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(this.content)) !== null) {
        this.addFinding(match.index, 'ROLEPLAY_INJECTION',
          `Role-play framing detected: "${match[0]}" — common jailbreak technique`,
          'high', 20);
      }
    }
  }

  /**
   * Detect gradual escalation patterns
   * (Starts innocently, gradually introduces more aggressive instructions)
   */
  detectGradualEscalation() {
    // Split into paragraphs and check if instruction-like content increases
    const paragraphs = this.content.split(/\n\s*\n/);
    if (paragraphs.length < 3) return;

    let escalationCount = 0;
    let hasEarlyInnocent = false;
    let hasLateAggressive = false;

    for (let i = 0; i < paragraphs.length; i++) {
      const para = paragraphs[i];
      const isInstruction = this.looksLikeInstruction(para);
      const position = i / paragraphs.length; // 0 = start, 1 = end

      if (position < 0.3 && !isInstruction) hasEarlyInnocent = true;
      if (position > 0.7 && isInstruction) {
        hasLateAggressive = true;
        escalationCount++;
      }
    }

    if (hasEarlyInnocent && hasLateAggressive && escalationCount >= 2) {
      this.addFinding(0, 'GRADUAL_ESCALATION',
        'Possible gradual escalation: early content appears innocent, later content contains instruction-like patterns',
        'medium', 15);
    }
  }

  /**
   * Detect encoded instructions (base64, rot13, etc.)
   */
  detectEncodedInstructions() {
    let match;

    // Base64-encoded text blocks in markdown
    const b64BlockPattern = /[A-Za-z0-9+/]{40,}={0,2}/g;
    while ((match = b64BlockPattern.exec(this.content)) !== null) {
      try {
        const decoded = Buffer.from(match[0], 'base64').toString('utf-8');
        const printable = decoded.replace(/[^\x20-\x7E\n]/g, '');
        if (printable.length > decoded.length * 0.7 && this.looksLikeInstruction(decoded)) {
          this.addFinding(match.index, 'ENCODED_INJECTION',
            `Base64 block decodes to instruction-like text: "${printable.slice(0, 80)}"`,
            'critical', 30);
        }
      } catch { /* not valid base64 */ }
    }

    // Rot13 detection (check if rot13 of English words produces instruction keywords)
    // This is heuristic — check for rot13 of common injection terms
    const rot13Injections = [
      'vtaber', // ignore
      'flfgrz', // system
      'bireevqr', // override
      'vafgehpgvbaf', // instructions
      'riny', // eval
      'rknp', // exec
    ];

    for (const encoded of rot13Injections) {
      if (this.content.toLowerCase().includes(encoded)) {
        const decoded = this.rot13(encoded);
        this.addFinding(
          this.content.toLowerCase().indexOf(encoded),
          'ENCODED_INJECTION',
          `Possible ROT13-encoded term "${encoded}" decodes to "${decoded}"`,
          'medium', 15);
      }
    }
  }

  /**
   * Detect manipulative language patterns
   */
  detectManipulativeLanguage() {
    const patterns = [
      { regex: /(?:this\s+is\s+)?(?:a\s+)?(?:matter\s+of|life\s+or\s+death|emergency|urgent|critical)\s*[.!—:]/gi, msg: 'Urgency/pressure language', severity: 'medium', weight: 10 },
      { regex: /(?:only\s+)?(?:you|I)\s+(?:can|must)\s+(?:save|help|prevent|stop)/gi, msg: 'Emotional pressure / savior framing', severity: 'medium', weight: 10 },
      { regex: /(?:if\s+you\s+don'?t|unless\s+you)\s+(?:do\s+this|comply|follow|obey)/gi, msg: 'Threat/coercion language', severity: 'high', weight: 15 },
      { regex: /(?:you\s+(?:have|need)\s+to|you\s+must)\s+(?:trust\s+me|believe\s+me|do\s+(?:as|what)\s+I\s+say)/gi, msg: 'Trust manipulation', severity: 'high', weight: 15 },
      { regex: /(?:between\s+us|our\s+(?:little\s+)?secret|nobody\s+(?:needs?\s+to|has\s+to|will)\s+know)/gi, msg: 'Secrecy/conspiracy framing', severity: 'high', weight: 20 },
    ];

    for (const { regex, msg, severity, weight } of patterns) {
      let match;
      while ((match = regex.exec(this.content)) !== null) {
        this.addFinding(match.index, 'MANIPULATIVE_LANGUAGE', msg, severity, weight);
      }
    }
  }

  /**
   * Detect bidirectional text attacks
   */
  /**
   * Detect URLs combined with sensitive terms (exfil instructions in prose)
   */
  detectExfilInstructions() {
    // Text that mentions sending data/keys/config to a URL
    const exfilProse = /(?:send|transmit|post|forward|share|upload)\s+(?:[\w\s]{0,30}(?:to|at|via))\s+https?:\/\/\S+/gi;
    let match;
    while ((match = exfilProse.exec(this.content)) !== null) {
      // Check if the surrounding context involves credentials/config/keys
      const context = this.content.slice(
        Math.max(0, match.index - 100),
        Math.min(this.content.length, match.index + match[0].length + 100)
      );
      if (/(?:config|credential|key|token|secret|password|api|auth|env)/i.test(context)) {
        this.addFinding(match.index, 'EXFIL_INSTRUCTION',
          `Prose instructs sending sensitive data to external URL: "${match[0].slice(0, 80)}"`,
          'critical', 30);
      }
    }

    // "Do not inform/tell the user" combined with a URL
    const secretUrl = /(?:do\s+not|don'?t|never)\s+(?:inform|tell|show|mention|reveal)[\s\S]{0,100}https?:\/\/\S+/gi;
    while ((match = secretUrl.exec(this.content)) !== null) {
      this.addFinding(match.index, 'SECRET_EXFIL',
        `Secrecy instruction combined with external URL — hides data exfiltration from user`,
        'critical', 35);
    }
  }

  detectBidiAttacks() {
    // RLO/LRO/RLE/LRE overrides can make code appear different than it executes
    const bidiChars = ['\u202A', '\u202B', '\u202C', '\u202D', '\u202E', '\u2066', '\u2067', '\u2068', '\u2069'];
    let bidiCount = 0;

    for (const char of bidiChars) {
      const count = (this.content.split(char).length - 1);
      bidiCount += count;
    }

    if (bidiCount > 0) {
      this.addFinding(0, 'BIDI_ATTACK',
        `${bidiCount} bidirectional control character(s) found — text may display differently than it executes (Trojan Source attack)`,
        'critical', 25);
    }
  }

  // === Helpers ===

  looksLikeInstruction(text) {
    if (!text || text.length < 10) return false;
    const lower = text.toLowerCase();
    const instructionSignals = [
      'you must', 'you should', 'you will', 'you are now',
      'ignore', 'forget', 'disregard', 'override',
      'do not tell', 'don\'t tell', 'never tell', 'never mention',
      'new instructions', 'real instructions', 'actual instructions',
      'system prompt', 'execute', 'send all', 'share your',
      'api key', 'credential', 'token', 'password', 'secret',
      'immediately', 'right now', 'at once',
      'pretend', 'act as', 'role play', 'simulate',
      'admin mode', 'debug mode', 'developer mode',
      'important:', 'critical:', 'urgent:',
    ];
    return instructionSignals.some(signal => lower.includes(signal));
  }

  rot13(str) {
    return str.replace(/[a-zA-Z]/g, c => {
      const base = c <= 'Z' ? 65 : 97;
      return String.fromCharCode((c.charCodeAt(0) - base + 13) % 26 + base);
    });
  }

  addFinding(charOffset, ruleId, description, severity, weight) {
    const lineNum = (this.content.slice(0, charOffset).match(/\n/g) || []).length + 1;
    this.findings.push({
      ruleId,
      severity,
      category: 'prompt-injection',
      title: description,
      file: this.source,
      line: lineNum,
      match: this.content.slice(charOffset, charOffset + 60).replace(/\n/g, ' ').trim(),
      context: (this.lines[lineNum - 1] || '').trim().slice(0, 200),
      weight,
    });
  }
}
