"""
Utility script to print driver information from the current iRacing
session.

This tool connects to iRacing using ``pyirsdk`` and retrieves the
``DriverInfo`` structure, which contains details about all drivers in
the session.  It then prints each driver's ``CarIdx``, ``UserID``,
``UserName`` and other optional fields such as ``CarNumber`` and
``CarClassName``.  You can run this script while you are in any iRacing
session (practice, qualifying or race) to gather the information
needed to build your pro driver list.

Example usage:

    python scripts/list_drivers.py

The script will poll the SDK every half‑second until it can connect.
If iRacing is not running it will wait and try again.

Note: You must have ``pyirsdk`` installed and iRacing running on the
same machine.  Run this script from a terminal or command prompt.
"""

from __future__ import annotations

import time

try:
    import irsdk  # type: ignore
except ImportError as exc:
    raise ImportError(
        "pyirsdk is required to run this script. Install with 'pip install pyirsdk'."
    ) from exc


def main() -> None:
    ir = irsdk.IRSDK()
    ir.startup()
    print("Waiting for iRacing… press Ctrl+C to exit.")
    try:
        while True:
            if ir.is_initialized and ir.is_connected:
                try:
                    driver_info = ir["DriverInfo"]
                    drivers = driver_info.get("Drivers", []) if isinstance(driver_info, dict) else []
                except KeyError:
                    drivers = []

                if not drivers:
                    print("No driver data available yet…")
                else:
                    print(f"Found {len(drivers)} drivers:")
                    for drv in drivers:
                        try:
                            car_idx = drv.get("CarIdx", "?")
                            user_id = drv.get("UserID", "?")
                            name = drv.get("UserName", "?")
                            car_num = drv.get("CarNumber", "?")
                            car_class = drv.get("CarClassName", "?")
                            print(
                                f"CarIdx={car_idx}, UserID={user_id}, Name='{name}', "
                                f"CarNumber='{car_num}', CarClass='{car_class}'"
                            )
                        except Exception:
                            continue
                    # Exit after printing once
                    return
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting.")


if __name__ == "__main__":
    main()