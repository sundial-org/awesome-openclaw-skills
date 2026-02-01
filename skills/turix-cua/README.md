# 🐾 TuriX-Mac Clawdbot Skill

This skill allows Clawdbot to control your macOS desktop visually by integrating with the **TuriX Computer Use Agent (CUA)**.

## 🚀 Overview
TuriX acts as the "eyes and hands" for Clawdbot. While Clawdbot is great at terminal and file operations, TuriX allows it to:
- Open and navigate GUI applications (Spotify, Chrome, System Settings, etc.)
- Click buttons and interact with complex UIs.
- Perform multi-step visual workflows.

It helps clawdbot complete the task automatically, makes clawdbot the real digital labour!

## 📦 Installation & Setup

### 1. TuriX Core Setup
Set up TuriX following the official repository:
`https://github.com/TurixAI/TuriX-CUA`

```bash
conda activate your_env
pip install -r requirements.txt
```

### 2. Mandatory Permissions
macOS security requires explicit permission for background processes to capture the screen.

1. **Screen Recording:**
   - Go to **System Settings > Privacy & Security > Screen Recording**.
   - Add **Terminal**, **VS COde**.
   - Add `/your_install_dir/bin/node` (The binary running Clawdbot, example:`/opt/homebrew/bin/node`).
   - Ensure the toggle is **ON**.
2. **Accessibility:**
   - Go to **System Settings > Privacy & Security > Accessibility**.
   - Add **Terminal**, **VS Code**, **Node**, and `/usr/bin/python3`.

### 3. Skill Configuration
The skill uses a helper script to bridge Clawdbot and TuriX.
- **Helper Script:** `scripts/run_turix.sh`
- **Skill Definition:** `SKILL.md`

## 🛠 Usage

In your 
```bash
your_dir/clawd/skills/local/turix-mac
```
put the files in this structure:
```
your_dir/clawd/skills/local/turix-mac/
├── README.md
├── SKILL.md
└── scripts/
    └── run_turix.sh
```

You can trigger this skill by asking Clawdbot to perform visual tasks:
> "Use Safari to go to turix.ai, and sign up with Google account."

Clawdbot will execute the following in the background:
```bash
your_dir/clawd/skills/local/turix-mac/scripts/run_turix.sh
```

## 🔍 Troubleshooting
- **`AttributeError: 'NoneType' object has no attribute 'save'`**: This means the screen capture failed. Usually fixed by adding `node` to Screen Recording permissions and running `clawdbot gateway restart`.
- **`screencapture: command not found`**: The script includes a `PATH` export to fix this, but ensure `/usr/sbin` is accessible.
- **Permissions not sticking**: Try removing and re-adding the application/binary in System Settings.
