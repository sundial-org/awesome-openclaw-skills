#!/usr/bin/env python3
"""
Daily Briefing Generator for Clawdbot AI Agents
Generates BRIEFING.md — a compact context file loaded at session start.
Combines personality reminders, active projects, recent decisions, and key facts.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Configuration - Auto-detect workspace
def get_workspace_dir() -> Path:
    """Auto-detect workspace directory from environment or standard locations."""
    # 1. Check CLAWDBOT_WORKSPACE env var
    if env_workspace := os.getenv("CLAWDBOT_WORKSPACE"):
        return Path(env_workspace)
    
    # 2. Check current working directory
    cwd = Path.cwd()
    if (cwd / "SOUL.md").exists() or (cwd / "AGENTS.md").exists():
        return cwd
    
    # 3. Fall back to ~/.clawdbot/workspace
    default_workspace = Path.home() / ".clawdbot" / "workspace"
    if not default_workspace.exists():
        default_workspace.mkdir(parents=True, exist_ok=True)
    
    return default_workspace

WORKSPACE_DIR = get_workspace_dir()
MEMORY_DIR = WORKSPACE_DIR / "memory"
EXTRACTED_FILE = MEMORY_DIR / "extracted.jsonl"
KNOWLEDGE_GRAPH = MEMORY_DIR / "knowledge-graph.json"
BRIEFING_FILE = WORKSPACE_DIR / "BRIEFING.md"
IDENTITY_FILE = WORKSPACE_DIR / "IDENTITY.md"
SOUL_FILE = WORKSPACE_DIR / "SOUL.md"
USER_FILE = WORKSPACE_DIR / "USER.md"

# Check for todos files (flexible naming)
TODOS_PATTERNS = [
    WORKSPACE_DIR / "todos.md",
    WORKSPACE_DIR / "TODO.md",
    WORKSPACE_DIR / "todos-*.md",
]

# API Configuration - support multiple providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def find_api_key() -> tuple[Optional[str], Optional[str]]:
    """Find available API key and return (provider, key)."""
    if OPENAI_API_KEY:
        return ("openai", OPENAI_API_KEY)
    if ANTHROPIC_API_KEY:
        return ("anthropic", ANTHROPIC_API_KEY)
    if GEMINI_API_KEY:
        return ("gemini", GEMINI_API_KEY)
    
    # Check config files
    config_paths = [
        Path.home() / ".config" / "openai" / "api_key",
        Path.home() / ".config" / "anthropic" / "api_key",
        Path.home() / ".config" / "gemini" / "api_key",
    ]
    
    for path in config_paths:
        if path.exists():
            key = path.read_text().strip()
            provider = path.parent.name
            return (provider, key)
    
    return (None, None)


def load_extracted_facts() -> List[Dict]:
    """Load all extracted facts."""
    if not EXTRACTED_FILE.exists():
        return []
    facts = []
    with open(EXTRACTED_FILE) as f:
        for line in f:
            try:
                facts.append(json.loads(line))
            except:
                pass
    return facts


def load_recent_daily_notes(days: int = 3) -> str:
    """Load recent daily memory notes."""
    parts = []
    today = datetime.now()
    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        path = MEMORY_DIR / f"{date}.md"
        if path.exists():
            content = path.read_text()
            parts.append(f"## {date}\n{content[:2000]}")
    return "\n\n".join(parts)


def load_file_safe(path: Path) -> str:
    """Load a file or return empty string."""
    try:
        return path.read_text().strip()
    except:
        return ""


def get_active_todos() -> str:
    """Get active todo items from any todos files found."""
    parts = []
    
    # Find all todos files
    todos_files = []
    for pattern in TODOS_PATTERNS:
        if "*" in str(pattern):
            # Glob pattern
            todos_files.extend(pattern.parent.glob(pattern.name))
        elif pattern.exists():
            todos_files.append(pattern)
    
    for path in todos_files:
        content = load_file_safe(path)
        if content:
            # Extract only active items (unchecked)
            active = [line for line in content.split("\n") 
                      if line.strip().startswith("- [ ]")]
            if active:
                parts.append(f"**{path.name}:**")
                parts.extend(active[:8])  # Max 8 items each
    
    return "\n".join(parts)


def categorize_facts(facts: List[Dict]) -> Dict[str, List[Dict]]:
    """Group facts by type, most recent first."""
    by_type = {}
    for fact in sorted(facts, key=lambda f: f.get("date", ""), reverse=True):
        t = fact.get("type", "fact")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(fact)
    return by_type


def generate_briefing_with_llm(context: str, provider: str, api_key: str) -> Optional[str]:
    """Use LLM to generate a concise briefing from raw context."""
    
    prompt = f"""You are generating a daily context briefing for an AI agent. This file gets loaded at the start of every session to maintain personality and context continuity.

Generate a BRIEFING.md that is:
- Under 2000 characters (STRICT limit — this must fit in context window)
- Structured with clear sections
- Focused on what the agent NEEDS to remember right now

Include these sections if relevant information exists in the context:
1. **Personality Quick-Check** — Key personality traits and communication style (extract from SOUL.md if available)
2. **Active Projects** — what's being worked on RIGHT NOW (max 4)
3. **Recent Decisions** — decisions made in last 2-3 days that affect behavior
4. **Key Context** — things that would be embarrassing to forget or re-ask about
5. **Don't Forget** — specific items worth highlighting

Be concise and punchy. This is a cheat sheet, not a novel. Only include sections where you have actual content.

Raw context to distill:
{context[:6000]}"""

    try:
        if provider == "openai":
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 1000
                },
                timeout=90
            )
        elif provider == "anthropic":
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-haiku-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
        elif provider == "gemini":
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 1000
                    }
                },
                timeout=30
            )
        else:
            return None
        
        response.raise_for_status()
        result = response.json()
        
        # Extract content based on provider
        if provider == "openai":
            content = result["choices"][0]["message"]["content"]
        elif provider == "anthropic":
            content = result["content"][0]["text"]
        elif provider == "gemini":
            content = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return None
        
        return content
    except Exception as e:
        print(f"LLM briefing generation failed ({provider}): {e}")
        return None


def generate_fallback_briefing(facts: List[Dict], recent_notes: str, todos: str, 
                                soul: str, identity: str, user: str) -> str:
    """Generate briefing without LLM — template-based."""
    categorized = categorize_facts(facts)
    
    lines = [
        "# BRIEFING.md",
        f"*Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — loaded at session start*",
        "",
    ]
    
    # Add personality section if SOUL.md exists
    if soul:
        lines.append("## Personality Quick-Check")
        # Extract key points from SOUL.md (first few lines or bullet points)
        soul_lines = [l.strip() for l in soul.split("\n")[:10] if l.strip() and not l.startswith("#")]
        for line in soul_lines[:5]:
            if line.startswith("-"):
                lines.append(line)
            else:
                lines.append(f"- {line}")
        lines.append("")
    
    # Add user context if USER.md exists
    if user:
        lines.append("## User Context")
        user_lines = [l.strip() for l in user.split("\n")[:5] if l.strip() and not l.startswith("#")]
        for line in user_lines[:3]:
            if line:
                lines.append(f"- {line}")
        lines.append("")
    
    lines.append("## Active Projects")
    
    # Pull recent subjects from facts
    subjects = {}
    for fact in facts[:30]:
        subj = fact.get("subject", "Unknown")
        if subj not in subjects:
            subjects[subj] = fact.get("content", "")[:80]
    
    for subj, desc in list(subjects.items())[:5]:
        lines.append(f"- **{subj}**: {desc}")
    
    lines.append("")
    lines.append("## Recent Decisions")
    for fact in categorized.get("decision", [])[:5]:
        lines.append(f"- {fact['content'][:100]}")
    
    if categorized.get("preference"):
        lines.append("")
        lines.append("## Key Preferences")
        for fact in categorized.get("preference", [])[:5]:
            lines.append(f"- {fact['content'][:100]}")
    
    if todos:
        lines.append("")
        lines.append("## Active Todos")
        lines.append(todos)
    
    lines.append("")
    lines.append("## Don't Forget")
    lines.append("- Check `memory_search` BEFORE answering questions about past work")
    lines.append("- Write important decisions and learnings to daily notes")
    
    return "\n".join(lines)


def main():
    print("Generating daily briefing...")
    print(f"Workspace: {WORKSPACE_DIR}")
    print("=" * 50)
    
    # Gather context
    facts = load_extracted_facts()
    print(f"Loaded {len(facts)} extracted facts")
    
    recent_notes = load_recent_daily_notes(3)
    print(f"Loaded recent daily notes ({len(recent_notes)} chars)")
    
    identity = load_file_safe(IDENTITY_FILE)
    soul = load_file_safe(SOUL_FILE)
    user = load_file_safe(USER_FILE)
    todos = get_active_todos()
    
    # Build raw context for LLM
    context_parts = []
    if soul:
        context_parts.append(f"## Soul/Personality\n{soul}")
    if identity:
        context_parts.append(f"## Identity\n{identity}")
    if user:
        context_parts.append(f"## User\n{user}")
    if todos:
        context_parts.append(f"## Active Todos\n{todos}")
    
    # Add recent facts
    categorized = categorize_facts(facts)
    for fact_type in ["decision", "preference", "commitment", "learning"]:
        items = categorized.get(fact_type, [])[:5]
        if items:
            context_parts.append(f"## Recent {fact_type.title()}s")
            for f in items:
                context_parts.append(f"- [{f.get('date','')}] {f['content']}")
    
    if recent_notes:
        context_parts.append(f"## Recent Notes\n{recent_notes[:3000]}")
    
    raw_context = "\n\n".join(context_parts)
    
    # Try LLM generation, fall back to template
    briefing = None
    provider, api_key = find_api_key()
    
    if provider:
        print(f"Using {provider} for briefing generation...")
        briefing = generate_briefing_with_llm(raw_context, provider, api_key)
    
    if not briefing:
        print("Using template-based briefing (no LLM or generation failed)")
        briefing = generate_fallback_briefing(facts, recent_notes, todos, soul, identity, user)
    else:
        print("✓ LLM-generated briefing")
    
    # Ensure it starts with the right header
    if not briefing.startswith("# BRIEFING"):
        briefing = f"# BRIEFING.md\n*Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n{briefing}"
    
    # Write
    BRIEFING_FILE.write_text(briefing)
    print(f"✓ Written to {BRIEFING_FILE}")
    print(f"  Size: {len(briefing)} chars")
    
    # Show preview
    preview = briefing[:500]
    print(f"\nPreview:\n{preview}...")


if __name__ == "__main__":
    main()
