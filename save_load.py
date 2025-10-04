from __future__ import annotations

import configparser
from typing import TypeAlias

from constants import key_names
from pyrgb_core import Color

# ButtonColors maps (x, y) -> Color
ButtonColors: TypeAlias = dict[tuple[int, int], Color]


def _get_name_to_pos() -> dict[str, tuple[int, int]]:
    """
    Creates a mapping from ISO key names to their (x, y) positions.
    Uses the first occurrence if names are duplicated.
    """
    name_to_pos: dict[str, tuple[int, int]] = {}
    for y, row in enumerate(key_names):
        for x, name in enumerate(row):
            if name and name not in name_to_pos:
                name_to_pos[name] = (x, y)
    return name_to_pos


def save(
    colors: list[list[Color | None]],
    filename: str,
    lightbar_color: Color | None = None,
    lightbar_brightness: int = -1,
    backlight_brightness: int = -1,
) -> None:
    """
    Saves the colors of the buttons, lightbar color and brightness, and backlight brightness to an INI file.

    The `colors` parameter is expected to be a nested list matching the keyboard
    layout (rows of columns). Each element may be:
      - a `Color` instance
      - a sequence of three ints (e.g. [r, g, b])
      - or None for empty positions

    The INI file format: each button section contains a "color" entry with "r,g,b".
    If lightbar_color is provided, adds a [lightbar] section with "color" and "brightness".
    If backlight_brightness is provided (>=0), adds a [backlight] section with "brightness".
    """
    config = configparser.ConfigParser()
    for y, row in enumerate(colors):
        for x, color in enumerate(row):
            if color is not None:
                section = (
                    key_names[y][x]
                    if y < len(key_names) and x < len(key_names[y])
                    else ""
                )
                if section == "":
                    # Skip unnamed entries to remain consistent with previous behavior
                    continue

                r, g, b = color.r, color.g, color.b

                config.add_section(section)
                color_str = f"{r},{g},{b}"
                config.set(section, "color", color_str)

    # Add lightbar section if provided
    if lightbar_color is not None:
        config.add_section("lightbar")
        config.set(
            "lightbar",
            "color",
            f"{lightbar_color.r},{lightbar_color.g},{lightbar_color.b}",
        )
        if lightbar_brightness >= 0:
            config.set("lightbar", "brightness", str(lightbar_brightness))

    # Add backlight section if provided
    if backlight_brightness >= 0:
        config.add_section("backlight")
        config.set("backlight", "brightness", str(backlight_brightness))

    with open(filename, "w") as configfile:
        config.write(configfile)


def load(filename: str) -> tuple[ButtonColors, Color | None, int, int]:
    """
    Loads the button colors, lightbar color and brightness, and backlight brightness from an INI file.

    Returns a tuple: (button_colors, lightbar_color, lightbar_brightness, backlight_brightness)
    where button_colors is a dict mapping (x, y) -> Color,
    lightbar_color is Color or None,
    lightbar_brightness is int (-1 if not found),
    backlight_brightness is int (-1 if not found).
    Sections are matched to keyboard positions using the mapping derived from `constants.key_names`.
    The function tolerates malformed values by skipping invalid entries.
    """
    config = configparser.ConfigParser()
    _ = config.read(filename)
    colors: ButtonColors = {}
    sections: list[str] = config.sections()
    name_to_pos = _get_name_to_pos()
    lightbar_color: Color | None = None
    lightbar_brightness: int = -1
    backlight_brightness: int = -1
    for section in sections:
        if section == "lightbar":
            try:
                color_str = config.get(section, "color")
                parts = list(map(int, color_str.split(",")))
                if len(parts) == 3:
                    lightbar_color = Color(parts[0], parts[1], parts[2])
                brightness_str = config.get(section, "brightness")
                lightbar_brightness = int(brightness_str)
            except (ValueError, configparser.NoOptionError):
                pass  # Skip malformed
        elif section == "backlight":
            try:
                brightness_str = config.get(section, "brightness")
                backlight_brightness = int(brightness_str)
            except (ValueError, configparser.NoOptionError):
                pass  # Skip malformed
        elif section in name_to_pos:
            x, y = name_to_pos[section]
            try:
                color_str = config.get(section, "color")
                parts = list(map(int, color_str.split(",")))
                if len(parts) == 3:
                    # Construct Color (this will clamp values to 0-255)
                    colors[(x, y)] = Color(parts[0], parts[1], parts[2])
            except (ValueError, configparser.NoOptionError):
                # Skip malformed entries
                continue
        else:
            # Unknown section name: ignore for compatibility
            continue
    return colors, lightbar_color, lightbar_brightness, backlight_brightness
