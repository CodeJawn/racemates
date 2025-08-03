"""
RaceMates application package.

This package provides a modular implementation of the RaceMates overlay
application.  The application connects to the iRacing SDK via the
``pyirsdk`` package, monitors the session to determine when the player
is on track, and displays a small overlay listing any professional
drivers in the current session.  Professional driver information is
fetched from a remote JSON file hosted on GitHub and cached locally
for efficiency.

Modules:

* ``main`` – Entry point for launching the application.
* ``prolist_manager`` – Downloads and caches the list of pro drivers.
* ``telemetry_listener`` – Connects to iRacing and emits driver lists.
* ``overlay`` – Implements the transparent, draggable overlay window.
* ``config_manager`` – Persists configuration such as window position.

To run the application, see ``racemates/README.md`` at the root of
the project.
"""

# Define package-level constants here if desired.  For now this file
# simply marks the directory as a Python package.