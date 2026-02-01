#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVES_DIR = os.path.join(BASE_DIR, "archives")
RESET_SCRIPT = os.path.join(BASE_DIR, "reset.sh")
MEMORY_FILE = os.path.expanduser("~/openclaw/MEMORY.md")

def ensure_dirs():
    if not os.path.exists(ARCHIVES_DIR):
        os.makedirs(ARCHIVES_DIR)

def create_archive(summary, tokens, session_id):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(ARCHIVES_DIR, filename)
    
    data = {
        "timestamp": timestamp,
        "session_id": session_id,
        "token_count": tokens,
        "summary": summary
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath, timestamp

def update_memory_md(summary, timestamp, tokens, archive_filename):
    if not os.path.exists(MEMORY_FILE):
        print(f"Error: MEMORY.md not found at {MEMORY_FILE}")
        return

    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Section Headers
    ARCHIVE_HEADER = "## Recent Archives"
    INDEX_HEADER = "### Archive Index"

    # Ensure headers exist
    if ARCHIVE_HEADER not in content:
        content += f"\n\n{ARCHIVE_HEADER}\n\n"
    
    # Split content to find the archives section
    parts = content.split(ARCHIVE_HEADER)
    pre_archive = parts[0]
    archive_section = parts[1] if len(parts) > 1 else ""

    # Parse existing archives from the text (simple heuristic or rigid structure)
    # We will reconstruct the section.
    # Current format hypothesis:
    # **[Timestamp]** (Tokens: X)
    # Summary text...
    # ---
    
    # For now, let's just append the new one to the top of the list and truncate.
    # Actually, parsing "existing" summaries from markdown is hard without a fixed format.
    # Strategy: We will read the JSONs from the archives/ folder to reconstruct the "Recent" list.
    # This is safer than parsing Markdown.
    
    # 1. List all JSONs in archives/
    files = [f for f in os.listdir(ARCHIVES_DIR) if f.endswith('.json')]
    files.sort(reverse=True) # Newest first
    
    recent_archives = []
    older_archives = []
    
    for i, f_name in enumerate(files):
        f_path = os.path.join(ARCHIVES_DIR, f_name)
        try:
            with open(f_path, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                if i < 3: # Keep top 3 detailed
                    recent_archives.append(data)
                else:
                    older_archives.append(data)
        except Exception as e:
            print(f"Skipping bad archive {f_name}: {e}")

    # Build new Markdown section
    new_section = "\n"
    
    for arc in recent_archives:
        ts = arc.get('timestamp', 'Unknown')
        tok = arc.get('token_count', 0)
        summ = arc.get('summary', '').strip()
        new_section += f"### Snapshot: {ts}\n"
        new_section += f"- **Tokens:** {tok}\n"
        new_section += f"- **Summary:** {summ}\n\n---\n\n"

    if older_archives:
        new_section += f"{INDEX_HEADER}\n\n"
        new_section += "| Date | Tokens | ID |\n"
        new_section += "|------|--------|----|\n"
        for arc in older_archives:
            ts = arc.get('timestamp', '').split('_')[0] # Just date
            full_ts = arc.get('timestamp', '')
            tok = arc.get('token_count', '')
            sid = arc.get('session_id', 'N/A')
            new_section += f"| {full_ts} | {tok} | {sid} |\n"
    
    # Reassemble MEMORY.md
    # We replace everything after "## Recent Archives" with our new section
    # Use a specific delimiter if possible, or just the end of file?
    # Risk: "## Recent Archives" might not be at the end.
    # Safer: Look for the next H2 "## " after Archives.
    
    post_archive = ""
    if "## " in archive_section:
        # Find if there are other sections after
        # This is tricky with split. Let's use regex or line iteration? 
        # Simple approach: Assume Recent Archives is at the end or handle the split carefully.
        # Let's try to preserve content after archives if it exists.
        
        # Split by newlines to handle line-by-line
        lines = archive_section.splitlines()
        
        # Check if there is another H2
        next_h2_index = -1
        for idx, line in enumerate(lines):
            if line.startswith("## ") and idx > 0: # Ignore immediate match if any
                next_h2_index = idx
                break
        
        if next_h2_index != -1:
            post_archive = "\n" + "\n".join(lines[next_h2_index:])
            # new_section is already built
        else:
            post_archive = ""
            
    final_content = pre_archive + ARCHIVE_HEADER + new_section + post_archive
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Updated {MEMORY_FILE} with snapshot {timestamp}")

def main():
    parser = argparse.ArgumentParser(description="Sophie Optimizer Logic")
    parser.add_argument("--summary", required=True, help="Context summary text")
    parser.add_argument("--tokens", type=int, default=0, help="Current token count")
    parser.add_argument("--session-id", default="main", help="Session ID")
    parser.add_argument("--reset", action="store_true", help="Trigger reset.sh after archiving")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    # Notify Start
    try:
        subprocess.run(["openclaw", "message", "send", "--message", f"🔄 Iniciando otimização de contexto ({args.tokens} tokens)..."], check=False)
    except Exception:
        pass

    print(f"Creating archive for session {args.session_id} ({args.tokens} tokens)...")
    filepath, timestamp = create_archive(args.summary, args.tokens, args.session_id)
    print(f"Archive saved to {filepath}")
    
    print("Updating MEMORY.md...")
    update_memory_md(args.summary, timestamp, args.tokens, os.path.basename(filepath))
    
    # Notify Progress
    try:
        subprocess.run(["openclaw", "message", "send", "--message", f"✅ Contexto arquivado em {os.path.basename(filepath)}. Memória atualizada."], check=False)
    except Exception:
        pass

    if args.reset:
        print("Triggering reset script...")
        # Notify Reset
        try:
            subprocess.run(["openclaw", "message", "send", "--message", "⚠️ Reiniciando sistema para limpeza de sessão. Volto já! 👑"], check=False)
        except Exception:
            pass
            
        # Use nohup to allow the script to survive if the parent dies, 
        # though systemctl restart might handle it.
        subprocess.Popen(["/bin/bash", RESET_SCRIPT], start_new_session=True)

if __name__ == "__main__":
    main()
