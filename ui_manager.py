"""
GUI manager for the pyrgb keyboard control application.

This module provides a Tkinter-based graphical user interface for interactively
controlling per-key RGB lighting on supported keyboards. It includes buttons
for each key, color pickers, brightness controls, animations, and save/load
functionality. Requires root privileges for LED control.
"""

from __future__ import annotations
import os
from tkinter import (
    Button,
    IntVar,
    Scale,
    Tk,
    Frame,
    Label,
    OptionMenu,
    StringVar,
    NORMAL,
    DISABLED,
)

# type: ignore
from tkcolorpicker import askcolor
from pyrgb_core import (
    LEDDevice,
    Color,
)
from constants import nom, key_names, localized_names
from tkinter import filedialog
from pyrgb_keyboard import KeyboardManager

from animations import RandomColorAnimation, WaveAnimation, PulseAnimation


class UiManager:
    """
    Manages the Tkinter GUI for keyboard RGB control.

    This class creates and handles all UI elements, including key buttons,
    color pickers, brightness sliders, animation toggles, and save/load buttons.
    It interacts with the KeyboardManager to apply changes to the keyboard LEDs.
    """

    def __init__(self, root: Tk) -> None:
        self.root: Tk = root
        self.selected: list[UiButton] = []
        self.buttons: list[list[UiButton | None]] = []
        self.var: IntVar | None = None
        self.brightness: Scale | None = None
        self.animation_sleep: float = 0.1
        self.animation_sleep_var: IntVar | None = None
        self.animation_sleep_scale: Scale | None = None
        self.keyboard: KeyboardManager = KeyboardManager()
        self.lightbar_btn: Button | None = None
        self.pulse_keyboard_btn: Button | None = None
        self.pulse_lightbar_btn: Button | None = None
        self.frm: Frame = Frame(root)
        self.frm.grid(column=0, row=0)
        self.current_lang: str = "de"
        self.is_root: bool = os.geteuid() == 0
        self.random_toggle_btn: Button | None = None
        self.wave_toggle_btn: Button | None = None
        self.pickColor_btn: Button | None = None
        self.randomColor_btn: Button | None = None
        self.deselectAll_btn: Button | None = None
        self.buttons = self.create_buttons()
        self.random_animation: RandomColorAnimation | None = None
        self.wave_animation: WaveAnimation | None = None
        self.pulse_keyboard_animation: PulseAnimation | None = None
        self.pulse_lightbar_animation: PulseAnimation | None = None
        self.lightbar_var: IntVar | None = None
        self.lightbar_brightness: Scale | None = None
        self.create_brightness()
        self.create_animation_sleep_scale()
        self.create_control_buttons()
        self.update_button_states()

    def create_buttons(self) -> list[list[UiButton | None]]:
        self.buttons = []
        for py, key_row in enumerate(key_names):
            row: list[UiButton | None] = []
            for px, key_name in enumerate(key_row):
                key_device = None
                # keyboard.keys is indexed as [y][x]
                if py < len(self.keyboard.keys) and px < len(self.keyboard.keys[py]):
                    key_device = self.keyboard.keys[py][px]
                if key_name == "Enter" and px < 15:
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            3,
                            2,
                            key_device,
                        )
                    )
                elif key_name == "ShiftRight":
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            3,
                            1,
                            key_device,
                        )
                    )
                elif key_name == "Backspace":
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            3,
                            1,
                            key_device,
                        )
                    )
                elif key_name == "Space":
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            6,
                            1,
                            key_device,
                        )
                    )
                elif key_name == "NumpadAdd" and px > 17:
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            1,
                            2,
                            key_device,
                        )
                    )
                elif key_name == "NumpadEnter" and px > 17:
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            1,
                            2,
                            key_device,
                        )
                    )
                elif key_name == "ControlRight" and px > 6:
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            2,
                            1,
                            key_device,
                        )
                    )
                elif key_name == "Numpad0" and px > 11:
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            2,
                            1,
                            key_device,
                        )
                    )
                elif key_name != "":
                    row.append(
                        UiButton(
                            self,
                            self.frm,
                            px,
                            py,
                            key_name,
                            self.current_lang,
                            key=key_device,
                        )
                    )
                else:
                    row.append(None)
            self.buttons.append(row)
        if self.keyboard.lightbar.supported:
            max_cols = max(len(row) for row in self.buttons if row)
            lightbar_btn = Button(
                self.frm,
                text="Lightbar Color",
                command=self.change_lightbar_color,
                bg=self.keyboard.lightbar.color.as_hex()
                if self.keyboard.lightbar.color
                else "#000000",
            )
            lightbar_btn.grid(
                row=len(self.buttons), column=0, columnspan=max_cols, sticky="ew"
            )
            self.lightbar_btn = lightbar_btn
        return self.buttons

    def selectAll(self) -> None:
        for row in self.buttons:
            for button in row:
                if button is None:
                    continue
                button.select()
        self.update_button_states()

    def deselectAll(self) -> None:
        for row in self.buttons:
            for button in row:
                if button is None:
                    continue
                button.deselect()
        self.update_button_states()

    def randomColors(self) -> None:
        for button in self.selected:
            button.randomColor()
        self.update_button_states()

    def toggle_random_colors(self) -> None:
        if self.random_animation and self.random_animation.is_active:
            self.random_animation.stop()
            self.random_animation = None
            if self.random_toggle_btn is not None:
                _ = self.random_toggle_btn.config(text="Changing random colours")
        else:
            self.random_animation = RandomColorAnimation(
                self.keyboard,
                update_callback=self.update_buttons,
                sleep_time=self.animation_sleep,
            )
            self.random_animation.start()
            if self.random_toggle_btn is not None:
                _ = self.random_toggle_btn.config(text="Deactivate Animation")

    def toggle_wave_colors(self) -> None:
        if self.wave_animation and self.wave_animation.is_active:
            self.wave_animation.stop()
            self.wave_animation = None
            if self.wave_toggle_btn is not None:
                _ = self.wave_toggle_btn.config(text="Wave Animation")
        else:
            self.wave_animation = WaveAnimation(
                self.keyboard,
                update_callback=self.update_buttons,
                sleep_time=self.animation_sleep,
            )
            self.wave_animation.start()
            if self.wave_toggle_btn is not None:
                _ = self.wave_toggle_btn.config(text="Deactivate Wave")

    def toggle_pulse_keyboard(self) -> None:
        if self.pulse_keyboard_animation and self.pulse_keyboard_animation.is_active:
            self.pulse_keyboard_animation.stop()
            self.pulse_keyboard_animation = None
            if self.pulse_keyboard_btn is not None:
                _ = self.pulse_keyboard_btn.config(text="Pulse Keyboard")
        else:
            self.pulse_keyboard_animation = PulseAnimation(
                [self.keyboard.backlight],
                50,
                update_callback=self.update_buttons,
                sleep_time=self.animation_sleep,
            )
            self.pulse_keyboard_animation.start()
            if self.pulse_keyboard_btn is not None:
                _ = self.pulse_keyboard_btn.config(text="Deactivate Pulse")

    def toggle_pulse_lightbar(self) -> None:
        if self.pulse_lightbar_animation and self.pulse_lightbar_animation.is_active:
            self.pulse_lightbar_animation.stop()
            self.pulse_lightbar_animation = None
            if self.pulse_lightbar_btn is not None:
                _ = self.pulse_lightbar_btn.config(text="Pulse Lightbar")
        else:
            self.pulse_lightbar_animation = PulseAnimation(
                [self.keyboard.lightbar],
                100,
                update_callback=self.update_buttons,
                sleep_time=self.animation_sleep,
            )
            self.pulse_lightbar_animation.start()
            if self.pulse_lightbar_btn is not None:
                _ = self.pulse_lightbar_btn.config(text="Deactivate Pulse")

    def changeColors(self) -> None:
        selected_color = askcolor(color="#FF0", parent=self.root)
        if selected_color == (None, None):
            return
        if not isinstance(selected_color[0], tuple):
            return
        color_obj = Color(
            int(selected_color[0][0]),
            int(selected_color[0][1]),
            int(selected_color[0][2]),
        )
        for button in self.selected:
            button.changeColor(color_obj)
        self.selected.clear()
        self.update_button_states()

    def changeAnimationSleep(self, _s: str) -> None:
        self.animation_sleep = float(_s)

    def changeBrightness(self, _b: str) -> None:
        if self.var is None:
            return
        brightness_value = int(self.var.get())
        self.keyboard.backlight.set_brightness(brightness_value)

    def change_lightbar_brightness(self, _b: str) -> None:
        if self.lightbar_var is None:
            return
        brightness_value = int(self.lightbar_var.get())
        self.keyboard.lightbar.set_brightness(brightness_value)

    def create_brightness(self) -> None:
        self.var = IntVar()
        self.brightness = Scale(
            self.root, variable=self.var, from_=50, to=0, command=self.changeBrightness
        )
        self.brightness.grid(column=20, row=0, columnspan=5, sticky="nesw")
        self.var.set(self.keyboard.backlight.get_brightness())
        if self.keyboard.lightbar.supported:
            self.lightbar_var = IntVar()
            self.lightbar_brightness = Scale(
                self.root,
                variable=self.lightbar_var,
                from_=100,
                to=0,
                command=self.change_lightbar_brightness,
            )
            self.lightbar_brightness.grid(column=25, row=0, columnspan=5, sticky="nesw")
            self.lightbar_var.set(self.keyboard.lightbar.get_brightness())

    def create_animation_sleep_scale(self) -> None:
        self.animation_sleep_var = IntVar()
        self.animation_sleep_scale = Scale(
            self.root,
            variable=self.animation_sleep_var,
            from_=100,
            to=1,
            command=self.changeAnimationSleep,
        )
        self.animation_sleep_scale.grid(column=30, row=0, columnspan=5, sticky="nesw")
        self.animation_sleep_var.set(10)

    def create_control_buttons(self) -> None:
        frm = Frame(self.root)
        frm.grid(column=0, row=1, sticky="ew")

        self.pickColor_btn = Button(frm, text="Pick Color", command=self.changeColors)
        self.pickColor_btn.grid(column=0, row=0, sticky="ew")
        self.randomColor_btn = Button(
            frm, text="Random Color", command=self.randomColors
        )
        self.randomColor_btn.grid(column=1, row=0, sticky="ew")

        selectAll_btn = Button(frm, text="Select all", command=self.selectAll)
        selectAll_btn.grid(column=0, row=1, sticky="ew")
        self.deselectAll_btn = Button(
            frm, text="Deselect all", command=self.deselectAll
        )
        self.deselectAll_btn.grid(column=1, row=1, sticky="ew")
        self.random_toggle_btn = Button(
            frm, text="Changing random colours", command=self.toggle_random_colors
        )
        self.random_toggle_btn.grid(column=0, row=2, sticky="ew")
        self.wave_toggle_btn = Button(
            frm, text="Wave Animation", command=self.toggle_wave_colors
        )
        self.wave_toggle_btn.grid(column=1, row=2, sticky="ew")
        self.pulse_keyboard_btn = Button(
            frm, text="Pulse Keyboard", command=self.toggle_pulse_keyboard
        )
        self.pulse_keyboard_btn.grid(column=0, row=3, sticky="ew")
        if self.keyboard.lightbar.supported:
            self.pulse_lightbar_btn = Button(
                frm, text="Pulse Lightbar", command=self.toggle_pulse_lightbar
            )
            self.pulse_lightbar_btn.grid(column=1, row=3, sticky="ew")
        save_btn = Button(frm, text="Save config", command=self.save_config)
        save_btn.grid(column=0, row=4, sticky="ew")
        self.load_btn: Button = Button(
            frm, text="Load config", command=self.load_config
        )
        self.load_btn.grid(column=1, row=4, sticky="ew")
        # Language selector
        self.lang_var: StringVar = StringVar(value=self.current_lang)
        self.lang_menu: OptionMenu = OptionMenu(
            frm, self.lang_var, *localized_names.keys(), command=self.change_lang
        )
        self.lang_menu.grid(column=0, row=5, sticky="ew")

        # Check if running as root
        if not self.is_root:
            # Disable buttons that change colors
            _ = self.pickColor_btn.config(state=DISABLED)
            _ = self.randomColor_btn.config(state=DISABLED)
            _ = self.random_toggle_btn.config(state=DISABLED)
            _ = self.wave_toggle_btn.config(state=DISABLED)
            _ = self.pulse_keyboard_btn.config(state=DISABLED)
            if self.keyboard.lightbar.supported and self.pulse_lightbar_btn:
                _ = self.pulse_lightbar_btn.config(state=DISABLED)
            _ = self.load_btn.config(state=DISABLED)
            # Brightness change requires write, disable
            if self.brightness is not None:
                _ = self.brightness.config(state=DISABLED)
            if self.lightbar_brightness is not None:
                _ = self.lightbar_brightness.config(state=DISABLED)
            # Add message label
            msg_label = Label(
                frm,
                text="Application needs to be run as root to change colors.",
                fg="red",
            )
            msg_label.grid(column=0, row=5, columnspan=2, sticky="ew")
            if self.keyboard.lightbar.supported and self.lightbar_btn:
                _ = self.lightbar_btn.config(state=DISABLED)

    def change_lightbar_color(self) -> None:
        lightbar_color = self.keyboard.lightbar.color
        current_color = "#000000"
        if lightbar_color:
            current_color = lightbar_color.as_hex()
        selected_color = askcolor(color=current_color, parent=self.root)
        if selected_color == (None, None):
            return
        if not isinstance(selected_color[0], tuple):
            return
        color_obj = Color(
            int(selected_color[0][0]),
            int(selected_color[0][1]),
            int(selected_color[0][2]),
        )
        self.keyboard.lightbar.set_color(color_obj)
        if self.lightbar_btn:
            _ = self.lightbar_btn.config(bg=color_obj.as_hex())

    def update_button_states(self) -> None:
        if (
            self.randomColor_btn is None
            or self.pickColor_btn is None
            or self.deselectAll_btn is None
        ):
            return
        state = NORMAL if self.selected else DISABLED
        _ = self.randomColor_btn.config(state=state)
        _ = self.pickColor_btn.config(state=state)
        _ = self.deselectAll_btn.config(state=state)
        # Disable animation sleep slider if any animation is active
        any_active = (
            (self.random_animation and self.random_animation.is_active)
            or (self.wave_animation and self.wave_animation.is_active)
            or (
                self.pulse_keyboard_animation
                and self.pulse_keyboard_animation.is_active
            )
            or (
                hasattr(self, "pulse_lightbar_animation")
                and self.pulse_lightbar_animation
                and self.pulse_lightbar_animation.is_active
            )
        )
        sleep_state = DISABLED if any_active else NORMAL
        if self.animation_sleep_scale:
            _ = self.animation_sleep_scale.config(state=sleep_state)

    def update_buttons(self) -> None:
        for row in self.buttons:
            for button in row:
                if button is not None:
                    button.load()

    def save_config(self) -> None:
        filename = filedialog.asksaveasfilename(
            defaultextension=".ini", filetypes=[("INI files", "*.ini")]
        )
        if filename:
            self.keyboard.save_config(filename)

    def load_config(self) -> None:
        filename = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if filename:
            _ = self.keyboard.load_config(filename)
            # Update UI elements
            if self.var is not None:
                self.var.set(self.keyboard.backlight.get_brightness())
            if self.lightbar_var is not None:
                self.lightbar_var.set(self.keyboard.lightbar.get_brightness())
            if self.lightbar_btn is not None:
                lightbar_color = self.keyboard.lightbar.color
                bg_color = "#000000"
                if lightbar_color:
                    bg_color = lightbar_color.as_hex()
                _ = self.lightbar_btn.config(bg=bg_color)
            self.deselectAll()
            for row in self.buttons:
                for button in row:
                    if button is None:
                        continue
                    button.load()

    def change_lang(self, new_lang: StringVar) -> None:
        self.current_lang = str(new_lang)
        for row in self.buttons:
            for button in row:
                if button is not None:
                    button.set_lang(self.current_lang)


class UiButton:
    """
    Represents a button in the GUI corresponding to a keyboard key.

    Handles color changes, selection, and user interactions for individual keys.
    """

    def __init__(
        self,
        manager: UiManager,
        frm: Frame,
        x: int,
        y: int,
        iso: str,
        lang: str,
        h: int = 1,
        w: int = 1,
        key: LEDDevice | None = None,
    ) -> None:
        self.manager: UiManager = manager
        self.frm: Frame = frm
        self.iso: str = iso
        self.lang: str = lang
        self.t: str = localized_names[self.lang].get(self.iso, self.iso)
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        # LEDDevice or None
        self.key: LEDDevice | None = (
            key if key is not None else LEDDevice.for_key(nom[self.y][self.x])
        )
        # Determine initial color and state for the UI button
        if self.key and not self.key.supported:
            color_hex = "#cccccc"
            button_state = DISABLED
        else:
            if self.key.color is None:
                color_hex = "#000000"
            else:
                color_hex = self.key.color.as_hex()
            button_state = NORMAL
        self.button: Button = Button(
            self.frm,
            text=self.t,
            bg=color_hex,
            state=button_state,
            command=lambda: self.clicked(),
            activebackground="#ff0000",
            highlightbackground="#000000",
        )
        self.button.grid(
            column=self.x, row=self.y, rowspan=self.w, columnspan=self.h, sticky="nesw"
        )

    def changeColor(self, color: Color) -> None:
        if self.key is None or not self.key.supported:
            return
        # LEDDevice.set_color accepts a Color or a sequence of three ints
        self.key.set_color(color)
        self.load()

    def load(self) -> None:
        if not self.key or not self.key.supported:
            return
        if self in self.manager.selected:
            color = "#00ff00"
        else:
            if self.key.color is None:
                color = "#000000"
            else:
                color = self.key.color.as_hex()
        _ = self.button.config(bg=color)

    def select(self, event: int = 0) -> None:
        del event
        if self not in self.manager.selected:
            self.manager.selected.append(self)
        self.load()
        self.manager.update_button_states()

    def deselect(self, event: int = 0) -> None:
        del event
        if self in self.manager.selected:
            del self.manager.selected[self.manager.selected.index(self)]
        self.load()
        self.manager.update_button_states()

    def randomColor(self, event: int = 0) -> None:
        del event
        if self.key is None or not self.key.supported:
            return
        self.key.random_color()
        self.load()

    def clicked(self, event: int = 0) -> None:
        del event
        if self in self.manager.selected:
            del self.manager.selected[self.manager.selected.index(self)]
        else:
            self.manager.selected.append(self)
        self.load()
        self.manager.update_button_states()

    def set_lang(self, new_lang: str) -> None:
        self.lang = new_lang
        self.t = localized_names[self.lang].get(self.iso, self.iso)
        _ = self.button.config(text=self.t)
