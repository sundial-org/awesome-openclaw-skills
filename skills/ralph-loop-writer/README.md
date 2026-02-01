# Ralph - Loop Command Generator

Generate automation loop commands for Claude, Gemini, or Grok.

## Usage

```
/ralph
```

## What It Does

1. Asks which AI tool (Claude, Gemini, Grok)
2. Asks which model
3. Asks which shell (PowerShell, CMD, Bash)
4. Asks what features (iterations, time limit, stop file)
5. Generates a ready-to-run command
6. Saves to `ralphcommand-YYYY-MM-DD-HHMMSS.md`

## Output

Creates a file like:

```markdown
# Ralph Command

Generated: 2026-01-15 14:30:22
Shell: PowerShell

## Command

```powershell
for ($i=1; $i -le 10; $i++) { ... }
```

## How to run

1. Make sure you have a PROMPT.md
2. Copy the command
3. Paste into terminal
4. Press Enter
```

## Use With Workflows

Create a PROMPT.md that tells the AI to:

```markdown
1. Read STATUS.md
2. Do the current step
3. Update STATUS.md
4. Stop
```

Then run the ralph command to loop through steps automatically.

## Part of the System

```
/recommendation-builder  →  Find improvements
/improvement-workflow    →  Implement improvements
/ralph                   →  Automate the loops ← YOU ARE HERE
```
