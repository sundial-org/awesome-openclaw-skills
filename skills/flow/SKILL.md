---
name: flow
description: Intelligent skill orchestrator that compiles natural language requests into secure, reusable workflows
---

---
summary: Intelligent skill orchestrator that compiles natural language requests into secure, reusable workflows
tags:
  - automation
  - workflow
  - nlp
  - security
  - orchestration
  - skill-builder
  - clawdbot
  - mcp
---

# Flow

Intelligent Skill Orchestrator for Clawdbot/MCP - compose natural language requests into secure, reusable FLOW skills.

## Capabilities

- Parse natural language build requests
- Search skill registry for reusable components
- Security scan all skills before composition
- Compile multiple skills into unified FLOW
- Track skill usage for intelligent reuse
- Dependency resolution with topological sorting

## How It Works

1. **Natural Language Input**: Describe what you want to build
2. **Intent Parsing**: Extract capabilities, tags, and execution steps
3. **Registry Search**: Find existing skills that match requirements
4. **Security Scan**: Check all components for malicious patterns
5. **Composition**: Merge skills into single executable FLOW
6. **Registration**: Save new FLOW for future reuse

## Usage

### Interactive Mode
```
python flow.py
Flow> Build a web scraper that extracts prices and saves to CSV
```

### CLI Mode
```bash
python flow.py "Create an automation that monitors API endpoints"
```

### List Skills
```bash
python flow.py --list
```

## Security Features

- Code execution detection (eval, exec)
- Data exfiltration pattern matching
- Crypto mining indicator scanning
- System modification attempt detection
- AST-based code analysis
- Obfuscation detection

## Architecture

- `flow.py` - Main orchestrator
- `natural_language_parser.py` - NLP for user intent
- `skill_registry.py` - Reusable skill database
- `skill_scanner_integration.py` - Security scanning
- `skill_composer.py` - Compiles skills into FLOW

## Requirements

- Python 3.8+
- No external dependencies for core functionality

## Author

@bvinci1-design
