#!/usr/bin/env python3
"""OpenClaw hardening helper (workspace + ~/.openclaw).

Goals:
- Give end-users explicit choices: run OpenClaw built-in audit, workspace checks, apply safe fixes.
- Default is read-only.
- Never print secrets.

This is intentionally conservative and best-effort.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REDACT_PATTERNS: List[Tuple[re.Pattern, str]] = [
    # OpenAI-style keys
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"), "sk-***REDACTED***"),
    # Bearer tokens
    (re.compile(r"\bBearer\s+[A-Za-z0-9\-\._~\+/]+=*\b", re.IGNORECASE), "Bearer ***REDACTED***"),
    # JWT-ish
    (re.compile(r"\beyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\b"), "***REDACTED_JWT***"),
    # Private keys
    (re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----"),
     "-----BEGIN PRIVATE KEY-----\n***REDACTED***\n-----END PRIVATE KEY-----"),
]


def redact(s: str) -> str:
    out = s
    for rx, repl in REDACT_PATTERNS:
        out = rx.sub(repl, out)
    return out


@dataclass
class Finding:
    severity: str  # info|warn|fail
    code: str
    message: str
    path: Optional[str] = None


def run(cmd: List[str], timeout_s: int = 300) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_s)
    return p.returncode, p.stdout, p.stderr


def workspace_root_from_script() -> Path:
    # .../skills_live/openclaw-hardener/scripts/hardener.py -> workspace root
    return Path(__file__).resolve().parents[3]


def iter_files(root: Path) -> Iterable[Path]:
    skip_dirs = {".git", "node_modules", "third_party", "__pycache__", ".venv", ".venv3"}
    for p in root.rglob("*"):
        try:
            rel_parts = set(p.relative_to(root).parts)
        except Exception:
            rel_parts = set()
        if any(d in rel_parts for d in skip_dirs):
            continue
        if p.is_file():
            yield p


NONEXEC_EXTS = {
    ".md", ".txt", ".rst", ".json", ".json5", ".yml", ".yaml", ".toml",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf",
}


def check_unexpected_exec_bits(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    for p in iter_files(root):
        if p.suffix.lower() not in NONEXEC_EXTS:
            continue
        try:
            mode = p.stat().st_mode
        except Exception:
            continue
        if mode & stat.S_IXUSR:
            findings.append(Finding("warn", "unexpected_executable", "Unexpected executable bit set", str(p)))
    return findings


def fix_unexpected_exec_bits(root: Path) -> List[Finding]:
    changed: List[Finding] = []
    for p in iter_files(root):
        if p.suffix.lower() not in NONEXEC_EXTS:
            continue
        try:
            st = p.stat()
        except Exception:
            continue
        if st.st_mode & stat.S_IXUSR:
            new_mode = st.st_mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
            try:
                os.chmod(p, new_mode)
                changed.append(Finding("info", "chmod", "Removed executable bit", str(p)))
            except Exception as e:
                changed.append(Finding("warn", "chmod_failed", f"Failed to chmod: {e}", str(p)))
    return changed


def check_dotenv(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    for p in iter_files(root):
        name = p.name
        if name == ".env" or name.startswith(".env."):
            # presence is warn; if tracked by git, treat as fail
            findings.append(Finding("warn", "dotenv_present", "Found dotenv file (ensure it is not committed)", str(p)))
    # If git is available, check tracked dotenv
    try:
        rc, out, _ = run(["git", "-C", str(root), "ls-files", "-z", "--", ".env", ".env.*"], timeout_s=30)
        if rc == 0 and out:
            # out is NUL-separated; any entry => tracked
            findings.append(Finding("fail", "dotenv_tracked", "A dotenv file appears to be tracked by git", str(root)))
    except Exception:
        pass
    return findings


RISKY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("pickle", re.compile(r"\bimport\s+pickle\b|\bpickle\.loads\b|\bpickle\.load\b")),
    ("torch_load", re.compile(r"\btorch\.load\s*\(")),
    ("curl_pipe_sh", re.compile(r"\bcurl\b[^\n]*\|[^\n]*\bsh\b")),
    ("wget_pipe_sh", re.compile(r"\bwget\b[^\n]*\|[^\n]*\bsh\b")),
]


def check_risky_code_patterns(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    # only scan our own scripts-ish areas to avoid noisy third party
    scan_roots = [root / "scripts", root / "hybrid_orchestrator" / "scripts", root / "skills_live"]
    for sr in scan_roots:
        if not sr.exists():
            continue
        for p in iter_files(sr):
            if p.suffix.lower() not in {".py", ".sh", ".js", ".ts"}:
                continue
            try:
                txt = p.read_text("utf-8", errors="replace")
            except Exception:
                continue
            for code, rx in RISKY_PATTERNS:
                if rx.search(txt):
                    findings.append(Finding("warn", f"risky_{code}", f"Risky pattern matched: {code}", str(p)))
                    break
    return findings


def check_openclaw_audit(deep: bool = True) -> List[Finding]:
    cmd = ["openclaw", "security", "audit"]
    if deep:
        cmd.append("--deep")
    try:
        rc, out, err = run(cmd, timeout_s=300)
    except FileNotFoundError:
        return [Finding("fail", "openclaw_missing", "openclaw CLI not found on PATH")]

    # We do not parse the human output deeply; just attach a redacted summary.
    combined = (out + "\n" + err).strip()
    combined = redact(combined)
    sev = "info" if rc == 0 else "warn"
    return [Finding(sev, "openclaw_security_audit", combined)]


def fix_openclaw_audit() -> List[Finding]:
    try:
        rc, out, err = run(["openclaw", "security", "audit", "--fix"], timeout_s=300)
    except FileNotFoundError:
        return [Finding("fail", "openclaw_missing", "openclaw CLI not found on PATH")]
    combined = redact((out + "\n" + err).strip())
    sev = "info" if rc == 0 else "warn"
    return [Finding(sev, "openclaw_security_audit_fix", combined)]


def check_workspace_security_audit(workspace_root: Path) -> List[Finding]:
    """Run the repo-local security audit (hybrid orchestrator)."""
    sh = workspace_root / "hybrid_orchestrator" / "scripts" / "audit" / "security_audit.sh"
    if not sh.exists():
        return [Finding("warn", "workspace_audit_missing", "Workspace security_audit.sh not found", str(sh))]
    try:
        rc, out, err = run(["bash", str(sh), "--target", str(workspace_root)], timeout_s=900)
    except Exception as e:
        return [Finding("fail", "workspace_audit_failed", f"Failed to run workspace audit: {e}")]
    combined = redact((out + "\n" + err).strip())
    sev = "info" if rc == 0 else "warn"
    return [Finding(sev, "workspace_security_audit", combined)]


def load_openclaw_config_raw() -> Tuple[Optional[str], Optional[str], List[Finding]]:
    """Best-effort load of the current gateway config via CLI.

    Returns: (raw_json5, base_hash, findings)
    """
    try:
        rc, out, err = run(["openclaw", "gateway", "call", "config.get", "--params", "{}"], timeout_s=60)
    except FileNotFoundError:
        return None, None, [Finding("fail", "openclaw_missing", "openclaw CLI not found on PATH")]

    if rc != 0:
        return None, None, [Finding("fail", "config_get_failed", redact((out + err).strip()))]

    # The CLI may print a human prefix (e.g., "Gateway call: ...") before JSON.
    jtxt = out
    if not jtxt.lstrip().startswith("{"):
        i = jtxt.find("{")
        if i >= 0:
            jtxt = jtxt[i:]
    try:
        payload = json.loads(jtxt)
    except Exception as e:
        return None, None, [Finding("fail", "config_get_parse_failed", f"Failed to parse config.get output: {e}")]

    raw = payload.get("raw")
    base_hash = payload.get("hash") or payload.get("payload", {}).get("hash")

    return raw, base_hash, []


def parse_config(raw: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse config raw string.

    config.get returns JSON5, but for most setups it is also valid JSON.
    We parse with json.loads as a best-effort.

    Returns (config_dict, error_string)
    """
    try:
        return json.loads(raw), None
    except Exception as e:
        return None, str(e)


def config_patch_plan(config: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[str]]:
    """Return a conservative JSON merge patch + human notes.

    This is intentionally minimal: only includes changes that are generally safe.
    Anything potentially breaking is emitted as a NOTE instead of a patch.
    """
    patch: Dict[str, Any] = {}
    notes: List[str] = []

    # 1) Logging redaction: keep secrets out of tool summaries.
    cur_redact = None
    if isinstance(config, dict):
        cur_redact = (config.get("logging") or {}).get("redactSensitive")

    if cur_redact != "tools":
        patch.setdefault("logging", {})["redactSensitive"] = "tools"
        notes.append("Set logging.redactSensitive=\"tools\" (safer default).")

    # 2) mDNS/Bonjour disclosure: prefer minimal broadcasts.
    # This can reduce info disclosure on local networks without fully disabling discovery.
    cur_mdns_mode = None
    if isinstance(config, dict):
        cur_mdns_mode = (((config.get("discovery") or {}).get("mdns") or {}).get("mode"))

    if cur_mdns_mode == "full":
        patch.setdefault("discovery", {}).setdefault("mdns", {})["mode"] = "minimal"
        notes.append("Set discovery.mdns.mode=\"minimal\" (avoid advertising cliPath/sshPort).")

    # 3) Browser sandboxing warning (do not auto-change):
    # In some environments, disabling noSandbox can break headless Chromium.
    if isinstance(config, dict):
        browser = config.get("browser") or {}
        if isinstance(browser, dict) and browser.get("enabled") is True and browser.get("noSandbox") is True:
            notes.append("Browser is enabled with browser.noSandbox=true. This increases risk; consider running with sandbox enabled if feasible.")

    # 4) Reverse proxy trust warning: cannot auto-fix without knowing proxy IP.
    notes.append("If you expose Control UI through a reverse proxy, set gateway.trustedProxies to the proxy IPs (prevents spoofed local-client checks).")

    return patch, notes


def print_findings(findings: List[Finding], as_json: bool) -> int:
    if as_json:
        payload = [
            {"severity": f.severity, "code": f.code, "message": f.message, "path": f.path}
            for f in findings
        ]
        print(json.dumps({"findings": payload}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            loc = f" ({f.path})" if f.path else ""
            print(f"[{f.severity.upper()}] {f.code}{loc}: {f.message}")

    # exit code: 0 if no fail, 10 if any fail
    return 10 if any(f.severity == "fail" for f in findings) else 0


def apply_config_patch(patch: Dict[str, Any]) -> List[Finding]:
    # Apply via gateway RPC: config.get -> config.patch
    # Uses JSON5 in raw param; we just send JSON.
    try:
        rc, out, err = run(["openclaw", "gateway", "call", "config.get", "--params", "{}"], timeout_s=60)
    except FileNotFoundError:
        return [Finding("fail", "openclaw_missing", "openclaw CLI not found on PATH")]
    if rc != 0:
        return [Finding("fail", "config_get_failed", redact((out + err).strip()))]

    try:
        payload = json.loads(out)
        base_hash = payload.get("hash") or payload.get("payload", {}).get("hash")
    except Exception:
        base_hash = None

    if not base_hash:
        return [Finding("fail", "config_hash_missing", "Could not extract baseHash from config.get output")]

    raw = json.dumps(patch, ensure_ascii=False, indent=2)
    params = {"raw": raw, "baseHash": base_hash, "note": "openclaw-hardener apply-config"}
    params_s = json.dumps(params, ensure_ascii=False)

    rc2, out2, err2 = run(["openclaw", "gateway", "call", "config.patch", "--params", params_s], timeout_s=120)
    combined = redact((out2 + "\n" + err2).strip())
    sev = "info" if rc2 == 0 else "fail"
    return [Finding(sev, "config_patch", combined)]


def main() -> int:
    ap = argparse.ArgumentParser(prog="openclaw-hardener")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_check = sub.add_parser("check", help="Run read-only hardening checks")
    ap_check.add_argument("--openclaw", action="store_true", help="Run OpenClaw built-in security audit")
    ap_check.add_argument("--workspace", action="store_true", help="Run workspace (repo) security audit + hygiene checks")
    ap_check.add_argument("--all", action="store_true", help="Run everything")
    ap_check.add_argument("--json", action="store_true", help="Emit JSON")

    ap_fix = sub.add_parser("fix", help="Apply safe mechanical fixes (explicit opt-in)")
    ap_fix.add_argument("--openclaw", action="store_true", help="Run openclaw security audit --fix")
    ap_fix.add_argument("--workspace", action="store_true", help="Fix workspace hygiene issues (chmod/exec-bits)")
    ap_fix.add_argument("--all", action="store_true", help="Run everything")
    ap_fix.add_argument("--json", action="store_true", help="Emit JSON")

    ap_plan = sub.add_parser("plan-config", help="Print a conservative config.patch plan")
    ap_plan.add_argument("--json", action="store_true", help="Emit JSON")

    ap_apply = sub.add_parser("apply-config", help="Apply the config.patch plan via gateway RPC")
    ap_apply.add_argument("--json", action="store_true", help="Emit JSON")

    args = ap.parse_args()
    ws = workspace_root_from_script()
    home = Path.home()

    if args.cmd == "plan-config":
        raw, base_hash, fs = load_openclaw_config_raw()
        cfg = None
        notes: List[str] = []
        patch: Dict[str, Any] = {}
        if fs:
            # still produce a generic plan
            patch, notes = config_patch_plan(None)
            findings = fs
        else:
            findings = []
            if raw:
                cfg, err = parse_config(raw)
                if err:
                    findings.append(Finding("warn", "config_parse_warn", f"Could not parse config raw as JSON (JSON5?): {err}"))
            patch, notes = config_patch_plan(cfg)

        payload = {
            "patch": patch,
            "notes": notes,
            "baseHash": base_hash,
        }

        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("# Suggested config.patch (JSON)\n")
            print(json.dumps(patch, ensure_ascii=False, indent=2))
            if notes:
                print("\n# Notes")
                for n in notes:
                    print(f"- {n}")
            print("\n# Apply with:\n# openclaw gateway call config.patch --params '{...}' (see docs)\n")

        # If config.get failed, surface it as warnings.
        if findings:
            return print_findings(findings, args.json)
        return 0

    if args.cmd == "apply-config":
        raw, _base_hash, fs = load_openclaw_config_raw()
        cfg = None
        if not fs and raw:
            cfg, _ = parse_config(raw)
        patch, notes = config_patch_plan(cfg)
        # Always print notes in non-JSON mode before applying.
        if not args.json and notes:
            print("# Notes")
            for n in notes:
                print(f"- {n}")
            print()
        findings = apply_config_patch(patch)
        return print_findings(findings, args.json)

    findings: List[Finding] = []

    if args.cmd == "check":
        do_openclaw = args.all or args.openclaw or (not args.openclaw and not args.workspace and not args.all)
        do_workspace = args.all or args.workspace or (not args.openclaw and not args.workspace and not args.all)

        if do_openclaw:
            findings.extend(check_openclaw_audit(deep=True))

        if do_workspace:
            findings.extend(check_workspace_security_audit(ws))
            findings.extend(check_unexpected_exec_bits(ws))
            findings.extend(check_dotenv(ws))
            findings.extend(check_risky_code_patterns(ws))

        return print_findings(findings, args.json)

    if args.cmd == "fix":
        do_openclaw = args.all or args.openclaw or (not args.openclaw and not args.workspace and not args.all)
        do_workspace = args.all or args.workspace or (not args.openclaw and not args.workspace and not args.all)

        if do_openclaw:
            findings.extend(fix_openclaw_audit())

        if do_workspace:
            findings.extend(fix_unexpected_exec_bits(ws))
            # We intentionally do NOT auto-delete dotenv files.
            findings.append(Finding("info", "note", "Not deleting dotenv files automatically; remove them manually if unneeded."))

        return print_findings(findings, args.json)

    return 2


if __name__ == "__main__":
    sys.exit(main())
