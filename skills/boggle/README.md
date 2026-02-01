# 🎲 Boggle Solver — OpenClaw Skill

Fast trie-based DFS Boggle solver for [OpenClaw](https://github.com/openclaw/openclaw).

## Features

- **1.7M dictionary words** — 359K English + 1.35M German
- **Qu-tile support** — standard Boggle rules
- **< 5ms solve time** per board
- **JSON output** with Boggle scoring
- **Bilingual** — run English and German separately

## Install

```bash
clawdhub install boggle
```

Or manually copy the `skills/boggle/` folder into your OpenClaw workspace.

## Usage

```bash
# English
python3 scripts/solve.py ELMU ZBTS ETVO CKNA --lang en

# German
python3 scripts/solve.py ELMU ZBTS ETVO CKNA --lang de

# With --letters flag
python3 scripts/solve.py --letters ELMUZBTSETVOCKNA --lang en

# JSON output
python3 scripts/solve.py ELMU ZBTS ETVO CKNA --lang en --json
```

## Options

| Flag | Description |
|---|---|
| `--lang en/de` | Dictionary language (default: en) |
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

- Builds a trie from dictionary files
- DFS traversal from every cell, pruned by trie prefixes
- Adjacency: 8 neighbors (horizontal, vertical, diagonal)
- Each cell used at most once per word
- Qu tiles handled as single cell
- **All matching is dictionary-only** — no AI guessing

## AI-Reviewed

This skill was reviewed by **Codex** and **Gemini Code Assist** across 5 review rounds. All findings addressed.

## License

MIT
