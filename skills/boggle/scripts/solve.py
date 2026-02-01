#!/usr/bin/env python3
"""
Boggle solver — finds all valid words on a 4x4 board.
Uses DFS with trie-based pruning for speed.

Usage:
  python3 solve.py HOPL NERI NIDO IEOT
  python3 solve.py --letters "H O P L N E R I N I D O I E O T"
  python3 solve.py --letters HOPLNERINIDOIEOT

Dictionaries auto-loaded from:
  1. skills/boggle/data/words_english_boggle.txt
  2. skills/boggle/data/words_german_boggle.txt
Or specify: --dict /path/to/wordlist.txt [--dict another.txt]
"""

import argparse
from itertools import groupby
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, "data")

DEFAULT_DICTS = [
    os.path.join(DATA_DIR, "words_english_boggle.txt"),
    os.path.join(DATA_DIR, "words_german_boggle.txt"),
]

DEFAULT_MIN_WORD_LEN = 3

def ensure_dictionaries(paths):
    """Auto-download dictionary files from GitHub if missing."""
    import urllib.request
    BASE_URL = 'https://raw.githubusercontent.com/christianhaberl/boggle-openclaw-skill/main/data'
    for path in paths:
        if not os.path.exists(path):
            fname = os.path.basename(path)
            url = f'{BASE_URL}/{fname}'
            print(f'Downloading {fname}...', file=sys.stderr)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(url, path)
            print(f'  -> {path}', file=sys.stderr)


SCORING = {3: 1, 4: 1, 5: 2, 6: 3, 7: 5}  # 8+ = 11
NEIGHBORS = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if not (dr == 0 and dc == 0))


class TrieNode:
    __slots__ = ['children', 'is_word']
    def __init__(self):
        self.children = {}
        self.is_word = False


def build_trie(words):
    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True
    return root


def load_dictionaries(paths, min_word_len=DEFAULT_MIN_WORD_LEN):
    words = set()
    for path in paths:
        if not os.path.exists(path):
            print(f"WARNING: Dictionary not found: {path}", file=sys.stderr)
            continue
        before = len(words)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip().lower()
                if len(w) >= min_word_len and w.isalpha():
                    words.add(w)
        added = len(words) - before
        print(f"Loaded {os.path.basename(path)}: {added} new words ({len(words)} total)", file=sys.stderr)
    return words


def tokenize_tiles(text):
    """Tokenize a string into Boggle tiles, handling multi-char tiles like 'Qu'.
    
    Standard Boggle has a single 'Qu' tile. This tokenizer scans left-to-right
    and greedily matches 'qu' as one tile; all other characters are single tiles.
    Returns a list of tile strings (lowercased).
    """
    tiles = []
    i = 0
    text = text.lower()
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] == 'qu':
            tiles.append('qu')
            i += 2
        else:
            tiles.append(text[i])
            i += 1
    return tiles


def parse_board(args):
    """Parse board from various input formats.
    
    Raises ValueError on invalid input instead of calling sys.exit(),
    so callers can handle errors gracefully and the function is testable.
    Supports standard Boggle 'Qu' tiles (counted as one cell).
    """
    if args.letters:
        raw = args.letters.replace(" ", "").replace(",", "")
        tiles = tokenize_tiles(raw)
        if len(tiles) != 16:
            raise ValueError(f"Need 16 tiles, got {len(tiles)} (hint: 'Qu' counts as one tile)")
        return [tiles[i:i+4] for i in range(0, 16, 4)]
    
    if args.rows:
        rows = []
        for r in args.rows:
            r = r.replace(" ", "")
            tiles = tokenize_tiles(r)
            rows.append(tiles)
        if len(rows) != 4 or any(len(r) != 4 for r in rows):
            raise ValueError("Need 4 rows of 4 tiles each (hint: 'Qu' counts as one tile)")
        return rows
    
    raise ValueError("Provide board as 4 row arguments or --letters")


def solve(board, trie, min_word_len=DEFAULT_MIN_WORD_LEN):
    found = set()
    rows, cols = len(board), len(board[0])
    
    def dfs(r, c, node, path, visited):
        tile = board[r][c]  # tile can be multi-char (e.g., 'qu')
        
        # Walk the trie through each character in the tile
        current = node
        for ch in tile:
            if ch not in current.children:
                return
            current = current.children[ch]
        
        new_path = path + tile
        
        if current.is_word:
            found.add(new_path)
        
        if not current.children:
            return
        
        visited.add((r, c))
        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                dfs(nr, nc, current, new_path, visited)
        visited.remove((r, c))
    
    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie, "", set())
    
    return found


def score_word(word):
    n = len(word)
    if n >= 8:
        return 11
    return SCORING.get(n, 0)


def main():
    parser = argparse.ArgumentParser(description="Boggle Solver")
    parser.add_argument("rows", nargs="*", help="4 rows of 4 letters (e.g., HOPL NERI NIDO IEOT)")
    parser.add_argument("--letters", "-l", help="All 16 letters as one string")
    parser.add_argument("--dict", "-d", action="append", dest="dicts", help="Dictionary file(s)")
    parser.add_argument("--min", type=int, default=3, help="Minimum word length (default: 3)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--lang", choices=["en", "de"], default="en", help="Dictionary language: 'en' for English, 'de' for German (run once per language for bilingual boards)")
    args = parser.parse_args()

    min_word_len = args.min

    try:
        board = parse_board(args)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print board
    print("Board:", file=sys.stderr)
    for row in board:
        print("  " + " ".join(t.upper() for t in row), file=sys.stderr)
    print(file=sys.stderr)

    # Load dictionaries
    dict_paths = args.dicts if args.dicts else []
    if not dict_paths:
        if args.lang == "en":
            dict_paths = [DEFAULT_DICTS[0]]
        elif args.lang == "de":
            dict_paths = [DEFAULT_DICTS[1]]

    ensure_dictionaries(dict_paths)
    t0 = time.time()
    words = load_dictionaries(dict_paths, min_word_len)
    if not words:
        print("ERROR: No dictionary words loaded", file=sys.stderr)
        sys.exit(1)
    
    t1 = time.time()
    trie = build_trie(words)
    t2_trie = time.time()
    print(f"Dictionary loaded in {t1-t0:.2f}s, trie built in {t2_trie-t1:.2f}s", file=sys.stderr)

    # Solve
    found = solve(board, trie, min_word_len)
    t2 = time.time()
    print(f"Solved in {t2-t2_trie:.3f}s — {len(found)} words found", file=sys.stderr)

    # Sort by length (desc) then alphabetically
    sorted_words = sorted(found, key=lambda w: (-len(w), w))
    
    total_score = sum(score_word(w) for w in sorted_words)

    if args.json:
        import json
        result = {
            "board": [row for row in board],
            "words": [{"word": w, "length": len(w), "score": score_word(w)} for w in sorted_words],
            "total_words": len(sorted_words),
            "total_score": total_score,
            "solve_time_ms": int((t2-t2_trie)*1000),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Group by length using itertools.groupby (sorted_words already sorted by -len)
        for length, group in groupby(sorted_words, key=len):
            words_list = list(group)
            pts = score_word(words_list[0])
            print(f"\n{'='*40}")
            print(f"{length} letters ({pts} pts each) — {len(words_list)} words:")
            print(", ".join(w.upper() for w in words_list))
        
        print(f"\n{'='*40}")
        print(f"TOTAL: {len(sorted_words)} words, {total_score} points")


if __name__ == "__main__":
    main()
