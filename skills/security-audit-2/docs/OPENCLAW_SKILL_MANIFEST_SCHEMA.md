# OpenClaw Skill Manifest (draft)

Hostile audit requires a machine-readable manifest at repo root:

- `openclaw-skill.json`

## Minimal example

```json
{
  "schemaVersion": 1,
  "name": "security-audit",
  "version": "0.1.0",
  "intent": "Audit skills and codebases for secrets, prompt injection, and capability abuse before enabling.",
  "permissions": {
    "network": {"required": false, "domains": []},
    "filesystem": {
      "read": ["<repo>/**"],
      "write": ["<sandbox>/**"],
      "deny": ["/etc/**", "/home/**", "/mnt/**"]
    },
    "subprocess": {"required": true, "allow": ["trufflehog", "semgrep", "jq", "docker"]}
  },
  "expectedWrites": ["<sandbox>/**"],
  "dependencies": {
    "ecosystems": ["python", "npm"],
    "lockfilesRequired": true,
    "banInstallHooks": true
  }
}
```

## Notes
- This is intentionally strict and may evolve.
- The hostile audit currently treats missing manifest as FAIL.
