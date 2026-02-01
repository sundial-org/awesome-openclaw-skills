---
name: gopass
description: "Store, retrieve, list, and manage secrets using gopass (the team password manager). Use when the user asks to save credentials, look up passwords, generate secrets, manage password entries, or interact with a gopass password store. Covers CRUD operations, secret generation, TOTP, recipients, mounting stores, and clipboard operations."
---

# gopass Skill

gopass is a CLI password manager for teams, built on GPG and Git.

## Prerequisites

- `gopass` binary installed
- GPG key available (gopass uses GPG for encryption)
- Store initialized (`gopass init` or `gopass setup`)

## Common Operations

### List secrets
```bash
gopass ls
gopass ls -f          # flat list
```

### Show a secret
```bash
gopass show path/to/secret           # full entry (password + metadata)
gopass show -o path/to/secret        # password only
gopass show -c path/to/secret        # copy to clipboard
gopass show path/to/secret key       # show specific field
```

### Create / Update
```bash
gopass insert path/to/secret         # interactive
gopass edit path/to/secret           # open in $EDITOR
echo "mypassword" | gopass insert -f path/to/secret   # non-interactive
```

Add key-value metadata below the first line (password):
```
mysecretpassword
username: erdGecrawl
url: https://github.com
notes: Created 2026-01-31
```

### Generate passwords
```bash
gopass generate path/to/secret 24           # 24-char password
gopass generate -s path/to/secret 32        # with symbols
gopass generate --xkcd path/to/secret 4     # passphrase (4 words)
```

### Delete
```bash
gopass rm path/to/secret
gopass rm -r path/to/folder          # recursive
```

### Move / Copy
```bash
gopass mv old/path new/path
gopass cp source/path dest/path
```

### Search
```bash
gopass find github                   # search entry names
gopass grep "username"               # search entry contents
```

## Store Management

### Initialize
```bash
gopass setup                         # guided first-time setup
gopass init <gpg-id>                 # init with specific GPG key
```

### Mount sub-stores
```bash
gopass mounts add work /path/to/work-store
gopass mounts remove work
gopass mounts                        # list mounts
```

### Sync (git push/pull)
```bash
gopass sync
```

### Recipients (team access)
```bash
gopass recipients                    # list
gopass recipients add <gpg-id>
gopass recipients remove <gpg-id>
```

## TOTP
```bash
gopass otp path/to/secret            # show current TOTP code
```
Store TOTP URI as `totp: otpauth://totp/...` in the entry body.

## Non-interactive Tips

- Use `echo "pw" | gopass insert -f path` for scripted inserts
- Use `gopass show -o path` for machine-readable password-only output
- Use `gopass show -f path` to suppress warnings
- Set `GOPASS_NO_NOTIFY=true` to suppress desktop notifications
- Use `gopass --yes` to auto-confirm prompts
