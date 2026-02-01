#!/usr/bin/env python3
"""Automated skill evaluation — structural and heuristic checks.

Usage:
    python3 eval-skill.py <path-to-skill-directory>
    python3 eval-skill.py <path-to-skill-directory> --json
    python3 eval-skill.py <path-to-skill-directory> --verbose

Checks file structure, SKILL.md quality, script health, and agent-specific heuristics.
Outputs a report with pass/warn/fail per check and an overall structural score.

This covers the AUTOMATABLE portion of the evaluation. The full rubric
(references/rubric.md) includes manual assessment criteria that require
human or agent judgment.
"""

import argparse
import ast
import json
import os
import re
import sys
import yaml


# --- Check infrastructure ---

class CheckResult:
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

    def __init__(self, name, status, message="", category=""):
        self.name = name
        self.status = status
        self.message = message
        self.category = category

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "category": self.category,
        }


def check(name, category="general"):
    """Decorator to register a check function."""
    def decorator(func):
        func._check_name = name
        func._check_category = category
        return func
    return decorator


# --- File structure checks ---

@check("SKILL.md exists", "structure")
def check_skill_md_exists(skill_path):
    path = os.path.join(skill_path, "SKILL.md")
    if os.path.isfile(path):
        return CheckResult("SKILL.md exists", CheckResult.PASS, category="structure")
    return CheckResult("SKILL.md exists", CheckResult.FAIL,
                       "SKILL.md is required", category="structure")


@check("SKILL.md has valid frontmatter", "structure")
def check_frontmatter(skill_path):
    path = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(path):
        return CheckResult("SKILL.md has valid frontmatter", CheckResult.FAIL,
                           "SKILL.md not found", category="structure")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return CheckResult("SKILL.md has valid frontmatter", CheckResult.FAIL,
                           "No YAML frontmatter found (must start with ---)", category="structure")

    try:
        fm = yaml.safe_load(match.group(1))
    except Exception as e:
        return CheckResult("SKILL.md has valid frontmatter", CheckResult.FAIL,
                           f"Invalid YAML: {e}", category="structure")

    if not isinstance(fm, dict):
        return CheckResult("SKILL.md has valid frontmatter", CheckResult.FAIL,
                           "Frontmatter must be a YAML mapping", category="structure")

    missing = []
    if not fm.get("name"):
        missing.append("name")
    if not fm.get("description"):
        missing.append("description")

    if missing:
        return CheckResult("SKILL.md has valid frontmatter", CheckResult.FAIL,
                           f"Missing required fields: {', '.join(missing)}", category="structure")

    return CheckResult("SKILL.md has valid frontmatter", CheckResult.PASS, category="structure")


@check("Skill name matches directory", "structure")
def check_name_matches_dir(skill_path):
    dir_name = os.path.basename(os.path.abspath(skill_path))
    path = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(path):
        return CheckResult("Skill name matches directory", CheckResult.FAIL,
                           "SKILL.md not found", category="structure")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return CheckResult("Skill name matches directory", CheckResult.WARN,
                           "No frontmatter to check", category="structure")
    try:
        fm = yaml.safe_load(match.group(1))
        name = fm.get("name", "")
    except Exception:
        return CheckResult("Skill name matches directory", CheckResult.WARN,
                           "Could not parse frontmatter", category="structure")

    if name == dir_name:
        return CheckResult("Skill name matches directory", CheckResult.PASS, category="structure")
    return CheckResult("Skill name matches directory", CheckResult.WARN,
                       f"name='{name}' but directory='{dir_name}'", category="structure")


@check("No extraneous files", "structure")
def check_no_extraneous(skill_path):
    """Check for files that shouldn't be in a skill (README, CHANGELOG, etc.)."""
    bad_files = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md",
                 "QUICK_REFERENCE.md", "LICENSE", "LICENSE.md"}
    found = []
    for f in os.listdir(skill_path):
        if f.upper() in {b.upper() for b in bad_files}:
            found.append(f)
    if found:
        return CheckResult("No extraneous files", CheckResult.WARN,
                           f"Found: {', '.join(found)} — skills shouldn't include these",
                           category="structure")
    return CheckResult("No extraneous files", CheckResult.PASS, category="structure")


@check("Resource directories are non-empty", "structure")
def check_resource_dirs(skill_path):
    """If scripts/, references/, or assets/ exist, they should contain files."""
    empty = []
    for d in ("scripts", "references", "assets"):
        dp = os.path.join(skill_path, d)
        if os.path.isdir(dp):
            contents = [f for f in os.listdir(dp) if not f.startswith(".") and f != "__pycache__"]
            if not contents:
                empty.append(d)
    if empty:
        return CheckResult("Resource directories are non-empty", CheckResult.WARN,
                           f"Empty directories: {', '.join(empty)}", category="structure")
    return CheckResult("Resource directories are non-empty", CheckResult.PASS, category="structure")


# --- Description quality ---

@check("Description length adequate", "trigger")
def check_description_length(skill_path):
    fm = _get_frontmatter(skill_path)
    if not fm:
        return CheckResult("Description length adequate", CheckResult.FAIL,
                           "No frontmatter", category="trigger")
    desc = fm.get("description", "")
    words = len(desc.split())
    if words < 15:
        return CheckResult("Description length adequate", CheckResult.FAIL,
                           f"Description is only {words} words — too short for reliable triggering",
                           category="trigger")
    if words < 30:
        return CheckResult("Description length adequate", CheckResult.WARN,
                           f"Description is {words} words — consider adding trigger contexts",
                           category="trigger")
    if words > 150:
        return CheckResult("Description length adequate", CheckResult.WARN,
                           f"Description is {words} words — may be too long (wastes context in metadata)",
                           category="trigger")
    return CheckResult("Description length adequate", CheckResult.PASS,
                       f"{words} words", category="trigger")


@check("Description includes trigger contexts", "trigger")
def check_trigger_contexts(skill_path):
    """Good descriptions say WHEN to use the skill, not just WHAT it does."""
    fm = _get_frontmatter(skill_path)
    if not fm:
        return CheckResult("Description includes trigger contexts", CheckResult.FAIL,
                           "No frontmatter", category="trigger")
    desc = fm.get("description", "").lower()
    trigger_phrases = ["use when", "use for", "use if", "when the user",
                       "when asked", "when you need", "for tasks like",
                       "such as", "e.g.", "for example"]
    found = [p for p in trigger_phrases if p in desc]
    if not found:
        return CheckResult("Description includes trigger contexts", CheckResult.WARN,
                           "No trigger phrases found — add 'Use when...' to improve activation",
                           category="trigger")
    return CheckResult("Description includes trigger contexts", CheckResult.PASS,
                       f"Found: {', '.join(found[:3])}", category="trigger")


# --- SKILL.md body quality ---

@check("SKILL.md body length", "documentation")
def check_body_length(skill_path):
    path = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(path):
        return CheckResult("SKILL.md body length", CheckResult.FAIL, "Not found", category="documentation")
    with open(path, "r") as f:
        lines = f.readlines()
    # Count lines after frontmatter
    in_fm = False
    body_lines = 0
    fm_ended = False
    for line in lines:
        if line.strip() == "---":
            if not fm_ended:
                in_fm = not in_fm
                if not in_fm:
                    fm_ended = True
                continue
        if fm_ended:
            body_lines += 1

    if body_lines < 10:
        return CheckResult("SKILL.md body length", CheckResult.FAIL,
                           f"Only {body_lines} lines — too short to be useful", category="documentation")
    if body_lines > 500:
        return CheckResult("SKILL.md body length", CheckResult.WARN,
                           f"{body_lines} lines — consider splitting into reference files", category="documentation")
    return CheckResult("SKILL.md body length", CheckResult.PASS,
                       f"{body_lines} lines", category="documentation")


@check("References are linked from SKILL.md", "documentation")
def check_references_linked(skill_path):
    """If references/ exists, SKILL.md should link to the files."""
    ref_dir = os.path.join(skill_path, "references")
    if not os.path.isdir(ref_dir):
        return CheckResult("References are linked from SKILL.md", CheckResult.PASS,
                           "No references/ directory", category="documentation")
    ref_files = [f for f in os.listdir(ref_dir) if not f.startswith(".")]
    if not ref_files:
        return CheckResult("References are linked from SKILL.md", CheckResult.PASS,
                           "No reference files", category="documentation")

    skill_md = os.path.join(skill_path, "SKILL.md")
    with open(skill_md, "r") as f:
        content = f.read()

    unlinked = [f for f in ref_files if f not in content]
    if unlinked:
        return CheckResult("References are linked from SKILL.md", CheckResult.WARN,
                           f"Unlinked references: {', '.join(unlinked)}", category="documentation")
    return CheckResult("References are linked from SKILL.md", CheckResult.PASS, category="documentation")


# --- Script health ---

@check("Python scripts parse without errors", "scripts")
def check_python_syntax(skill_path):
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return CheckResult("Python scripts parse without errors", CheckResult.PASS,
                           "No scripts/ directory", category="scripts")

    errors = []
    checked = 0
    for f in os.listdir(scripts_dir):
        if f.endswith(".py"):
            checked += 1
            fpath = os.path.join(scripts_dir, f)
            try:
                with open(fpath, "r") as fh:
                    ast.parse(fh.read(), filename=f)
            except SyntaxError as e:
                errors.append(f"{f}:{e.lineno}: {e.msg}")

    if not checked:
        return CheckResult("Python scripts parse without errors", CheckResult.PASS,
                           "No Python scripts", category="scripts")
    if errors:
        return CheckResult("Python scripts parse without errors", CheckResult.FAIL,
                           "\n".join(errors), category="scripts")
    return CheckResult("Python scripts parse without errors", CheckResult.PASS,
                       f"{checked} script(s) OK", category="scripts")


@check("Scripts use no external dependencies", "scripts")
def check_no_ext_deps(skill_path):
    """Check that Python scripts only import stdlib modules."""
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return CheckResult("Scripts use no external dependencies", CheckResult.PASS,
                           "No scripts/", category="scripts")

    # Common stdlib modules (not exhaustive, but covers common ones)
    stdlib = {
        "abc", "argparse", "ast", "base64", "bisect", "calendar", "cgi",
        "cmd", "codecs", "collections", "configparser", "contextlib", "copy",
        "csv", "dataclasses", "datetime", "decimal", "difflib", "email",
        "enum", "errno", "fnmatch", "fractions", "ftplib", "functools",
        "getopt", "getpass", "glob", "gzip", "hashlib", "heapq", "hmac",
        "html", "http", "imaplib", "importlib", "inspect", "io", "ipaddress",
        "itertools", "json", "keyword", "linecache", "locale", "logging",
        "lzma", "math", "mimetypes", "multiprocessing", "operator", "os",
        "pathlib", "pickle", "platform", "plistlib", "pprint", "profile",
        "queue", "random", "re", "readline", "reprlib", "secrets",
        "select", "shelve", "shlex", "shutil", "signal", "smtplib",
        "socket", "sqlite3", "ssl", "stat", "statistics", "string",
        "struct", "subprocess", "sys", "syslog", "tarfile", "tempfile",
        "textwrap", "threading", "time", "timeit", "token", "tokenize",
        "tomllib", "traceback", "types", "typing", "unicodedata",
        "unittest", "urllib", "uuid", "venv", "warnings", "weakref",
        "webbrowser", "xml", "xmlrpc", "zipfile", "zipimport", "zlib",
        "_thread", "__future__",
    }

    ext_deps = []
    for f in os.listdir(scripts_dir):
        if not f.endswith(".py"):
            continue
        fpath = os.path.join(scripts_dir, f)
        try:
            with open(fpath, "r") as fh:
                tree = ast.parse(fh.read())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in stdlib:
                        ext_deps.append(f"{f}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    if top not in stdlib:
                        ext_deps.append(f"{f}: from {node.module}")

    if ext_deps:
        return CheckResult("Scripts use no external dependencies", CheckResult.WARN,
                           f"Possible external deps: {'; '.join(ext_deps[:5])}",
                           category="scripts")
    return CheckResult("Scripts use no external dependencies", CheckResult.PASS, category="scripts")


@check("No hardcoded credentials or emails", "security")
def check_no_hardcoded_secrets(skill_path):
    """Scan for common patterns: API keys, emails, tokens in source files."""
    patterns = [
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "email address"),
        (r'(?:api[_-]?key|token|secret|password)\s*[=:]\s*["\'][^"\']{8,}', "possible credential"),
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI-style API key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub PAT"),
    ]
    findings = []

    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for f in files:
            if f.endswith((".py", ".md", ".sh", ".js", ".ts", ".yaml", ".yml", ".json", ".toml")):
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, skill_path)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                        for i, line in enumerate(fh, 1):
                            for pattern, desc in patterns:
                                if re.search(pattern, line):
                                    if desc == "email address":
                                        match = re.search(pattern, line)
                                        if match:
                                            email = match.group().lower()
                                            # Skip well-known safe patterns
                                            safe_domains = (
                                                "example.com", "example.org",
                                                "outlook.com", "hotmail.com",
                                                "googlegroups.com",
                                                "iam.gserviceaccount.com",
                                                "placeholder", "your",
                                            )
                                            if any(d in email for d in safe_domains):
                                                continue
                                            if "your" in email:
                                                continue
                                    findings.append(f"{rel}:{i}: {desc}")
                except (IOError, UnicodeDecodeError):
                    pass

    if findings:
        # Deduplicate
        unique = list(dict.fromkeys(findings))[:10]
        return CheckResult("No hardcoded credentials or emails", CheckResult.WARN,
                           f"Found {len(findings)} potential issues:\n" + "\n".join(unique),
                           category="security")
    return CheckResult("No hardcoded credentials or emails", CheckResult.PASS, category="security")


@check("Environment variables documented", "security")
def check_env_vars_documented(skill_path):
    """If scripts reference os.environ, SKILL.md should document those vars."""
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return CheckResult("Environment variables documented", CheckResult.PASS,
                           "No scripts/", category="security")

    env_vars = set()
    for f in os.listdir(scripts_dir):
        if not f.endswith(".py"):
            continue
        fpath = os.path.join(scripts_dir, f)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        # Match os.environ.get("VAR") and os.environ["VAR"]
        for m in re.finditer(r'os\.environ(?:\.get)?\s*[\[(]\s*["\'](\w+)', content):
            var = m.group(1)
            # Skip obviously dummy/example variable names
            if var not in ("VAR", "KEY", "VALUE", "NAME", "ENV"):
                env_vars.add(var)

    if not env_vars:
        return CheckResult("Environment variables documented", CheckResult.PASS,
                           "No env vars found in scripts", category="security")

    skill_md = os.path.join(skill_path, "SKILL.md")
    with open(skill_md, "r") as f:
        skill_content = f.read()

    undocumented = [v for v in env_vars if v not in skill_content]
    if undocumented:
        return CheckResult("Environment variables documented", CheckResult.WARN,
                           f"Undocumented env vars: {', '.join(sorted(undocumented))}",
                           category="security")
    return CheckResult("Environment variables documented", CheckResult.PASS,
                       f"All {len(env_vars)} env vars documented", category="security")


# --- Helpers ---

def _get_frontmatter(skill_path):
    path = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except Exception:
        return None


# --- Runner ---

ALL_CHECKS = [
    check_skill_md_exists,
    check_frontmatter,
    check_name_matches_dir,
    check_no_extraneous,
    check_resource_dirs,
    check_description_length,
    check_trigger_contexts,
    check_body_length,
    check_references_linked,
    check_python_syntax,
    check_no_ext_deps,
    check_no_hardcoded_secrets,
    check_env_vars_documented,
]


def run_checks(skill_path, verbose=False):
    results = []
    for check_fn in ALL_CHECKS:
        try:
            result = check_fn(skill_path)
            results.append(result)
        except Exception as e:
            results.append(CheckResult(
                check_fn._check_name, CheckResult.FAIL,
                f"Check crashed: {e}", check_fn._check_category
            ))
    return results


def print_report(results, skill_path, verbose=False):
    counts = {CheckResult.PASS: 0, CheckResult.WARN: 0, CheckResult.FAIL: 0}
    by_category = {}

    for r in results:
        counts[r.status] += 1
        by_category.setdefault(r.category, []).append(r)

    skill_name = os.path.basename(os.path.abspath(skill_path))
    print(f"\n📋 Skill Evaluation: {skill_name}")
    print(f"{'=' * 50}")
    print(f"Path: {os.path.abspath(skill_path)}")
    print()

    icons = {CheckResult.PASS: "✅", CheckResult.WARN: "⚠️ ", CheckResult.FAIL: "❌"}

    for cat in ["structure", "trigger", "documentation", "scripts", "security"]:
        if cat not in by_category:
            continue
        print(f"  [{cat.upper()}]")
        for r in by_category[cat]:
            icon = icons[r.status]
            print(f"    {icon} {r.name}")
            if r.message and (verbose or r.status != CheckResult.PASS):
                for line in r.message.split("\n"):
                    print(f"       {line}")
        print()

    print(f"{'=' * 50}")
    print(f"  ✅ Pass: {counts[CheckResult.PASS]}  "
          f"⚠️  Warn: {counts[CheckResult.WARN]}  "
          f"❌ Fail: {counts[CheckResult.FAIL]}")

    total = len(results)
    score = counts[CheckResult.PASS] / total * 100 if total else 0
    print(f"  Structural score: {score:.0f}% ({counts[CheckResult.PASS]}/{total} checks passed)")
    print()
    print("  ⓘ  This covers automated/structural checks only.")
    print("     For the full evaluation, use the manual rubric in references/rubric.md")
    print()


def main():
    parser = argparse.ArgumentParser(description="Evaluate a Clawdbot skill")
    parser.add_argument("path", help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details for passing checks too")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: '{args.path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    results = run_checks(args.path, verbose=args.verbose)

    if args.json:
        output = {
            "skill": os.path.basename(os.path.abspath(args.path)),
            "path": os.path.abspath(args.path),
            "checks": [r.to_dict() for r in results],
            "summary": {
                "pass": sum(1 for r in results if r.status == CheckResult.PASS),
                "warn": sum(1 for r in results if r.status == CheckResult.WARN),
                "fail": sum(1 for r in results if r.status == CheckResult.FAIL),
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(results, args.path, verbose=args.verbose)


if __name__ == "__main__":
    main()
