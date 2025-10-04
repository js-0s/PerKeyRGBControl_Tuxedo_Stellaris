"""
Core module for RGB keyboard control.

This module provides low-level abstractions for interacting with LED devices
exposed via the Linux sysfs interface. It includes color representations,
device management, and utilities for reading/writing RGB values and brightness.
Requires root privileges for sysfs writes.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Self, TypeAlias, override

# Note: Writing to sysfs LED files requires root privileges.
# The application will check for root before attempting writes.

RGB: TypeAlias = tuple[int, int, int]


def _clamp_component(value: int) -> int:
    """
    Clamp a single RGB component to the 0-255 integer range.
    Accepts numbers or numeric-looking strings; converts to int.
    Raises TypeError if conversion to int is not possible.
    """
    try:
        iv = int(value)
    except Exception as e:
        raise TypeError("RGB components must be convertible to int") from e
    if iv < 0:
        return 0
    if iv > 255:
        return 255
    return iv


def rgb2hex(r: int, g: int, b: int) -> str:
    """Convert an (r, g, b) triple to a hex color string."""
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


@dataclass(frozen=True)
class Color:
    """
    Immutable RGB color container.

    - Components are integers in the 0-255 range.
    - Construction will clamp values automatically.
    - Provide convenience methods for conversion and generation.
    """

    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        # Enforce/clamp and ensure values are ints even if strings were passed.
        object.__setattr__(self, "r", _clamp_component(self.r))
        object.__setattr__(self, "g", _clamp_component(self.g))
        object.__setattr__(self, "b", _clamp_component(self.b))

    @classmethod
    def from_sequence(cls, seq: list[int] | list[str]) -> "Color":
        """
        Create a Color from a sequence (list/tuple) of three components.
        Components may be ints or strings convertible to ints. Values are clamped.
        """
        if len(seq) != 3:
            raise ValueError("sequence must be of length 3 (r, g, b)")
        return cls(int(seq[0]), int(seq[1]), int(seq[2]))

    @classmethod
    def random(cls) -> "Color":
        """Return a random Color with components in 0-255."""
        return cls(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create a Color from a hex string like '#ff0000'."""
        if not (hex_str.startswith("#") and len(hex_str) == 7):
            raise ValueError("Hex color must be in format '#rrggbb'")
        try:
            r = int(hex_str[1:3], 16)
            g = int(hex_str[3:5], 16)
            b = int(hex_str[5:7], 16)
        except ValueError:
            raise ValueError("Invalid hex color string")
        return cls(r, g, b)

    def as_tuple(self) -> RGB:
        return (self.r, self.g, self.b)

    def as_hex(self) -> str:
        return rgb2hex(self.r, self.g, self.b)

    def __iter__(self):
        # Allow unpacking: r, g, b = color
        return iter((self.r, self.g, self.b))


@dataclass
class LEDDevice:
    """
       Generic abstraction for an RGB-capable LED exposed via sysfs under
       `/sys/class/leds/<name>/`.

       - Color is read/written through `multi_intensity` as three integers.
         Internal representation is an immutable `Color`.
       -
    Brightness is read/written through `brightness` when present.
         The `rgb:lightbar` device enforces a 0-100 brightness range.
    """

    base_path: str
    color: Color | None = None
    brightness: int = -1
    _brightness_max: int = 50

    def __post_init__(self) -> None:
        # Determine device-specific brightness constraints.
        if self.base_path.rstrip("/").endswith("rgb:lightbar"):
            self._brightness_max = 100
        else:
            self._brightness_max = 50

        # Attempt to populate initial state, but don't hard-fail if sysfs is
        # temporarily unavailable. Callers can call the getters to force errors.
        try:
            self.color = self.get_color()
        except Exception:
            self.color = Color(0, 0, 0)
        try:
            self.brightness = self.get_brightness()
        except Exception:
            self.brightness = -1

    # --- internal path helpers ---
    def _multi_intensity_path(self) -> str:
        return f"{self.base_path}/multi_intensity"

    def _brightness_path(self) -> str:
        return f"{self.base_path}/brightness"

    # --- color APIs ---
    def get_color(self) -> Color:
        """
        Read the current RGB intensities from `multi_intensity`.
        Returns an immutable `Color`. Raises RuntimeError if the sysfs entry is missing or malformed.
        """
        path = self._multi_intensity_path()
        try:
            with open(path, "r") as fh:
                content = fh.read().strip()
        except FileNotFoundError as e:
            raise RuntimeError(f"multi_intensity not found at {path}") from e

        if not content:
            raise RuntimeError(f"multi_intensity at {path} is empty")

        parts = content.split()
        if len(parts) < 3:
            raise RuntimeError(f"Unexpected format for multi_intensity: '{content}'")

        # Use Color.from_sequence which clamps and converts values.
        try:
            color = Color.from_sequence(parts[:3])
        except Exception as e:
            raise RuntimeError(f"Invalid values in multi_intensity: '{content}'") from e

        self.color = color
        return color

    def set_color(self, rgb: Color) -> None:
        """
        Set the RGB intensities by writing three integers separated by spaces to `multi_intensity`.
        Accepts:
         - a `Color` instance
         - a sequence (list/tuple) of three components (ints or strings convertible to int)
        Components are clamped to 0-255 and stored as an immutable `Color`.
        """
        color = rgb

        path = self._multi_intensity_path()
        try:
            with open(path, "w") as fh:
                _ = fh.write(f"{color.r} {color.g} {color.b}")
        except FileNotFoundError as e:
            raise RuntimeError(f"multi_intensity not found at {path}") from e
        except PermissionError:
            print("Warn: cannot modify sysfs as user")
        self.color = color

    def random_color(self) -> None:
        """Set a random color on the device."""
        self.set_color(Color.random())

    def to_hex(self) -> str:
        """Return the current color as a hex string."""
        if self.color is None:
            _ = self.get_color()
        if self.color is None:
            return "#000000"
        return self.color.as_hex()

    # --- brightness APIs ---
    def get_brightness(self) -> int:
        """
        Read the device brightness from `brightness` and return it as an int.
        Raises RuntimeError if the brightness entry is missing or malformed.
        """
        path = self._brightness_path()
        try:
            with open(path, "r") as fh:
                content = fh.read().strip()
        except FileNotFoundError as e:
            raise RuntimeError(f"brightness not found at {path}") from e

        if not content:
            raise RuntimeError(f"brightness at {path} is empty")

        try:
            val = int(content)
        except ValueError as e:
            raise RuntimeError(f"Non-integer value in brightness: '{content}'") from e

        self.brightness = val
        return val

    def set_brightness(self, brightness: int) -> None:
        """
        Set the device brightness by writing to `brightness`.

        - Requires an integer input >= 0.
        - For the lightbar device, enforces a 0-100 maximum.
        """
        if brightness < 0:
            raise ValueError("brightness must be >= 0")

        if getattr(self, "_brightness_max", None) is not None:
            max_val = self._brightness_max
            if brightness > max_val:
                raise ValueError(
                    f"brightness must be <= {max_val} for device {self.base_path!r}"
                )

        path = self._brightness_path()
        try:
            with open(path, "w") as fh:
                _ = fh.write(str(brightness))
        except FileNotFoundError as e:
            raise RuntimeError(f"brightness not found at {path}") from e
        except PermissionError:
            print("Warn: cannot modify sysfs as user")

        self.brightness = brightness

    # --- convenience / factories ---
    @classmethod
    def for_key(cls, nom: int) -> Self:
        """
        Create an LEDDevice that represents a keyboard key (or the keyboard backlight).
        - nom == -1 -> main keyboard backlight at `/sys/class/leds/rgb:kbd_backlight`
        - nom >= 0 -> per-key LED at `/sys/class/leds/rgb:kbd_backlight_<nom>`
        """
        if nom == -1:
            base = "/sys/class/leds/rgb:kbd_backlight"
        else:
            base = f"/sys/class/leds/rgb:kbd_backlight_{nom}"
        return cls(base)

    @classmethod
    def lightbar(cls) -> Self:
        """
        Create an LEDDevice for the system lightbar exposed at `/sys/class/leds/rgb:lightbar`.
        This factory ensures the lightbar device enforces a 0-100 brightness maximum.
        """
        return cls("/sys/class/leds/rgb:lightbar")

    @property
    def supported(self) -> bool:
        """Check if the sysfs LED device is available."""
        return os.path.exists(self.base_path)

    @override
    def __repr__(self) -> str:
        return (
            f"LEDDevice(base_path={self.base_path!r}, "
            f"color={getattr(self, 'color', None)!r}, "
            f"brightness={getattr(self, 'brightness', None)!r})"
        )
