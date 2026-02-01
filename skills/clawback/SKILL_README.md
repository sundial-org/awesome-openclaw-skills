# ClawBack OpenClaw Skill

**Congressional Stock Trade Mirroring with Automated Execution**

This is the OpenClaw skill version of the ClawBack congressional trading system. For the full system documentation, see the main README.md.

## Skill Installation

### From Local Directory
```bash
# Install from local directory
clawhub install ./clawback

# Or manually copy to skills directory
cp -r . ~/.openclaw/skills/clawback
```

### From ClawHub (when published)
```bash
clawhub install clawback
```

## Quick Start for OpenClaw Users

1. **Install the skill** (see above)
2. **Run setup**:
   ```bash
   cd ~/.openclaw/skills/clawback
   ./setup.sh
   ```
3. **Configure credentials** in `.env` file
4. **Test the system**:
   ```bash
   cd ~/.openclaw/skills/clawback
   python3 src/main.py interactive
   ```

## Skill Structure

```
clawback/
├── SKILL.md              # OpenClaw skill definition (this file)
├── package.json          # Skill metadata
├── setup.sh             # Installation script
├── SKILL_README.md      # Skill-specific documentation (this file)
├── README.md            # Full system documentation
├── requirements.txt     # Python dependencies
├── src/                 # Python source code
├── config/              # Configuration files
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── docs/                # Documentation
└── venv/                # Python virtual environment (created by setup.sh)
```

## Skill Metadata

The skill includes proper OpenClaw metadata:

- **Name**: clawback
- **Version**: 1.0.0
- **Category**: finance
- **Emoji**: 📊
- **Required packages**: pdfplumber, selenium, yfinance, schedule, python-dotenv
- **Required config**: ETRADE_API_KEY, ETRADE_API_SECRET, ETRADE_ACCOUNT_ID

## Usage Examples

When the skill is installed, OpenClaw will automatically load it when users ask about:
- Congressional stock trades
- Automated trading systems
- E*TRADE integration
- Risk management for trading
- Stock market automation

## Integration with OpenClaw

The skill provides:
1. **Automated setup** via `setup.sh`
2. **Environment-based configuration** (no hardcoded credentials)
3. **Virtual environment isolation** for dependencies
4. **Comprehensive testing** suite
5. **Documentation** for both users and developers

## Development

To update the skill:

1. Make changes to the system
2. Update version in `package.json` and `SKILL.md`
3. Test with: `./setup.sh`
4. Publish to ClawHub (when ready):
   ```bash
   clawhub publish . --slug clawback --version 1.0.0
   ```

## Support

- **System documentation**: See main README.md
- **Quick start**: QUICK_START.md
- **Congressional data**: CONGRESSIONAL_DATA.md
- **System overview**: AUTOMATED_SYSTEM_SUMMARY.md

## License

MIT License - See LICENSE file

---

*Built for the OpenClaw community*