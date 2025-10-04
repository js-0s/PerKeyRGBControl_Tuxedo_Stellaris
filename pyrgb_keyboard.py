from __future__ import annotations


from constants import nom, key_names
from pyrgb_core import Color, LEDDevice
from save_load import load, save


class KeyboardManager:
    """
    Manage a 2D grid of LED devices representing keyboard keys, lightbar, and backlight.

    - `self.keys` mirrors the layout in `constants.nom` and stores either an
      `LEDDevice` (for a present key) or `None` (for empty positions).
    - `self.lightbar` is the LEDDevice for the system lightbar.
    - `self.backlight` is the LEDDevice for the keyboard backlight.
    - `save_config` / `load_config` interoperate with the INI-based
      save/load helpers in `save_load`, which expect simple 3-component
      sequences (e.g. `[r, g, b]`).
    """

    def __init__(self) -> None:
        # keys[y][x] to match existing code layout (rows of keys)
        self.keys: list[list[LEDDevice | None]] = []
        for row in nom:
            key_row: list[LEDDevice | None] = []
            for key_nom in row:
                if key_nom == -1:
                    key_row.append(None)
                else:
                    # Create an LEDDevice representing the key
                    key_row.append(LEDDevice.for_key(key_nom))
            self.keys.append(key_row)
        self.lightbar: LEDDevice = LEDDevice.lightbar()
        self.backlight: LEDDevice = LEDDevice.for_key(-1)

    def save_config(self, filename: str) -> None:
        """
        Save the current per-key colors, lightbar color/brightness, and backlight brightness to an INI file via `save`.

        The `save` helper expects nested lists of simple 3-element
        sequences or `None`. Convert internal `Color` dataclass instances to
        plain lists of ints before delegating to the helper.
        Automatically includes lightbar and backlight values if the devices are supported.
        """
        colors: list[list[Color | None]] = []
        for row in self.keys:
            row_colors: list[Color | None] = []
            for dev in row:
                if dev is None or dev.color is None:
                    row_colors.append(None)
                else:
                    row_colors.append(dev.color)
            colors.append(row_colors)
        lightbar_color = self.lightbar.color if self.lightbar.supported else None
        lightbar_brightness = (
            self.lightbar.brightness if self.lightbar.supported else -1
        )
        backlight_brightness = (
            self.backlight.brightness if self.backlight.supported else -1
        )
        save(
            colors, filename, lightbar_color, lightbar_brightness, backlight_brightness
        )

    def load_config(self, filename: str) -> tuple[Color | None, int, int]:
        """
        Load per-key colors, lightbar color/brightness, and backlight brightness from an INI file via `load`.

        `load` returns a tuple (button_colors, lightbar_color, lightbar_brightness, backlight_brightness).
        For each button entry, set the color on the corresponding `LEDDevice` if it exists.
        If lightbar/backlight data is present, apply it to the devices.
        Returns the lightbar color, lightbar brightness, and backlight brightness.
        """
        button_colors, lightbar_color, lightbar_brightness, backlight_brightness = load(
            filename
        )
        for (x, y), color in button_colors.items():
            # Ensure coordinates exist in our keyboard layout
            if 0 <= y < len(self.keys) and 0 <= x < len(self.keys[y]):
                dev = self.keys[y][x]
                if dev is not None:
                    # LEDDevice.set_color accepts a sequence of 3 ints or a Color
                    dev.set_color(color)
        if lightbar_color is not None and self.lightbar.supported:
            self.lightbar.set_color(lightbar_color)
        if lightbar_brightness >= 0 and self.lightbar.supported:
            self.lightbar.set_brightness(lightbar_brightness)
        if backlight_brightness >= 0 and self.backlight.supported:
            self.backlight.set_brightness(backlight_brightness)
        return lightbar_color, lightbar_brightness, backlight_brightness

    def get_device(self, x: int, y: int) -> LEDDevice | None:
        """
        Return the `LEDDevice` at (x, y) or `None` if missing or out of bounds.
        """
        if y < 0 or y >= len(self.keys):
            return None
        if x < 0 or x >= len(self.keys[y]):
            return None
        return self.keys[y][x]

    def set_device_color(self, x: int, y: int, color: Color) -> None:
        """
        Convenience: set the color of the device at (x, y) if it exists.
        Accepts any sequence of three integers (or values convertible to int).
        """
        dev = self.get_device(x, y)
        if dev is not None:
            dev.set_color(color)

    def get_device_by_name(self, name: str) -> LEDDevice | None:
        """
        Find the LEDDevice for a key by its name (e.g., "Space").
        Returns None if the name is not found or the device is not present.
        """
        for y, row in enumerate(key_names):
            for x, key_name in enumerate(row):
                if key_name == name:
                    return self.get_device(x, y)
        return None

    def randomize_all(self) -> None:
        """Set a random color on every present key device."""
        for row in self.keys:
            for dev in row:
                if dev is not None:
                    dev.random_color()
