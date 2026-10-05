# Setup before Friday's class

Please do this **before** the class starts. It takes about 10–15 minutes, mostly waiting for downloads. At the end, you will run the first two notebooks to make sure everything works.

You will need:

- Python 3.12, 3.13 or 3.14. **Not 3.15**: it is brand new and some packages don't support it yet.
- The course folder. Go to <https://github.com/pooyasf/drone-example>, click the green **Code** button, then **Download ZIP**, and unzip it. You get a folder called `drone-example-main`. (If you use git: `git clone https://github.com/pooyasf/drone-example.git`, which gives a folder called `drone-example`.)

Pick your operating system below. You type every command into a terminal; press Enter after each one.

---

## macOS

1. **Install Python.** Download and run the [Python 3.14 macOS installer](https://www.python.org/ftp/python/3.14.8/python-3.14.8-macos11.pkg). When it finishes, double-click **Install Certificates.command** in the Python folder that opens.
2. **Open Terminal** (Cmd+Space, type `Terminal`, press Enter).
3. **Go to the course folder.** Type `cd ` (with a trailing space), drag the `drone-example-main` folder from Finder into the Terminal window, and press Enter.
4. **Create an environment and install the packages:**
   ```bash
   python3 -m venv .venv
   ```
   ```bash
   source .venv/bin/activate
   ```
   ```bash
   pip install -r requirements.txt
   ```

## Linux (Ubuntu/Debian)

1. **Install Python and the libraries the drone window needs:**
   ```bash
   sudo apt update && sudo apt install python3 python3-venv python3-pip libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0
   ```
   (Fedora: `sudo dnf install python3 python3-pip`. Other distributions: install Python 3 with `venv` and `pip`.)
2. **Open a terminal in the course folder:**
   ```bash
   cd ~/Downloads/drone-example-main
   ```
   (Change the path to wherever you unzipped it.)
3. **Create an environment and install the packages:**
   ```bash
   python3 -m venv .venv
   ```
   ```bash
   source .venv/bin/activate
   ```
   ```bash
   pip install -r requirements.txt
   ```

## Windows

1. **Install Python.** Download and run the [Python 3.14 Windows installer](https://www.python.org/ftp/python/3.14.8/python-3.14.8-amd64.exe) (this one also works on ARM/Snapdragon laptops). On the first screen of the installer, **tick "Add python.exe to PATH"**, then click *Install Now*.
2. **Unzip the course folder.** Right-click the downloaded zip, choose *Extract All*, and extract it to your user folder, e.g. `C:\Users\<your name>\drone-example-main`. Don't work inside the zip, and avoid OneDrive-synced folders (Desktop and Documents often are): syncing the installed packages is slow and can break them.
3. **Open the course folder in Command Prompt.** Open the extracted `drone-example-main` folder in File Explorer, click the address bar, type `cmd`, and press Enter. Use Command Prompt, not PowerShell (see Troubleshooting).
4. **Create an environment and install the packages:**
   ```bat
   py -m venv .venv
   ```
   ```bat
   .venv\Scripts\activate
   ```
   ```bat
   pip install -r requirements.txt
   ```

## Using Anaconda instead?

If you already use Anaconda or Miniconda, you can skip the steps above. In the course folder, run:

```bash
conda env create -f environment.yml
```
```bash
conda activate dropship
```

---

## Test your setup: run the first two notebooks

Each time you open a new terminal, go to the course folder and activate the environment first:

| Setup | Activate |
|---|---|
| macOS / Linux | `source .venv/bin/activate` |
| Windows | `.venv\Scripts\activate` |
| Anaconda | `conda activate dropship` |

Then start Jupyter:

```bash
jupyter lab
```

Your browser opens with the course files on the left.

1. **`student0_example_notebook.ipynb`:** open it and run every cell (menu *Run → Run All Cells*). You should see printed output and two plots.
2. **`student1_keyboard.ipynb`:** open it and run the cells one by one with Shift+Enter. A separate window with the drone opens. Click on that window and fly the drone with the **W A S D** keys, then press **Esc** to stop.

If both work, you're ready for Friday. If a cell shows a red error message, see Troubleshooting below.

## Troubleshooting

- **`python3` / `py` not found:** Python isn't installed, or (Windows) "Add to PATH" wasn't ticked. Re-run the installer, choose *Modify*, and enable it, then open a new terminal.
- **Windows: "running scripts is disabled on this system" when activating:** you're in PowerShell. Type `cmd`, press Enter, and run the activate command again.
- **Windows: `py` not found:** Python came from the Microsoft Store or another installer. Install it with the link in Windows step 1, then open a new Command Prompt.
- **`pip install` fails with "Could not find a version" or "ResolutionImpossible":** your Python is too new (3.15) or too old. Install Python 3.14 with the link for your OS, delete the `.venv` folder, and redo the install steps. On Windows, if you have several Pythons, create the environment with `py -3.14 -m venv .venv`.
- **`pip install` fails on PyQt5:** run `python -m pip install --upgrade pip`, then try `pip install -r requirements.txt` again.
- **`ModuleNotFoundError` in a notebook:** Jupyter was started without the environment active. Close it, activate the environment (see the table above), and run `jupyter lab` again.
- **Linux: "could not load the Qt platform plugin xcb":** install the libraries from Linux step 1. If you're on Wayland and it still fails, run `export QT_QPA_PLATFORM=xcb` before `jupyter lab`.
- **macOS: SSL / certificate errors during `pip install`:** run *Install Certificates.command* (macOS step 1).
- **Still stuck?** Bring your laptop 15 minutes early, or send us a screenshot of the error.
