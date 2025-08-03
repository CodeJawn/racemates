"""
Telemetry listener for RaceMates.

This module provides a ``TelemetryListener`` class which connects to the
iRacing SDK via ``pyirsdk``, monitors the player's session state, and
emits updates about the list of drivers currently in the session.

``TelemetryListener`` runs in its own thread and emits Qt signals
using the PySide6 framework.  The overlay subscribes to these
signals to update its display.  The class is careful not to
interrogate the SDK unless it is connected and initialised.  When
there are no valid telemetry data (e.g. iRacing is not running) the
listener periodically checks again until it can connect.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import List, Dict, Any

from PySide6.QtCore import QObject, Signal

try:
    import irsdk  # type: ignore
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError(
        "The pyirsdk package is required to run RaceMates. "
        "Install it with 'pip install pyirsdk'."
    ) from exc

from .prolist_manager import get_pro_list

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelemetryListener(QObject):
    """Monitor iRacing telemetry and emit driver updates."""

    drivers_updated = Signal(list)  # List[Dict[str, Any]]
    session_active = Signal(bool)  # bool indicating whether the overlay should be shown

    def __init__(self, poll_interval: float = 0.2) -> None:
        """Create a new telemetry listener.

        Args:
            poll_interval: The interval in seconds between telemetry polls.
        """
        super().__init__()
        self.poll_interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self.ir = irsdk.IRSDK()

    def start(self) -> None:
        """Start the telemetry listener thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run, name="TelemetryListener", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the telemetry listener to stop."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        """Worker method that runs in a background thread."""
        # Attempt to initialise the SDK.  This is safe to call repeatedly.
        try:
            self.ir.startup()
        except Exception as e:
            logger.error("Failed to start pyirsdk: %s", e)
            # Wait before retrying
            time.sleep(5)

        while self._running:
            try:
                if not (self.ir.is_initialized and self.ir.is_connected):
                    # Not connected; wait and try again
                    self.session_active.emit(False)
                    time.sleep(self.poll_interval)
                    continue
                # Query session state and on-track status
                try:
                    session_state = self.ir["SessionState"]
                    is_on_track = self.ir["IsOnTrack"]
                except KeyError:
                    # If the variables are missing, treat as inactive
                    session_state = 0
                    is_on_track = 0

                # Determine if we should display the overlay
                active = (session_state == 4) and (is_on_track == 1)
                self.session_active.emit(bool(active))

                if active:
                    # Fetch the list of drivers in session
                    try:
                        driver_info = self.ir["DriverInfo"]
                        drivers = (
                            driver_info.get("Drivers", [])
                            if isinstance(driver_info, dict)
                            else []
                        )
                    except Exception as e:
                        logger.error("Error reading DriverInfo: %s", e)
                        drivers = []

                    pro_map = get_pro_list()
                    pro_drivers: List[Dict[str, Any]] = []
                    for drv in drivers:
                        try:
                            uid = int(drv.get("UserID"))
                            # Only include drivers present in our pro list
                            if uid in pro_map:
                                entry = pro_map[uid]
                                pro_drivers.append(
                                    {
                                        "UserID": uid,
                                        "Name": entry.get("Name", ""),
                                        "Description": entry.get("Description", ""),
                                        "CarNumber": drv.get("CarNumber", ""),
                                    }
                                )
                        except Exception:
                            continue
                    # Emit updated list (could be empty)
                    self.drivers_updated.emit(pro_drivers)
                else:
                    # When not active emit empty list
                    self.drivers_updated.emit([])
                time.sleep(self.poll_interval)
            except Exception as ex:
                logger.error("Unhandled exception in telemetry listener: %s", ex)
                time.sleep(self.poll_interval)
