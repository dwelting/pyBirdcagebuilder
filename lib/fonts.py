"""
Description:    Library with some custom tk fonts.
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

from tkinter import font


class MyFonts:
    def __init__(self):
        self.default_font = font.nametofont("TkDefaultFont")  # set default font
        self.default_font.configure(family='freemono', size=11)

        self.myfont_bold = self.default_font.copy()  # bold font
        self.myfont_bold.configure(weight="bold")

        self.myfont_small_bold = self.default_font.copy()  # small font
        self.myfont_small_bold.configure(weight="bold", size=9)

        self.myfont_graph = self.default_font.copy()  # small font
        self.myfont_graph.configure(weight="bold", size=2)

        self.myfont_small = self.default_font.copy()  # small font
        self.myfont_small.configure(size=8)

        self.myfont_underlined = self.default_font.copy()
        self.myfont_underlined.configure(underline=True)
