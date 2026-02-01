#!/usr/bin/env python3
"""
Memory Extraction Script for Clawdbot AI Agents
Extracts structured facts from session transcripts or daily memory files.
"""

import json
import os
import re
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
TRANSCRIPTS_DIR = Path.home() / ".clawdbot" / "agents" / "main" / "sessions"

# API Configuration
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


def extract_with_openai(text: str, api_key: str) -> List[Dict]:
    """Extract facts using OpenAI API (gpt-4o-mini)."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""Extract structured facts from the following conversation/notes. For each significant fact, decision, preference, learning, or commitment, output a JSON object with these fields:
- type: one of "decision", "preference", "learning", "commitment", "fact"
- content: the actual fact/decision/etc (concise but complete)
- subject: what/who this is about (infer from context - projects, people, technologies, etc.)
- confidence: 0.0-1.0 (how certain is this fact)

Return ONLY a JSON array of fact objects. No other text.

Text to analyze:
{text[:8000]}"""  # Limit to avoid token limits

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Try to parse JSON from response
        # Sometimes the model wraps in markdown code blocks
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\n', '', content)
            content = re.sub(r'\n```$', '', content)
        
        facts = json.loads(content)
        return facts if isinstance(facts, list) else []
    except Exception as e:
        print(f"OpenAI extraction error: {e}")
        return []


def extract_with_anthropic(text: str, api_key: str) -> List[Dict]:
    """Extract facts using Anthropic API (claude-haiku)."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    prompt = f"""Extract structured facts from the following conversation/notes. For each significant fact, decision, preference, learning, or commitment, output a JSON object with these fields:
- type: one of "decision", "preference", "learning", "commitment", "fact"
- content: the actual fact/decision/etc (concise but complete)
- subject: what/who this is about (infer from context - projects, people, technologies, etc.)
- confidence: 0.0-1.0 (how certain is this fact)

Return ONLY a JSON array of fact objects. No other text.

Text to analyze:
{text[:8000]}"""

    payload = {
        "model": "claude-haiku-4-20250514",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["content"][0]["text"]
        
        # Clean up markdown if present
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\n', '', content)
            content = re.sub(r'\n```$', '', content)
        
        facts = json.loads(content)
        return facts if isinstance(facts, list) else []
    except Exception as e:
        print(f"Anthropic extraction error: {e}")
        return []


def extract_with_gemini(text: str, api_key: str) -> List[Dict]:
    """Extract facts using Gemini API (gemini-flash)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""Extract structured facts from the following conversation/notes. For each significant fact, decision, preference, learning, or commitment, output a JSON object with these fields:
- type: one of "decision", "preference", "learning", "commitment", "fact"
- content: the actual fact/decision/etc (concise but complete)
- subject: what/who this is about (infer from context - projects, people, technologies, etc.)
- confidence: 0.0-1.0 (how certain is this fact)

Return ONLY a JSON array of fact objects. No other text.

Text to analyze:
{text[:8000]}"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2000
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Clean up markdown if present
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\n', '', content)
            content = re.sub(r'\n```$', '', content)
        
        facts = json.loads(content)
        return facts if isinstance(facts, list) else []
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        return []


def extract_facts(text: str) -> List[Dict]:
    """Extract facts using available LLM API."""
    provider, api_key = find_api_key()
    
    if not provider:
        print("ERROR: No API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
        print("Or create a file at ~/.config/openai/api_key (or anthropic/gemini)")
        return []
    
    print(f"Using {provider} for extraction...")
    
    if provider == "openai":
        return extract_with_openai(text, api_key)
    elif provider == "anthropic":
        return extract_with_anthropic(text, api_key)
    elif provider == "gemini":
        return extract_with_gemini(text, api_key)
    
    return []


def read_daily_memory(date: str) -> Optional[str]:
    """Read daily memory file for a given date (YYYY-MM-DD)."""
    file_path = MEMORY_DIR / f"{date}.md"
    if file_path.exists():
        return file_path.read_text()
    return None


def read_transcripts() -> Optional[str]:
    """Read session transcripts. Only reads recent messages to avoid OOM on large files."""
    MAX_CHARS = 15000  # Limit total text to avoid huge LLM calls
    
    if not TRANSCRIPTS_DIR.exists():
        return None
    
    # Find all JSONL files, sorted by modification time (most recent first)
    jsonl_files = sorted(TRANSCRIPTS_DIR.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    
    if not jsonl_files:
        return None
    
    text_parts = []
    total_chars = 0
    
    for file in jsonl_files[:3]:  # Check up to 3 most recent session files
        # Only read the tail of large files
        file_size = file.stat().st_size
        read_offset = max(0, file_size - 500_000)  # Last 500KB max
        
        with open(file) as f:
            if read_offset > 0:
                f.seek(read_offset)
                f.readline()  # Skip partial line
            
            for line in f:
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    role = msg.get("role", "")
                    if role not in ("user", "assistant"):
                        continue
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        # Extract text from content blocks
                        content = " ".join(
                            b.get("text", "") for b in content 
                            if isinstance(b, dict) and b.get("type") == "text"
                        )
                    if not isinstance(content, str) or not content.strip():
                        continue
                    label = "User" if role == "user" else "Assistant"
                    text_parts.append(f"{label}: {content[:500]}")
                    total_chars += len(text_parts[-1])
                except (json.JSONDecodeError, KeyError):
                    pass
                
                if total_chars >= MAX_CHARS:
                    break
        
        if total_chars >= MAX_CHARS:
            break
    
    if text_parts:
        return "\n".join(text_parts[-100:])  # Last 100 messages max
    
    return None


def load_existing_facts() -> List[Dict]:
    """Load existing facts from extracted.jsonl."""
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


def normalize_for_comparison(text: str) -> str:
    """Normalize text for dedup comparison."""
    t = text.lower().strip()
    t = re.sub(r'[^\w\s]', '', t)  # Remove punctuation
    t = re.sub(r'\s+', ' ', t)  # Collapse whitespace
    return t

def word_overlap_ratio(a: str, b: str) -> float:
    """Calculate Jaccard similarity between word sets."""
    words_a = set(normalize_for_comparison(a).split())
    words_b = set(normalize_for_comparison(b).split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)

def is_duplicate(new_fact: Dict, existing_facts: List[Dict]) -> bool:
    """Check if a fact is a duplicate using normalized text + word overlap."""
    new_content = new_fact.get("content", "")
    new_norm = normalize_for_comparison(new_content)
    
    for existing in existing_facts:
        existing_content = existing.get("content", "")
        existing_norm = normalize_for_comparison(existing_content)
        
        # Exact normalized match
        if new_norm == existing_norm:
            return True
        
        # Substring containment
        if len(new_norm) > 20 and new_norm in existing_norm:
            return True
        if len(existing_norm) > 20 and existing_norm in new_norm:
            return True
        
        # High word overlap (>75% Jaccard similarity) with same subject
        if (new_fact.get("subject", "").lower() == existing.get("subject", "").lower()
                and word_overlap_ratio(new_content, existing_content) > 0.75):
            return True
    
    return False


def main():
    """Main extraction pipeline."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Memory Extraction for {today}")
    print(f"Workspace: {WORKSPACE_DIR}")
    print("=" * 50)
    
    # Try to read source text — prefer daily notes (curated), fall back to transcripts
    source = None
    source_type = None
    
    # Try daily memory first (cleaner, smaller, curated)
    print("Checking for daily memory file...")
    daily_text = read_daily_memory(today)
    if daily_text:
        source = daily_text
        source_type = "daily-note"
        print(f"✓ Found today's memory file ({len(source)} chars)")
    else:
        # Try yesterday's file
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        daily_text = read_daily_memory(yesterday)
        if daily_text:
            source = daily_text
            source_type = "daily-note"
            today = yesterday  # Set date for extracted facts
            print(f"✓ Found yesterday's memory file ({len(source)} chars)")
        else:
            print("✗ No daily memory files found")
    
    # Try transcripts as fallback or supplement
    if not source:
        print("Checking for session transcripts...")
        transcript_text = read_transcripts()
        if transcript_text:
            source = transcript_text
            source_type = "session"
            print(f"✓ Found session transcripts ({len(source)} chars)")
        else:
            print("✗ No session transcripts found")
    
    if not source:
        print("\nERROR: No source text found to extract from")
        print(f"  Memory dir: {MEMORY_DIR}")
        print(f"  Transcripts dir: {TRANSCRIPTS_DIR}")
        return
    
    # Extract facts
    print("\nExtracting facts...")
    facts = extract_facts(source)
    
    if not facts:
        print("No facts extracted")
        return
    
    print(f"✓ Extracted {len(facts)} facts")
    
    # Load existing facts for deduplication
    existing_facts = load_existing_facts()
    print(f"Loaded {len(existing_facts)} existing facts")
    
    # Deduplicate and save
    new_facts = []
    duplicates = 0
    
    MEMORY_DIR.mkdir(exist_ok=True)
    
    with open(EXTRACTED_FILE, "a") as f:
        for fact in facts:
            # Add metadata
            fact["date"] = today
            fact["source"] = source_type
            
            if is_duplicate(fact, existing_facts):
                duplicates += 1
                continue
            
            # Write to file
            f.write(json.dumps(fact) + "\n")
            new_facts.append(fact)
            existing_facts.append(fact)  # Add to existing for subsequent checks
    
    print(f"\n✓ Saved {len(new_facts)} new facts")
    print(f"✗ Skipped {duplicates} duplicates")
    
    # Show sample facts
    if new_facts:
        print("\nSample extracted facts:")
        for fact in new_facts[:3]:
            print(f"  [{fact['type']}] {fact['content'][:80]}...")
    
    print(f"\nExtracted facts saved to: {EXTRACTED_FILE}")


if __name__ == "__main__":
    main()
