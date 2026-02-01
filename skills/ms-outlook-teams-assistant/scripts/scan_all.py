"""Run Outlook + Teams scans and cache results to state/.

This is separated from remind.py so reminder generation is fast and does not hang.

Usage:
  python scripts/scan_all.py --config references/config.json

Outputs:
  - state/latest_outlook.json
  - state/latest_teams.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _run_json_to_file(cmd: list[str], cwd: str, timeout_s: int, out_path: str) -> dict:
    """Run a JSON-printing command and write stdout to out_path.

    Avoids deadlocks from large stdout when using capture_output.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Important: don't pipe stderr. Some tools (notably MSAL device-code flows)
    # can print a lot to stderr, which can deadlock if piped.
    err_path = out_path + ".stderr.txt"
    with open(out_path, "w", encoding="utf-8") as out_f, open(err_path, "w", encoding="utf-8") as err_f:
        p = subprocess.run(cmd, cwd=cwd, stdout=out_f, stderr=err_f, text=True, timeout=timeout_s)

    if p.returncode != 0:
        stderr = ""
        try:
            with open(err_path, "r", encoding="utf-8") as f:
                stderr = f.read()
        except Exception:
            stderr = "(failed to read stderr log)"
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDERR:\n{stderr}")

    return _load_json(out_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--outlook-timeout", type=int, default=45)
    ap.add_argument("--teams-timeout", type=int, default=60)
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    skill_dir = os.path.dirname(os.path.dirname(cfg_path))
    cfg = _load_json(cfg_path)

    out_dir = os.path.join(skill_dir, "state")

    # Outlook
    out_path = os.path.join(out_dir, "latest_outlook.json")
    try:
        o = cfg.get("outlook", {})
        out_json = _run_json_to_file(
            [
                "python",
                os.path.join("scripts", "scan_outlook.py"),
                "--config",
                os.path.relpath(cfg_path, skill_dir),
                "--days",
                str(int(o.get("days", 7))),
                "--max-items",
                str(int(o.get("maxItems", 200))),
            ],
            cwd=skill_dir,
            timeout_s=args.outlook_timeout,
            out_path=out_path,
        )
    except Exception as e:
        out_json = {"error": str(e)}
        _write_json(out_path, out_json)

    out_json = _load_json(out_path)
    out_json["cachedAt"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _write_json(out_path, out_json)

    # Teams
    teams_path = os.path.join(out_dir, "latest_teams.json")
    try:
        if cfg.get("teams", {}).get("enabled"):
            t_json = _run_json_to_file(
                [
                    "python",
                    os.path.join("scripts", "teams_scan.py"),
                    "--config",
                    os.path.relpath(cfg_path, skill_dir),
                    "--days",
                    str(int(cfg.get("outlook", {}).get("days", 7))),
                ],
                cwd=skill_dir,
                timeout_s=args.teams_timeout,
                out_path=teams_path,
            )
        else:
            t_json = {"disabled": True}
            _write_json(teams_path, t_json)
    except Exception as e:
        t_json = {"error": str(e)}
        _write_json(teams_path, t_json)

    t_json = _load_json(teams_path)
    t_json["cachedAt"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _write_json(teams_path, t_json)

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
