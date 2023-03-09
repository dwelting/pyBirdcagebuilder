"""
Description:    Source file with constants/defines used in the rets of the program.
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

PROGRAM_NAME = "pyBirdcagebuilder"
VERSION = "v0.2"
WEBSITE = "github.com/dwelting/pyBirdcagebuilder"

ICON_FOLDER = "icon/"

MAX_PRECISION = 2
MIN_LEGS = 8
MAX_LEGS = 32

class Window:
    X = 500
    Y = 600

class Config:
    ELLIPSE = 0
    CIRCLE = 1
    DEFAULT = CIRCLE

class Axis:
    SHORT = 1
    LONG = 2
    DEFAULT = SHORT

class Mode:
    HIGHPASS = 1
    LOWPASS = 2
    BANDPASS = 3
    DEFAULT = HIGHPASS

class Shape:
    RECT = 1
    TUBE = 2
    DEFAULT = RECT

class Part:
    LEG = 1
    ER = 2
    DEFAULT = LEG

