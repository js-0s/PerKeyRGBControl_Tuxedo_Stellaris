import time
import random
import colorsys
import threading
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pyrgb_keyboard import KeyboardManager


class RandomColorAnimation:
    def __init__(
        self,
        keyboard: KeyboardManager,
        update_callback: Callable[[], None] | None = None,
    ):
        self.keyboard: KeyboardManager = keyboard
        self.update_callback: Callable[[], None] | None = update_callback
        self.thread: threading.Thread | None = None
        self._active: bool = False

    def start(self) -> None:
        if not self._active:
            self._active = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        self._active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    @property
    def is_active(self) -> bool:
        return self._active

    def _run(self) -> None:
        while self._active:
            time.sleep(0.5)
            all_keys = [
                key for row in self.keyboard.keys for key in row if key is not None
            ]
            if all_keys:
                random_key = random.choice(all_keys)
                random_key.random_color()
                if self.update_callback:
                    self.update_callback()


class WaveAnimation:
    def __init__(
        self,
        keyboard: KeyboardManager,
        update_callback: Callable[[], None] | None = None,
    ):
        self.keyboard: KeyboardManager = keyboard
        self.update_callback: Callable[[], None] | None = update_callback
        self.thread: threading.Thread | None = None
        self._active: bool = False
        num_columns = len(self.keyboard.keys[0]) if self.keyboard.keys else 0
        self.colors: list[list[int]] = []
        for col in range(num_columns):
            color_found = False
            for row in self.keyboard.keys:
                if col < len(row) and row[col] is not None:
                    key = row[col]
                    if key is None:
                        continue
                    self.colors.append(key.color.copy())
                    color_found = True
                    break
            if not color_found:
                self.colors.append([0, 0, 0])
        self.hue: float = 0.0

    def start(self) -> None:
        if not self._active:
            self._active = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        self._active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    @property
    def is_active(self) -> bool:
        return self._active

    def _run(self) -> None:
        while self._active:
            time.sleep(0.1)
            rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            new_color = [int(c * 255) for c in rgb]
            self.hue = (self.hue + 0.1) % 1.0
            self.colors = [new_color] + self.colors[:-1]
            for row in self.keyboard.keys:
                for col_idx, key in enumerate(row):
                    if key is not None:
                        key.set_color(self.colors[col_idx])
            if self.update_callback:
                self.update_callback()
