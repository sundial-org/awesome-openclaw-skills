# Sudoku Skill

Fetch, render, and reveal Sudoku puzzles. This is a skill for [Clawdbot](https://github.com/clawdbot/clawdbot).

📦 **Install via ClawdHub:** [clawdhub.com/skill/sudoku](https://clawdhub.com/skill/sudoku)

## Functions

- **Fetch Puzzles:** Download new 9x9 or 6x6 puzzles from sudokuonline.io.
- **Render:** Generate clean PNG images or A4 PDFs for printing.
- **Reveal:** Show solutions for the whole grid, specific boxes, or single cells.
- **Share:** Generate SudokuPad-compatible share links (Native, SCL, F-Puzzles).

## Usage

### Get a Puzzle

Fetches a new puzzle and stores it as JSON.

**Get a Classic Easy puzzle:**
```bash
./scripts/sudoku.py get easy9
```

**Get a Kids 6x6 puzzle:**
```bash
./scripts/sudoku.py get kids6
```

### Render Puzzle

Render a puzzle as an image or PDF.

**Render latest puzzle as A4 PDF (for printing):**
```bash
./scripts/sudoku.py render --pdf
```

**Render latest puzzle as clean PNG (for viewing):**
```bash
./scripts/sudoku.py render
```

### Reveal Solution

Reveal the solution for the latest or specific puzzle.

**Reveal full solution as printable PDF:**
```bash
./scripts/sudoku.py reveal --pdf
```

**Reveal a single cell (row 3, column 7):**
```bash
./scripts/sudoku.py reveal --cell 3 7
```

### Share Link

**Generate a SudokuPad share link:**
```bash
./scripts/sudoku.py share
```
