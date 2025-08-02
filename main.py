"""
Entry point for the RaceMates application.

This module initialises the Qt application, sets up the telemetry
listener and overlay window, and starts the event loop.  Run this
module directly to launch RaceMates.
"""

from __future__ import annotations

import argparse
import sys
import logging

from PySide6.QtWidgets import QApplication

from .telemetry_listener import TelemetryListener
from .overlay import OverlayWindow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RaceMates overlay application")
    parser.add_argument(
        "--refresh-pro",
        action="store_true",
        help="Force refresh of pro driver list on startup",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.show()  # Show initially; visibility managed by signals

    telemetry_listener = TelemetryListener(poll_interval=0.2)
    # Connect signals
    telemetry_listener.drivers_updated.connect(overlay.update_pro_drivers)
    telemetry_listener.session_active.connect(overlay.setVisible)

    # Start telemetry thread
    telemetry_listener.start()

    try:
        ret = app.exec()
    finally:
        telemetry_listener.stop()
    return ret


if __name__ == "__main__":
    sys.exit(main())