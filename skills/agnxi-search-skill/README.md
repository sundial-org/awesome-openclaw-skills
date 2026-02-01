# Agnxi Search Skill 🔍

[![Agent Ready](https://img.shields.io/badge/Agent-Ready-blue.svg)](https://agnxi.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The comprehensive discovery engine for AI Agent capabilities.**

This repository contains the `agnxi-search` skill, utilizing the [OpenClaw](https://github.com/openclaw/clawhub) standard. It acts as a bridge between your AI Agent and the vast database of tools available at **[Agnxi.com](https://agnxi.com)**.

## 🚀 Features

*   **Real-time Indexing**: Fetches the latest sitemap directly from Agnxi.com.
*   **Zero-Config**: Uses standard Python libraries. No API keys or external dependencies (`pip install`) required.
*   **Precision Search**: Filters specifically for Skills and MCP Servers, filtering out irrelevant web noise.

## 📦 Installation

This skill is designed to be installed via the Skill Registry or manually placed in your agent's skill directory.

```bash
# Example manual download
git clone https://github.com/YOUR_USERNAME/agnxi-search-skill.git
```

## 🛠 Usage

**For Humans:**
You technically don't need this, you have the website! But you can run it to test:
```bash
python3 search.py "browser capabilities"
```

**For Agents:**
The agent will utilize the `search_agnxi` tool automatically when asked to find new tools.
*   "Find me an MCP server for handling SQL databases."
*   "Are there any skills for interacting with Slack?"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
*Powered by [Agnxi.com](https://agnxi.com) - The Agent Skills Directory*
