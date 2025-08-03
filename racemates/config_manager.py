"""
Configuration management for RaceMates.

This module stores and retrieves application settings such as the
overlay window position and the timestamp of the last pro driver list
update.  Configuration is persisted in JSON format inside the user's
home directory.  On Windows systems the file is placed in
``%APPDATA%\RaceMates\config.json``; on other platforms it falls back
to ``~/.racemates/config.json``.  Although iRacing is a Windows-only
application, this fallback keeps the code portable and easy to test.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Tuple

CONFIG_FILENAME = "config.json"

def _get_config_dir() -> Path:
    """Return the directory where configuration data should be stored."""
    # Use APPDATA on Windows if available
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "RaceMates"
    # Fallback to home directory on non‑Windows platforms
    return Path.home() / ".racemates"


def _ensure_config_dir() -> Path:
    """Ensure the configuration directory exists and return it."""
    cfg_dir = _get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def _get_config_path() -> Path:
    """Return the full path to the configuration file."""
    return _ensure_config_dir() / CONFIG_FILENAME


def _read_config() -> Dict[str, object]:
    """Read the configuration file and return a dictionary.

    If the file does not exist or cannot be parsed, an empty dict is
    returned.
    """
    path = _get_config_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_config(cfg: Dict[str, object]) -> None:
    """Write the configuration dictionary to disk."""
    path = _get_config_path()
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        # Fail silently; configuration errors should not crash the app
        pass


def get_window_position() -> Tuple[int, int]:
    """Return the saved window position as ``(x, y)``.

    If no position has been saved, a default of ``(None, None)`` is
    returned, signalling that the overlay should use its default
    placement.
    """
    cfg = _read_config()
    pos = cfg.get("window_position")
    if isinstance(pos, list) and len(pos) == 2 and all(isinstance(c, int) for c in pos):
        return pos[0], pos[1]
    return None, None


def set_window_position(x: int, y: int) -> None:
    """Persist the overlay window position to the configuration file."""
    cfg = _read_config()
    cfg["window_position"] = [int(x), int(y)]
    _write_config(cfg)


def get_last_pro_update() -> float:
    """Return the UNIX timestamp (seconds) of the last pro driver list update.

    Returns 0 if no timestamp is stored.
    """
    cfg = _read_config()
    ts = cfg.get("last_pro_update")
    if isinstance(ts, (int, float)):
        return float(ts)
    return 0.0


def set_last_pro_update(timestamp: float) -> None:
    """Persist the timestamp of the last pro driver list update."""
    cfg = _read_config()
    cfg["last_pro_update"] = float(timestamp)
    _write_config(cfg)