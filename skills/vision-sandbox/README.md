# Vision Sandbox 🔭

Agentic Vision via Gemini's native Python code execution sandbox. 

Instead of just "guessing" what's in an image, the model can write and execute code to verify spatial relationships, count objects, or perform complex visual reasoning with pixel-level precision.

## 🚀 Primary Use Cases

Designed as a core skill for **OpenClaw**, Vision Sandbox provides visual grounding for agentic workflows:
- **Spatial Grounding:** Get precise [x, y] coordinates for UI elements.
- **Visual Calculation:** Let the model use Python to calculate values from visual data.
- **UI Auditing:** Automatically check for overlaps, alignment, and accessibility.

## 🛠 Prerequisites

- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Python 3.11 (Locked for stability)
- `GEMINI_API_KEY` set in your environment.

## 📦 Installation

### Via ClawHub (Recommended)
```bash
clawhub install vision-sandbox
```

### For Local Development
```bash
git clone https://github.com/johanesalxd/vision-sandbox.git
cd vision-sandbox
uv sync
```

## 📖 Quick Start

Run a vision task using the CLI:
```bash
uv run vision-sandbox --image "sample/how-many-fingers.png" --prompt "Count the fingers."
```

### Example: Visual Reasoning
```bash
uv run vision-sandbox --image "sample/how-many-fingers.png" --prompt "Count the number of fingers on this hand. Use code execution to identify the bounding box for each finger and return the total count."
```
**Result:** The model writes Python code to define bounding boxes for each digit, ensuring an accurate count rather than a visual guess.

![Verification Output](sample/sandbox_output_0_2.png)

## 🤖 OpenCode Integration

Vision Sandbox is a powerful companion for **OpenCode**.

### Installation for OpenCode
1. **Global Installation:**
   Copy `SKILL.md` to your global OpenCode skills directory:
   ```bash
   mkdir -p ~/.config/opencode/skills/vision-sandbox
   cp SKILL.md ~/.config/opencode/skills/vision-sandbox/SKILL.md
   ```

2. **Project Installation:**
   If you want the skill available only for a specific project:
   ```bash
   mkdir -p .opencode/skills/vision-sandbox
   cp SKILL.md .opencode/skills/vision-sandbox/SKILL.md
   ```

### Example Interaction
> "Hey OpenCode, run the `vision-sandbox` skill on this screenshot to find the exact padding of the login card, then update `styles.css` accordingly."

## 🧑‍💻 Development

### Linting & Formatting
This project uses `ruff` for code quality.
```bash
uv run ruff format .
uv run ruff check --fix .
```

### Running Tests
```bash
uv run pytest
```

## 📜 License
MIT
