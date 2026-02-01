import json
import os
from pathlib import Path
from typing import Any, Dict

GLOBAL_CONFIG_DIR = Path.home() / ".inkjet"
LOCAL_CONFIG_DIR = Path.cwd() / ".inkjet"

DEFAULT_CONFIG = {
    "default_printer": None,
    "printers": {},  # Alias map: {"name": "address"}
    "energy": 9500,
    "print_speed": 10,
    "quality": 3,
    "padding_left": 0,
    "padding_top": 10,
    "line_spacing": 8,
    "align": "left",
    "font_size": 18
}

def get_config_path() -> Path:
    """Returns the local config path if it exists, otherwise global."""
    local_file = LOCAL_CONFIG_DIR / "config.json"
    if local_file.exists():
        return local_file
    return GLOBAL_CONFIG_DIR / "config.json"

def load_config() -> Dict[str, Any]:
    path = get_config_path()
    if not path.exists():
        return DEFAULT_CONFIG
    
    try:
        with open(path, "r") as f:
            config = json.load(f)
            # Merge with defaults for missing keys
            return {**DEFAULT_CONFIG, **config}
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], local: bool = False):
    """Saves config. If local is True or local config exists, save locally."""
    path = LOCAL_CONFIG_DIR / "config.json" if (local or (LOCAL_CONFIG_DIR / "config.json").exists()) else GLOBAL_CONFIG_DIR / "config.json"
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

def update_config(key: str, value: Any, local: bool = False):
    config = load_config()
    config[key] = value
    save_config(config, local=local)

def get_config_val(key: str) -> Any:
    return load_config().get(key)