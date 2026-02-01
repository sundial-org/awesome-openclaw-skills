# Changelog

All notable changes to the Skill Auditor will be documented here.

Follow the project on GitHub for update notifications. Updates are manual — download, scan, replace.

## [1.0.0] - 2026-01-31

### Added
- Initial release
- Static analysis scanner for local directories and GitHub URLs
- Visual threat report with threat gauge, accuracy score, publisher info
- Prompt injection detection
- Data exfiltration detection (file access, network, env vars, credentials)
- Obfuscation detection (base64, hex, string concat, dynamic imports)
- Shell/command execution detection
- Persistence mechanism detection
- Integrity verification against source (SHA-256)
- False positive reference guide
- License file URL grouping (reduces noise, preserves prompt injection detection)
- Known limitations documented
- 🔍 Details / ✅ Install / ❌ Pass workflow after every scan
