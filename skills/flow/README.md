# Flow - Intelligent Skill Orchestrator

Flow allows users to express build ideas or tasks in natural language, finds the best existing skills, scans them for security, and compiles them into a single executable FLOW skill.

## Features

- **Natural Language Processing**: Describe what you want to build in plain English
- **Skill Registry**: Reusable object architecture - never reinvent the wheel
- **Security Scanning**: Integrated security checks for malware, spyware, and malicious code
- **Smart Composition**: Automatically combines skills into unified workflows
- **Dependency Resolution**: Handles skill dependencies with topological sorting

## Installation

### Prerequisites

- Python 3.8+
- pip

### Clone the Repository

```bash
git clone https://github.com/bvinci1-design/flow.git
cd flow
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## How to Run

### Web UI (Streamlit Interface)

For the most user-friendly experience, use the Streamlit web interface:

```bash
streamlit run streamlit_ui.py
```

This will open a web interface in your browser with:
- 🏠 **Build Flow**: Enter natural language requests and watch the 5-step process
- 📚 **Skill Registry**: Browse, search, and filter available skills
- ℹ️ **About**: Learn more about Flow's architecture and features

The web UI provides real-time feedback on:
- Intent parsing results
- Skill matching scores
- Security scan status (✅ Safe / ⚠️ Warning / ❌ Unsafe)
- Composition progress

### In Clawdbot

1. Import the Flow skill into Clawdbot
2. Use natural language to describe what you want:
   ```
   Flow> Build a web scraper that extracts product prices and saves to CSV
   ```
3. Flow will:
   - Parse your request
   - Search for existing skills
   - Security scan all components
   - Compose a unified FLOW skill

### On Any Device (CLI)

#### Interactive Mode
```bash
python flow.py
```

Then type your requests:
```
Flow> Create an automation that monitors a webpage for changes
Flow> quit
```

#### Single Command
```bash
python flow.py "Build a data pipeline that fetches API data and stores in database"
```

#### List Available Skills
```bash
python flow.py --list
```

#### Get Skill Info
```bash
python flow.py --info skill_name
```

## Architecture

```
flow/
├── flow.py                      # Main orchestrator
├── natural_language_parser.py   # NLP for user intent
├── skill_registry.py            # Reusable skill database
├── skill_scanner_integration.py # Security scanning
├── skill_composer.py            # Compiles skills into FLOW
├── README.md
└── SKILL.md                     # ClawdHub skill definition
```

## How It Works

1. **Parse Request**: NLP parser extracts intent, capabilities, and steps
2. **Search Registry**: Finds existing skills matching requirements
3. **Security Scan**: Checks all skills for malicious patterns
4. **Compose**: Merges skills into single executable FLOW
5. **Register**: Saves new FLOW for future reuse

## Security Features

Flow includes comprehensive security scanning:

- Code execution detection (eval, exec)
- Data exfiltration patterns
- Crypto mining indicators
- System modification attempts
- Obfuscation detection
- AST-based analysis

## Configuration

Create a `flow_config.json`:

```json
{
  "skills_directory": "./skills",
  "output_directory": "./flows",
  "registry_path": "./skill_registry.json",
  "security_level": "standard",
  "auto_update_registry": true
}
```

## Examples

```python
from flow import Flow

# Create Flow instance
flow = Flow()

# Process a natural language request
result = flow.process(
    "Build a skill that monitors YouTube channels and sends notifications"
)

print(f"Created: {result.flow_name}")
print(f"Skills used: {result.skills_used}")
print(f"Security: {result.security_status}")
```

## License

MIT

## Author

@bvinci1-design
