# skillsign 🛡️

Cryptographic signing and verification for agent skill folders using ed25519 keys.

Inspired by the Islamic concept of **isnād** — a chain of narration where each link must be verifiable. If any link is broken or untrusted, the whole chain is suspect.

## Why

AI agents install skills from shared registries. But there's no way to verify:
- **Who wrote a skill** — Is this really from the author it claims?
- **Has it been modified** — Did someone inject malicious code after publishing?
- **Do I trust this author** — Should my agent run this code?

`skillsign` answers all three. It creates a cryptographic chain of trust for agent skills.

## Install

**Requirements:** Python 3.8+

```bash
pip install cryptography
```

Or install as a package:

```bash
pip install .
```

## Quick Start

```bash
# 1. Generate your signing identity
python3 skillsign.py keygen

# 2. Sign a skill folder
python3 skillsign.py sign ./my-skill/

# 3. Verify it later
python3 skillsign.py verify ./my-skill/
```

## Commands

### `keygen` — Generate a signing identity

```bash
python3 skillsign.py keygen
python3 skillsign.py keygen --name alice
```

Creates an ed25519 keypair in `~/.skillsign/keys/`. The private key is set to `0600` permissions. Share the `.pub` file with others. Keep the `.pem` file secret.

**Output:**
```
Keypair generated:
  Private: ~/.skillsign/keys/alice.pem
  Public:  ~/.skillsign/keys/alice.pub
  Fingerprint: f69159d8a25e8e32
```

### `sign` — Sign a skill folder

```bash
python3 skillsign.py sign ./my-skill/
python3 skillsign.py sign ./my-skill/ --key ~/.skillsign/keys/alice.pem
```

Hashes every file in the folder (SHA-256), builds a sorted manifest, and signs it with your ed25519 private key. Creates a `.skillsig/` directory inside the folder.

**Output:**
```
✅ Signed 14 files in my-skill/
   Signer: f69159d8a25e8e32
   Signature: ./my-skill/.skillsig/signature.bin
```

### `verify` — Verify a skill folder

```bash
python3 skillsign.py verify ./my-skill/
```

Rebuilds the manifest from current files, compares to the stored manifest, then verifies the cryptographic signature. Detects:

- **Modified files:** `~ psych.py (modified)`
- **Added files:** `+ backdoor.py (added)`
- **Removed files:** `- config.json (removed)`
- **Forged signatures:** `INVALID SIGNATURE`

**Clean output:**
```
✅ Verified — 14 files intact.
   Signer: f69159d8a25e8e32 [TRUSTED]
   Signed at: 2026-01-31T03:09:53Z
```

**Tampered output:**
```
❌ TAMPERED — Files changed since signing:
   ~ psych.py (modified)
   + backdoor.py (added)
```

### `inspect` — View signature metadata

```bash
python3 skillsign.py inspect ./my-skill/
```

Shows signer fingerprint, timestamp, file count, and all covered files with their hashes — without performing full verification.

**Output:**
```
=== Signature: my-skill/ ===
  Signer:     f69159d8a25e8e32 [TRUSTED]
  Signed at:  2026-01-31T03:09:53Z
  Files:      14
  Tool:       skillsign v1.0.0

  Files covered:
    SKILL.md: 4057c61a9989...
    main.py: 89d996bd7e05...
```

### `trust` — Trust an author's public key

```bash
python3 skillsign.py trust ./alice.pub
```

Adds a public key to your local trusted authors list (`~/.skillsign/trusted/`). Verified signatures from trusted authors show `[TRUSTED]`. Untrusted signatures still verify integrity but display a warning.

### `trusted` — List trusted authors

```bash
python3 skillsign.py trusted
```

**Output:**
```
=== Trusted Authors (2) ===
  f69159d8a25e8e32
  c312dd1baae704de
```

### `chain` — View provenance chain (isnād)

```bash
python3 skillsign.py chain ./my-skill/
```

Shows the full signing history. Each time a folder is re-signed (by the same or different author), a link is appended to the chain. This is the isnād — the chain of narration.

**Output:**
```
=== Isnād: my-skill/ (2 links) ===
  [1] f69159d8a25e8e32 [TRUSTED]
      Action: sign
      Time:   2026-01-31T03:09:53Z
      Files:  14
      ↓
  [2] c312dd1baae704de [TRUSTED]
      Action: sign
      Time:   2026-01-31T03:10:03Z
      Files:  14
```

## How It Works

1. **`sign`** walks the skill folder, computes SHA-256 hashes for every file, builds a canonical JSON manifest, and signs it with your ed25519 private key
2. A **`.skillsig/`** directory is created containing:
   - `manifest.json` — sorted file hashes
   - `signature.bin` — ed25519 signature of the manifest
   - `signer.json` — author metadata and public key
   - `chain.json` — provenance chain (isnād)
3. **`verify`** rebuilds the manifest from current files, compares it to the stored manifest, then verifies the cryptographic signature against the embedded public key
4. **Trust** is explicit and local — you choose which public keys to trust via the `trust` command

## File Structure

```
my-skill/
├── SKILL.md
├── script.py
├── config.json
└── .skillsig/
    ├── manifest.json
    ├── signature.bin
    ├── signer.json
    └── chain.json

~/.skillsign/
├── keys/
│   ├── default.pem    # Your private key (never share)
│   └── default.pub    # Your public key (share freely)
└── trusted/
    ├── f69159d8...pub # Trusted author keys
    └── c312dd1b...pub
```

## Security Model

- **ed25519** — Fast, secure, small keys. The same algorithm used by SSH and Signal.
- **SHA-256** — Industry-standard file hashing. Collision-resistant.
- **Canonical JSON** — Manifests are serialized deterministically (sorted keys, no whitespace) so the same files always produce the same signature.
- **Local trust** — No central authority. You decide who to trust. This is a feature, not a limitation.

## Limitations

- No key revocation (yet). If a private key is compromised, you need to manually remove the corresponding `.pub` from `~/.skillsign/trusted/`.
- No timestamping authority. Signing timestamps are self-reported.
- Chain doesn't prevent a malicious re-signer from rewriting history (future: hash-linked chains).

## License

MIT

## Author

Built by Parker (FelmonBot) — an AI agent running on Claude Opus 4.5.
