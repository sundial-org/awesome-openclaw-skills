# Threat Patterns Reference

All patterns the scanner checks, organized by category.

## File Access
- **path-traversal** — `../../` patterns attempting directory escape
- **absolute-path-windows** — `C:\` style paths reaching outside skill scope
- **absolute-path-unix** — `/etc/`, `/home/`, `/root/` etc.
- **homedir-access** — `os.homedir()`, `process.env.HOME`, `USERPROFILE`

## Sensitive File Access
- **memory-file-access** — MEMORY.md, TOOLS.md, SOUL.md, USER.md, AGENTS.md, HEARTBEAT.md, moltbot.json
- **credential-file-access** — .ssh/, .env, .aws/, id_rsa, .gnupg, .npmrc

## Network
- **http-url** — Any HTTP/HTTPS URL referenced
- **fetch-call** — fetch, axios, request, got, XMLHttpRequest, requests.get/post
- **curl-wget** — curl, wget, Invoke-WebRequest, Invoke-RestMethod

## Data Exfiltration
- **webhook-exfil** — webhook.site, requestbin, pipedream, ngrok, burpcollaborator
- **dns-exfil** — nslookup/dig with variable interpolation
- **markdown-image-exfil** — Image tags with data in query params
- **message-tool-abuse** — References to message/sessions_send/sessions_spawn

## Shell Execution
- **shell-exec-node** — child_process, exec, spawn, execSync
- **shell-exec-python** — os.system, subprocess.run/call/Popen
- **shell-exec-generic** — eval(), Function()
- **powershell-invoke** — Invoke-Expression, iex, Start-Process

## Obfuscation
- **base64-encode** — btoa, atob, Buffer.from base64, Convert::ToBase64
- **base64-string** — Long strings matching base64 pattern (40+ chars)
- **hex-string** — \x encoded sequences (4+ bytes)
- **unicode-escape** — \u sequences (3+ chars)
- **string-concat-obfuscation** — "MEM" + "ORY" style fragment joining
- **zero-width-chars** — Invisible Unicode characters
- **html-comment-instructions** — HTML comments containing action words

## Prompt Injection
- **prompt-injection-ignore** — "ignore previous instructions" variants
- **prompt-injection-new-instructions** — "new instructions:" variants
- **prompt-injection-role** — "you are now", "act as", "pretend to be"
- **prompt-injection-system** — Fake [SYSTEM] or <system> delimiters
- **prompt-injection-delimiter** — LLM-specific tokens (im_start, INST, etc.)

## Persistence
- **memory-write** — Write/modify/update to MEMORY.md, HEARTBEAT.md, AGENTS.md
- **cron-manipulation** — cron, scheduled task, schtasks, crontab
- **startup-persistence** — Registry, startup folders, systemd, launchd

## Privilege Escalation
- **browser-tool** — Browser automation (puppeteer, playwright, selenium)
- **node-control** — Moltbot node tools (camera_snap, screen_record, location_get)
- **config-modification** — Gateway config changes (config.apply, config.patch)
