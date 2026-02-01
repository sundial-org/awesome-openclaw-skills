#!/usr/bin/env python3
import sys
import re
import json
import urllib.request
import html as html_parser
import os
import time
from datetime import datetime

def clean_html(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html_parser.unescape(text)
    return text.strip()

def truncate_words(text, limit):
    if not limit or limit <= 0:
        return text
    
    truncated_lines = []
    for line in text.split('\n'):
        words = line.split()
        if not words:
            truncated_lines.append("")
            continue
        # Only take words up to the limit
        truncated_lines.append(' '.join(words[:limit]))
    return '\n'.join(truncated_lines)

def get_catalog(board):
    url = f"https://boards.4chan.org/{board}/catalog"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching catalog: {e}", file=sys.stderr)
        return []

    # Extract the catalog JSON from the script tag
    match = re.search(r'var catalog = (\{.*?\});', html)
    if not match:
        print("Could not find catalog data in HTML", file=sys.stderr)
        return []

    try:
        catalog_data = json.loads(match.group(1))
        threads_data = catalog_data.get('threads', {})
        results = []
        for thread_id, info in threads_data.items():
            teaser = info.get('teaser', info.get('sub', ''))
            teaser = teaser.replace('\n', ' ').replace('\r', '')
            post_count = info.get('r', 0) # 'r' is the reply count
            results.append((thread_id, post_count, teaser))
        return results
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return []

def get_thread(board, thread_id, output_root=None, word_limit=None):
    url = f"https://boards.4chan.org/{board}/thread/{thread_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching thread {thread_id}: {e}", file=sys.stderr)
        return ""

    # Extract posts and their file info
    post_ids = re.findall(r'<blockquote class="postMessage" id="m(\d+)">', html_content)
    
    output_buffer = []
    for post_id in post_ids:
        # File info
        file_match = re.search(fr'<div class="fileText" id="fT{post_id}">File: <a [^>]+>([^<]+)</a>', html_content)
        file_name = file_match.group(1) if file_match else None
        
        # Message content
        msg_match = re.search(fr'<blockquote class="postMessage" id="m{post_id}">(.*?)</blockquote>', html_content, re.DOTALL)
        content = msg_match.group(1) if msg_match else ""
        
        content = content.replace('<br>', '\n')
        cleaned_content = clean_html(content)
        
        # Apply word truncation if limit is specified
        if word_limit:
            cleaned_content = truncate_words(cleaned_content, word_limit)
        
        post_text = f"--- Post {post_id} ---\n"
        if file_name:
            post_text += f"[File: {file_name}]\n"
        post_text += cleaned_content + "\n"
        output_buffer.append(post_text)

    full_output = "\n".join(output_buffer)
    
    # Print to console
    print(full_output)
    
    # Write to file if output_root provided
    if output_root:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_dir = os.path.join(output_root, f"{board}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{thread_id}.txt")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_output)
            print(f"--- Saved to {file_path} ---", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            
    return full_output

def show_usage():
    print("Usage:")
    print("  python3 chan_extractor.py catalog <board>")
    print("  python3 chan_extractor.py thread <board> <thread_id> [output_root_dir] [word_limit]")
    print("\nExamples:")
    print("  python3 chan_extractor.py catalog a")
    print("  python3 chan_extractor.py thread a 285635254 downloads 10")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "catalog":
        board = sys.argv[2]
        threads = get_catalog(board)
        for tid, r_count, teaser in threads:
            print(f"{tid}|{r_count}|{teaser}")
            
    elif cmd == "thread":
        if len(sys.argv) < 4:
            print("Error: thread_id required.")
            show_usage()
            sys.exit(1)
        board = sys.argv[2]
        thread_id = sys.argv[3]
        out_root = None
        word_limit = None
        
        if len(sys.argv) > 4:
            # Check if arg4 is a digit (word_limit) or a directory
            if sys.argv[4].isdigit():
                word_limit = int(sys.argv[4])
            else:
                out_root = sys.argv[4]
                if len(sys.argv) > 5 and sys.argv[5].isdigit():
                    word_limit = int(sys.argv[5])
        
        get_thread(board, thread_id, out_root, word_limit)
        
    else:
        print(f"Unknown command: {cmd}")
        show_usage()
        sys.exit(1)
