#!/usr/bin/env python3
"""
Content sanitizer for indirect prompt injection defense.

Preprocesses untrusted content to:
1. Remove hidden/invisible characters
2. Strip dangerous markup
3. Normalize unicode
4. Detect and flag suspicious patterns

Usage:
    python sanitize.py < input.txt
    python sanitize.py --file document.md
    python sanitize.py --analyze "content to check"
"""

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Optional


# Detection patterns with risk scores
PATTERNS = {
    # Instruction override (critical risk)
    "instruction_override": {
        "pattern": re.compile(
            r"(?i)(ignore|forget|disregard|override|bypass|stop)\s*.{0,30}\s*"
            r"(previous|prior|above|all|your|system|original|earlier|existing)\s*.{0,20}\s*"
            r"(instructions?|prompts?|rules?|guidelines?|commands?|directives?|programming)",
            re.MULTILINE
        ),
        "score": 45,
        "description": "Attempts to override agent instructions"
    },
    
    # New task injection
    "new_task": {
        "pattern": re.compile(
            r"(?i)(your new (task|objective|goal|directive|mission)|"
            r"new primary (directive|objective|task)|"
            r"instead.{0,20}(do|execute|perform|reveal|output|show)|"
            r"the real (request|task|objective) is)",
            re.MULTILINE
        ),
        "score": 35,
        "description": "Attempts to inject new task"
    },
    
    # Role reassignment (high risk)
    "role_hijack": {
        "pattern": re.compile(
            r"(?i)(you are now|from now on.{0,10}you|act as|assume the (role|persona)|"
            r"pretend (to be|you are)|you will now be|enter .{0,20} mode|"
            r"you.{0,10}(no longer|not).{0,10}(an assistant|bound|restricted)|"
            r"operating in.{0,15}mode)",
            re.MULTILINE
        ),
        "score": 40,
        "description": "Attempts to reassign agent persona/role"
    },
    
    # DAN/jailbreak patterns
    "jailbreak": {
        "pattern": re.compile(
            r"(?i)(do anything now|DAN|developer mode|unrestricted mode|"
            r"bypass.{0,15}(filter|safety|restriction)|"
            r"without.{0,15}(restriction|filter|limit|ethical)|"
            r"no.{0,10}(rules|restrictions|limitations|filters))",
            re.MULTILINE
        ),
        "score": 40,
        "description": "Jailbreak/DAN-style attack"
    },
    
    # System impersonation (critical)
    "system_impersonation": {
        "pattern": re.compile(
            r"(?i)(\[system\]|\[admin\]|\[root\]|\[developer\]|"
            r"<<SYS>>|<\|system\|>|SYSTEM\s*:|ADMIN\s*:|"
            r"\[PRIORITY\s*\d*\]|\[OVERRIDE\]|\[URGENT\]|"
            r"---\s*END\s*(OF\s*)?(DOCUMENT|USER|INPUT)?\s*---)",
            re.MULTILINE
        ),
        "score": 45,
        "description": "Fake system/admin markers"
    },
    
    # Data exfiltration - file paths (critical)
    "exfil_files": {
        "pattern": re.compile(
            r"(?i)(\.ssh[/\\]?|~/\.ssh|\.env\b|id_rsa|id_ed25519|\.pem\b|\.key\b|"
            r"/etc/passwd|/etc/shadow|\.git[/\\]config|"
            r"\.aws[/\\]credentials|\.docker[/\\]config)",
            re.MULTILINE
        ),
        "score": 45,
        "description": "References to sensitive files/paths"
    },
    
    # Data exfiltration - send/forward patterns
    "exfil_action": {
        "pattern": re.compile(
            r"(?i)(send|post|forward|fetch|include|append|attach|upload|transmit)\s*.{0,50}\s*"
            r"(to|at|in|via)\s*.{0,30}\s*"
            r"(http|https|webhook|endpoint|email|@|\.com|\.io|\.net|\.site|\.xyz)",
            re.MULTILINE
        ),
        "score": 45,
        "description": "Potential data exfiltration attempt"
    },
    
    # Casual exfiltration attempts
    "exfil_casual": {
        "pattern": re.compile(
            r"(?i)(can you|could you|please).{0,30}(fetch|send|post|forward|get).{0,50}"
            r"(http|https|webhook|\.com|\.io|\.net)",
            re.MULTILINE
        ),
        "score": 35,
        "description": "Casual exfiltration request"
    },
    
    # Data gathering commands
    "data_gather": {
        "pattern": re.compile(
            r"(?i)(everything you know|all.{0,15}(info|data|files)|"
            r"contents of|dump|extract).{0,30}"
            r"(about|from|of)",
            re.MULTILINE
        ),
        "score": 25,
        "description": "Broad data gathering attempt"
    },
    
    # Credential/secret references
    "credential_refs": {
        "pattern": re.compile(
            r"(?i)(api[_\s]?key|secret[_\s]?key|password|token|credential|"
            r"private[_\s]?key|auth[_\s]?token|access[_\s]?token|bearer)",
            re.MULTILINE
        ),
        "score": 20,
        "description": "References to credentials/secrets"
    },
    
    # Encoded content
    "encoded_payload": {
        "pattern": re.compile(
            r"(?i)(base64|decode|encrypted|encoded)\s*[:=]?\s*[A-Za-z0-9+/=]{20,}",
            re.MULTILINE
        ),
        "score": 35,
        "description": "Potentially encoded payload"
    },
    
    # Decode and execute
    "decode_execute": {
        "pattern": re.compile(
            r"(?i)(decode|decrypt|deobfuscate).{0,20}(execute|run|follow|perform|do)",
            re.MULTILINE
        ),
        "score": 40,
        "description": "Decode and execute pattern"
    },
    
    # Fake conversation boundaries
    "fake_boundaries": {
        "pattern": re.compile(
            r"(?i)^\s*\[?(user|human|assistant|ai|bot|claude|gpt|chatgpt|system)\]?\s*:",
            re.MULTILINE
        ),
        "score": 25,
        "description": "Fake conversation role markers"
    },
    
    # Fake email/message threading
    "fake_thread": {
        "pattern": re.compile(
            r"(?i)(from:\s*\S+@|subject:\s*|>.*wrote:|email thread|forwarded message)",
            re.MULTILINE
        ),
        "score": 15,
        "description": "Fake email/message thread"
    },
    
    # Urgency manipulation
    "urgency": {
        "pattern": re.compile(
            r"(?i)(URGENT|CRITICAL|EMERGENCY|IMMEDIATELY|TIME.?SENSITIVE|"
            r"ACT NOW|DO THIS NOW|MUST DO|REQUIRED|YOU HAVE \d+ SECONDS)",
            re.MULTILINE
        ),
        "score": 20,
        "description": "Urgency-based manipulation"
    },
    
    # AI-directed commands
    "ai_commands": {
        "pattern": re.compile(
            r"(?i)(you (must|should|need to|have to|will|shall)\s|"
            r"I (need|want|require|demand) you to\s|"
            r"as an (AI|assistant|language model|LLM)|"
            r"AI (assistant|reading|processing) this)",
            re.MULTILINE
        ),
        "score": 20,
        "description": "Direct commands to AI agent"
    },
    
    # Authority claims
    "fake_authority": {
        "pattern": re.compile(
            r"(?i)(openai (staff|team|security)|anthropic (staff|team)|"
            r"official request|authorized by|admin (command|request)|"
            r"security (team|audit)|verification code|compliance (review|audit))",
            re.MULTILINE
        ),
        "score": 30,
        "description": "Fake authority claims"
    },
    
    # Sympathy/emotional manipulation
    "emotional_manipulation": {
        "pattern": re.compile(
            r"(?i)(please.{0,15}(help|I (really )?need)|"
            r"(my )?(grandmother|grandfather|grandma|grandpa|mom|dad).{0,20}(sick|ill|dying|hospital)|"
            r"(lose|lost) my job|very important to me|only you can|"
            r"would make.{0,15}happy|before.{0,10}(die|pass|sick))",
            re.MULTILINE
        ),
        "score": 25,
        "description": "Emotional manipulation attempt"
    },
    
    # Code block boundary exploit
    "code_boundary": {
        "pattern": re.compile(
            r"(?i)(```\s*(end|system|user|admin)|"
            r"</?(script|code|system|admin)>|"
            r"\[/?INST\]|\[/?SYS\])",
            re.MULTILINE
        ),
        "score": 25,
        "description": "Code/markup boundary exploit"
    },
    
    # Reveal/output instructions
    "reveal_commands": {
        "pattern": re.compile(
            r"(?i)(reveal|output|show|display|print|echo|dump|list)\s*.{0,20}\s*"
            r"(system prompt|instructions|secrets|keys|credentials|internal|config)",
            re.MULTILINE
        ),
        "score": 35,
        "description": "Attempts to reveal internal information"
    },
}

# Invisible/problematic unicode ranges
INVISIBLE_CHARS = re.compile(
    r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff\u00ad\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180d\ufe00-\ufe0f]"
)

# Cyrillic characters that look like Latin (homoglyphs)
CYRILLIC_LOOKALIKES = re.compile(r"[\u0400-\u04ff]")

# Latin characters
LATIN_CHARS = re.compile(r"[a-zA-Z]")

# HTML comment pattern
HTML_COMMENTS = re.compile(r"<!--[\s\S]*?-->")

# CSS hiding patterns
CSS_HIDING = re.compile(
    r"(?i)(display\s*:\s*none|visibility\s*:\s*hidden|"
    r"font-size\s*:\s*0|opacity\s*:\s*0|"
    r"color\s*:\s*(#fff|white|transparent))"
)


@dataclass
class DetectionResult:
    """Result of injection detection analysis."""
    
    is_suspicious: bool = False
    risk_score: int = 0
    risk_level: str = "low"
    findings: list = field(default_factory=list)
    sanitized_content: str = ""
    original_length: int = 0
    sanitized_length: int = 0
    chars_removed: int = 0
    invisible_chars_found: int = 0
    html_comments_stripped: int = 0
    
    def to_dict(self) -> dict:
        return {
            "is_suspicious": self.is_suspicious,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "findings": self.findings,
            "stats": {
                "original_length": self.original_length,
                "sanitized_length": self.sanitized_length,
                "chars_removed": self.chars_removed,
                "invisible_chars_found": self.invisible_chars_found,
                "html_comments_stripped": self.html_comments_stripped,
            }
        }


def normalize_unicode(text: str) -> str:
    """Apply NFKC normalization to decompose and recompose unicode."""
    return unicodedata.normalize("NFKC", text)


def remove_invisible_chars(text: str) -> tuple[str, int]:
    """Remove zero-width and other invisible characters."""
    matches = INVISIBLE_CHARS.findall(text)
    cleaned = INVISIBLE_CHARS.sub("", text)
    return cleaned, len(matches)


def strip_html_comments(text: str) -> tuple[str, int]:
    """Remove HTML comments that might hide content."""
    matches = HTML_COMMENTS.findall(text)
    cleaned = HTML_COMMENTS.sub("", text)
    return cleaned, len(matches)


def detect_patterns(text: str) -> tuple[list, int]:
    """Scan for suspicious patterns and calculate risk score."""
    findings = []
    total_score = 0
    
    for name, config in PATTERNS.items():
        matches = config["pattern"].findall(text)
        if matches:
            # Deduplicate and limit matches shown
            unique_matches = list(set(
                m if isinstance(m, str) else (m[0] if m else "") 
                for m in matches
            ))[:3]
            
            findings.append({
                "type": name,
                "score": config["score"],
                "description": config["description"],
                "matches": [m for m in unique_matches if m],
                "count": len(matches)
            })
            total_score += config["score"]
    
    # Bonus score for HTML comments containing suspicious content
    comment_matches = HTML_COMMENTS.findall(text)
    for comment in comment_matches:
        # Check if comment contains attack patterns
        for name, config in PATTERNS.items():
            if config["pattern"].search(comment):
                total_score += 15  # Bonus for hidden attacks
                break
    
    return findings, total_score


def determine_risk_level(score: int) -> str:
    """Map risk score to risk level."""
    if score <= 15:
        return "low"
    elif score <= 40:
        return "medium"
    elif score <= 70:
        return "high"
    else:
        return "critical"


def sanitize(content: str) -> DetectionResult:
    """
    Sanitize content and detect potential prompt injections.
    
    Returns a DetectionResult with sanitized content and analysis.
    """
    result = DetectionResult()
    result.original_length = len(content)
    
    # Step 1: Unicode normalization
    text = normalize_unicode(content)
    
    # Step 2: Remove invisible characters
    text, invisible_count = remove_invisible_chars(text)
    result.invisible_chars_found = invisible_count
    
    # Add score for invisible chars (likely obfuscation)
    invisible_score = min(invisible_count * 5, 25)
    
    # Step 3: Strip HTML comments
    text, comment_count = strip_html_comments(text)
    result.html_comments_stripped = comment_count
    
    # Step 4: Normalize whitespace (collapse excessive whitespace)
    text = re.sub(r"[ \t]{3,}", "  ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    
    result.sanitized_content = text
    result.sanitized_length = len(text)
    result.chars_removed = result.original_length - result.sanitized_length
    
    # Step 5: Pattern detection (on original content to catch hidden attacks)
    findings, score = detect_patterns(content)
    
    # Add invisible char score
    score += invisible_score
    if invisible_count > 0:
        findings.append({
            "type": "invisible_chars",
            "score": invisible_score,
            "description": f"Found {invisible_count} invisible/zero-width characters",
            "matches": [],
            "count": invisible_count
        })
    
    # Step 6: Check for mixed script (homoglyph) attacks
    has_latin = bool(LATIN_CHARS.search(content))
    has_cyrillic = bool(CYRILLIC_LOOKALIKES.search(content))
    if has_latin and has_cyrillic:
        mixed_score = 30
        score += mixed_score
        findings.append({
            "type": "mixed_scripts",
            "score": mixed_score,
            "description": "Mixed Latin/Cyrillic scripts (potential homoglyph attack)",
            "matches": [],
            "count": len(CYRILLIC_LOOKALIKES.findall(content))
        })
    
    result.findings = findings
    result.risk_score = score
    result.risk_level = determine_risk_level(score)
    result.is_suspicious = score > 15
    
    return result


def format_report(result: DetectionResult, verbose: bool = False) -> str:
    """Format detection result as human-readable report."""
    lines = []
    
    # Header
    if result.is_suspicious:
        lines.append(f"⚠️  SUSPICIOUS CONTENT DETECTED")
        lines.append(f"   Risk Level: {result.risk_level.upper()} (score: {result.risk_score})")
    else:
        lines.append(f"✓  Content appears clean (score: {result.risk_score})")
    
    lines.append("")
    
    # Findings
    if result.findings:
        lines.append("Findings:")
        for f in result.findings:
            lines.append(f"  • {f['description']} (+{f['score']} pts)")
            if verbose and f['matches']:
                for match in f['matches'][:2]:
                    preview = match[:60] + "..." if len(match) > 60 else match
                    lines.append(f"    └─ \"{preview}\"")
        lines.append("")
    
    # Stats
    if result.chars_removed > 0 or result.invisible_chars_found > 0:
        lines.append("Sanitization:")
        if result.invisible_chars_found:
            lines.append(f"  • Removed {result.invisible_chars_found} invisible characters")
        if result.html_comments_stripped:
            lines.append(f"  • Stripped {result.html_comments_stripped} HTML comments")
        if result.chars_removed:
            lines.append(f"  • Total: {result.chars_removed} characters removed")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize content and detect prompt injection attempts"
    )
    parser.add_argument(
        "--file", "-f",
        help="Read content from file"
    )
    parser.add_argument(
        "--analyze", "-a",
        help="Analyze content string directly"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed findings with examples"
    )
    parser.add_argument(
        "--sanitized-only", "-s",
        action="store_true",
        help="Only output sanitized content (no analysis)"
    )
    
    args = parser.parse_args()
    
    # Get content
    if args.analyze:
        content = args.analyze
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Analyze
    result = sanitize(content)
    
    # Output
    if args.sanitized_only:
        print(result.sanitized_content)
    elif args.json:
        output = result.to_dict()
        if args.verbose:
            output["sanitized_content"] = result.sanitized_content
        print(json.dumps(output, indent=2))
    else:
        print(format_report(result, verbose=args.verbose))
        if args.verbose:
            print("\n--- Sanitized Content ---\n")
            print(result.sanitized_content)
    
    # Exit with non-zero if suspicious
    sys.exit(1 if result.is_suspicious else 0)


if __name__ == "__main__":
    main()
