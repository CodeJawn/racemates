# RaceMates Overlay Application

RaceMates is a lightweight Windows overlay for **iRacing** that tells you when you are racing alongside professional drivers.  It listens to live telemetry via the iRacing SDK to detect when your car is on track and, when a race session is active, displays a small list of any pro drivers sharing the session along with a short description for each driver.

The application uses the open‑source [`pyirsdk`](https://pypi.org/project/pyirsdk/) library to consume iRacing telemetry and [`PySide6`](https://pypi.org/project/PySide6/) for the graphical overlay.  The list of professional drivers is maintained externally as a JSON file hosted on GitHub and is cached locally.

## Features

* **Automatic overlay** – The overlay appears only when you are in a race session and your car is on track (using the `IsOnTrack` telemetry variable【284833693424139†L38-L45】) and hides otherwise.
* **Professional driver detection** – RaceMates reads the `DriverInfo.Drivers` array from iRacing’s telemetry, which contains `UserID` and `UserName` fields for each driver【137150626052293†L145-L152】【137150626052293†L246-L249】.  These IDs are cross‑referenced against a remote list of pro drivers to decide who to display.
* **Driver descriptions** – Each pro driver in your list can include a short description (e.g. `F1`, `Nascar`, `F2`).  The overlay shows this description after the driver’s name.
* **Unobtrusive UI** – The overlay is a frameless, always‑on‑top window with a transparent background.  It lists pro drivers’ car numbers and names in a dark box and highlights them in yellow.  If no pro drivers are present it shows “No pro drivers in session”.  You can drag the overlay anywhere on the screen; its position persists between runs.
* **Cached pro list** – Pro driver information is fetched from a JSON file hosted on GitHub (or another web service) once every 24 hours and cached on disk.  If the network is unavailable, the cached list is used.
* **Portable or installed** – The application can be run directly from source or packaged into a standalone executable using PyInstaller.

## Directory structure

```
your-project/
│
├── README.md             # Setup, usage and testing instructions
├── requirements.txt      # Python dependencies
│
├── racemates/            # The Python package implementing RaceMates
│   ├── __init__.py
│   ├── main.py           # Entry point used when running as a module
│   ├── config_manager.py
│   ├── overlay.py        # Overlay UI implementation
│   ├── prolist_manager.py# Fetches and caches pro driver list (with descriptions)
│   └── telemetry_listener.py# Reads telemetry from iRacing via pyirsdk
│
└── scripts/
    └── list_drivers.py   # Helper script to list all drivers in a session
```

## Getting started

1. **Install Python** – RaceMates requires Python 3.9 or later.  On Windows, download it from [python.org](https://www.python.org/downloads/) and ensure that Python and `pip` are on your `PATH`.

2. **Clone or download the repository**.  If you plan to develop or modify the code, we recommend cloning with Git; otherwise you can download the ZIP and extract it.

3. **Create a virtual environment (optional but recommended)**:

   ```sh
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

4. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

   Dependencies include:

   * `PySide6` – provides the Qt widgets used for the overlay
   * `pyirsdk` – Python wrapper around the iRacing C++ SDK; it exposes the `DriverInfo` array and telemetry variables used by RaceMates【728417220236884†L1-L6】
   * `requests` – used to download the pro driver list from a remote URL

5. **Configure the pro driver list URL** – Open `racemates/prolist_manager.py` and set the `PRO_LIST_URL` constant to the raw URL of your pro driver JSON.  The JSON file should be an array of objects like:

   ```json
   [
     {"UserID": 123456, "Name": "John Doe", "Description": "F1"},
     {"UserID": 789012, "Name": "Jane Smith", "Description": "Past F1"}
   ]
   ```

   You can host this file in a GitHub repository (e.g. `https://raw.githubusercontent.com/CodeJawn/racemates/refs/heads/main/pro_drivers/prodrivers.json`).  GitHub’s raw file hosting supports moderate traffic and is free, making it suitable for a few thousand users.

6. **Run the application**:

   ```sh
   # From the directory containing the 'racemates' folder
   python -m racemates.main
   ```

   When iRacing is running and you join a race session, the overlay will appear in the top‑right corner.  Drag it to reposition it; the location is saved under `%APPDATA%\RaceMates\config.json` (or `~/.racemates` on non‑Windows platforms).

### Testing without pro drivers

It’s unlikely to encounter a professional driver in every session.  To test RaceMates locally you can:

1. **Identify a driver** – Join any session and use the `scripts/list_drivers.py` script to list all drivers currently in your session along with their `UserID` and `UserName`:

   ```sh
   python scripts/list_drivers.py
   ```

   The script will print lines such as:

   ```
   CarIdx=5, UserID=123456, Name='Random Racer', CarNumber='12', CarClass='NASCAR Xfinity'
   ```

2. **Add the driver to your pro list** – Edit the JSON file on your GitHub repository (referenced by `PRO_LIST_URL`) and add an entry for this driver with a description:

   ```json
   [
     {"UserID": 123456, "Name": "Random Racer", "Description": "Test"},
     ...
   ]
   ```

3. **Force a refresh** – Restart RaceMates with the `--refresh-pro` flag to bypass the 24‑hour cache:

   ```sh
   python -m racemates.main --refresh-pro
   ```

   The overlay should now display “Random Racer Test” when you are in session with that driver, allowing you to verify that everything works.

## Packaging as a standalone executable

If you would like a portable `.exe` you can distribute to users, use [PyInstaller](https://pyinstaller.org/).  First install PyInstaller (preferably in a virtual environment):

```sh
pip install pyinstaller
```

Then run the following command from the project root:

```sh
pyinstaller --noconsole --onefile racemates/main.py --name RaceMates
```

* `--onefile` produces a single self‑contained executable (portable).  Omit this flag to create a folder with dependencies.
* `--noconsole` hides the console window.
* `--name RaceMates` names the output executable `RaceMates.exe`.

After PyInstaller finishes, you will find `RaceMates.exe` in the `dist` directory.  This binary includes a minimal Python interpreter, `pyirsdk`, and Qt libraries.  Users can run it without installing Python.  If you want to create an installer (MSI), you can use tools such as [Inno Setup](https://jrsoftware.org/isinfo.php) or PyInstaller’s [–collect‑all and –add‑data options](https://pyinstaller.readthedocs.io/) together with external packaging software.

### Running at Windows startup

To have RaceMates start automatically when Windows boots, you can create a shortcut to `RaceMates.exe` in your Startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`).  Alternatively, use Task Scheduler to run the executable at logon.  A future version of RaceMates could automate this via a settings dialog or registry entry, but currently it is a manual step.

## Extending and contributing

The code is modular and intended for clarity and ease of modification:

* **`telemetry_listener.py`** – Responsible for connecting to iRacing via `pyirsdk`, monitoring session state, and emitting Qt signals with pro driver lists.  It runs on a background thread and checks the `SessionState` variable to see when the session is `4` (race)【284833693424139†L38-L45】 and `IsOnTrack` to ensure the player is on track.  It extracts the `UserID`/`UserName` fields from `DriverInfo.Drivers`【137150626052293†L145-L152】.
* **`prolist_manager.py`** – Downloads the pro driver list (including descriptions) from a remote JSON file and caches it locally.  It refreshes the cache once per day by default.  The cache and last update timestamp are stored in the same directory as other configuration files.
* **`config_manager.py`** – Handles reading and writing configuration data (window position and last pro list refresh time) to a JSON file.  On Windows it stores data under `%APPDATA%\RaceMates`.
* **`overlay.py`** – Implements the transparent overlay using PySide6.  It listens for driver list updates and updates its UI accordingly.  The overlay can be dragged anywhere; releasing the mouse saves the new position via `config_manager`.
* **`main.py`** – Parses command‑line arguments, sets up the application and its components, and starts the Qt event loop.  Pass `--refresh-pro` to force an immediate refresh of the pro driver list on startup.
* **`scripts/list_drivers.py`** – Utility script to list all drivers in the current iRacing session, useful for building or testing your pro driver list.

If you wish to contribute or extend the project (e.g. add a settings dialog, more visual customisation, or integration with other sims), please open a pull request.

## Troubleshooting

* **`ImportError: pyirsdk`** – Install the `pyirsdk` package with `pip install pyirsdk`.  Note that iRacing must be installed and running for `pyirsdk` to connect successfully.
* **Overlay not appearing** – The overlay only shows during a race session when your car is on track.  If you join a practice or qualifying session it remains hidden.  The detection relies on the `SessionState` and `IsOnTrack` telemetry variables; ensure that `pyirsdk` is receiving data and that your Python environment has permission to access telemetry (run as administrator if needed).
* **Pro list never populates** – Make sure the `PRO_LIST_URL` is set correctly and points to a valid JSON file.  The list is refreshed once per day; use the `--refresh-pro` flag when launching to refresh immediately.

## License

RaceMates is provided under the MIT License.  The `pyirsdk` library is licensed under MIT【728417220236884†L1-L6】 and PySide6 under LGPL, allowing you to use and redistribute them in open‑source or proprietary software.
