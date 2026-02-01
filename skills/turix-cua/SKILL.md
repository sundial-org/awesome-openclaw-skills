---
name: turix-mac
description: Computer Use Agent (CUA) for macOS automation using TuriX. Use when you need to perform visual tasks on the desktop, such as opening apps, clicking buttons, or navigating UIs that don't have a CLI or API.
---

# TuriX-Mac Skill

This skill allows Clawdbot to control the macOS desktop visually using the TuriX Computer Use Agent.

## When to Use

- When asked to perform actions on the Mac desktop (e.g., "Open Spotify and play my liked songs").
- When navigating applications that lack command-line interfaces.
- For multi-step visual workflows (e.g., "Find the latest invoice in my email and upload it to the company portal").
- When you need the agent to plan, reason, and execute complex tasks autonomously.

## Key Features

### 🤖 Multi-Model Architecture
TuriX uses a sophisticated multi-model system:
- **Brain**: Understands the task and generates step-by-step plans
- **Actor**: Executes precise UI actions based on visual understanding
- **Planner**: Coordinates high-level task decomposition (when `use_plan: true`)
- **Memory**: Maintains context across task steps

### 📋 Skills System
Skills are markdown playbooks that guide the agent for specific domains:
- `github-web-actions`: GitHub navigation, repo search, starring
- `browser-tasks`: General web browser operations
- Custom skills can be added to the `skills/` directory

### 🔄 Resume Capability
The agent can resume interrupted tasks by setting a stable `agent_id`.

## Running TuriX

### Basic Task
```bash
skills/local/turix-mac/scripts/run_turix.sh "Open Chrome and go to github.com"
```

### Resume Interrupted Task
```bash
skills/local/turix-mac/scripts/run_turix.sh --resume my-task-001
```

> ⚠️ **Important**: The `./run_turix.sh` command does NOT automatically update the task in `config.json`. **You must manually edit `examples/config.json` and modify the `agent.task` field before running!**


### Tips for Effective Tasks

**✅ Good Examples:**
- "Open Safari, go to google.com, search for 'TuriX AI', and click the first result"
- "Open System Settings, click on Dark Mode, then return to System Settings"
- "Open Finder, navigate to Documents, and create a new folder named 'Project X'"

**❌ Avoid:**
- Vague instructions: "Help me" or "Fix this"
- Impossible actions: "Delete all files"
- Tasks requiring system-level permissions without warning

**💡 Best Practices:**
1. Be specific about the target application
2. Break complex tasks into clear steps, but do not mention the precise coordinates on the screen.

## Hotkeys

- **Force Stop**: `Cmd+Shift+2` - Immediately stops the agent

## Monitoring & Logs

Logs are saved to `.turix_tmp/logging.log` in the project directory. Check this for:
- Step-by-step execution details
- LLM interactions and reasoning
- Errors and recovery attempts

## Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| `NoneType has no attribute 'save'` | Screen recording permission missing. Grant in System Settings and restart Terminal. |
| `Screen recording access denied` | Run: `osascript -e 'tell application "Safari" to do JavaScript "alert(1)"'` and click Allow |
| `Conda environment not found` | Ensure `turix_env` exists: `conda create -n turix_env python=3.12` |
| Module import errors | Activate environment: `conda activate turix_env` then `pip install -r requirements.txt` |
| Permission errors for keyboard listener | Add Terminal/IDE to **Accessibility** permissions |

### Debug Mode

Logs include DEBUG level by default. Check:
```bash
tail -f your_dir/TuriX-CUA/.turix_tmp/logging.log
```

## Architecture

```
User Request
     ↓
[Clawdbot] → [TuriX Skill] → [run_turix.sh] → [TuriX Agent]
                                              ↓
                    ┌─────────────────────────┼─────────────────────────┐
                    ↓                         ↓                         ↓
               [Planner]                 [Brain]                  [Memory]
                    ↓                         ↓                         ↓
                                         [Actor] ───→ [Controller] ───→ [macOS UI]
```

## Skill System Details

Skills are markdown files with YAML frontmatter in the `skills/` directory:

```md
---
name: skill-name
description: When to use this skill
---
# Skill Instructions
High-level workflow like: Open Safari,then go to Google.
```

The Planner selects relevant skills based on name/description; the Brain uses full content for step guidance.

## Advanced Options

| Option | Description |
|--------|-------------|
| `use_plan: true` | Enable planning for complex tasks |
| `use_skills: true` | Enable skill selection |
| `resume: true` | Resume from previous interruption |
| `max_steps: N` | Limit total steps (default: 100) |
| `max_actions_per_step: N` | Actions per step (default: 5) |
| `force_stop_hotkey` | Custom hotkey to stop agent |

---

## TuriX Skills System

TuriX supports **Skills**: markdown playbooks that help the agent behave more reliably in specific domains.

### 1. Built-in Skills

| Skill | Use |
|-------|-----|
| `github-web-actions` | GitHub web actions (search repos, star, etc.) |

### 2. Create a Custom Skill

Create a `.md` file in the TuriX project's `skills/` directory:

```md
---
name: my-custom-skill
description: When performing X specific task
---
# Custom Skill

## Guidelines
- Step 1: Do this first
- Step 2: Then do that
- Step 3: Verify the result
```

**Field definitions:**
- `name`: Skill identifier (used by the Planner to select)
- `description`: When to use this skill (Planner matches on this)
- The body below: Full execution guide (used by the Brain)

### 3. Enable Skills

In `examples/config.json`:

```json
{
  "agent": {
    "use_plan": true,
    "use_skills": true,
    "skills_dir": "skills",
    "skills_max_chars": 4000
  }
}
```

### 4. Run a Task with Skills

```bash
skills/local/turix-mac/scripts/run_turix.sh "Search for turix-cua on GitHub and star it"
```

The agent will automatically:
1. Planner reads the skill name and description
2. Selects relevant skills
3. Brain uses the full skill content to guide execution

### 5. Chinese Text Support

**Background:**
Passing Chinese text to TuriX via a shell heredoc (`cat << 'EOF' > file`) can cause encoding issues because shell variable handling of UTF-8 may introduce escaping errors.

**Solution:**
The `run_turix.sh` script uses Python to handle UTF-8 correctly:

```python
import json

# Read with UTF-8
with open(config_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Write without escaping non-ASCII text
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

**Key points:**
1. Always use `encoding='utf-8'` when reading/writing files
2. Use `ensure_ascii=False` to preserve non-ASCII text
3. Pass task content via an inline Python script instead of a shell heredoc

### 6. Document Creation Best Practices

**Challenges:**
- Asking TuriX to collect news, then create and send a document directly
- TuriX is a GUI agent, so it can be slow and less deterministic. Prefer using TuriX only for tasks Clawdbot cannot do or where TuriX is faster.

**Recommended approach:** create the document yourself and let TuriX only send it
1. Create the Word document with python-docx
2. Let TuriX only send the file

```python
from docx import Document
doc = Document()
doc.add_heading('Title')
doc.save('/path/to/file.docx')
```

**Suggested workflow:**
1. Use `web_fetch` to gather information
2. Use Python to create the Word document
3. Use TuriX to send the file. Specify the file path and say to send the file, not just the file name.
4. If you really need TuriX to manually create a Word document and type in collected information, put the content in turix skills (for large amounts) or in the task name (for small amounts).

### 7. Example: Add a New Skill

Create `skills/browser-tasks.md`:

```md
---
name: browser-tasks
description: When performing tasks in a web browser (search, navigate, fill forms).
---
# Browser Tasks

## Navigation
- Use the address bar or search box to navigate
- Open new tabs for each distinct task
- Wait for page to fully load before proceeding

## Forms
- Click on input fields to focus
- Type content clearly
- Look for submit/button to complete actions

## Safety
- Confirm before submitting forms
- Do not download files without user permission
```

### 8. Skill Development Tips

1. **Be precise in the description** - helps the Planner select correctly
2. **Make steps clear** - the Brain needs explicit guidance
3. **Include safety checks** - confirmations for important actions
4. **Keep it concise** - recommended under 4000 characters

---

## Monitoring and Debugging Guide

### 1. Run a Task

```bash
# Run in background (recommended)
cd /Users/tonyyan/clawd/skills/local/turix-mac/scripts
./run_turix.sh "Your task description" --background

# Or use timeout to set a max runtime
./run_turix.sh "Task" &
```

### 2. Monitor Progress

**Method 1: Session logs**
```bash
# List running sessions
clawdbot sessions_list

# View history
clawdbot sessions_history <session_key>
```

**Method 2: TuriX logs**
```bash
# Tail logs in real time
tail -f your_dir/TuriX-CUA/.turix_tmp/logging.log

# Or inspect completed step files
ls -lt your_dir/TuriX-CUA/examples/.turix_tmp/brain_llm_interactions.log_brain_*.txt
```

**Method 3: Check processes**
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**Method 4: Check generated files**
```bash
# List files created by the agent
ls -la your_dir/TuriX-CUA/examples/.turix_tmp/*.txt
```

### 3. Log File Reference

| File | Description |
|------|-------------|
| `logging.log` | Main log file |
| `brain_llm_interactions.log_brain_N.txt` | Brain model conversations (one per step) |
| `actor_llm_interactions.log_actor_N.txt` | Actor model conversations (one per step) |

**Key log markers:**
- `📍 Step N` - New step started
- `✅ Eval: Success/Failed` - Current step evaluation
- `🎯 Goal to achieve this step` - Current goal
- `🛠️  Action` - Executed action
- `✅ Task completed successfully` - Task completed

### 4. Common Monitoring Issues

| Issue | Check |
|-------|-------|
| Process unresponsive | `ps aux | grep main.py` |
| Stuck on step 1 | Check whether `.turix_tmp/` was created |
| Model loading is slow | First run can take 1-2 minutes to load models |
| No log output | Check `config.json` `logging_level` |

### 5. Force Stop

**Hotkey**: `Cmd+Shift+2` - stop the agent immediately

**Command**:
```bash
pkill -f "python examples/main.py"
```

### 6. View Results

After completion, the agent will:
1. Create interaction logs in `.turix_tmp/`
2. Create record files (if `record_info` is used)
3. Keep screenshots in memory for subsequent steps

**Example: view a summary file**
```bash
cat your_dir/TuriX-CUA/examples/.turix_tmp/latest_ai_news_summary_jan2026.txt
```

### 7. Debugging Tips

1. **Inspect Brain reasoning**: check `brain_llm_interactions.log_brain_*.txt` for `analysis` and `next_goal`
2. **Inspect Actor actions**: check `actor_llm_interactions.log_actor_*.txt` for actions
3. **Check screenshots**: TuriX captures a screenshot each step (kept in memory)
4. **Read record files**: the agent uses `record_info` to save key info to `.txt` files

### 8. Example Monitoring Flow

```bash
# 1. Run a task
./run_turix.sh "Search AI news and summarize" &

# 2. Wait a few seconds and check the process
sleep 10 && ps aux | grep main.py

# 3. Check if logs are being created
ls -la your_dir/TuriX-CUA/examples/.turix_tmp/

# 4. Tail progress in real time
tail -f your_dir/TuriX-CUA/.turix_tmp/logging.log

# 5. Check current step count
ls your_dir/TuriX-CUA/examples/.turix_tmp/brain_llm_interactions.log_brain_*.txt | wc -l
```
