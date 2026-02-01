# MCP Server for Standard Claude Desktop

> **This is a Clawdbot skill.** If you want to use Garmin data with standard Claude Desktop, use the dedicated MCP server instead.

## 📦 Dedicated MCP Server Repository

We've created a separate, purpose-built MCP server for Claude Desktop users:

### **[garmin-health-mcp-server](https://github.com/eversonl/garmin-health-mcp-server)**

This is a standalone Node.js-based MCP server optimized for Claude Desktop, with:
- ✅ Easy `npm install` setup
- ✅ Built-in authentication helper
- ✅ Test suite for verification
- ✅ Comprehensive documentation
- ✅ Full troubleshooting guide

## Quick Start (MCP Server)

```bash
# Clone the MCP server (separate repo)
git clone https://github.com/eversonl/garmin-health-mcp-server.git
cd garmin-health-mcp-server

# Install and setup
npm install
pip3 install garminconnect fitparse gpxpy
cp .env.example .env
# Edit .env with your credentials

# Authenticate
npm run auth

# Configure Claude Desktop (see full guide)
# Add to claude_desktop_config.json
```

**[📖 Full Installation Guide →](https://github.com/eversonl/garmin-health-mcp-server#readme)**

---

## This Skill (Clawdbot)

If you're using **Clawdbot**, you're in the right place! This skill provides:
- Automated health monitoring
- Scheduled reports and summaries  
- Proactive workout notifications
- Integration with other Clawdbot skills

**[📖 Clawdbot Skill Setup →](../SKILL.md)**

---

## Using Both?

You can use both the Clawdbot skill and the MCP server simultaneously! They share authentication tokens, so you only need to log in once.

**Recommended setup:**
- **Clawdbot**: Morning health summaries, weekly reports, automated tracking
- **Claude Desktop**: Quick ad-hoc queries during the day

Authentication tokens are shared at `~/.clawdbot/garmin-tokens.json` (or `~/.garmin-tokens.json`).
