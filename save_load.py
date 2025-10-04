from __future__ import annotations

import configparser
from typing import TypeAlias

from constants import key_names

Color: TypeAlias = list[int]
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


def save_buttons(colors: list[list[Color | None]], filename: str) -> None:
    """
    Saves the colors of the buttons to an INI file.
    Each button is saved under a section named after the button's ISO name from constants,
    or 'button_x_y' if the name is empty.
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
                    continue
                print(f"[{section}] {x} {y} {color}")
                config.add_section(section)
                color_str = ",".join(map(str, color))
                config.set(section, "color", color_str)
    with open(filename, "w") as configfile:
        config.write(configfile)


def load_buttons(filename: str) -> ButtonColors:
    """
    Loads the button colors from an INI file.
    Supports sections named after ISO key names or 'button_x_y'.
    Returns a dictionary with keys as (x, y) tuples and values as [r, g, b] lists.
    """
    config = configparser.ConfigParser()
    _ = config.read(filename)
    colors: ButtonColors = {}
    sections: list[str] = config.sections()
    name_to_pos = _get_name_to_pos()
    for section in sections:
        if section in name_to_pos:
            x, y = name_to_pos[section]
        else:
            continue
        try:
            color_str = config.get(section, "color")
            color = list(map(int, color_str.split(",")))
            if len(color) == 3:
                colors[(x, y)] = color
        except (ValueError, configparser.NoOptionError):
            pass
    return colors
