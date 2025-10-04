# pyrgb — Tuxedo Stellaris keyboard RGB control

Overview
--------
`pyrgb` is a small Python application that lets you control per-key RGB lighting on Tuxedo (Stellaris series) keyboards from userspace. It includes:

- A graphical user interface (`pyrgb-tk.py`) built with `tkinter` for interactive per-key color editing, brightness control, animations, and saving/loading color configurations.
- A headless command-line interface (`pyrgb-cli.py`) for saving/loading configs and running simple animations (useful for scripts or SSH).
- A keyboard abstraction layer that reads/writes the LED sysfs interfaces exposed by the Tuxedo kernel driver.

Important: this project was implemented against the LED naming scheme used by the Tuxedo Stellaris series (`rgb:kbd_backlight`, `rgb:kbd_backlight_<n>`) and uses the `tuxedo_driver` kernel module. It may not work on other laptops/keyboards without appropriate kernel support and matching sysfs LED names.

Requirements
------------
- Linux with root access (the application requires direct write access to LED sysfs entries).
- Python 3.14 (the project development used `/usr/bin/python3.14`; other Python 3.x versions may work but were not explicitly tested).
- The Python dependencies listed in `requirements.txt`.
- The Tuxedo kernel module/driver that exposes per-key LEDs (commonly named `tuxedo_driver` or provided by your distribution/Tuxedo's packages). This driver must be installed and loaded so the LED nodes exist under `/sys/class/leds/`.
- For the GUI: X11 (or another display server) and `tkinter` support. `tkcolorpicker` (installed from `requirements.txt`) is used by the UI color picker.

Installation (recommended)
--------------------------
1. Create and activate a virtual environment (recommended for the UI):
```pyrgb/README.md#L1-10
$ python3.14 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

2. Make sure the `tuxedo_driver` (or equivalent) is installed and loaded so `/sys/class/leds/rgb:kbd_backlight*` entries exist:
```pyrgb/README.md#L11-20
# Example (requires appropriate package or kernel module to be present)
# Load the module if installed:
$ sudo modprobe tuxedo_driver
# Or install via your distro's packages / the vendor's instructions.
```

3. The application requires root privileges to read/write the LED sysfs entries. You will run the CLI/UI with `sudo` (see "Running" below).

Tuxedo driver / kernel module
-----------------------------
- The software expects the kernel driver to create LED sysfs entries like:
  - `/sys/class/leds/rgb:kbd_backlight/multi_intensity`
  - `/sys/class/leds/rgb:kbd_backlight_<n>/multi_intensity`
- If those nodes are not present, the program will not be able to read or write colors.
- Install the `tuxedo_driver` (or vendor-provided) package and load it (for example with `modprobe tuxedo_driver`), or follow your distribution/vender instructions to enable per-key LED support.

Running
-------
CLI
- The CLI entrypoint is `pyrgb-cli.py`. It is headless and performs save/load or animations. Because the code requires root, run it with `sudo`:
```pyrgb/README.md#L21-40
$ sudo python3 pyrgb-cli.py save path/to/config.ini
$ sudo python3 pyrgb-cli.py load path/to/config.ini
$ sudo python3 pyrgb-cli.py animate --type random
$ sudo python3 pyrgb-cli.py animate --type wave
$ sudo python3 pyrgb-cli.py animate --type pulse --target keyboard
$ sudo python3 pyrgb-cli.py animate --type pulse --target lightbar --color "#ff0000"
```

GUI
- The graphical UI entrypoint is `pyrgb-tk.py`. It must be run in an X session (or any environment where `tkinter` can create windows). The UI also needs the virtualenv (if you installed dependencies in one) and root privileges:
```pyrgb/README.md#L41-60
# Activate virtualenv if used:
$ source venv/bin/activate

# Run GUI with root (to access /sys/class/leds):
$ sudo python3 pyrgb-tk.py
```

CLI: options and behavior
-------------------------
The CLI provides a small set of commands via argparse:

- `save <filename>`: Reads the current keyboard colors and writes them to an INI file. Usage:
  - `sudo python3 pyrgb-cli.py save mycolors.ini`
- `load <filename>`: Loads an INI color file and applies it to the keyboard:
  - `sudo python3 pyrgb-cli.py load mycolors.ini`
- `animate --type {random,wave,pulse}`: Starts an animation loop that modifies keys until interrupted:
  - `sudo python3 pyrgb-cli.py animate --type random`
  - `sudo python3 pyrgb-cli.py animate --type wave`
  - `sudo python3 pyrgb-cli.py animate --type pulse --target {keyboard,lightbar,key} [--key-name NAME] [--color HEX]`
  - Press Ctrl+C to stop the animation. The animations are implemented in `animations.py`:
    - `random` picks random keys and assigns random colors periodically.
    - `wave` cycles a hue across keyboard columns.
    - `pulse` pulses the brightness of the target (keyboard backlight, lightbar, or specific key) up and down, optionally setting a color first.

GUI: features and controls
--------------------------
The UI (in `pyrgb-tk.py`) exposes an interactive representation of the keyboard with the following capabilities:

- Per-key buttons showing the current LED color.
- Click to select/deselect individual keys (selected keys are highlighted in the UI).
- "Pick Color" — open a color picker and apply the chosen color to all selected keys.
- "Random Color" — assign a random color to each selected key.
- "Select all" / "Deselect all" — quick selection controls.
- Brightness slider — reads and writes the brightness value (via `/sys/class/leds/rgb:kbd_backlight/brightness`).
- "Changing random colours" toggle — start/stop the background random-key animation.
- "Wave Animation" toggle — start/stop the wave animation.
- "Pulse Keyboard" toggle — start/stop the pulse animation for the keyboard backlight.
- "Pulse Lightbar" toggle — start/stop the pulse animation for the lightbar.
- "Save config" / "Load config" — save the current layout/colors to an INI file, or load one and apply it.
- Language selector — switch UI labels using localized names (if available in `constants/localized_names.py`).

Notes & limitations
-------------------
- Root required: The code performs an early check for UID 0 and will exit if not run with root. Always run the CLI/UI with `sudo` or otherwise as root (or modify file permissions at your own risk).
- Hardware compatibility: This project uses LED names tailored to Tuxedo Stellaris keyboards. If your machine exposes different sysfs LED names, you will need either:
  - a kernel driver that exposes the same names, or
  - modify `pyrgb_core.py` and `constants` to match your platform's LED nodes.
- `tuxedo_driver`: Ensure the driver is installed/loaded. Without it, `/sys/class/leds/...` entries will be missing and the app cannot operate.
- Concurrency: Animations run on background threads and directly write to sysfs nodes. Use with caution; avoid conflicting writers to the same node from other tools.

Files of interest
-----------------
- `pyrgb-tk.py` — GUI entrypoint.
- `pyrgb-cli.py` — CLI entrypoint.
- `pyrgb_core.py` — low-level sysfs reads/writes and root check.
- `pyrgb_keyboard.py` — keyboard abstraction (mapping keys to the `Key` objects).
- `animations.py` — random, wave, and pulse animations.
- `requirements.txt` — Python dependencies for the UI (and CLI helpers).
- `constants/` — key naming mapping and localized labels.

Troubleshooting
---------------
- If the program exits immediately with a message about privileges, ensure you run it under `sudo`:
```pyrgb/README.md#L61-80
$ sudo python3 pyrgb-tk.py
# or for CLI
$ sudo python3 pyrgb-cli.py save out.ini
```
- If you see errors about missing LED sysfs paths, verify that the `tuxedo_driver` module is installed and loaded and that entries under `/sys/class/leds/` like `rgb:kbd_backlight` or `rgb:kbd_backlight_0` exist.
- For issues with the color picker or tkinter windows, ensure your Python environment has `tkinter` and `tkcolorpicker` installed (they are listed in `requirements.txt`).

Contributing & changes
----------------------
This is a small utility focused on a specific hardware target. If you want to add support for other keyboards or LED naming schemes, consider:
- Adding a configuration layer to map LED sysfs nodes for different vendors.
- Adding a non-root daemon to mediate LED access and provide a safer IPC interface.

License
-------

MIT

Origin
------

The original implementation was done by https://github.com/RexLightHorus/PerKeyRGBControl_Tuxedo_Stellaris

In order to have more features added and a maintainable codebase the
following LLM models were used:
x-ai/grok-code-fast-1	8.01M Tokens (agentic code changes)
openai/gpt-5-mini-2025-08-07	89K Tokens (Readme)

If anything in this README is unclear or you want help adapting `pyrgb` to a different keyboard/driver, open an issue or ask for guidance and include:
- your kernel module name or `/sys/class/leds` listing,
- the output of `ls /sys/class/leds` and a short description of your platform.
