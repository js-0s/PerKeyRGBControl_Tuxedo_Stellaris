# pyrgb/animations.py
"""
Animations for controlling keyboard LED devices.

This module provides three simple animations:
- RandomColorAnimation: periodically picks a random present key and assigns it
  a random color.
- WaveAnimation: produces a column-based color wave that moves across the keyboard.
- PulseAnimation: pulses the brightness of all keys up and down.

All animations run in background threads and call an optional `update_callback`
to let the UI refresh after changes. Errors writing to individual devices are
caught and suppressed so the animation threads remain alive.
"""

import time
import random
import colorsys
import math
import threading
from typing import TYPE_CHECKING, Callable

from pyrgb_core import Color

if TYPE_CHECKING:
    # Import for type checking only to avoid runtime import cycles.
    from pyrgb_keyboard import KeyboardManager
    from pyrgb_core import LEDDevice


class RandomColorAnimation:
    """
    Periodically sets a random color on a random present key.

    Parameters
    - keyboard: KeyboardManager — the keyboard manager with the `keys` grid.
    - update_callback: optional callable invoked after a color change to allow
      the UI to refresh.
    - sleep_time: time in seconds to sleep between color changes (default 0.5).
    """

    def __init__(
        self,
        keyboard: "KeyboardManager",
        update_callback: Callable[[], None] | None = None,
        sleep_time: float = 0.5,
    ) -> None:
        self.keyboard: "KeyboardManager" = keyboard
        self.update_callback: Callable[[], None] | None = update_callback
        self.sleep_time: float = sleep_time
        self.thread: threading.Thread | None = None
        self._active: bool = False

    def start(self) -> None:
        """Start the background animation thread (no-op if already running)."""
        if not self._active:
            self._active = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Stop the animation and join the thread if it is running."""
        self._active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    @property
    def is_active(self) -> bool:
        """Return whether the animation is currently active."""
        return self._active

    def _run(self) -> None:
        """Internal loop that performs the random color changes."""
        while self._active:
            time.sleep(self.sleep_time)

            # Collect present devices
            all_devices = [
                dev for row in self.keyboard.keys for dev in row if dev is not None
            ]
            if not all_devices:
                continue

            device = random.choice(all_devices)
            try:
                # Set a random color (Color.random() clamps values)
                device.set_color(Color.random())
            except Exception:
                # Ignore individual device write failures and continue animation
                continue

            if self.update_callback:
                try:
                    self.update_callback()
                except Exception:
                    # Don't let UI callback errors kill the animation thread
                    pass


class WaveAnimation:
    """
    Column-based wave animation.

    - Builds a per-column list of `Color` objects. Each tick, a new color is
      generated from an HSV hue, the list is rotated, and the new colors are
      written to the keys in each column.
    - Safe for missing keys: missing devices are skipped.
    - sleep_time: time in seconds to sleep between wave steps (default 0.1).
    """

    def __init__(
        self,
        keyboard: "KeyboardManager",
        update_callback: Callable[[], None] | None = None,
        sleep_time: float = 0.1,
    ) -> None:
        self.keyboard: "KeyboardManager" = keyboard
        self.update_callback: Callable[[], None] | None = update_callback
        self.sleep_time: float = sleep_time
        self.thread: threading.Thread | None = None
        self._active: bool = False

        # Determine number of columns from the keyboard layout.
        num_columns = len(self.keyboard.keys[0]) if self.keyboard.keys else 0

        # Initialize per-column colors. For each column, pick the first present
        # device's color; fall back to black if none present or on error.
        self.colors: list[Color] = []
        for col in range(num_columns):
            found_color: Color | None = None
            for row in self.keyboard.keys:
                if col < len(row) and row[col] is not None:
                    dev = row[col]
                    if dev is None:
                        found_color = Color(0, 0, 0)
                        break
                    try:
                        found_color = (
                            dev.color if dev.color is not None else dev.get_color()
                        )
                    except Exception:
                        found_color = Color(0, 0, 0)
                    break
            if found_color is None:
                found_color = Color(0, 0, 0)
            self.colors.append(found_color)

        # Starting hue for the wave (0.0 - 1.0)
        self.hue: float = 0.0

    def start(self) -> None:
        """Start the wave animation thread."""
        if not self._active:
            self._active = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Stop the animation and join the thread if running."""
        self._active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    @property
    def is_active(self) -> bool:
        """Return whether the animation is currently active."""
        return self._active

    def _run(self) -> None:
        """Internal loop that advances the wave and writes colors to keys."""
        while self._active:
            time.sleep(self.sleep_time)

            # Generate next color from HSV
            rgbf = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            new_color = Color(
                int(rgbf[0] * 255), int(rgbf[1] * 255), int(rgbf[2] * 255)
            )
            # Advance hue a small amount each tick
            self.hue = (self.hue + 0.05) % 1.0

            # Rotate the per-column color buffer
            if self.colors:
                self.colors = [new_color] + self.colors[:-1]

            # Apply column color to each key in that column
            for row in self.keyboard.keys:
                for col_idx, dev in enumerate(row):
                    if dev is None:
                        continue
                    if col_idx >= len(self.colors):
                        # No color defined for this column — skip
                        continue
                    try:
                        # LEDDevice.set_color accepts a Color directly
                        dev.set_color(self.colors[col_idx])
                    except Exception:
                        # Ignore write errors for individual keys
                        continue

            # Notify the UI once per tick (if provided)
            if self.update_callback:
                try:
                    self.update_callback()
                except Exception:
                    # Ignore callback errors so the animation continues
                    pass


class PulseAnimation:
    """
    Brightness pulse animation for a list of LED devices.

    - Cycles the brightness of the devices from 0 to max_brightness and back,
      using a sine wave for smooth pulsing.
    - Safe for missing devices: errors are ignored.
    - devices: list of LEDDevice instances to pulse.
    - max_brightness: maximum brightness value for the devices.
    - sleep_time: time in seconds to sleep between pulse steps (default 0.1).
    """

    def __init__(
        self,
        devices: list[LEDDevice],
        max_brightness: int,
        update_callback: Callable[[], None] | None = None,
        sleep_time: float = 0.1,
    ) -> None:
        self.devices: list["LEDDevice"] = devices
        self.max_brightness: int = max_brightness
        self.update_callback: Callable[[], None] | None = update_callback
        self.sleep_time: float = sleep_time
        self.thread: threading.Thread | None = None
        self._active: bool = False
        self.phase: float = 0.0

    def start(self) -> None:
        """Start the pulse animation thread."""
        if not self._active:
            self._active = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Stop the animation and join the thread if running."""
        self._active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    @property
    def is_active(self) -> bool:
        """Return whether the animation is currently active."""
        return self._active

    def _run(self) -> None:
        """Internal loop that pulses brightness for the devices."""
        while self._active:
            time.sleep(self.sleep_time)

            # Calculate brightness using sine wave (0 to max_brightness)
            brightness = int((math.sin(self.phase) + 1) / 2 * self.max_brightness)
            self.phase += 0.1

            # Apply brightness to all devices
            for dev in self.devices:
                try:
                    dev.set_brightness(brightness)
                except Exception:
                    # Ignore write errors for individual devices
                    continue

            # Notify the UI once per tick (if provided)
            if self.update_callback:
                try:
                    self.update_callback()
                except Exception:
                    # Ignore callback errors so the animation continues
                    pass
