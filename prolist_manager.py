"""
Pro driver list management.

This module is responsible for downloading and caching the list of
professional drivers.  The list is expected to be provided as a JSON
array of objects, where each object contains at least ``UserID`` (an
integer) and ``Name`` (a string).  The remote list is retrieved
periodically (default: once per day) and stored locally so that the
application continues to function when offline.

The remote URL should be set via the ``PRO_LIST_URL`` constant.  By
default it points to a placeholder GitHub raw URL; update this value
to point at the actual JSON file once it has been created.  The
structure of the JSON file should resemble:

```
[
  {"UserID": 123456, "Name": "John Doe"},
  {"UserID": 789012, "Name": "Jane Smith"},
  ...
]
```

If the remote list cannot be retrieved (due to network issues or
unavailability) and no cache exists, the module returns an empty
dictionary, which results in the overlay showing no pro drivers.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict

import requests

from .config_manager import (
    get_last_pro_update,
    set_last_pro_update,
    _ensure_config_dir,
)

# Remote location of the pro driver list.  Replace "username" and
# repository name with your own GitHub account and repository that
# hosts the JSON file.  The file should be publicly accessible.
PRO_LIST_URL = (
    "https://raw.githubusercontent.com/yourusername/RaceMatesProDrivers/main/prodrivers.json"
)

PRO_CACHE_FILENAME = "pro_drivers_cache.json"


def _get_cache_path() -> Path:
    """Return the path to the cached pro driver list file."""
    return _ensure_config_dir() / PRO_CACHE_FILENAME


def _read_cache() -> Dict[int, str]:
    """Read the cached pro driver list.

    Returns a dictionary mapping ``UserID`` to ``Name``.  If the cache
    file does not exist or cannot be parsed, an empty dict is returned.
    """
    path = _get_cache_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure keys are integers
        return {int(k): str(v) for k, v in data.items()}
    except Exception:
        return {}


def _write_cache(pro_map: Dict[int, str]) -> None:
    """Write the pro driver map to the cache file."""
    path = _get_cache_path()
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in pro_map.items()}, f, indent=2)
    except Exception:
        pass


def fetch_and_cache_pro_list() -> Dict[int, str]:
    """Download the pro driver list from ``PRO_LIST_URL`` and cache it.

    Returns a dictionary mapping ``UserID`` to ``Name``.  If the
    download fails, the function falls back to whatever is stored in
    the local cache.
    """
    try:
        response = requests.get(PRO_LIST_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        pro_map: Dict[int, str] = {}
        for item in data:
            try:
                uid = int(item["UserID"])
                name = str(item["Name"])
                pro_map[uid] = name
            except (KeyError, ValueError, TypeError):
                continue
        # Cache the list and update timestamp
        _write_cache(pro_map)
        set_last_pro_update(time.time())
        return pro_map
    except Exception:
        # On error, return cached values if available
        return _read_cache()


def get_pro_list(force_refresh: bool = False) -> Dict[int, str]:
    """Return the pro driver map, refreshing from remote if needed.

    By default this function checks whether 24 hours have elapsed
    since the last successful refresh.  Set ``force_refresh=True`` to
    bypass this check.
    """
    # Determine if we need to refresh
    refresh_interval = 24 * 3600  # one day in seconds
    last_update = get_last_pro_update()
    if force_refresh or (time.time() - last_update) > refresh_interval:
        pro_map = fetch_and_cache_pro_list()
        if pro_map:
            return pro_map
    # Fallback to cache
    return _read_cache()


def is_pro_driver(user_id: int) -> bool:
    """Return True if the given ``user_id`` belongs to a pro driver."""
    pro_map = get_pro_list()
    return int(user_id) in pro_map


def get_pro_name(user_id: int) -> str:
    """Return the name of the pro driver with the given ``user_id``.

    If the user is not a pro driver or the name is unavailable, an
    empty string is returned.
    """
    pro_map = get_pro_list()
    return pro_map.get(int(user_id), "")