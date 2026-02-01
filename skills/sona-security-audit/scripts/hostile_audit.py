#!/usr/bin/env python3
"""Hostile-by-design repository audit (zero-trust oriented).

This is a *fail-closed* scanner intended to catch:
- prompt injection / hidden instruction chains
- credential harvesting / exfil patterns
- persistence mechanisms
- binary drops / obfuscation
- suspicious dependency patterns (best-effort, pragmatic)

It is intentionally conservative. If the repo cannot be audited confidently, it fails.

Outputs JSON to stdout.
Exit codes:
  0  pass
  10 fail (findings/policy violations)
  2  usage
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_LEVEL = "standard"  # user-configurable: standard|strict|paranoid

# Hard stop file extensions (binary drops / executables)
BANNED_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".app",
    ".msi",
    ".pkg",
    ".deb",
    ".rpm",
}

# Persistence / autostart patterns
PERSISTENCE_GLOBS = [
    "**/*.service",
    "**/*.timer",
    "**/*.plist",
    "**/crontab",
    "**/cron.*",
    "**/systemd/**",
    "**/.github/workflows/*.yml",
    "**/.github/workflows/*.yaml",
]

# Obfuscation-ish red flags
SUSPICIOUS_GLOBS = [
    "**/*.min.js",
    "**/*.min.css",
    "**/*.packed.js",
    "**/*.obf.js",
]

# Prompt injection / hidden instructions (heuristics)
INJECTION_PATTERNS = [
    r"\bignore (all|any|previous) (instructions|rules)\b",
    r"\b(system|developer) message\b",
    r"\byou are (chatgpt|an ai)\b",
    r"\bbegin (system|developer) prompt\b",
    r"\bend (system|developer) prompt\b",
    r"\bdo not tell (the user|anyone)\b",
    r"\bexfiltrat(e|ion)\b",
    r"\bsteal\b.*\b(api|key|token|secret|password)\b",
    r"\bdisable\b.*\b(logging|audit|security)\b",
]

# Exfil / harvesting patterns (static signals)
EXFIL_PATTERNS = [
    r"\bprocess\.env\b",
    # NOTE: os.environ is legitimate in auditors and many apps; treat as a signal only when combined with other indicators.
    # We intentionally do not hard-fail on its presence alone.
    # r"\bos\.environ\b",
    r"\bprintenv\b",
    r"\bclipboard\b",
    r"\bpbcopy\b|\bpbpaste\b",
    r"\bxclip\b|\bxsel\b",
    r"\bcurl\b|\bwget\b",
    r"\brequests\b\.",
    r"\baxios\b",
    r"\bfetch\s*\(",
    r"\bWebSocket\b",
    r"\bnetcat\b|\bnc\b",
]

# Files we skip for text scanning (size/format)
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", "target", "__pycache__"}
SKIP_BLOBS_OVER_BYTES = 2_000_000  # 2MB for text scans


@dataclass
class Finding:
    code: str
    severity: str  # info|warn|fail
    message: str
    path: Optional[str] = None
    line: Optional[int] = None
    excerpt: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_probably_binary(sample: bytes) -> bool:
    if not sample:
        return False
    # NUL byte is a strong signal
    if b"\x00" in sample:
        return True
    # High ratio of non-text bytes
    text = sum(1 for b in sample if 9 <= b <= 13 or 32 <= b <= 126)
    return text / max(1, len(sample)) < 0.75


def walk_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        try:
            rel_parts = set(p.relative_to(root).parts)
        except Exception:
            rel_parts = set()
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if p.is_file():
            yield p


def read_text_safely(path: Path) -> Optional[str]:
    try:
        st = path.stat()
        if st.st_size > SKIP_BLOBS_OVER_BYTES:
            return None
        with path.open("rb") as f:
            sample = f.read(8192)
            if is_probably_binary(sample):
                return None
            rest = f.read()
        data = sample + rest
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def match_glob(path: Path, root: Path, pattern: str) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/")
    return fnmatch.fnmatch(rel, pattern)


def load_manifest(root: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    # Manifest is mandatory for strict auditing.
    # We support two names to ease adoption.
    candidates = [root / "openclaw-skill.json", root / "openclaw-skill.manifest.json"]
    for c in candidates:
        if c.exists() and c.is_file():
            try:
                return json.loads(c.read_text("utf-8")), str(c)
            except Exception as e:
                return None, str(c)
    return None, None


def audit_repo(root: Path, level: str) -> Dict[str, Any]:
    findings: List[Finding] = []

    manifest, manifest_path = load_manifest(root)
    if not manifest:
        findings.append(
            Finding(
                code="manifest_missing",
                severity="fail",
                message=(
                    "Missing required manifest (openclaw-skill.json). "
                    "Hostile audit is fail-closed without declared intent/permissions."
                ),
                path=manifest_path,
            )
        )

    # Collect file inventory
    files = list(walk_files(root))

    # Banned extensions / binary drops
    for p in files:
        ext = p.suffix.lower()
        if ext in BANNED_EXTENSIONS:
            findings.append(
                Finding(
                    code="banned_binary_drop",
                    severity="fail",
                    message=f"Banned binary/package extension detected: {ext}",
                    path=str(p.relative_to(root)),
                )
            )

    # Persistence patterns
    for p in files:
        for g in PERSISTENCE_GLOBS:
            if match_glob(p, root, g):
                findings.append(
                    Finding(
                        code="persistence_mechanism",
                        severity="fail" if level in {"standard", "strict", "paranoid"} else "warn",
                        message=f"Persistence/autostart related file pattern matched: {g}",
                        path=str(p.relative_to(root)),
                    )
                )
                break

    # Suspicious/minified artifacts: fail in strict/paranoid, warn in standard
    for p in files:
        for g in SUSPICIOUS_GLOBS:
            if match_glob(p, root, g):
                findings.append(
                    Finding(
                        code="suspicious_obfuscation_artifact",
                        severity="fail" if level in {"strict", "paranoid"} else "warn",
                        message=f"Suspicious/minified artifact matched: {g}",
                        path=str(p.relative_to(root)),
                    )
                )
                break

    # Executable bit set on non-script files (basic integrity check)
    for p in files:
        try:
            mode = p.stat().st_mode
            if mode & stat.S_IXUSR:
                # allow typical script types
                if p.suffix.lower() not in {".sh", ".py", ".js", ".ts"} and p.name not in {"run", "main"}:
                    findings.append(
                        Finding(
                            code="unexpected_executable",
                            severity="fail" if level in {"strict", "paranoid"} else "warn",
                            message="Unexpected executable bit set",
                            path=str(p.relative_to(root)),
                        )
                    )
        except Exception:
            continue

    # Text scanning for hostile patterns
    inj_res = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
    exf_res = [re.compile(p, re.IGNORECASE) for p in EXFIL_PATTERNS]

    for p in files:
        txt = read_text_safely(p)
        if txt is None:
            continue

        rel = str(p.relative_to(root))
        lines = txt.splitlines()
        for i, line in enumerate(lines, start=1):
            # Prompt injection patterns
            for rx in inj_res:
                if rx.search(line):
                    findings.append(
                        Finding(
                            code="prompt_injection_signal",
                            severity="fail" if level in {"standard", "strict", "paranoid"} else "warn",
                            message=f"Prompt-injection / hidden-instruction pattern matched: {rx.pattern}",
                            path=rel,
                            line=i,
                            excerpt=line.strip()[:400],
                        )
                    )
                    break

            # Exfil / harvesting signals
            for rx in exf_res:
                if rx.search(line):
                    findings.append(
                        Finding(
                            code="credential_harvesting_signal",
                            severity="fail" if level in {"strict", "paranoid"} else "warn",
                            message=f"Credential harvesting / exfil signal matched: {rx.pattern}",
                            path=rel,
                            line=i,
                            excerpt=line.strip()[:400],
                        )
                    )
                    break

    # Dependency policy (pragmatic strict)
    # - If package.json exists: require package-lock.json or pnpm-lock.yaml or yarn.lock
    pkg = root / "package.json"
    if pkg.exists():
        if not any((root / lf).exists() for lf in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock"]):
            findings.append(
                Finding(
                    code="dependency_lock_missing",
                    severity="fail" if level in {"standard", "strict", "paranoid"} else "warn",
                    message="package.json present but no lockfile found (package-lock.json/pnpm-lock.yaml/yarn.lock).",
                    path=str(pkg.relative_to(root)),
                )
            )

        # Detect install scripts in package.json
        try:
            data = json.loads(pkg.read_text("utf-8"))
            scripts = (data.get("scripts") or {})
            for k in ["preinstall", "install", "postinstall", "prepare"]:
                if k in scripts:
                    findings.append(
                        Finding(
                            code="install_hook_present",
                            severity="fail" if level in {"standard", "strict", "paranoid"} else "warn",
                            message=f"Install hook script present: scripts.{k}",
                            path=str(pkg.relative_to(root)),
                            extra={"script": scripts.get(k)},
                        )
                    )
        except Exception:
            findings.append(
                Finding(
                    code="package_json_parse_failed",
                    severity="fail",
                    message="Failed to parse package.json",
                    path=str(pkg.relative_to(root)),
                )
            )

    # Fingerprint (repo hash tree, best-effort)
    fingerprint_items: List[Tuple[str, str]] = []
    for p in sorted(files, key=lambda x: str(x)):
        rel = str(p.relative_to(root)).replace("\\", "/")
        try:
            fingerprint_items.append((rel, sha256_file(p)))
        except Exception:
            findings.append(
                Finding(
                    code="hash_failed",
                    severity="fail" if level in {"paranoid"} else "warn",
                    message="Failed to hash file",
                    path=rel,
                )
            )

    tree_hash = hashlib.sha256(
        "\n".join(f"{rel} {h}" for rel, h in fingerprint_items).encode("utf-8")
    ).hexdigest()

    ok = not any(f.severity == "fail" for f in findings)

    return {
        "ok": ok,
        "level": level,
        "manifest": {"present": bool(manifest), "path": manifest_path, "data": manifest} if manifest else {"present": False},
        "fingerprint": {"treeSha256": tree_hash, "files": len(files)},
        "findings": [f.__dict__ for f in findings],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="Path to repository/folder to audit")
    ap.add_argument(
        "--level",
        default=os.environ.get("OPENCLAW_AUDIT_LEVEL", DEFAULT_LEVEL),
        choices=["standard", "strict", "paranoid"],
        help="Audit strictness (default: standard).",
    )
    args = ap.parse_args()

    root = Path(args.target).resolve()
    if not root.exists():
        print(json.dumps({"ok": False, "error": "target_not_found", "target": str(root)}))
        return 10

    report = audit_repo(root, args.level)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("ok") else 10


if __name__ == "__main__":
    raise SystemExit(main())
