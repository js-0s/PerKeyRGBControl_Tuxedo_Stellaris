from __future__ import annotations

from typing import TypeAlias

from constants import nom
from pyrgb_core import Key
from save_load import load_buttons, save_buttons

Color: TypeAlias = list[int]


class KeyboardManager:
    def __init__(self) -> None:
        self.keys: list[list[Key | None]] = []
        for row in nom:
            key_row: list[Key | None] = []
            for key_nom in row:
                if key_nom == -1:
                    key_row.append(None)
                else:
                    key_row.append(Key(key_nom))
            self.keys.append(key_row)

    def save_config(self, filename: str) -> None:
        colors = [
            [key.color if key is not None else None for key in row] for row in self.keys
        ]
        save_buttons(colors, filename)

    def load_config(self, filename: str) -> None:
        button_colors = load_buttons(filename)
        for (x, y), color in button_colors.items():
            if y < len(self.keys) and x < len(self.keys[y]):
                key = self.keys[y][x]
                if key is not None:
                    key.set_color(color)
