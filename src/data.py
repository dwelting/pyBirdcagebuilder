"""
Description:    Source file with classes used as storage for settings and results.
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

import tkinter as tk
import src.constants as const


class Settings:
    def __init__(self):
        self.setting_calc = const.Config.DEFAULT
        self.setting_coil_configuration = tk.IntVar()
        self.setting_coil_axis = tk.IntVar()
        self.setting_leg_type = tk.IntVar()
        self.setting_er_type = tk.IntVar()
        self.setting_bp_cap_location = tk.IntVar()

        self.freq = tk.DoubleVar()  # variable for Resonance frequency
        self.bp_cap = tk.DoubleVar()

        self.nr_of_legs = tk.IntVar()
        self.leg_length = tk.DoubleVar()
        self.leg_width = tk.DoubleVar()
        self.leg_od = tk.DoubleVar()
        self.leg_id = tk.DoubleVar()

        self.er_width = tk.DoubleVar()
        self.er_od = tk.DoubleVar()
        self.er_id = tk.DoubleVar()

        self.coil_diameter = tk.DoubleVar()
        self.coil_diameter_short = tk.DoubleVar()
        self.coil_diameter_long = tk.DoubleVar()

        self.shield_diameter = tk.DoubleVar()

        self.reset()

    def reset(self):
        self.setting_calc = const.Config.DEFAULT
        self.setting_coil_configuration.set(const.Mode.DEFAULT)
        self.setting_coil_axis.set(const.Axis.DEFAULT)
        self.setting_leg_type.set(const.Shape.DEFAULT)
        self.setting_er_type.set(const.Shape.DEFAULT)
        self.setting_bp_cap_location.set(const.Part.DEFAULT)

        self.freq.set(298)  # variable for resonance frequency
        self.bp_cap.set(56)

        self.nr_of_legs.set(12)
        self.leg_length.set(20)
        self.leg_width.set(0.5)
        self.leg_od.set(0.396)
        self.leg_id.set(0.246)

        self.er_width.set(0.5)
        self.er_od.set(1)
        self.er_id.set(0.6)

        self.coil_diameter.set(30)
        self.coil_diameter_short.set(7.6 * 2)
        self.coil_diameter_long.set(12.6 * 2)

        self.shield_diameter.set(33)


class Results:
    def __init__(self):
        self.radius = [0.0 for _ in range(const.MAX_LEGS)]
        self.thetas = [0.0 for _ in range(const.MAX_LEGS)]
        self.x_coords = [0.0 for _ in range(const.MAX_LEGS)]
        self.y_coords = [0.0 for _ in range(const.MAX_LEGS)]
        self.leg_currs = [0.0 for _ in range(const.MAX_LEGS)]
        self.er_currs = [0.0 for _ in range(const.MAX_LEGS)]
        self.cap = [tk.DoubleVar(value=0.0) for _ in range(const.MAX_LEGS)]
        self.leg_eff = [tk.DoubleVar(value=0.0) for _ in range(const.MAX_LEGS)]  # calculated effective inductance of legs
        self.er_eff = [tk.DoubleVar(value=0.0) for _ in range(const.MAX_LEGS)]  # calculated effective inductance of end ring
        self.leg_self = tk.DoubleVar(value=0.0)  # calculated self inductance of legs
        self.er_self = tk.DoubleVar(value=0.0)  # calculated self inductance of end ring
        self.er_segment_length = tk.DoubleVar(value=0)

    def reset(self):
        self.radius[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        self.thetas[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        self.x_coords[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        self.y_coords[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        self.leg_currs[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        self.er_currs[:const.MAX_LEGS] = [0] * const.MAX_LEGS
        [self.cap[i].set(0) for i in range(const.MAX_LEGS)]
        [self.leg_eff[i].set(0) for i in range(const.MAX_LEGS)]  # calculated effective inductance of legs
        [self.er_eff[i].set(0) for i in range(const.MAX_LEGS)]  # calculated effective inductance of end ring
        self.leg_self.set(0)  # calculated self inductance of legs
        self.er_self.set(0)  # calculated self inductance of end ring
        self.er_segment_length.set(0)
