# Changelog

All notable changes to mogcli will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-01-26

### Added
- `mail list` command as alias for `mail search *` (consistent with sog CLI)

## [0.3.0] - 2026-01-26

### Added
- Keychain storage option for OAuth tokens (`--storage keychain`)
- SKILL.md for Clawdbot integration
- Calendar ACL and OneNote commands
- Comprehensive unit tests with ≥85% coverage
- CHANGELOG.md

### Changed
- Aligned param names with Node version (gog compat)
- Extracted Client interface for dependency injection

### Fixed
- Node token compatibility issues

### Documentation
- Added credential storage details for all platforms
- Added `--body-file` and `--body-html` examples to SKILL.md
- Full README adapted from Node version

## [0.2.0] - 2025-01-24

### Added
- Go implementation of mogcli (rewrite from Node.js)
- PowerPoint/Slides module
- Word/Docs module
- Integration test harness (42 tests)
- Taskfile for build automation

### Changed
- Rebranded to Microsoft Ops Gadget

## [0.1.0] - 2025-01-20

### Added
- Initial Microsoft Graph CLI implementation
- Mail, Calendar, Drive, Contacts modules
- OAuth2 device flow authentication
- Basic test coverage

[Unreleased]: https://github.com/visionik/mogcli/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/visionik/mogcli/releases/tag/v0.3.1
[0.3.0]: https://github.com/visionik/mogcli/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/visionik/mogcli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/visionik/mogcli/releases/tag/v0.1.0
