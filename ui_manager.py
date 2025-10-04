from __future__ import annotations
from tkinter import (
    Button,
    IntVar,
    Scale,
    Tk,
    Frame,
    OptionMenu,
    StringVar,
    NORMAL,
    DISABLED,
)
from tkcolorpicker import askcolor
from pyrgb_core import (
    rgb2hex,
    Key,
    read_brightness,
    set_brightness,
)
from constants import nom, key_names, localized_names
from tkinter import filedialog
from pyrgb_keyboard import KeyboardManager

from animations import RandomColorAnimation, WaveAnimation


class UiManager:
    def __init__(self, root: Tk) -> None:
        self.root: Tk = root
        self.selected: list[UiButton] = []
        self.buttons: list[list[UiButton | None]] = []
        self.var: IntVar | None = None
        self.brightness: Scale | None = None
        self.keyboard: KeyboardManager = KeyboardManager()
        self.frm: Frame = Frame(root)
        self.frm.grid(column=0, row=0)
        self.current_lang: str = "de"
        self.random_toggle_btn: Button | None = None
        self.wave_toggle_btn: Button | None = None
        self.buttons = self.create_buttons()
        self.random_animation: RandomColorAnimation = RandomColorAnimation(
            self.keyboard, update_callback=self.update_buttons
        )
        self.wave_animation: WaveAnimation = WaveAnimation(
            self.keyboard, update_callback=self.update_buttons
        )
        self.create_brightness()
        self.create_control_buttons()
        self.update_button_states()

    def create_buttons(self) -> list[list[UiButton | None]]:
        self.buttons = []
        for py, key_row in enumerate(key_names):
            row: list[UiButton | None] = []
            for px, key_name in enumerate(key_row):
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            self.keyboard.keys[py][px],
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
                            key=self.keyboard.keys[py][px],
                        )
                    )
                else:
                    row.append(None)
            self.buttons.append(row)
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
        if self.random_animation.is_active:
            self.random_animation.stop()
            if self.random_toggle_btn is not None:
                _ = self.random_toggle_btn.config(text="Changing random colours")
        else:
            self.random_animation.start()
            if self.random_toggle_btn is not None:
                _ = self.random_toggle_btn.config(text="Deactivate Animation")

    def toggle_wave_colors(self) -> None:
        if self.wave_animation.is_active:
            self.wave_animation.stop()
            if self.wave_toggle_btn is not None:
                _ = self.wave_toggle_btn.config(text="Wave Animation")
        else:
            self.wave_animation.start()
            if self.wave_toggle_btn is not None:
                _ = self.wave_toggle_btn.config(text="Deactivate Wave")

    def changeColors(self) -> None:
        selected_color = askcolor(color="#FF0", parent=self.root)
        if selected_color == (None, None):
            return
        if not isinstance(selected_color[0], tuple):
            return
        color: list[int] = [
            int(selected_color[0][0]),
            int(selected_color[0][1]),
            int(selected_color[0][2]),
        ]
        for button in self.selected:
            button.changeColor(color)
        self.selected.clear()
        self.update_button_states()

    def changeBrightness(self, _b: str) -> None:
        if self.var is None:
            return
        brightness_value = int(self.var.get())
        set_brightness(brightness_value)

    def create_brightness(self) -> None:
        self.var = IntVar()
        self.brightness = Scale(
            self.root, variable=self.var, from_=50, to=0, command=self.changeBrightness
        )
        self.brightness.grid(column=20, row=0, columnspan=5, sticky="nesw")
        self.var.set(read_brightness())

    def create_control_buttons(self) -> None:
        frm = Frame(self.root)
        frm.grid(column=0, row=1, sticky="ew")

        self.pickColor_BTN: Button = Button(
            frm, text="Pick Color", command=self.changeColors
        )
        self.pickColor_BTN.grid(column=0, row=0, sticky="ew")
        self.randomColor_BTN: Button = Button(
            frm, text="Random Color", command=self.randomColors
        )
        self.randomColor_BTN.grid(column=1, row=0, sticky="ew")

        selectAll_BTN = Button(frm, text="Select all", command=self.selectAll)
        selectAll_BTN.grid(column=0, row=1, sticky="ew")
        self.deselectAll_BTN: Button = Button(
            frm, text="Deselect all", command=self.deselectAll
        )
        self.deselectAll_BTN.grid(column=1, row=1, sticky="ew")
        self.random_toggle_btn = Button(
            frm, text="Changing random colours", command=self.toggle_random_colors
        )
        self.random_toggle_btn.grid(column=0, row=2, sticky="ew")
        self.wave_toggle_btn = Button(
            frm, text="Wave Animation", command=self.toggle_wave_colors
        )
        self.wave_toggle_btn.grid(column=1, row=2, sticky="ew")
        save_BTN = Button(frm, text="Save config", command=self.save_config)
        save_BTN.grid(column=0, row=3, sticky="ew")
        load_BTN = Button(frm, text="Load config", command=self.load_config)
        load_BTN.grid(column=1, row=3, sticky="ew")
        # Language selector
        self.lang_var: StringVar = StringVar(value=self.current_lang)
        self.lang_menu: OptionMenu = OptionMenu(
            frm, self.lang_var, *localized_names.keys(), command=self.change_lang
        )
        self.lang_menu.grid(column=0, row=4, sticky="ew")

    def update_button_states(self) -> None:
        state = NORMAL if self.selected else DISABLED
        _ = self.pickColor_BTN.config(state=state)
        _ = self.randomColor_BTN.config(state=state)
        _ = self.deselectAll_BTN.config(state=state)

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
            self.keyboard.load_config(filename)
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
        key: Key | None = None,
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
        self.key: Key = key if key is not None else Key(nom[self.y][self.x])
        color = rgb2hex(*self.key.color)
        self.button: Button = Button(
            self.frm,
            text=self.t,
            bg=color,
            command=lambda: self.clicked(),
            activebackground="#ff0000",
            highlightbackground="#000000",
        )
        self.button.grid(
            column=self.x, row=self.y, rowspan=self.w, columnspan=self.h, sticky="nesw"
        )

    def changeColor(self, rgb: list[int]) -> None:
        self.key.set_color(rgb)
        self.load()

    def load(self) -> None:
        if self in self.manager.selected:
            color = "#00ff00"
        else:
            color = rgb2hex(*self.key.color)
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
