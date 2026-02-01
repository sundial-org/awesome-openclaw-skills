#!/usr/bin/env python3
"""
Ingest ChatGPT export into structured memory files.

Usage:
  python3 scripts/ingest-chatgpt.py imports/conversations.json
  python3 scripts/ingest-chatgpt.py imports/chatgpt-export.zip

Options:
  --min-turns N     Skip conversations with fewer than N user messages (default: 2)
  --min-length N    Skip conversations where total content < N chars (default: 200)
  --keep-all        Keep everything, no filtering
  --dry-run         Show what would be created without writing files
"""

import json
import sys
import os
import re
import zipfile
import argparse
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "memory" / "knowledge" / "chatgpt"


def extract_conversations_json(source_path: str) -> list:
    """Extract conversations.json from a zip or read directly."""
    path = Path(source_path)
    
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            # Look for conversations.json in the zip
            candidates = [n for n in zf.namelist() if n.endswith("conversations.json")]
            if not candidates:
                print(f"ERROR: No conversations.json found in {path}")
                print(f"  Contents: {zf.namelist()[:20]}")
                sys.exit(1)
            with zf.open(candidates[0]) as f:
                return json.load(f)
    elif path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    else:
        print(f"ERROR: Unsupported file type: {path.suffix}")
        sys.exit(1)


def traverse_conversation(mapping: dict) -> list:
    """Walk the message tree in order, returning [(role, text, timestamp), ...]"""
    if not mapping:
        return []
    
    # Find the root node (no parent or parent not in mapping)
    root_id = None
    for node_id, node in mapping.items():
        parent = node.get("parent")
        if parent is None or parent not in mapping:
            root_id = node_id
            break
    
    if not root_id:
        return []
    
    # Walk the tree depth-first, following first child
    messages = []
    current_id = root_id
    visited = set()
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        node = mapping.get(current_id, {})
        msg = node.get("message")
        
        if msg and msg.get("content"):
            content = msg["content"]
            role = msg.get("author", {}).get("role", "unknown")
            
            # Extract text from content parts
            text = ""
            if content.get("content_type") == "text" and content.get("parts"):
                text = "\n".join(
                    str(p) for p in content["parts"] 
                    if isinstance(p, str) and p.strip()
                )
            elif content.get("content_type") == "code" and content.get("text"):
                text = f"```\n{content['text']}\n```"
            
            timestamp = msg.get("create_time")
            
            if text.strip() and role in ("user", "assistant"):
                messages.append((role, text.strip(), timestamp))
        
        # Follow children (take the first/main branch)
        children = node.get("children", [])
        current_id = children[0] if children else None
    
    return messages


def slugify(text: str, max_len: int = 60) -> str:
    """Convert title to filesystem-safe slug."""
    if not text:
        text = "untitled"
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:max_len].rstrip('-')


def format_conversation(title: str, messages: list, create_time: float) -> str:
    """Format a conversation as clean markdown."""
    date_str = "Unknown date"
    if create_time:
        dt = datetime.fromtimestamp(create_time, tz=timezone.utc)
        date_str = dt.strftime("%Y-%m-%d")
    
    lines = [
        f"# {title}",
        f"**Source:** ChatGPT | **Date:** {date_str} | **Turns:** {len([m for m in messages if m[0] == 'user'])}",
        "",
    ]
    
    for role, text, ts in messages:
        if role == "user":
            lines.append(f"## Q: {text[:120]}")
            if len(text) > 120:
                lines.append("")
                lines.append(text)
        else:
            lines.append("")
            lines.append(text)
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ingest ChatGPT exports into memory")
    parser.add_argument("source", help="Path to conversations.json or export zip")
    parser.add_argument("--min-turns", type=int, default=2, help="Min user messages to keep (default: 2)")
    parser.add_argument("--min-length", type=int, default=200, help="Min total chars to keep (default: 200)")
    parser.add_argument("--keep-all", action="store_true", help="Keep all conversations")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    print(f"📂 Loading from: {args.source}")
    conversations = extract_conversations_json(args.source)
    print(f"📊 Found {len(conversations)} conversations")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Topic exclusion filters (case-insensitive, checked against title + first few messages)
    EXCLUDE_PATTERNS = [
        r'asthma', r'pediatric', r'inhaler', r'school.nurse', r'sbhc',
        r'\birb\b', r'pcori', r'\bnih\b', r'\br01\b', r'school.based.health',
        r'\bchc\b', r'flovent', r'albuterol', r'intervention.fidelity',
        r'umass', r'glp-1', r'cognitive.testing', r'research.letter',
        r'journal.submission', r'letter.of.support', r'dropout.rate',
        r'navigator.effectiveness', r'nebulizer', r'spirometry',
        r'pulmonary', r'bronchial', r'wheez', r'aafa',
        r'school.health.center', r'clinical.trial', r'fte.for.nih',
    ]
    exclude_re = re.compile('|'.join(EXCLUDE_PATTERNS), re.IGNORECASE)
    
    kept = 0
    skipped = 0
    excluded = 0
    total_chars = 0
    
    # Track slugs to handle duplicates
    used_slugs = {}
    
    for conv in conversations:
        title = conv.get("title") or "Untitled"
        create_time = conv.get("create_time")
        mapping = conv.get("mapping", {})
        
        messages = traverse_conversation(mapping)
        
        if not messages:
            skipped += 1
            continue
        
        user_turns = len([m for m in messages if m[0] == "user"])
        total_text = sum(len(m[1]) for m in messages)
        
        # Filter
        if not args.keep_all:
            if user_turns < args.min_turns:
                skipped += 1
                continue
            if total_text < args.min_length:
                skipped += 1
                continue
        
        # Exclusion filter: check title + first few user messages
        check_text = title + " " + " ".join(
            m[1][:500] for m in messages[:6] if m[0] == "user"
        )
        if exclude_re.search(check_text):
            excluded += 1
            continue
        
        # Generate filename
        date_prefix = ""
        if create_time:
            dt = datetime.fromtimestamp(create_time, tz=timezone.utc)
            date_prefix = dt.strftime("%Y%m%d-")
        
        slug = slugify(title)
        if not slug:
            slug = "untitled"
        
        full_slug = f"{date_prefix}{slug}"
        
        # Handle duplicate slugs
        if full_slug in used_slugs:
            used_slugs[full_slug] += 1
            full_slug = f"{full_slug}-{used_slugs[full_slug]}"
        else:
            used_slugs[full_slug] = 1
        
        filename = f"{full_slug}.md"
        filepath = OUTPUT_DIR / filename
        
        content = format_conversation(title, messages, create_time)
        
        if args.dry_run:
            print(f"  Would write: {filename} ({user_turns} turns, {total_text} chars)")
        else:
            with open(filepath, "w") as f:
                f.write(content)
        
        kept += 1
        total_chars += total_text
    
    print(f"\n✅ Done!")
    print(f"  Kept: {kept} conversations")
    print(f"  Skipped: {skipped} (below thresholds)")
    print(f"  Excluded: {excluded} (matched exclusion filters)")
    print(f"  Total content: {total_chars:,} characters")
    print(f"  Output: {OUTPUT_DIR}/")
    
    if args.dry_run:
        print(f"\n  (Dry run — no files written)")


if __name__ == "__main__":
    main()
