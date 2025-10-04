"""
Graphical user interface entrypoint for pyrgb keyboard control.

This script launches the Tkinter-based GUI for interactively controlling
RGB lighting on supported keyboards. It requires root privileges and a
graphical environment.
"""

from tkinter import Tk
from ui_manager import UiManager


root = Tk()
ui = UiManager(root)

# At the End the loop for tkinter is started
root.mainloop()
