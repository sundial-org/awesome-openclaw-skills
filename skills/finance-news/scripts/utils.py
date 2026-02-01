"""Shared helpers."""

import os
import sys
import time
from pathlib import Path


def ensure_venv() -> None:
    """Re-exec inside local venv if available and not already active."""
    if os.environ.get("FINANCE_NEWS_VENV_BOOTSTRAPPED") == "1":
        return
    if sys.prefix != sys.base_prefix:
        return
    venv_python = Path(__file__).resolve().parent.parent / "venv" / "bin" / "python3"
    if not venv_python.exists():
        print("⚠️ finance-news venv missing; run scripts from the repo venv to avoid dependency errors.", file=sys.stderr)
        return
    env = os.environ.copy()
    env["FINANCE_NEWS_VENV_BOOTSTRAPPED"] = "1"
    os.execvpe(str(venv_python), [str(venv_python)] + sys.argv, env)


def compute_deadline(deadline_sec: int | None) -> float | None:
    if deadline_sec is None:
        return None
    if deadline_sec <= 0:
        return None
    return time.monotonic() + deadline_sec


def time_left(deadline: float | None) -> int | None:
    if deadline is None:
        return None
    remaining = int(deadline - time.monotonic())
    return remaining


def clamp_timeout(default_timeout: int, deadline: float | None, minimum: int = 1) -> int:
    remaining = time_left(deadline)
    if remaining is None:
        return default_timeout
    if remaining <= 0:
        raise TimeoutError("Deadline exceeded")
    return max(min(default_timeout, remaining), minimum)
