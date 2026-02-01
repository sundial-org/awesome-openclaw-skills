# Idea Exploration Skill

Launch autonomous Claude Code sessions to explore business ideas in depth.

## Installation

1. Copy scripts to your scripts directory:
   ```bash
   cp scripts/*.sh ~/clawd/scripts/
   chmod +x ~/clawd/scripts/explore-idea.sh
   chmod +x ~/clawd/scripts/notify-research-complete.sh
   ```

2. Copy template:
   ```bash
   cp templates/idea-exploration-prompt.md ~/clawd/templates/
   ```

3. Install the skill:
   ```bash
   mkdir -p ~/clawdis/skills/idea-exploration
   cp SKILL.md ~/clawdis/skills/idea-exploration/
   ```

4. Add to your AGENTS.md:
   ```markdown
   **When user says "Idea: [description]":**
   1. Extract the idea description
   2. Execute: `CLAWD_SESSION_KEY="main" ~/clawd/scripts/explore-idea.sh "[idea]"`
   3. Confirm: "Idea exploration started. You'll be notified when complete."
   ```

## Requirements

- `claude` CLI (Claude Code)
- `tmux`
- `telegram` CLI (supertelegram) - for notifications
- Clawdbot (optional, for cron notifications)

## Usage

Say: `Idea: [your idea description]`

The assistant will:
1. Spin up a Claude Code session in tmux
2. Research and analyze the idea
3. Save results to `~/clawd/ideas/<slug>/research.md`
4. Send file to Telegram Saved Messages
5. Notify you when complete

## Customization

Edit `templates/idea-exploration-prompt.md` to change the analysis framework.

Edit `scripts/explore-idea.sh` to change output paths or behavior.
