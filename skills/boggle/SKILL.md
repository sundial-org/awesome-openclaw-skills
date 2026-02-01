---
name: boggle
description: Solve Boggle boards — find all valid words (German + English) on a 4x4 letter grid. Use when the user shares a Boggle photo, asks for words on a grid, or plays word games. Includes 1.7M word dictionaries (DE+EN).
---

# Boggle Solver

Fast trie-based DFS solver with dictionary-only matching. No AI/LLM guessing — words are validated exclusively against bundled dictionaries (359K English + 1.35M German).

## Workflow (from photo)

1. **Read the 4x4 grid** from the photo (left-to-right, top-to-bottom)
2. **Show the grid to the user and ask for confirmation** before solving
3. Only after user confirms → run the solver
4. **Always run English and German SEPARATELY** — present as two labeled sections (🇬🇧 / 🇩🇪)

## Solve a board

```bash
# English
python3 skills/boggle/scripts/solve.py ELMU ZBTS ETVO CKNA --lang en

# German
python3 skills/boggle/scripts/solve.py ELMU ZBTS ETVO CKNA --lang de
```

Each row is one argument (4 letters). Or use `--letters`:
```bash
python3 skills/boggle/scripts/solve.py --letters ELMUZBTSETVOCKNA --lang en
```

## Options

| Flag | Description |
|---|---|
| `--lang en/de` | Language (default: en; **always run EN and DE separately**) |
| `--min N` | Minimum word length (default: 3) |
| `--json` | JSON output with scores |
| `--dict FILE` | Custom dictionary (repeatable) |

## Scoring (standard Boggle)

- 3-4 letters: 1 pt
- 5 letters: 2 pts
- 6 letters: 3 pts
- 7 letters: 5 pts
- 8+ letters: 11 pts

## How it works

- Builds a trie from dictionary files (one-time, ~11s)
- DFS traversal from every cell, pruned by trie prefixes
- Adjacency: 8 neighbors (horizontal, vertical, diagonal)
- Each cell used at most once per word
- **Qu tile support:** Standard Boggle "Qu" tiles are handled as a single cell (e.g., `QUENHARI...` → "QU" occupies one position)
- **All matching is dictionary-only** — no generative/guessed words

## Data

Dictionaries are auto-downloaded from GitHub on first run if missing.


- `data/words_english_boggle.txt` — 359K English words
- `data/words_german_boggle.txt` — 1.35M German words

## Performance

- Trie build: ~11s (first run, 1.7M words)
- Solve: <5ms per board

