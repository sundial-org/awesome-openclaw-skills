
---
name: ralph
description: "Generate Claude Code, Gemini CLI, or Grok CLI automation loop commands. Asks questions about your requirements and outputs a ready-to-run command for PowerShell, Windows CMD, or Bash/Linux."
allowed-tools:
  - AskUserQuestion
  - Write
  - Read
---

# Ralph Command Generator

Generate optimized loop commands for automating Claude Code, Gemini CLI, or Grok CLI with PROMPT.md.

## Step 1: Choose AI Tool

Use AskUserQuestion:
- Question: "Which AI CLI tool do you want to use?"
- Header: "AI Tool"
- Options:
  1. "Claude Code (Recommended)" - "Claude AI assistant CLI"
  2. "Gemini CLI" - "Google Gemini AI assistant"
  3. "Grok CLI" - "xAI Grok AI assistant with agentic coding"

Store the choice for later.

## Step 2: Choose Model

Use AskUserQuestion based on AI tool choice:

**If Claude Code selected:**
- Question: "Which Claude model do you want to use?"
- Header: "Model"
- Options:
  1. "Default (Recommended)" - "Use default model (currently Sonnet 4.5)"
  2. "Haiku" - "Fastest and most cost-effective"
  3. "Sonnet" - "Balanced performance and cost"
  4. "Opus" - "Most capable, higher cost"

**If Gemini CLI selected:**
- Question: "Which Gemini model do you want to use?"
- Header: "Model"
- Options:
  1. "Default (Recommended)" - "Use default model"
  2. "gemini-3-flash" - "Latest Gemini 3, fastest and most cost-effective"
  3. "gemini-3-pro" - "Latest Gemini 3, most capable for complex tasks"
  4. "gemini-2.5-flash" - "Stable production model, fast"
  5. "gemini-2.5-pro" - "Stable production model, more capable"

**If Grok CLI selected:**
- Question: "Which Grok model do you want to use?"
- Header: "Model"
- Options:
  1. "Default (Recommended)" - "Use grok-code-fast-1, optimized for fast code generation and agentic loops"
  2. "grok-4-latest" - "Latest Grok 4, most capable for complex reasoning"
  3. "grok-beta" - "Preview of upcoming features"

Store the choice for later.

## Step 3: Choose Operating System

Use AskUserQuestion:
- Question: "Which shell environment are you using?"
- Header: "Shell"
- Options:
  1. "PowerShell (Recommended)" - "Windows PowerShell"
  2. "Windows CMD" - "Command Prompt (cmd.exe)"
  3. "Bash/Linux" - "Linux, Mac, or WSL"

Store the choice for later.

## Step 4: Choose Complexity Level

Use AskUserQuestion:
- Question: "What level of control do you need?"
- Header: "Complexity"
- Options:
  1. "Simple (Recommended)" - "Basic loop with minimal options"
  2. "Intermediate" - "Combine 2 control mechanisms"
  3. "Advanced" - "Full control with multiple safeguards"

## Step 5: Choose Loop Type (Based on Complexity)

### If Simple:
Use AskUserQuestion:
- Question: "What type of loop?"
- Header: "Loop Type"
- Options:
  1. "Fixed count (Recommended)" - "Run exactly N times"
  2. "Infinite with delay" - "Run forever with pauses"
  3. "Stop file trigger" - "Run until STOP.txt exists"

### If Intermediate:
Use AskUserQuestion:
- Question: "What combination do you need?"
- Header: "Features"
- multiSelect: true
- Options:
  1. "Fixed iterations" - "Run max N times"
  2. "Time limit" - "Run for max X minutes"
  3. "Stop file" - "Stop when STOP.txt appears"
  4. "Delay between runs" - "Pause X seconds"
  5. "Show counter" - "Display run number"
  6. "File monitoring" - "Stop at file size/lines"

### If Advanced:
Use AskUserQuestion:
- Question: "What features do you want?"
- Header: "Features"
- multiSelect: true
- Options:
  1. "Max iterations (Recommended)" - "Limit runs"
  2. "Time limit (Recommended)" - "Max duration"
  3. "Stop file (Recommended)" - "Manual stop"
  4. "Delay between runs" - "Pause X seconds"
  5. "Timestamp logging" - "Show time of each run"
  6. "Counter display" - "Show run number"

## Step 6: Gather Parameters

Based on selected features, ask for values:

**If fixed iterations selected:**
- Question: "How many iterations?"
- Options: "5 (Recommended)", "10", "20", "50", "100", "Custom"

**If time limit selected:**
- Question: "Maximum duration?"
- Options: "10 minutes (Recommended)", "30 minutes", "1 hour", "Custom"

**If delay selected:**
- Question: "Delay between runs?"
- Options: "5 seconds (Recommended)", "10 seconds", "30 seconds", "Custom"

**If file monitoring selected:**
- Question: "Monitor by?"
- Options: "File size (e.g., 5KB)", "Line count (e.g., 50 lines)", "Content (e.g., 'THE END')"

## Step 7: Generate Command

Build the appropriate command based on:
1. AI tool choice (Claude or Gemini)
2. Model choice
3. Shell choice (PowerShell, CMD, Bash)
4. Complexity level
5. Selected features
6. Parameter values

**IMPORTANT - Command Syntax:**

**For Claude Code (PowerShell/Bash):**
Use `claude-code` (NOT `claude -p`) to accept piped input. The `-p` flag requires an argument, not pipe.

- Default: `Get-Content PROMPT.md -Raw | claude-code --dangerously-skip-permissions`
- Haiku: `Get-Content PROMPT.md -Raw | claude-code --model haiku --dangerously-skip-permissions`
- Sonnet: `Get-Content PROMPT.md -Raw | claude-code --model sonnet --dangerously-skip-permissions`
- Opus: `Get-Content PROMPT.md -Raw | claude-code --model opus --dangerously-skip-permissions`

**For Claude Code (Bash):**
- Default: `cat PROMPT.md | claude-code --dangerously-skip-permissions`
- With model: `cat PROMPT.md | claude-code --model haiku --dangerously-skip-permissions`

**For Gemini CLI (PowerShell):**
Gemini CLI accepts stdin piping.

- Default: `Get-Content PROMPT.md -Raw | gemini --yolo`
- gemini-3-flash: `Get-Content PROMPT.md -Raw | gemini --model gemini-3-flash --yolo`
- gemini-3-pro: `Get-Content PROMPT.md -Raw | gemini --model gemini-3-pro --yolo`
- gemini-2.5-flash: `Get-Content PROMPT.md -Raw | gemini --model gemini-2.5-flash --yolo`
- gemini-2.5-pro: `Get-Content PROMPT.md -Raw | gemini --model gemini-2.5-pro --yolo`

**For Grok CLI (PowerShell):**
- Default: `Get-Content PROMPT.md -Raw | grok-auto` (uses default model from GROK_MODEL env var, auto-approves permissions)
- grok-code-fast-1: `Get-Content PROMPT.md -Raw | grok-auto -m grok-code-fast-1`
- grok-4-latest: `Get-Content PROMPT.md -Raw | grok-auto -m grok-4-latest`
- grok-beta: `Get-Content PROMPT.md -Raw | grok-auto -m grok-beta`

### Command Templates

**IMPORTANT - Placeholder Replacement:**

For **Claude Code**: Replace `[AI_COMMAND_WITH_PROMPT]` with the FULL command including the prompt argument:
- Default: `claude -p (Get-Content PROMPT.md -Raw) --dangerously-skip-permissions`
- With model: `claude -p (Get-Content PROMPT.md -Raw) --model haiku --dangerously-skip-permissions`

For **Gemini CLI**: Replace `[AI_COMMAND_WITH_PROMPT]` with piped command:
- Default: `Get-Content PROMPT.md -Raw | gemini --yolo`
- With model: `Get-Content PROMPT.md -Raw | gemini --model gemini-3-flash --yolo`

For **Grok CLI**: Replace `[AI_COMMAND_WITH_PROMPT]` with piped command:
- Default: `Get-Content PROMPT.md -Raw | grok-auto`
- With model: `Get-Content PROMPT.md -Raw | grok-auto -m grok-4-latest`

**CRITICAL**: Claude Code requires the prompt as a command-line argument. Piping does NOT work with `claude -p`.

**PowerShell - Simple Fixed:**
```powershell
for ($i=1; $i -le N; $i++) { $start = Get-Date; Write-Host "`n=== Run $i/N ===" -ForegroundColor Cyan; [AI_COMMAND_WITH_PROMPT]; $duration = ((Get-Date) - $start).TotalSeconds; Write-Host "⏱️  Time: $([math]::Round($duration, 2))s" -ForegroundColor Magenta }
```

**PowerShell - Simple Fixed + Delay:**
```powershell
for ($i=1; $i -le N; $i++) { $start = Get-Date; Write-Host "`n=== Run $i/N ===" -ForegroundColor Cyan; [AI_COMMAND_WITH_PROMPT]; $duration = ((Get-Date) - $start).TotalSeconds; Write-Host "⏱️  Time: $([math]::Round($duration, 2))s" -ForegroundColor Magenta; if ($i -lt N) { Write-Host "⏸️  Waiting X seconds..." -ForegroundColor Yellow; Start-Sleep -Seconds X } }
```

**PowerShell - Simple Infinite + Delay:**
```powershell
$i=1; while ($true) { $start = Get-Date; Write-Host "`n=== Run $i ===" -ForegroundColor Cyan; [AI_COMMAND_WITH_PROMPT]; $duration = ((Get-Date) - $start).TotalSeconds; Write-Host "⏱️  Time: $([math]::Round($duration, 2))s" -ForegroundColor Magenta; Write-Host "⏸️  Waiting X seconds..." -ForegroundColor Yellow; Start-Sleep -Seconds X; $i++ }
```

**PowerShell - Advanced Full Control:**
```powershell
$end = (Get-Date).AddMinutes(M); for ($i=1; $i -le N -and (Get-Date) -lt $end -and -not (Test-Path STOP.txt); $i++) { $start = Get-Date; Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] Run $i" -ForegroundColor Cyan; [AI_COMMAND_WITH_PROMPT]; $duration = ((Get-Date) - $start).TotalSeconds; Write-Host "⏱️  Time: $([math]::Round($duration, 2))s" -ForegroundColor Magenta; if ($i -lt N) { Write-Host "⏸️  Waiting X seconds..." -ForegroundColor Yellow; Start-Sleep -Seconds X } }; Write-Host "`n✅ Complete!" -ForegroundColor Green
```

**CMD - Simple Fixed:**
```cmd
for /L %i in (1,1,N) do @(echo. & echo === Run %i === & type PROMPT.md | [AI_COMMAND])
```
Note: CMD has limited capabilities. For time tracking, recommend PowerShell.

**CMD - Simple Infinite + Delay:**
```cmd
for /L %i in (1,0,2) do @(echo. & echo === Run %i === & type PROMPT.md | [AI_COMMAND] & timeout /t X /nobreak > nul)
```

**CMD - Advanced:**
```cmd
for /L %i in (1,1,N) do @(if exist STOP.txt exit & echo. & echo [%time%] Run %i & type PROMPT.md | [AI_COMMAND] & timeout /t X /nobreak > nul)
```
Note: For time tracking, use PowerShell (see RalphPowerShellComands.md).

**Bash - Simple Fixed:**
```bash
for i in {1..N}; do echo -e "\n=== Run $i/N ==="; start=$(date +%s); cat PROMPT.md | [AI_COMMAND]; dur=$(($(date +%s) - start)); echo "⏱️  Time: ${dur}s"; done
```

**Bash - Simple Fixed + Delay:**
```bash
for i in {1..N}; do echo -e "\n=== Run $i/N ==="; start=$(date +%s); cat PROMPT.md | [AI_COMMAND]; dur=$(($(date +%s) - start)); echo "⏱️  Time: ${dur}s"; [ $i -lt N ] && { echo "⏸️  Waiting X seconds..."; sleep X; }; done
```

**Bash - Simple Infinite + Delay:**
```bash
i=1; while :; do echo -e "\n=== Run $i ==="; start=$(date +%s); cat PROMPT.md | [AI_COMMAND]; dur=$(($(date +%s) - start)); echo "⏱️  Time: ${dur}s"; echo "⏸️  Waiting X seconds..."; sleep X; ((i++)); done
```

**Bash - Advanced:**
```bash
end=$(($(date +%s) + M*60)); for i in {1..N}; do [ $(date +%s) -ge $end ] && break; [ -f STOP.txt ] && break; echo -e "\n[$(date +%H:%M:%S)] Run $i"; start=$(date +%s); cat PROMPT.md | [AI_COMMAND]; dur=$(($(date +%s) - start)); echo "⏱️  Time: ${dur}s"; [ $i -lt N ] && { echo "⏸️  Waiting X seconds..."; sleep X; }; done; echo -e "\n✅ Complete!"
```

## Step 8: Create Command File

Create a timestamped filename in the format: `ralphcommand-YYYY-MM-DD-HHMMSS.md`

Example: `ralphcommand-2026-01-14-233045.md`

Use the Write tool to create this file in the current directory with:

**File structure:**
```markdown
# Ralph Command

Generated: [timestamp]
Shell: [PowerShell/CMD/Bash]

## Command

```[shell-type]
[THE ACTUAL COMMAND]
```

## How to run

1. Make sure you have a PROMPT.md file in this directory
2. Copy the command above
3. Paste into your [PowerShell/CMD/Bash] terminal
4. Press Enter

## How to stop

- Press Ctrl+C at any time
[- OR create STOP.txt: `echo $null > STOP.txt` / `touch STOP.txt`] (if stop file enabled)

## What it does

Runs [claude/gemini/grok] with PROMPT.md as input [N times / for M minutes / until stopped].
[Pauses X seconds between runs.]
[Shows timestamp and run number.]
[Displays execution time for each run.]

```

## Step 9: Notify User

After creating the file, tell the user the exact filename created:
```
✅ Created ralphcommand-YYYY-MM-DD-HHMMSS.md in your current directory!

The file contains your command ready to run. Just open it and copy the command.

For more variations and explanations, see:
- RalphPowerShellComands.md - Full PowerShell reference
- RalphWindowsCommands.md - Full CMD reference
- RalphLinuxCommands.md - Full Bash reference
- RalphGemini.md - Full Gemini CLI guide
- RalphGrok.md - Full Grok CLI guide
```

## Notes

- **CRITICAL FOR CLAUDE CODE**: The prompt MUST be passed as a command-line argument, NOT via stdin pipe. Use `claude -p (Get-Content PROMPT.md -Raw) --dangerously-skip-permissions`. Piping does NOT work with `claude -p`.
- **For Gemini and Grok**: Stdin piping works fine. Use `Get-Content PROMPT.md -Raw | gemini --yolo` or `Get-Content PROMPT.md -Raw | grok-auto`.
- **Model Selection is Optional**: Always ask which model, but "Default" option omits the `--model` flag
- **For Claude Code (PowerShell)**:
  - Default format: `claude -p (Get-Content PROMPT.md -Raw) --dangerously-skip-permissions`
  - With model: `claude -p (Get-Content PROMPT.md -Raw) --model <model> --dangerously-skip-permissions`
  - Models: `haiku`, `sonnet`, `opus`
- **For Gemini CLI**:
  - Default format: `Get-Content PROMPT.md -Raw | gemini --yolo`
  - With model: `Get-Content PROMPT.md -Raw | gemini --model <model> --yolo`
  - Models: `gemini-3-flash`, `gemini-3-pro`, `gemini-2.5-flash`, `gemini-2.5-pro`
  - Note: `-p` flag is deprecated in Gemini
- **For Grok CLI**:
  - Use `grok-auto` PowerShell function which calls xAI API directly (perfect for automation)
  - Default format: `Get-Content PROMPT.md -Raw | grok-auto` (no -m flag, uses GROK_MODEL env var if set)
  - With model: `Get-Content PROMPT.md -Raw | grok-auto -m <model>`
  - Models: `grok-code-fast-1`, `grok-4-latest`, `grok-beta`, `grok-4`
  - Note: `grok-auto` is a PowerShell function that calls the xAI API directly (no CLI needed)
  - Default model (grok-code-fast-1 via GROK_MODEL env var) is recommended for automation loops (fastest responses)
- Default to "Recommended" options when user is unsure
- Keep commands on one line when possible for easy copy-paste
- **Always include time tracking** - Show how long each run takes using `Get-Date` (PowerShell) or `date +%s` (Bash)
- **Always create timestamped file** - Format: `ralphcommand-YYYY-MM-DD-HHMMSS.md`
- **DO NOT include cost tracking** - No Get-LastCallCost function, no cost calculations, only time tracking
- For cost tracking with Claude, tell users to check https://console.anthropic.com for actual API usage
- When generating the final command for PowerShell:
  - For Claude: Replace `[AI_COMMAND_WITH_PROMPT]` with the full claude command including prompt argument
  - For Gemini/Grok: The piping is included in the template, just replace `[AI_COMMAND]` with the command after the pipe
