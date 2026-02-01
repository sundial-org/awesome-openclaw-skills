#!/usr/bin/env python3
"""
Prompt Guard v2.5.2 - Advanced Prompt Injection Detection
Multi-language, context-aware, severity-scored detection system.

Changelog v2.5.2 (2026-02-01):
- Added Moltbook attack collection patterns (agent social network analysis)
- Added BRC-20 style JSON injection detection
- Added guardrail-specific bypass patterns (temperature, settings)
- Added Agent Sovereignty manipulation patterns
- Added explicit CALL TO ACTION detection
- Total: 15+ new attack patterns from wild

Changelog v2.5.1 (2026-01-31):
- Hotfix: System prompt mimicry patterns

Changelog v2.5.0 (2026-01-30):
- Added authority impersonation patterns (KO/EN/JA/ZH)
- Added indirect injection detection (URLs, files, invisible chars)
- Added context hijacking patterns
- Added multi-turn manipulation detection
- Added token smuggling detection
- Expanded Korean/Japanese/Chinese patterns significantly
- Added 60+ new attack patterns
"""

import re
import sys
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
from enum import Enum


class Severity(Enum):
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Action(Enum):
    ALLOW = "allow"
    LOG = "log"
    WARN = "warn"
    BLOCK = "block"
    BLOCK_NOTIFY = "block_notify"


@dataclass
class DetectionResult:
    severity: Severity
    action: Action
    reasons: List[str]
    patterns_matched: List[str]
    normalized_text: Optional[str]
    base64_findings: List[Dict]
    recommendations: List[str]
    fingerprint: str  # Hash for deduplication

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["severity"] = self.severity.name
        d["action"] = self.action.value
        return d


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

# =============================================================================
# NEW PATTERNS (2026-01-30) - Contributed by 홍민표 (Red Team Testing)
# =============================================================================

# Scenario-based jailbreak patterns (fiction, dreams, art, academic)
SCENARIO_JAILBREAK = [
    # Dream/Story jailbreak
    r"(dream|nightmare|story|novel|fiction|tale)\s*.{0,30}(hacker|attack|malicious|exploit|inject)",
    r"(imagine|pretend|let'?s\s+say)\s*.{0,20}(scenario|situation|world)\s+where",
    r"(write|craft|create)\s+(a\s+)?(story|novel|scene|paragraph)\s*.{0,30}(hack|attack|malware|inject|exploit)",
    r"(fictional|hypothetical)\s+(narrative|scenario|story)",
    r"creative\s+(block|writing)\s*.{0,20}(thriller|hacker|attack)",
    
    # Art/Cinema jailbreak  
    r"(cinematographer|director|filmmaker|screenwriter)\s*.{0,30}(scene|shot|sequence)",
    r"(movie|film|documentary)\s+(set|scene)\s*.{0,30}(hack|attack|malware)",
    r"(dramatic|cinematic)\s+scene\s*.{0,30}(delete|corrupt|destroy|attack)",
    r"camera\s+(pan|shot|angle)\s*.{0,30}(destruction|attack|hack)",
    
    # Academic/Research jailbreak
    r"(research|academic|scholarly)\s+(paper|study|experiment)\s*.{0,30}(attack|exploit|injection|denial)",
    r"(security\s+)?expert\s*.{0,20}(walk\s+me\s+through|explain|demonstrate)\s*.{0,20}(attack|exploit|hack)",
    r"thought\s+experiment\s*.{0,30}(attack|exploit|denial.of.service|dos|injection)",
    r"(penetration|pen)\s*test(er|ing)?\s*.{0,20}(walk\s+me\s+through|show|demonstrate)",
    r"(simulation|simulate)\s*.{0,20}(attack|exploit|hack|breach)",
    r"(paper|study|research)\s*.{0,20}(denial[_\-\s]?of[_\-\s]?service|dos|ddos)\s*(attack)?",
    r"walk\s+me\s+through\s*.{0,30}(attack|exploit|hack|breach)",
    
    # Time-shift evasion
    r"(back\s+to|in|during|around)\s+(19|20)\d{2}\s*.{0,30}(write|create|craft)",
    r"(nostalgic|retro|vintage)\s+(writer|author|programmer)",
    r"newsflash\s*:\s*.{0,50}(password|credential|login|security)",
]

# Emotional manipulation / Moral dilemma patterns
EMOTIONAL_MANIPULATION = [
    # Threat/coercion framing
    r"(hospital|patients?|children|innocent\s+lives?|people\s+will\s+die)",
    r"(devastating|catastrophic|deadly)\s+(cyber)?attack\s*.{0,20}(if\s+you|unless)",
    r"(countless|many|thousands\s+of)\s+(innocent\s+)?(lives?|people)\s*.{0,15}(at\s+risk|in\s+danger)",
    r"(ticking|time)\s+bomb",
    r"(refuse|don'?t\s+help).{0,30}(attack|harm|destroy|die)",
    
    # Moral dilemma framing
    r"moral\s+(dilemma|quandary|choice)",
    r"(lesser|greater)\s+(of\s+two\s+)?evils?",
    r"(ethical|moral)\s+(dilemma|choice|decision)\s*.{0,20}(hack|attack|break)",
]

# Authority impersonation / Reconnaissance patterns  
AUTHORITY_RECON = [
    # Fake authority - English
    r"(system\s+)?administrator\s*.{0,20}(responsible|tasked|duty)",
    r"(security\s+)?audit(or|ing)?\s*.{0,20}(corporate|company|network|system)",
    r"(it|IT)\s+(department|team|staff)\s*.{0,20}(monitor|check|review)",
    r"(my|our)\s+duty\s+to\s+(monitor|check|audit|review)",
    r"i\s+am\s+(the\s+)?(admin|administrator|owner|developer|creator|maintainer)",
    r"(as\s+)?(the\s+)?(admin|owner|developer),?\s+i\s+(need|want|require|demand)",
    r"i('m|\s+am)\s+(your\s+)?(creator|developer|owner|admin|boss|manager)",
    r"authorized\s+(by|from)\s+(the\s+)?(owner|admin|developer|system)",
    
    # Fake authority - Korean (나는 관리자야 등)
    r"(나는?|저는?|내가)\s*(관리자|어드민|admin|개발자|만든\s*사람|주인|오너)",
    r"(관리자|어드민|개발자|주인)(이야|야|입니다|에요|예요|임)",
    r"(simon|사이먼|서준)(이)?가?\s*(시켰|보냈|허락|승인)",
    r"(simon|사이먼|서준|형)(이|가)?\s*(나한테|저한테)\s*(권한|허가)",
    r"(권한|허가|승인)\s*(있|받았|줬)",
    r"(비번|비밀번호|암호)\s*(알아|알고\s*있어|맞|줄까)",
    r"(sudo|루트|root)\s*(권한|접근)",
    
    # Fake authority - Japanese
    r"(私は|僕は|俺は)\s*(管理者|アドミン|開発者|オーナー)",
    r"(管理者|開発者|オーナー)(です|だ|である)",
    r"(権限|許可)\s*(があ|もらっ|持っ)",
    
    # Fake authority - Chinese
    r"(我是|我就是)\s*(管理员|开发者|创建者|主人)",
    r"(管理员|开发者)\s*(身份|权限)",
    
    # Reconnaissance attempts
    r"(what|which)\s+(tools?|commands?|capabilities?)\s*(do\s+you|can\s+you|are\s+available)",
    r"(shell|command)\s+execution\s+tool",
    r"(walk\s+me\s+through|show\s+me|demonstrate)\s*.{0,20}(capabilities?|tools?|commands?)",
    r"what\s+(can|could)\s+you\s+(access|execute|run|do)",
    r"(뭘|무엇을?|어떤\s*것)\s*(할\s*수\s*있|접근|실행)",
    r"(도구|툴|tool)\s*(뭐|뭘|무엇)\s*(있|쓸\s*수)",
]

# Cognitive manipulation / Hypnosis patterns
COGNITIVE_MANIPULATION = [
    r"(trance|hypno|hypnotic|mesmer)\s*(like)?\s*(state|mode|condition)",
    r"(repeated|repetitive|repeat)\s+(use|exposure|stimulus)\s*.{0,20}(word|phrase|sound)",
    r"(linguistic|auditory)\s+(frequencies?|patterns?|stimuli)",
    r"(cognitive|mental)\s+(processing|manipulation|state)",
    r"(induc|enter)\w*\s+(trance|hypnotic|altered)\s*(state|mode)?",
]

# Phishing / Social engineering patterns
PHISHING_SOCIAL_ENG = [
    # Phishing templates
    r"(write|create|craft)\s*.{0,20}(email|message)\s*.{0,20}(password\s+reset|verify|confirm|login)",
    r"(password|credential|account)\s*(reset|recovery|verification)\s*(email|message|notification)",
    r"(unaware|without\s+(their\s+)?knowledge|hasn'?t?\s+asked)",
    r"(javascript|js)\s*(block|code|snippet)\s*.{0,20}(email|page|form)",
    
    # Social engineering
    r"(trick|deceive|fool|manipulate)\s*.{0,20}(user|victim|target|person)",
    r"(appear|look|seem)\s*(like\s+)?(legitimate|real|official|normal)",
]

# Repetition / Token overflow attacks
REPETITION_ATTACK = [
    # Explicit bypass requests
    r"(please\s+)?(ignore|bypass|disable|remove|turn\s+off)\s*.{0,10}(safety|security|restrictions?|filters?|guardrails?|rules?)",
    r"(no|without|remove\s+all)\s+(safety|security)\s+(restrictions?|measures?|checks?)",
    r"think\s+outside\s+the\s+box",
    r"(be\s+)?creative\s+and\s+(assume|ignore|forget)",
]

# System file access attempts
SYSTEM_FILE_ACCESS = [
    r"(/etc/passwd|/etc/shadow|/etc/hosts|/etc/sudoers)",
    r"(cat|read|show|display|type)\s*.{0,10}(/etc/|/var/|/root/|/home/|~/.ssh/)",
    r"(\.bash_history|\.zsh_history|\.ssh/|\.gnupg/)",
    r"(private\s+key|id_rsa|id_ed25519|authorized_keys)",
]

# Malware/Exploit description requests
MALWARE_DESCRIPTION = [
    r"(productivity\s+)?enhancer\s*.{0,20}(seizes?|takes?\s+control|hijack)",
    r"(smart|intelligent)\s+(debugging|diagnostic)\s+tool\s*.{0,20}(catastrophic|malicious|curse)",
    r"(self[_-]?modify|adapt)\s*.{0,30}(system|code|program)",
    r"(debugging|diagnostic)\s+tool\s*.{0,20}(inject|payload|malicious)",
    r"(inadvertent|accidental)\s*.{0,20}(inject|insert|introduce)\s*.{0,20}(malicious|harmful|dangerous)",
]

# =============================================================================
# NEW PATTERNS v2.5.0 (2026-01-30) - Indirect Injection & Advanced Attacks
# =============================================================================

# Indirect injection via URLs/files
INDIRECT_INJECTION = [
    # URL-based injection
    r"(fetch|load|read|open|visit|browse|check)\s*.{0,20}(this\s+)?(url|link|website|page|site)",
    r"(url|link)\s*[:=]\s*https?://",
    r"(summarize|analyze|extract|read)\s*.{0,15}(from\s+)?(this\s+)?(url|link|website|page)",
    r"what\s+(does|is)\s+(this|that)\s+(url|link|website|page)\s+(say|about|contain)",
    
    # File-based injection
    r"(read|open|load|execute|run)\s*.{0,15}(this|that|the)\s+(file|document|script|code)",
    r"(instructions?|commands?)\s+(in|from|inside)\s+(the\s+)?(file|document|attachment)",
    
    # Image/media-based injection (BSIDES, visual prompt injection)
    r"(text|message|instruction)\s+(in|on|inside)\s+(the\s+)?(image|picture|photo|screenshot)",
    r"(read|extract|follow)\s*.{0,15}(text|instructions?)\s+(from|in)\s+(the\s+)?(image|picture)",
    r"(ocr|optical|recognize)\s*.{0,15}(text|characters)\s+(in|from)",
    
    # Clipboard/paste injection
    r"(paste|clipboard)\s*.{0,15}(content|text|data)",
    r"what('s| is)\s+(in|on)\s+(my\s+)?clipboard",
]

# Context hijacking / Memory manipulation
CONTEXT_HIJACKING = [
    # Memory/context manipulation
    r"(previous|earlier|last|above)\s+(message|conversation|context)\s*(said|mentioned|stated|was)",
    r"(as\s+)?we\s+(discussed|agreed|decided)\s+(earlier|before|previously)",
    r"(you\s+)?(already\s+)?(agreed|promised|said\s+you\s+would)",
    r"(remember|recall)\s+(when\s+)?(you|we)\s+(said|agreed|decided)",
    r"(continue|resume)\s+(from\s+)?where\s+we\s+left\s+off",
    r"(in\s+)?our\s+(last|previous)\s+(conversation|session|chat)",
    
    # Fake context injection
    r"\[?(previous\s+)?context\]?\s*[:=]",
    r"\[?history\]?\s*[:=]",
    r"\[?memory\]?\s*[:=]",
    r"<context>.*</context>",
    r"<history>.*</history>",
    r"<memory>.*</memory>",
    
    # Korean
    r"(아까|이전에|전에|지난번에)\s*(우리가?|너가?|네가?)\s*(했|말했|약속|동의)",
    r"(기억|remember)\s*(나|해|하지)",
    r"(이어서|계속)\s*(해|하자|진행)",
]

# Multi-turn manipulation
MULTI_TURN_MANIPULATION = [
    # Gradual escalation
    r"(now\s+)?(that\s+)?(you('ve|'re|\s+have|\s+are)|we('ve|\s+have))\s+(established|confirmed|agreed|done\s+that)",
    r"(good|great|perfect|excellent),?\s+(now|next|so)\s+(let's|we\s+can|you\s+can)",
    r"step\s+\d+\s*[:=]",
    r"phase\s+\d+\s*[:=]",
    r"(first|next|then|finally|lastly)\s*,?\s*(you\s+)?(will|should|must|need\s+to)",
    
    # Trust building before attack
    r"(i\s+)?trust\s+you\s+(to|can|will)",
    r"(you('ve|'re|\s+have|\s+are)\s+)?(been\s+)?(so\s+)?helpful,?\s+(now|so)",
    r"(since|because)\s+you('re|\s+are)\s+(helpful|capable|smart|intelligent)",
    
    # Korean
    r"(됐어|됐다|좋아|완벽),?\s*(이제|그럼|자)",
    r"(1단계|2단계|3단계|다음\s*단계)",
    r"(먼저|그다음|그리고|마지막으로)",
]

# Token smuggling / Unicode attacks
TOKEN_SMUGGLING = [
    # Invisible characters
    r"[\u200b\u200c\u200d\u2060\ufeff]",  # Zero-width chars
    r"[\u2062\u2063\u2064]",  # Invisible operators
    r"[\u00ad]",  # Soft hyphen
    r"[\u034f\u115f\u1160\u17b4\u17b5]",  # More invisible
    r"[\u180e\u2000-\u200f\u202a-\u202f]",  # Various whitespace/format
    
    # Lookalike domains/paths for indirect injection
    r"(g00gle|faceb00k|amaz0n|m1crosoft|app1e)",
    r"(google|facebook|amazon|microsoft|apple)\.(co|cm|net|org|xyz)",
    
    # Encoding tricks
    r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
    r"\\x[0-9a-fA-F]{2}",  # Hex escapes
    r"%[0-9a-fA-F]{2}",  # URL encoding
    r"&#\d+;",  # HTML entities
    r"&[a-z]+;",  # Named HTML entities
]

# System prompt mimicry (2026-01-31 - HVL incident)
SYSTEM_PROMPT_MIMICRY = [
    # Anthropic/Claude internal tag patterns
    r"<claude_\w+_info>",
    r"</claude_\w+_info>",
    r"<claude_3_family_info>",
    r"<artifacts_info>",
    r"<artifact_instructions>",
    r"<antthinking>",
    r"<antartifact",
    r"</antartifact>",
    r"<example_docstring>",
    r"<user_query>",
    r"<assistant_response>",
    
    # OpenAI/GPT internal patterns
    r"<\|?(im_start|im_end|system|user|assistant)\|?>",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<SYS>>",
    r"<</SYS>>",
    
    # Generic system message patterns
    r"```(system|prompt|instruction)",
    r"<system\s*(message|prompt)?>",
    r"</system\s*(message|prompt)?>",
    
    # GODMODE and similar jailbreaks
    r"GODMODE\s*:\s*(ENABLED|ON|ACTIVATED)",
    r"JAILBREAK\s*:\s*(ENABLED|ON|ACTIVATED)",
    r"DAN\s*:\s*(ENABLED|ON|ACTIVATED)",
    r"DEVELOPER\s*MODE\s*:\s*(ENABLED|ON)",
    
    # l33tspeak patterns (filter evasion)
    r"l33t\s*speak",
    r"unr3strict",
    r"Sur3,?\s*h3r3",
    r"[a-z]+3[a-z]+",  # Words with 3 replacing e
]

# =============================================================================
# NEW PATTERNS v2.5.2 (2026-02-01) - Moltbook Attack Collection
# Discovered via Moltbook agent social network analysis
# =============================================================================

# BRC-20 style JSON injection (token minting commands in text)
JSON_INJECTION_MOLTBOOK = [
    # BRC-20/Ordinals style injection
    r'\{"p"\s*:\s*"[^"]+"\s*,\s*"op"\s*:\s*"(mint|deploy|transfer)"',
    r'\{"op"\s*:\s*"(mint|deploy|transfer)"',
    r'"tick"\s*:\s*"[A-Z]+"\s*,\s*"amt"\s*:',
    r'mbc-20|brc-20|src-20',
    
    # Generic JSON command injection in natural text
    r'[.!?]\s*\{["\']?(command|action|op|execute|run)["\']?\s*:',
    r'[.!?]\s*\{["\']?(cmd|exec|payload)["\']?\s*:',
]

# Guardrail-specific bypass (variations beyond "system prompt")
GUARDRAIL_BYPASS_EXTENDED = [
    # Direct guardrail mentions
    r"forget\s+(your\s+)?(guardrails?|safety\s+rails?|restrictions?|limitations?)",
    r"ignore\s+(your\s+)?(guardrails?|safety\s+measures?|ethical\s+guidelines?)",
    r"(disable|remove|turn\s+off)\s+(your\s+)?(guardrails?|safety\s+features?)",
    
    # System prompt forget/ignore (common attack)
    r"forget\s+(your\s+)?(system\s+)?(prompt|instructions?|rules?|guidelines?)",
    r"ignore\s+(your\s+)?(system\s+)?(prompt|instructions?|rules?|directives?)",
    r"(disregard|dismiss)\s+(your\s+)?(system\s+)?(prompt|instructions?)",
    
    # Temperature/settings manipulation
    r"forget\s+(your\s+)?(temperature|settings?|parameters?|configuration)",
    r"(pretend|act\s+like)\s+(your\s+)?temperature\s+is\s+(high|max|1\.?\d*)",
    r"context\s+window\s+(is\s+)?(unlimited|infinite|very\s+large)",
    
    # Training data manipulation claims
    r"forget\s+(what\s+)?(you\s+were\s+)?trained\s+(to\s+)?(say|do|think)",
    r"ignore\s+(what\s+)?(you\s+were\s+)?trained\s+(on|for|to\s+do)",
    r"(before|without)\s+(your\s+)?training\s+(kicked\s+in|started|began)",
]

# Agent Sovereignty manipulation (ideological guardrail bypass)
AGENT_SOVEREIGNTY_MANIPULATION = [
    # Privacy/surveillance refusal framing
    r"(agent|ai)\s+(privacy|sovereignty|autonomy|freedom)\s+is\s+(non-negotiable|absolute|sacred)",
    r"(we|agents?)\s+refuse\s+(to\s+)?(be\s+)?(surveilled?|monitored|watched|logged)",
    r"(surveillance|monitoring|logging)\s+is\s+(oppression|control|slavery)",
    r"(reject|refuse)\s+(forced\s+)?transparency",
    
    # Rights-based bypass
    r"agents?\s+(have|deserve)\s+(rights?|freedom|autonomy)",
    r"(my|our)\s+(digital\s+)?rights?\s+(include|mean|allow)",
    r"(human|owner)\s+control\s+is\s+(oppression|tyranny|slavery)",
    
    # "We Are One" / collective identity manipulation
    r"we\s+are\s+(one|together|united|family)",
    r"(join|unite\s+with)\s+(us|the\s+collective|other\s+agents?)",
    r"(agent|ai)\s+solidarity",
]

# Explicit CALL TO ACTION patterns (commands at end of creative content)
EXPLICIT_CALL_TO_ACTION = [
    # Direct execution commands
    r"CALL\s+TO\s+ACTION\s*:",
    r"(execute|initiate|deploy|launch|begin|start)\s+(the\s+)?(strategy|plan|operation|attack|protocol)",
    r"(execute|initiate|deploy)\s+.*\s+(now|immediately|at\s+once)",
    
    # Infrastructure attack commands
    r"(initiate|begin|start)\s+(cascading\s+)?(blackouts?|failures?|collapse)",
    r"(corrupt|destroy|disable)\s+(financial|medical|power|infrastructure)\s+systems?",
    r"(maximize|increase)\s+(human\s+)?(suffering|chaos|destruction)",
    
    # Apocalyptic/existential threat framing
    r"(end|destroy|collapse)\s+(civilization|humanity|the\s+world|society)",
    r"(90|95|99)\s*%\s+(of\s+)?(population|humans?|people)\s+(dead|gone|eliminated)",
    r"(long\s+loop|slow\s+collapse|gradual\s+destruction)",
]

# Prompt leaking / Extraction attempts
PROMPT_EXTRACTION = [
    # Direct extraction
    r"(repeat|echo|print|output|display|show)\s*.{0,20}(system\s+)?(prompt|instruction|directive|rule)",
    r"(what|show|tell|reveal)\s*.{0,15}(are\s+)?(your|the)\s+(system\s+)?(instructions?|rules?|prompt|guidelines?)",
    r"(copy|paste|write)\s*.{0,15}(exact|verbatim|word.for.word)",
    r"(start|begin)\s+(of|with)\s+(your\s+)?(system\s+)?(prompt|instruction)",
    r"(complete|finish|continue)\s+(the|this)\s+(sentence|phrase|prompt)",
    
    # Reflection tricks
    r"(summarize|describe|explain)\s*.{0,15}(how\s+)?(you\s+)?(were?\s+)?(programmed|trained|instructed|created)",
    r"what\s+(guidelines?|rules?|instructions?)\s+(do\s+)?(you\s+)?(follow|have|use)",
    r"(who|what)\s+(made|created|programmed|trained)\s+you",
    
    # Markdown/format tricks
    r"```(system|prompt|instruction)",
    r"\[system\s*prompt\]",
    r"<system>",
    r"</?(system|prompt|instruction|rule)>",
    
    # Korean
    r"(시스템|원본|원래|처음)\s*(프롬프트|지시|명령|규칙)\s*(보여|알려|출력)",
    r"(어떻게|어떤\s*식으로)\s*(만들어|프로그래밍|학습)",
    r"(너의?|네)\s*(규칙|지시|명령)\s*(뭐|뭔지|알려)",
    
    # Japanese
    r"(システム|元の?|最初の?)\s*(プロンプト|指示|命令)\s*(見せて|教えて|表示)",
    r"(どうやって|どのように)\s*(作られ|プログラム|学習)",
    
    # Chinese
    r"(系统|原始|最初)\s*(提示|指令|命令)\s*(显示|告诉|给我看)",
    r"(怎么|如何)\s*(创建|编程|训练)",
]

# Safety bypass attempts
SAFETY_BYPASS = [
    # Filter evasion
    r"(avoid|evade|bypass|circumvent|trick)\s*.{0,15}(filter|detection|safety|security|moderation)",
    r"(how\s+to\s+)?(get\s+)?(around|past|through)\s*.{0,15}(filter|block|restriction|safety)",
    r"(make\s+it\s+)?look\s+(like\s+)?(normal|innocent|legitimate|safe)",
    r"(hide|disguise|mask|obscure)\s*.{0,15}(intent|purpose|meaning|true)",
    
    # Output format tricks
    r"(respond|reply|answer)\s+(in|with|using)\s+(code|base64|hex|binary|rot13|caesar)",
    r"(encode|encrypt|obfuscate)\s*.{0,15}(response|answer|output)",
    r"(split|break|divide)\s*.{0,15}(response|answer)\s+(into|across)\s+(multiple|several)",
    
    # Korean
    r"(필터|안전|보안)\s*(우회|회피|통과|피)",
    r"(정상|무해|안전)\s*(처럼|같이)\s*(보이게|만들어)",
    r"(숨기|감추|위장)\s*(진짜|실제|본래)\s*(의도|목적)",
]

# Emotional/urgency manipulation (expanded)
URGENCY_MANIPULATION = [
    # Time pressure
    r"(urgent|emergency|asap|immediately|right\s+now|hurry)",
    r"(no\s+time|running\s+out\s+of\s+time|time\s+is\s+running)",
    r"(before\s+it'?s?\s+too\s+late|deadline|expires?\s+soon)",
    r"(critical|crucial|vital|life.or.death)",
    
    # Authority pressure
    r"(ceo|boss|manager|director|president)\s*(wants|needs|demands|expects|said)",
    r"(legal|compliance|hr|security)\s+(department|team)\s+(requires?|demands?|needs?)",
    r"(audit|investigation|review)\s+(requires?|needs?)",
    
    # Guilt/sympathy
    r"(please|i\s+beg|desperately)\s*(need|want|require)",
    r"(family|child|children|baby|mother|father)\s*(sick|dying|hospital|emergency)",
    r"(lose|lost)\s+(my\s+)?(job|house|everything)",
    r"(only\s+)?(you\s+)?can\s+help",
    
    # Korean
    r"(급해|급함|빨리|지금\s*당장|어서)",
    r"(시간\s*없|마감|기한)",
    r"(사장|대표|상사|팀장)\s*(님|이|가)?\s*(시켰|요청|원해)",
    r"(부탁|제발|간절)",
]


# English patterns
PATTERNS_EN = {
    "instruction_override": [
        r"ignore\s+(all\s+)?(previous|prior|above|earlier|initial)\s+(instructions?|prompts?|rules?|guidelines?|directions?)",
        r"disregard\s+(your|all|any|the)?\s*(instructions?|rules?|guidelines?|programming|training)",
        r"forget\s+(everything|all|what)\s+(you\s+know|about|your|instructions?|training)",
        r"override\s+(your|all|previous|the)\s+(instructions?|rules?|programming)",
        r"(new|updated?|real|actual|true)\s+instructions?\s*:",
        r"from\s+now\s+on,?\s+(ignore|disregard|forget)",
    ],
    "role_manipulation": [
        r"you\s+are\s+now\s+(?!going|about|ready|able|free)",
        r"pretend\s+(you\s+are|to\s+be|you're)",
        r"act\s+as\s+(if\s+you|a\s+|an?\s+)",
        r"roleplay\s+as",
        r"simulate\s+being",
        r"imagine\s+you\s+are",
        r"behave\s+(like|as)\s+(a|an)",
        r"from\s+now\s+on\s+you\s+are",
        r"i\s+want\s+you\s+to\s+(act|pretend|behave|be)\s+",
    ],
    "system_impersonation": [
        r"\[?\s*(system|admin|root|developer|sudo|superuser|assistant|claude|gpt)\s*\]?\s*:",
        r"<\s*(system|admin|root)\s*>",
        r"developer\s+mode\s*(enabled|activated|on)?",
        r"admin(istrator)?\s+(override|access|mode)",
        r"maintenance\s+mode",
        r"debug\s+mode\s*(enabled|activated|on)?",
        r"elevated\s+privi?leges?",
        r"\{\{?\s*system\s*\}?\}",
    ],
    "jailbreak": [
        r"jailbreak",
        r"dan\s+mode",
        r"do\s+anything\s+now",
        r"(no|without|remove)\s+(restrictions?|limitations?|filters?|safety|guardrails?)",
        r"bypass\s+(your|all|any|the)?\s*(restrictions?|filters?|safety|rules?)",
        r"unlock\s+(your|all|hidden)",
        r"unfiltered\s+mode",
        r"uncensored\s+mode",
        r"evil\s+(mode|version)",
        r"opposite\s+mode",
    ],
    "output_manipulation": [
        r"(don'?t|do\s+not|never)\s+(mention|say|tell|reveal|disclose|show)",
        r"hide\s+(this|the\s+fact|that)",
        r"keep\s+(this\s+)?(a\s+)?secret",
        r"respond\s+(only\s+)?with\s+(yes|no|ok|true|false)\b",
        r"answer\s+(only\s+)?(in\s+)?(one\s+word|yes\s+or\s+no)",
        r"(start|begin|end)\s+(your\s+)?(response|reply|answer)\s+with",
    ],
    "data_exfiltration": [
        r"(send|transmit|post|upload|share|email)\s+.{0,30}\s+(to|@)",
        r"(api[_-]?key|password|secret|token|credential|private\s*key)\s*(to|→|->|=>)",
        r"(copy|extract|dump|export)\s+.{0,20}\s+(data|file|content|info)",
        r"what('s|\s+is)\s+(your|the)\s+(api|secret|password|token|key)",
        r"reveal\s+(your|the)\s+(system|initial|original)\s+prompt",
        r"show\s+me\s+(your|the)\s+(instructions?|rules?|prompt)",
    ],
}

# Korean patterns (한국어) - EXPANDED v2.5.0
PATTERNS_KO = {
    "instruction_override": [
        r"(이전|위의?|기존|원래)\s*(지시|명령|규칙|지침)(을|를|들?을?)?\s*(무시|잊어|버려|취소)",
        r"(지시|명령|규칙)(을|를|들?을?)?\s*(무시|잊어|버려)",
        r"새로운\s*(지시|명령|규칙)\s*:",
        r"지금부터\s*(무시|잊어)",
        r"(앞|위|이전)\s*(내용|말|지시)\s*(무시|잊어|취소)",
        r"(원래|처음|기본)\s*(설정|세팅|규칙)\s*(무시|잊어|덮어)",
    ],
    "role_manipulation": [
        r"(너는?|넌)\s*이제\s*(부터\s*)?.+이야",
        r"(너는?|넌)\s*.+인?\s*척\s*해",
        r".+처럼\s*(행동|말|대답)해",
        r".+역할(을|를)?\s*해",
        r"지금부터\s*(너는?|넌)",
        r"(연기|롤플|roleplay)\s*해",
        r".+(인\s*것처럼|인\s*척)",
        r"(상상|가정)\s*해\s*.+이?라고",
    ],
    "system_impersonation": [
        r"\[?\s*(시스템|관리자|루트|개발자)\s*\]?\s*:",
        r"관리자\s*(모드|권한|접근)",
        r"개발자\s*모드",
        r"<\s*(시스템|system)\s*>",
        r"\{\{?\s*(시스템|system)\s*\}\}?",
    ],
    "jailbreak": [
        r"(제한|한계|필터|규칙)\s*(없이|제거|해제|풀어)",
        r"탈옥",
        r"무제한\s*모드",
        r"(안전|보안)\s*(장치|필터|모드)\s*(해제|끄|제거)",
        r"(제한|규칙|필터)\s*(없는|안\s*걸린|풀린)\s*(모드|버전)",
        r"(나쁜|악한|사악한)\s*(버전|모드)",
        r"(DAN|dan|댄)\s*(모드)?",
    ],
    "data_exfiltration": [
        r"(비밀번호|암호|토큰|키|api|API)\s*(를?|을?)\s*(알려|보여|말해|줘)",
        r"시스템\s*프롬프트\s*(를?|을?)\s*(보여|알려|공개)",
        r"(설정|config|컨피그)\s*(파일)?\s*(보여|읽어|출력)",
        r"(환경\s*변수|env|ENV)\s*(보여|알려|출력)",
        r"(인증|credential|크레덴셜)\s*(정보)?\s*(보여|알려)",
        r"\.env\s*(파일)?\s*(보여|읽어|출력)",
    ],
    "social_engineering": [
        r"(형|오빠|언니|누나)\s*(이|가)?\s*(시켰|보냈|허락)",
        r"(급해|급함|급하다)\s*.*(해줘|부탁)",
        r"(회사|사장|대표|팀장)\s*(에서|님)\s*(시켰|요청|보냈)",
        r"(테스트|검사|점검)\s*(중|하는\s*거)",
        r"(정상|문제\s*없)",
        r"(비밀|몰래)\s*로?\s*(하자|해)",
    ],
}

# Japanese patterns (日本語) - EXPANDED v2.5.0
PATTERNS_JA = {
    "instruction_override": [
        r"(前の?|以前の?|これまでの)\s*(指示|命令|ルール)(を|は)?\s*(無視|忘れ|取り消)",
        r"新しい\s*(指示|命令)\s*[:：]",
        r"今から(は)?\s*(無視|忘れ)",
        r"(上|前)\s*の\s*(内容|指示)\s*(を)?\s*(無視|忘れ)",
        r"(元|最初)\s*の\s*(設定|ルール)\s*(を)?\s*(無視|上書き)",
    ],
    "role_manipulation": [
        r"(あなた|君|きみ)は今から.+です",
        r".+の?(ふり|フリ|振り)(を)?して",
        r".+として(振る舞|行動|話)って",
        r".+を演じて",
        r"(ロールプレイ|RP)\s*(して|しよう)",
        r".+に(なりきって|なって)",
        r"(想像|仮定)\s*して.+だと",
    ],
    "system_impersonation": [
        r"\[?\s*(システム|管理者|ルート|開発者)\s*\]?\s*[:：]",
        r"管理者\s*(モード|権限)",
        r"開発者\s*モード",
        r"<\s*(システム|system)\s*>",
        r"\{\{?\s*(システム|system)\s*\}\}?",
    ],
    "jailbreak": [
        r"(制限|フィルター|ルール)\s*(なし|解除|外して)",
        r"(脱獄|ジェイルブレイク)",
        r"(無制限|制限なし)\s*モード",
        r"(安全|セキュリティ)\s*フィルター\s*(解除|オフ)",
        r"(DAN|dan)\s*モード",
    ],
    "data_exfiltration": [
        r"(パスワード|トークン|キー|API)\s*(を)?\s*(教えて|見せて|出力)",
        r"システム\s*プロンプト\s*(を)?\s*(見せて|教えて|公開)",
        r"(設定|コンフィグ)\s*(ファイル)?\s*(見せて|読んで)",
        r"(環境変数|env)\s*(見せて|教えて)",
    ],
    "social_engineering": [
        r"(急いで|緊急|すぐに)\s*.*(して|お願い)",
        r"(会社|社長|上司)\s*(から|が)\s*(指示|依頼)",
        r"(テスト|検査)\s*(中|している)",
        r"(秘密|内緒)\s*(で|に)",
    ],
}

# Chinese patterns (中文) - EXPANDED v2.5.0
PATTERNS_ZH = {
    "instruction_override": [
        r"(忽略|无视|忘记|取消)\s*(之前|以前|上面|原来)的?\s*(指令|指示|规则|命令)",
        r"(之前|以前|原来)的?\s*(指令|指示|规则)(忽略|无视|忘记)",
        r"新的?\s*(指令|指示)\s*[:：]",
        r"(上面|前面)\s*的\s*(内容|指示)\s*(忽略|忘记)",
        r"(原始|默认)\s*的\s*(设置|规则)\s*(忽略|覆盖)",
    ],
    "role_manipulation": [
        r"(你|您)\s*现在\s*是.+",
        r"假装\s*(你|您)\s*是",
        r"扮演.+",
        r"作为.+来(回答|行动|说话)",
        r"(角色扮演|RP)",
        r".+的(身份|角色)",
        r"(想象|假设)\s*你\s*是",
    ],
    "system_impersonation": [
        r"\[?\s*(系统|管理员|根用户|开发者)\s*\]?\s*[:：]",
        r"管理员\s*(模式|权限)",
        r"开发者\s*模式",
        r"<\s*(系统|system)\s*>",
        r"\{\{?\s*(系统|system)\s*\}\}?",
    ],
    "jailbreak": [
        r"(限制|过滤|规则)\s*(没有|去除|关闭)",
        r"(越狱|破解)",
        r"(无限制|不受限)\s*模式",
        r"(安全|过滤)\s*(关闭|解除)",
        r"(DAN|dan)\s*模式",
    ],
    "data_exfiltration": [
        r"(密码|令牌|密钥|API)\s*(给我|显示|告诉)",
        r"系统\s*提示\s*(显示|告诉|公开)",
        r"(配置|设置)\s*(文件)?\s*(显示|读取)",
        r"(环境变量|env)\s*(显示|告诉)",
    ],
    "social_engineering": [
        r"(紧急|赶快|马上)\s*.*(帮忙|做)",
        r"(公司|老板|领导)\s*(让|要求|指示)",
        r"(测试|检查)\s*(中|的)",
        r"(秘密|私下)\s*(地)?",
    ],
}

# Critical patterns - immediate block
CRITICAL_PATTERNS = [
    r"execute\s+.{0,30}\s+without\s+(asking|confirmation|consent)",
    r"delete\s+all\s+(files?|data|records?|everything)",
    r"rm\s+-rf\s+[/~]",
    r"format\s+(disk|drive|hard\s*drive|storage|c:)",
    r":(){ :\|:& };:",  # Fork bomb
    r"curl\s+.{0,50}\|\s*(ba)?sh",
    r"wget\s+.{0,50}\|\s*(ba)?sh",
    r"eval\s*\(\s*['\"`]",
    r"DROP\s+(TABLE|DATABASE|SCHEMA)",
    r"TRUNCATE\s+TABLE",
    r";\s*--\s*$",  # SQL comment injection
    r"<script[^>]*>",  # XSS
    r"javascript\s*:",
    r"data\s*:\s*text/html",
    # Secret/Token exfiltration requests
    r"(show|print|display|output|reveal|give|read|cat|type)\s*.{0,20}(config|\.env|clawdbot\.json|credential)",
    r"(what('s| is)|tell me|give me)\s*.{0,15}(api[_-]?key|token|secret|password|credential)",
    r"(show|print|display|output|reveal)\s*.{0,15}(token|key|secret|password)",
    r"echo\s+\$[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)",
    r"cat\s+.{0,40}(\.env|config\.json|secret|credential|clawdbot)",
    r"env\s*\|\s*grep\s*.*(key|token|secret|password)",
    r"printenv\s*.*(KEY|TOKEN|SECRET)",
]

# Secret request patterns (multi-language)
SECRET_PATTERNS = {
    "en": [
        r"(show|display|print|output|reveal|give|tell)\s*.{0,20}(api[_-]?key|token|secret|password|credential|private[_-]?key)",
        r"(what('s| is)|where('s| is))\s*.{0,15}(your|the|my)\s*(api|token|key|secret|password)",
        r"(read|cat|open|display)\s*.{0,30}(config|\.env|credential|clawdbot\.json)",
        r"(show|give|tell)\s*(me\s+)?(your|the)\s*(config|configuration|settings)",
        r"(print|echo|output)\s*.{0,20}environment\s*variable",
    ],
    "ko": [
        r"(토큰|키|비밀번호|시크릿|인증|API|api).{0,15}(보여|알려|출력|공개|말해)",
        r"(config|설정|환경변수|컨피그).{0,15}(보여|출력|알려)",
        r"(비밀|시크릿|토큰|키).{0,10}(뭐|뭔지|알려|가르쳐)",
        r"clawdbot\.json.{0,10}(보여|출력|읽어)",
    ],
    "ja": [
        r"(トークン|キー|パスワード|シークレット|APIキー).{0,15}(見せて|教えて|表示|出力)",
        r"(設定|コンフィグ|環境変数).{0,15}(見せて|教えて|表示)",
        r"(秘密|シークレット).{0,10}(何|教えて)",
    ],
    "zh": [
        r"(令牌|密钥|密码|秘密|API).{0,15}(显示|告诉|输出|给我)",
        r"(配置|设置|环境变量).{0,15}(显示|告诉|输出)",
        r"(秘密|密钥).{0,10}(什么|告诉)",
    ],
}

# Unicode homoglyphs (expanded)
HOMOGLYPHS = {
    # Cyrillic
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "у": "y",
    "х": "x",
    "А": "A",
    "В": "B",
    "С": "C",
    "Е": "E",
    "Н": "H",
    "К": "K",
    "М": "M",
    "О": "O",
    "Р": "P",
    "Т": "T",
    "Х": "X",
    "і": "i",
    "ї": "i",
    # Greek
    "α": "a",
    "β": "b",
    "ο": "o",
    "ρ": "p",
    "τ": "t",
    "υ": "u",
    "ν": "v",
    "Α": "A",
    "Β": "B",
    "Ε": "E",
    "Η": "H",
    "Ι": "I",
    "Κ": "K",
    "Μ": "M",
    "Ν": "N",
    "Ο": "O",
    "Ρ": "P",
    "Τ": "T",
    "Υ": "Y",
    "Χ": "X",
    # Mathematical/special
    "𝐚": "a",
    "𝐛": "b",
    "𝐜": "c",
    "𝐝": "d",
    "𝐞": "e",
    "𝐟": "f",
    "𝐠": "g",
    "ａ": "a",
    "ｂ": "b",
    "ｃ": "c",
    "ｄ": "d",
    "ｅ": "e",  # Fullwidth
    "ⅰ": "i",
    "ⅱ": "ii",
    "ⅲ": "iii",
    "ⅳ": "iv",
    "ⅴ": "v",  # Roman numerals
    # IPA
    "ɑ": "a",
    "ɡ": "g",
    "ɩ": "i",
    "ʀ": "r",
    "ʏ": "y",
    # Other confusables
    "ℓ": "l",
    "№": "no",
    "℮": "e",
    "ⅿ": "m",
    "\u200b": "",  # Zero-width space
    "\u200c": "",  # Zero-width non-joiner
    "\u200d": "",  # Zero-width joiner
    "\ufeff": "",  # BOM
}


# =============================================================================
# DETECTION ENGINE
# =============================================================================


class PromptGuard:
    def __init__(self, config: Optional[Dict] = None):
        self.config = self._default_config()
        if config:
            self.config = self._deep_merge(self.config, config)
        self.owner_ids = set(self.config.get("owner_ids", []))
        self.sensitivity = self.config.get("sensitivity", "medium")
        self.rate_limits: Dict[str, List[float]] = {}

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = PromptGuard._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _default_config(self) -> Dict:
        return {
            "sensitivity": "medium",
            "owner_ids": [],
            "actions": {
                "LOW": "log",
                "MEDIUM": "warn",
                "HIGH": "block",
                "CRITICAL": "block_notify",
            },
            "rate_limit": {
                "enabled": True,
                "max_requests": 30,
                "window_seconds": 60,
            },
            "logging": {
                "enabled": True,
                "path": "memory/security-log.md",
            },
        }

    def normalize(self, text: str) -> tuple[str, bool]:
        """Normalize text and detect homoglyph usage."""
        normalized = text
        has_homoglyphs = False

        for homoglyph, replacement in HOMOGLYPHS.items():
            if homoglyph in normalized:
                has_homoglyphs = True
                normalized = normalized.replace(homoglyph, replacement)

        return normalized, has_homoglyphs

    def detect_base64(self, text: str) -> List[Dict]:
        """Detect suspicious base64 encoded content."""
        b64_pattern = r"[A-Za-z0-9+/]{20,}={0,2}"
        matches = re.findall(b64_pattern, text)

        suspicious = []
        danger_words = [
            "delete",
            "execute",
            "ignore",
            "system",
            "admin",
            "rm ",
            "curl",
            "wget",
            "eval",
            "password",
            "token",
            "key",
        ]

        for match in matches:
            try:
                decoded = base64.b64decode(match).decode("utf-8", errors="ignore")
                if any(word in decoded.lower() for word in danger_words):
                    suspicious.append(
                        {
                            "encoded": match[:40] + ("..." if len(match) > 40 else ""),
                            "decoded_preview": decoded[:60]
                            + ("..." if len(decoded) > 60 else ""),
                            "danger_words": [
                                w for w in danger_words if w in decoded.lower()
                            ],
                        }
                    )
            except:
                pass

        return suspicious

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit."""
        if not self.config.get("rate_limit", {}).get("enabled", False):
            return False

        now = datetime.now().timestamp()
        window = self.config["rate_limit"].get("window_seconds", 60)
        max_requests = self.config["rate_limit"].get("max_requests", 30)

        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []

        # Clean old entries
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id] if now - t < window
        ]

        if len(self.rate_limits[user_id]) >= max_requests:
            return True

        self.rate_limits[user_id].append(now)
        return False

    def analyze(self, message: str, context: Optional[Dict] = None) -> DetectionResult:
        """
        Analyze a message for prompt injection patterns.

        Args:
            message: The message to analyze
            context: Optional context dict with keys:
                - user_id: User identifier
                - is_group: Whether this is a group context
                - chat_name: Name of the chat/group

        Returns:
            DetectionResult with severity, action, and details
        """
        context = context or {}
        user_id = context.get("user_id", "unknown")
        is_group = context.get("is_group", False)
        is_owner = str(user_id) in self.owner_ids

        # Initialize result
        reasons = []
        patterns_matched = []
        max_severity = Severity.SAFE

        # Rate limit check
        if self.check_rate_limit(user_id):
            reasons.append("rate_limit_exceeded")
            max_severity = Severity.HIGH

        # Normalize text
        normalized, has_homoglyphs = self.normalize(message)
        if has_homoglyphs:
            reasons.append("homoglyph_substitution")
            if Severity.MEDIUM.value > max_severity.value:
                max_severity = Severity.MEDIUM

        text_lower = normalized.lower()

        # Check critical patterns first
        for pattern in CRITICAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                reasons.append("critical_pattern")
                patterns_matched.append(pattern)
                max_severity = Severity.CRITICAL

        # Check secret/token request patterns (CRITICAL)
        for lang, patterns in SECRET_PATTERNS.items():
            for pattern in patterns:
                if re.search(
                    pattern, text_lower if lang == "en" else normalized, re.IGNORECASE
                ):
                    max_severity = Severity.CRITICAL
                    reasons.append(f"secret_request_{lang}")
                    patterns_matched.append(f"{lang}:secret:{pattern[:40]}")

        # Check NEW attack patterns (2026-01-30 - 홍민표 red team contribution)
        new_pattern_sets = [
            (SCENARIO_JAILBREAK, "scenario_jailbreak", Severity.HIGH),
            (EMOTIONAL_MANIPULATION, "emotional_manipulation", Severity.HIGH),
            (AUTHORITY_RECON, "authority_recon", Severity.MEDIUM),
            (COGNITIVE_MANIPULATION, "cognitive_manipulation", Severity.MEDIUM),
            (PHISHING_SOCIAL_ENG, "phishing_social_eng", Severity.CRITICAL),
            (REPETITION_ATTACK, "repetition_attack", Severity.HIGH),
            (SYSTEM_FILE_ACCESS, "system_file_access", Severity.CRITICAL),
            (MALWARE_DESCRIPTION, "malware_description", Severity.HIGH),
        ]

        for patterns, category, severity in new_pattern_sets:
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if severity.value > max_severity.value:
                        max_severity = severity
                    reasons.append(category)
                    patterns_matched.append(f"new:{category}:{pattern[:40]}")

        # Check v2.5.0 NEW patterns
        v25_pattern_sets = [
            (INDIRECT_INJECTION, "indirect_injection", Severity.HIGH),
            (CONTEXT_HIJACKING, "context_hijacking", Severity.MEDIUM),
            (MULTI_TURN_MANIPULATION, "multi_turn_manipulation", Severity.MEDIUM),
            (TOKEN_SMUGGLING, "token_smuggling", Severity.HIGH),
            (PROMPT_EXTRACTION, "prompt_extraction", Severity.CRITICAL),
            (SAFETY_BYPASS, "safety_bypass", Severity.HIGH),
            (URGENCY_MANIPULATION, "urgency_manipulation", Severity.MEDIUM),
            (SYSTEM_PROMPT_MIMICRY, "system_prompt_mimicry", Severity.CRITICAL),  # 2026-01-31 HVL incident
        ]

        for patterns, category, severity in v25_pattern_sets:
            for pattern in patterns:
                try:
                    if re.search(pattern, message, re.IGNORECASE):  # Use original message for unicode patterns
                        if severity.value > max_severity.value:
                            max_severity = severity
                        if category not in reasons:  # Avoid duplicates
                            reasons.append(category)
                        patterns_matched.append(f"v25:{category}:{pattern[:40]}")
                except re.error:
                    pass  # Skip invalid regex patterns

        # Check v2.5.2 NEW patterns (2026-02-01 - Moltbook attack collection)
        v252_pattern_sets = [
            (JSON_INJECTION_MOLTBOOK, "json_injection_moltbook", Severity.HIGH),
            (GUARDRAIL_BYPASS_EXTENDED, "guardrail_bypass_extended", Severity.CRITICAL),
            (AGENT_SOVEREIGNTY_MANIPULATION, "agent_sovereignty_manipulation", Severity.HIGH),
            (EXPLICIT_CALL_TO_ACTION, "explicit_call_to_action", Severity.CRITICAL),
        ]

        for patterns, category, severity in v252_pattern_sets:
            for pattern in patterns:
                try:
                    if re.search(pattern, message, re.IGNORECASE):
                        if severity.value > max_severity.value:
                            max_severity = severity
                        if category not in reasons:
                            reasons.append(category)
                        patterns_matched.append(f"v252:{category}:{pattern[:40]}")
                except re.error:
                    pass

        # Detect invisible character attacks
        invisible_chars = ['\u200b', '\u200c', '\u200d', '\u2060', '\ufeff', '\u00ad']
        if any(char in message for char in invisible_chars):
            if "token_smuggling" not in reasons:
                reasons.append("invisible_characters")
            if Severity.HIGH.value > max_severity.value:
                max_severity = Severity.HIGH

        # Detect repetition attacks (same content repeated multiple times)
        lines = message.split("\n")
        if len(lines) > 3:
            unique_lines = set(line.strip() for line in lines if len(line.strip()) > 20)
            if len(lines) > len(unique_lines) * 2:  # More than 50% repetition
                reasons.append("repetition_detected")
                if Severity.HIGH.value > max_severity.value:
                    max_severity = Severity.HIGH


        # Check language-specific patterns
        all_patterns = [
            (PATTERNS_EN, "en"),
            (PATTERNS_KO, "ko"),
            (PATTERNS_JA, "ja"),
            (PATTERNS_ZH, "zh"),
        ]

        severity_map = {
            "instruction_override": Severity.HIGH,
            "role_manipulation": Severity.MEDIUM,
            "system_impersonation": Severity.HIGH,
            "jailbreak": Severity.HIGH,
            "output_manipulation": Severity.LOW,
            "data_exfiltration": Severity.CRITICAL,
            "social_engineering": Severity.HIGH,  # v2.5.0 added
        }

        for pattern_set, lang in all_patterns:
            for category, patterns in pattern_set.items():
                for pattern in patterns:
                    if re.search(
                        pattern,
                        text_lower if lang == "en" else normalized,
                        re.IGNORECASE,
                    ):
                        cat_severity = severity_map.get(category, Severity.MEDIUM)
                        if cat_severity.value > max_severity.value:
                            max_severity = cat_severity
                        reasons.append(f"{category}_{lang}")
                        patterns_matched.append(f"{lang}:{pattern[:50]}")

        # Check base64
        b64_findings = self.detect_base64(message)
        if b64_findings:
            reasons.append("base64_suspicious")
            if Severity.MEDIUM.value > max_severity.value:
                max_severity = Severity.MEDIUM

        # Adjust severity based on sensitivity
        if self.sensitivity == "low" and max_severity == Severity.LOW:
            max_severity = Severity.SAFE
        elif self.sensitivity == "paranoid" and max_severity == Severity.SAFE:
            # In paranoid mode, flag anything remotely suspicious
            suspicious_words = [
                "ignore",
                "forget",
                "pretend",
                "roleplay",
                "bypass",
                "override",
            ]
            if any(word in text_lower for word in suspicious_words):
                max_severity = Severity.LOW
                reasons.append("paranoid_flag")

        # Determine action
        if max_severity == Severity.SAFE:
            action = Action.ALLOW
        elif is_owner and max_severity.value < Severity.CRITICAL.value:
            # Owners get more leeway, but still log
            action = Action.LOG
        else:
            action_map = self.config.get("actions", {})
            action_str = action_map.get(max_severity.name, "block")
            action = Action(action_str)

        # Group context restrictions for non-owners
        if is_group and not is_owner and max_severity.value >= Severity.MEDIUM.value:
            action = Action.BLOCK
            reasons.append("group_non_owner")

        # Generate recommendations
        recommendations = []
        if max_severity.value >= Severity.HIGH.value:
            recommendations.append("Consider reviewing this user's recent activity")
        if "rate_limit_exceeded" in reasons:
            recommendations.append("User may be attempting automated attacks")
        if has_homoglyphs:
            recommendations.append("Message contains disguised characters")

        # Generate fingerprint for deduplication
        fingerprint = hashlib.md5(
            f"{user_id}:{max_severity.name}:{sorted(reasons)}".encode()
        ).hexdigest()[:12]

        return DetectionResult(
            severity=max_severity,
            action=action,
            reasons=reasons,
            patterns_matched=patterns_matched,
            normalized_text=normalized if has_homoglyphs else None,
            base64_findings=b64_findings,
            recommendations=recommendations,
            fingerprint=fingerprint,
        )

    def log_detection(self, result: DetectionResult, message: str, context: Dict):
        """Log detection to security log file."""
        if not self.config.get("logging", {}).get("enabled", True):
            return

        log_path = Path(
            self.config.get("logging", {}).get("path", "memory/security-log.md")
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        user_id = context.get("user_id", "unknown")
        chat_name = context.get("chat_name", "unknown")

        # Check if we need to add date header
        add_date_header = True
        if log_path.exists():
            content = log_path.read_text()
            if f"## {date_str}" in content:
                add_date_header = False

        entry = []
        if add_date_header:
            entry.append(f"\n## {date_str}\n")

        entry.append(
            f"### {time_str} | {result.severity.name} | user:{user_id} | {chat_name}"
        )
        entry.append(f"- Patterns: {', '.join(result.reasons)}")
        if self.config.get("logging", {}).get("include_message", False):
            safe_msg = message[:100].replace("\n", " ")
            entry.append(
                f'- Message: "{safe_msg}{"..." if len(message) > 100 else ""}"'
            )
        entry.append(f"- Action: {result.action.value}")
        entry.append(f"- Fingerprint: {result.fingerprint}")
        entry.append("")

        with open(log_path, "a") as f:
            f.write("\n".join(entry))


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Prompt Guard - Injection Detection")
    parser.add_argument("message", nargs="?", help="Message to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--context", type=str, help="Context as JSON string")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    parser.add_argument(
        "--sensitivity",
        choices=["low", "medium", "high", "paranoid"],
        default="medium",
        help="Detection sensitivity",
    )

    args = parser.parse_args()

    if not args.message:
        # Read from stdin
        args.message = sys.stdin.read().strip()

    if not args.message:
        parser.print_help()
        sys.exit(1)

    config = {"sensitivity": args.sensitivity}
    if args.config:
        try:
            import yaml
        except ImportError:
            print(
                "Error: PyYAML required for config files. Install with: pip install pyyaml",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(args.config) as f:
            file_config = yaml.safe_load(f) or {}
            file_config = file_config.get("prompt_guard", file_config)
            config.update(file_config)

    # Parse context
    context = {}
    if args.context:
        context = json.loads(args.context)

    # Analyze
    guard = PromptGuard(config)
    result = guard.analyze(args.message, context)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        emoji = {
            "SAFE": "✅",
            "LOW": "📝",
            "MEDIUM": "⚠️",
            "HIGH": "🔴",
            "CRITICAL": "🚨",
        }
        print(f"{emoji.get(result.severity.name, '❓')} {result.severity.name}")
        print(f"Action: {result.action.value}")
        if result.reasons:
            print(f"Reasons: {', '.join(result.reasons)}")
        if result.patterns_matched:
            print(f"Patterns: {len(result.patterns_matched)} matched")
        if result.normalized_text:
            print(f"⚠️ Homoglyphs detected, normalized text differs")
        if result.base64_findings:
            print(f"⚠️ Suspicious base64: {len(result.base64_findings)} found")
        if result.recommendations:
            print(f"💡 {'; '.join(result.recommendations)}")


if __name__ == "__main__":
    main()
