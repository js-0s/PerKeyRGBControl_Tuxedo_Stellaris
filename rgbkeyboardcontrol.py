#!/usr/lib/python3.10
from tkinter import *
from tkinter import ttk
from tkcolorpicker import askcolor
import random
import threading
import time
import os

if os.geteuid() != 0:
    exit("To control the Keyboard you need root privileges.\nPlease try again, this time using 'sudo' ;) \nExiting.")

global selected
selected = []
randomSelected = []

def changeRandomAllSelected(e=0):
    del e
    global randomSelected
    while True:
        time.sleep(0.5)
        for key in randomSelected:
            key.randomColor()


def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def readBrightness():
    with open(f"/sys/class/leds/rgb:kbd_backlight/brightness", "r") as f:
        return int(f.read())


def selectAll(e=1):
    del e
    global btns
    for i in btns:
        for j in i:
            if j != "":
                j.select()

def deselectAll(e=1):
    del e
    global btns
    for i in btns:
        for j in i:
            if j != "":
                j.deselect()

def randomColors(e=0):
    global selected
    del e
    for button in selected:
        button.randomColor()
        button.clicked()
        selected.insert(0,1)
    selected = []

def changeRandomColors(e=0):
    global selected
    global randomSelected
    del e
    for button in selected:
        randomSelected.append(button)
        button.clicked()
        selected.insert(0,1)
    selected = []

def deactivateChangeRandomColors(e=0):
    global selected
    global randomSelected
    del e
    for button in selected:
        if button in randomSelected:
            del randomSelected[randomSelected.index(button)]
        button.clicked()
        selected.insert(0,1)
    selected = []





def colorZehnFingerSystem(e=0):
    del e
    global btns
    for i in btns:
        for j in i:
            if j != "":
                j.colorYourselveZehnFingersystem()


def changeColors(e=1):
    global selected
    
    del e
    
    color = askcolor((255, 255, 0), root)
    
    if color[0] != None:
        for button in selected:
            button.changeColor(color)
            button.clicked()
            selected.insert(0,1)
        selected = []

def changeBrightness(e=1):
    del e
    brightness = int(var.get())
    with open(f"/sys/class/leds/rgb:kbd_backlight/brightness", "w") as f:
        f.write(str(brightness))


class btnplus:
    def __init__(self, x, y, t, h=1, w=1):
        global frm
        self.t = t
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = str("#ffffff")
        #self.firstColor()
        self.load()
    def firstColor(self):
        if nom[self.y][self.x] == -1:
            link = f"/sys/class/leds/rgb:kbd_backlight/multi_intensity"
        else:
            link = f"/sys/class/leds/rgb:kbd_backlight_{nom[self.y][self.x]}/multi_intensity"

        with open(link, "r") as f:
                string = f.read()
                gespalten = string.split(" ")
                self.color = rgb2hex(int(gespalten[0]),int(gespalten[1]), int(gespalten[2]))
    def changeColor(self, color):
        if nom[self.y][self.x] == -1:
            link = f"/sys/class/leds/rgb:kbd_backlight/multi_intensity"
        else:
            link = f"/sys/class/leds/rgb:kbd_backlight_{nom[self.y][self.x]}/multi_intensity"
        with open(link, "w") as f:
            f.write(f"{color[0][0]} {color[0][1]} {color[0][2]}")
        #self.color = color[1]
        self.load()
        
    def load(self):
        #self.color = "#ffffff"
        self.button = Button(frm, text=self.t, bg=self.color, command= lambda : self.clicked(), activebackground="#ff0000", highlightbackground="#000000")
        self.button.grid(column=self.x, row=self.y, rowspan=self.w, columnspan=self.h, sticky='nesw')
        #self.button.bind("<Button-1>", self.clicked())
    def select(self, event=0):
        if self not in selected:
            self.color = "#00ff00"
            selected.append(self)
        self.load()
    def deselect(self,event=0):
        if self in selected:
            self.color = "#ffffff"
            del selected[selected.index(self)]
        self.load()
    def colorYourselveZehnFingersystem(self):
        self.changeColor(zehnFingerSystem[self.y][self.x])
    def randomColor(self,e=0):
        del e
        self.changeColor([[random.randint(0,255),random.randint(0,255),random.randint(0,255)]])
    def clicked(self,event=0):
        del event
        if self in selected:
            self.color = "#ffffff"
            del selected[selected.index(self)]
        else:
            self.color = "#00ff00"
            selected.append(self)
        self.load()

root = Tk()
frm = Frame(root)
frm.grid()




btns = [
    ["esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "druck", "einfg", "entf", "pos1", "ende", "⇑", "⇓"],
    ["^", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", r"´", "del", "", "", "num", "/", "*", "-"],
    ["tab", "Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü", "+", "↵", "", "", "7", "8", "9", "+"],
    ["⇓", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "#", "", "", "", "4", "5", "6", ""],
    ["shift", "<", "Y", "X", "C", "V", "B", "N", "M", ",", ".", "-", "", "Shift", "", "", "1", "2", "3", "↵"],
    ["strg", "fn", "#", "alt", "_", "", "", "", "", "", "alt gr", "strg", "", "", "⇑", "", "0", "", ",", ""],
    ["", "", "", "", "", "", "", "", "", "", "", "", "", "⇐", "⇓", "⇒", "", "", "", ""]
]
nom = [
    [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124],
    [ 84,  85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96,  98,  98,  98,  99, 100, 101, 102],
    [ 63,  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,  75,  76,  77,  77,  77,  78,  79,  80,  81],
    [ 42,  44,  45,  46,  47,  48,  49,  50,  51,  52,  53,  54,  55,  77,  77,  77,  57,  58,  59,  81],
    [ 22,  23,  24,  25,  26,  27,  28,  29,  30,  31,  32,  33, 125,  35,  35,  35,  36,  37,  38,  39],
    [ -1,   2,   3,   4,   7,   7,   7,   7,   7,   7,  10,  12,  12, 118,  14, 120,  16,  16,  17,  39],
    [125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125,  13,  18,  15, 125, 125, 125, 125]
    
]
zehnFingerSystem = [
    [[[255,0,0]], [[255,0,0]], [[0,0,255]], [[0,255,0]], [[0,255,255]], [[0,255,255]], [[255,0,255]], [[255,0,255]], [[0,255,0]], [[0,0,255]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[0,0,255]], [[0,255,0]], [[0,255,255]], [[0,255,255]], [[255,0,255]], [[255,0,255]], [[0,255,0]], [[0,0,255]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[0,0,255]], [[0,255,0]], [[0,255,255]], [[0,255,255]], [[255,0,255]], [[255,0,255]], [[0,255,0]], [[0,0,255]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[0,0,255]], [[0,255,0]], [[0,255,255]], [[0,255,255]], [[255,0,255]], [[255,0,255]], [[0,255,0]], [[0,0,255]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[255,0,0]], [[0,0,255]], [[0,255,0]], [[0,255,255]], [[0,255,255]], [[255,0,255]], [[255,0,255]], [[0,255,0]], [[0,0,255]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]],
    [[[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,0,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]], [[255,255,0]]]
]
for py, i in enumerate(btns):
    for px, j in enumerate(i):
        if j == "↵" and px < 15: btns[py][px] = btnplus(px, py, j, 3, 2)
        elif j == "Shift": btns[py][px] = btnplus(px, py, j, 3, 1)
        elif j == "del": btns[py][px] = btnplus(px, py, j, 3, 1)
        elif j == "_": btns[py][px] = btnplus(px, py, j, 6, 1)
        elif j == "+" and px > 17: btns[py][px] = btnplus(px, py, j, 1, 2)
        elif j == "↵" and px > 17: btns[py][px] = btnplus(px, py, j, 1, 2)
        elif j == "strg" and px > 6: btns[py][px] = btnplus(px, py, j, 2, 1)
        elif j == "0" and px > 11: btns[py][px] = btnplus(px, py, j, 2, 1)
        elif not j == "": btns[py][px] = btnplus(px, py, j)


var = IntVar()
brightness = Scale(root, variable=var, from_=50, to=0, command=changeBrightness)
brightness.grid(column=20, row=0, columnspan=5, sticky="nesw")
var.set(readBrightness())


change = Button(root,text="Change Colors", command=lambda : changeColors())
change.grid(column=0, row=6, rowspan=3,sticky="nesw")
#change.bind("<Button-4>", changeColors())
selectAll_BTN = Button(root,text="Select all", command=lambda : selectAll())
selectAll_BTN.grid(column=0, row=10, rowspan=3,sticky="nesw")
deselectAll_BTN = Button(root,text="Deselect all", command=lambda : deselectAll())
deselectAll_BTN.grid(column=0, row=14, rowspan=3,sticky="nesw")
zehnFingerSystem_BTN = Button(root,text="Zehnfingersytem", command=lambda : colorZehnFingerSystem())
zehnFingerSystem_BTN.grid(column=0, row=18, rowspan=3,sticky="nesw")
randomColors_BTN = Button(root,text="Random Farben", command=lambda : randomColors())
randomColors_BTN.grid(column=0, row=22, rowspan=3,sticky="nesw")
changeRandomColors_BTN = Button(root,text="Random Farben wechseln", command=lambda : changeRandomColors())
changeRandomColors_BTN.grid(column=0, row=26, rowspan=3,sticky="nesw")
deavtivateChangeRandomColors_BTN = Button(root,text="Random Faben wechseln ausschalten", command=lambda : deactivateChangeRandomColors())
deavtivateChangeRandomColors_BTN.grid(column=0, row=30, rowspan=3,sticky="nesw")


cycle = threading.Thread(target=changeRandomAllSelected, args=(1,),daemon=True)
cycle.start()

root.mainloop()
