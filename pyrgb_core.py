from __future__ import annotations

import random
import os

if os.geteuid() != 0:
    # In the beginning the Program has to check whether the user has root privileges
    # because to write to the files of the keys the program needs root privileges
    exit(
        "To control the Keyboard you need root privileges.\nPlease try again, this time using 'sudo' ;) \nExiting."
    )


def rgb2hex(r: int, g: int, b: int) -> str:
    """
    This function converts a rgb value to its corresponding hex value
    """
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def read_brightness() -> int:
    """
    This function returns the current brightness of the keyboard
    """
    with open("/sys/class/leds/rgb:kbd_backlight/brightness", "r") as f:
        return int(f.read())


def set_brightness(brightness: int) -> None:
    """
    This function sets the brightness of the keyboard
    """
    with open("/sys/class/leds/rgb:kbd_backlight/brightness", "w") as f:
        _ = f.write(str(brightness))


class Key:
    def __init__(self, nom_value: int) -> None:
        self.nom: int = nom_value
        self.color: list[int] = self.get_color()

    def get_color(self) -> list[int]:
        if self.nom == -1:
            link = "/sys/class/leds/rgb:kbd_backlight/multi_intensity"
        else:
            link = f"/sys/class/leds/rgb:kbd_backlight_{self.nom}/multi_intensity"
        with open(link, "r") as f:
            string = f.read()
            rgb = string.split(" ")
            return [int(rgb[0]), int(rgb[1]), int(rgb[2])]

    def set_color(self, rgb: list[int]) -> None:
        if self.nom == -1:
            link = "/sys/class/leds/rgb:kbd_backlight/multi_intensity"
        else:
            link = f"/sys/class/leds/rgb:kbd_backlight_{self.nom}/multi_intensity"
        with open(link, "w") as f:
            _ = f.write(f"{rgb[0]} {rgb[1]} {rgb[2]}")
        self.color = rgb

    def random_color(self) -> None:
        self.set_color(
            [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        )
