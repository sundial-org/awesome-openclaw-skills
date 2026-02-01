#!/usr/bin/env python3
"""
Clawd Presence Display

Terminal-based status display for AI agents.
Designed for dedicated screens (old laptops, Raspberry Pi, spare monitors).
"""

from __future__ import annotations

import curses
import json
import math
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths relative to script location
SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = ROOT_DIR / "config.json"
STATE_FILE = ROOT_DIR / "state.json"
MONOGRAMS_DIR = ROOT_DIR / "assets" / "monograms"

# Defaults
DEFAULT_CONFIG: dict[str, Any] = {
    "letter": "A",
    "name": "AGENT",
    "idle_timeout": 300,
}

DEFAULT_STATE: dict[str, Any] = {
    "state": "idle",
    "message": "",
    "updated": 0,
}

# Color mappings
STATE_COLORS = {"idle": 10, "work": 11, "think": 12, "alert": 13, "sleep": 14}
PULSE_SPEEDS = {"idle": 0.08, "work": 0.15, "think": 0.12, "alert": 0.15, "sleep": 0}
GLOW_SPEEDS = {"idle": 0.03, "work": 0.06, "think": 0.04, "alert": 0.08, "sleep": 0}


def load_json_file(filepath: Path, default: dict[str, Any]) -> dict[str, Any]:
    """Load JSON file with fallback to default."""
    if not filepath.exists():
        return default.copy()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                result = default.copy()
                result.update(data)
                return result
    except (json.JSONDecodeError, IOError, OSError):
        pass
    return default.copy()


def save_json_file(filepath: Path, data: dict[str, Any]) -> bool:
    """Save data to JSON file. Returns True on success."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except (IOError, OSError):
        return False


def get_mtime(filepath: Path) -> float:
    """Get file modification time, 0 if doesn't exist."""
    try:
        return filepath.stat().st_mtime
    except (OSError, IOError):
        return 0.0


def load_monogram(letter: str) -> list[str]:
    """Load monogram design for a letter."""
    letter = letter.upper()
    if not letter.isalpha() or len(letter) != 1:
        letter = "A"
    
    mono_file = MONOGRAMS_DIR / f"{letter}.txt"
    if mono_file.exists():
        try:
            with open(mono_file, "r", encoding="utf-8") as f:
                return [line.rstrip() for line in f.readlines()]
        except (IOError, OSError):
            pass
    
    # Fallback: simple block letter
    return [
        f"  {letter}  ",
        f" {letter}{letter}{letter} ",
        f"{letter}   {letter}",
        f"{letter}{letter}{letter}{letter}{letter}",
        f"{letter}   {letter}",
    ]


def build_pulse(pos: int, width: int, sleeping: bool) -> str:
    """Build pulse animation string."""
    if sleeping:
        return "─" * width
    
    chars = []
    for i in range(width):
        dist = min(abs(i - pos), width - abs(i - pos))
        if dist == 0:
            chars.append("█")
        elif dist == 1:
            chars.append("▓")
        elif dist == 2:
            chars.append("▒")
        elif dist == 3:
            chars.append("░")
        else:
            chars.append("─")
    return "".join(chars)


def init_colors() -> None:
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    
    # Grayscale palette
    curses.init_pair(1, 255, -1)  # Bright white
    curses.init_pair(2, 252, -1)  # White
    curses.init_pair(3, 248, -1)  # Light gray
    curses.init_pair(4, 244, -1)  # Mid gray
    curses.init_pair(5, 240, -1)  # Dark gray
    curses.init_pair(6, 236, -1)  # Darker gray
    
    # State accent colors
    curses.init_pair(10, 73, -1)   # Dusty cyan (idle)
    curses.init_pair(11, 108, -1)  # Sage green (work)
    curses.init_pair(12, 179, -1)  # Warm gold (think)
    curses.init_pair(13, 167, -1)  # Muted red (alert)
    curses.init_pair(14, 67, -1)   # Steel blue (sleep)


def safe_addstr(stdscr: Any, y: int, x: int, text: str, attr: int = 0) -> None:
    """Safely add string to screen, handling boundary errors."""
    try:
        h, w = stdscr.getmaxyx()
        if 0 <= y < h and 0 <= x < w:
            # Truncate text to fit
            max_len = w - x - 1
            if max_len > 0:
                stdscr.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


def safe_addch(stdscr: Any, y: int, x: int, ch: str, attr: int = 0) -> None:
    """Safely add character to screen."""
    try:
        h, w = stdscr.getmaxyx()
        if 0 <= y < h - 1 and 0 <= x < w - 1:
            stdscr.addch(y, x, ch, attr)
    except curses.error:
        pass


def draw(stdscr: Any) -> None:
    """Main display loop."""
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(33)  # ~30fps
    
    # Handle terminal resize
    def handle_resize(signum: int, frame: Any) -> None:
        curses.endwin()
        stdscr.refresh()
    
    signal.signal(signal.SIGWINCH, handle_resize)
    
    # Initial load
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    state_data = load_json_file(STATE_FILE, DEFAULT_STATE)
    monogram = load_monogram(config["letter"])
    
    # Tracking for efficient updates
    frame = 0
    state_mtime = get_mtime(STATE_FILE)
    config_mtime = get_mtime(CONFIG_FILE)
    last_state = ""
    last_message = ""
    last_time_str = ""
    last_size = (0, 0)
    
    pulse_width = 32
    
    while True:
        try:
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):  # q, Q, ESC
                break
            
            now = time.time()
            h, w = stdscr.getmaxyx()
            
            # Handle resize - full redraw
            if (h, w) != last_size:
                stdscr.clear()
                last_state = ""
                last_message = ""
                last_time_str = ""
                last_size = (h, w)
            
            # Check state file by mtime (efficient)
            new_state_mtime = get_mtime(STATE_FILE)
            if new_state_mtime != state_mtime:
                state_data = load_json_file(STATE_FILE, DEFAULT_STATE)
                state_mtime = new_state_mtime
                
                # Auto-idle timeout
                timeout = config.get("idle_timeout", 300)
                if timeout > 0:
                    elapsed = now - state_data.get("updated", now)
                    current = state_data.get("state", "idle")
                    if elapsed > timeout and current not in ("idle", "sleep"):
                        state_data["state"] = "idle"
                        state_data["message"] = ""
                        save_json_file(STATE_FILE, state_data)
            
            # Check config file by mtime
            new_config_mtime = get_mtime(CONFIG_FILE)
            if new_config_mtime != config_mtime:
                new_config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
                if new_config.get("letter") != config.get("letter"):
                    monogram = load_monogram(new_config["letter"])
                    stdscr.clear()  # Full redraw for new monogram
                config = new_config
                config_mtime = new_config_mtime
            
            state = state_data.get("state", "idle")
            message = state_data.get("message", "")
            
            cx, cy = w // 2, h // 2
            accent = STATE_COLORS.get(state, 10)
            
            # === MONOGRAM ===
            mark_y = cy - len(monogram) // 2 - 3
            glow_speed = GLOW_SPEEDS.get(state, 0.03)
            
            if state == "sleep":
                brightness = 4
            else:
                glow = (math.sin(frame * glow_speed) + 1) / 2
                brightness = 2 if glow > 0.5 else 3
            
            for i, line in enumerate(monogram):
                x = cx - len(line) // 2
                y = mark_y + i
                safe_addstr(stdscr, y, x, line, curses.color_pair(brightness))
            
            # === PULSE LINE ===
            pulse_y = mark_y + len(monogram) + 1
            pulse_x = cx - pulse_width // 2
            
            speed = PULSE_SPEEDS.get(state, 0.08)
            pos = int((frame * speed) % pulse_width) if speed > 0 else 0
            pulse = build_pulse(pos, pulse_width, state == "sleep")
            
            color = 6 if state == "sleep" else accent
            safe_addstr(stdscr, pulse_y, pulse_x, pulse, curses.color_pair(color))
            
            # === STATE (only on change) ===
            status_y = pulse_y + 3
            if state != last_state:
                state_str = state.upper()
                # Clear previous
                safe_addstr(stdscr, status_y, cx - 10, " " * 20)
                safe_addstr(stdscr, status_y, cx - len(state_str) // 2, state_str, 
                           curses.color_pair(accent))
                last_state = state
            
            # === MESSAGE (only on change) ===
            msg_y = pulse_y + 5
            if message != last_message:
                safe_addstr(stdscr, msg_y, 2, " " * (w - 4))
                if message:
                    msg = message[:w - 4]
                    safe_addstr(stdscr, msg_y, cx - len(msg) // 2, msg, 
                               curses.color_pair(5))
                last_message = message
            
            # === CORNERS ===
            safe_addch(stdscr, 0, 0, "+", curses.color_pair(6))
            safe_addch(stdscr, 0, w - 2, "+", curses.color_pair(6))
            safe_addch(stdscr, h - 2, 0, "+", curses.color_pair(6))
            safe_addch(stdscr, h - 2, w - 2, "+", curses.color_pair(6))
            
            # === TIME (only on change) ===
            time_str = datetime.now().strftime("%H:%M")
            if time_str != last_time_str:
                safe_addstr(stdscr, 1, cx - len(time_str) // 2, time_str, 
                           curses.color_pair(6))
                last_time_str = time_str
            
            # === NAME ===
            name = config.get("name", "AGENT")
            safe_addstr(stdscr, h - 2, cx - len(name) // 2, name, curses.color_pair(6))
            
            stdscr.refresh()
            frame += 1
            
        except curses.error:
            pass
        except KeyboardInterrupt:
            break


def main() -> None:
    """Entry point."""
    # Create state file if missing
    if not STATE_FILE.exists():
        state = DEFAULT_STATE.copy()
        state["updated"] = time.time()
        save_json_file(STATE_FILE, state)
    
    # Create config file if missing
    if not CONFIG_FILE.exists():
        save_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
