"""
Description:    Source file with GUI definitions.
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""


import tkinter as tk
from tkinter import ttk
import math
import itertools
import os

import lib.fonts as ft
import lib.my_tk as my_tk
import src.constants as const


class MyMenuBar:
    def __init__(self, parent, settings, results):
        self.parent = parent
        self.settings = settings
        self.results = results

        self.menu = tk.Menu(parent.window)

    def initialize(self):
        self._fileMenu()
        self._optionMenu()
        self._helpMenu()

    def _optionMenu(self):
        self.coil_shape = tk.BooleanVar()  # selects which coil type
        self.coil_shape.set(const.Shape.DEFAULT)

        optionmenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=optionmenu)

        optionmenu.add_checkbutton(label="Circular", onvalue=const.Config.CIRCLE, offvalue=const.Config.ELLIPSE,
                                   command=lambda: self._coilModeChanged(), variable=self.coil_shape)

        optionmenu.add_checkbutton(label="Elliptical (experimental)", onvalue=const.Config.ELLIPSE, offvalue=const.Config.CIRCLE,
                                   command=lambda: self._coilModeChanged(), variable=self.coil_shape)

    def _coilModeChanged(self):  # TODO move to parent class/event handler
        self.settings.setting_calc = self.coil_shape.get()
        self.parent.guiTabSettings.guiAdjust()
        self.parent.guiTabResults.initializeGraphs()
        self.parent.tab_control.select(0)

    def _helpMenu(self):
        helpmenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=helpmenu)

        helpmenu.add_command(label=f"About {const.PROGRAM_NAME}", command=lambda: MyAboutWindow(self.parent.window)) #TODO move to eventhandler

    def _fileMenu(self):
        filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=filemenu)

        # filemenu.add_command(label="Save config", command=self.parent.Config.save)  #TODO add config save all input settings
        # filemenu.add_command(label="Save config as...", command=self.parent.Config.saveAs)
        # filemenu.add_command(label="Load config", command=self.parent.Config.load) #TODO add config load all input settings
        # filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.parent.window.quit) #TODO move to main program class/event handler


class MyMoreInfoTab:
    def __init__(self, parent, settings, results):
        self.parent = parent
        self.ft = ft.MyFonts()
        self.settings = settings
        self.results = results

        self.tab = ttk.Frame(parent.tab_control)

        lf_ind_calc = tk.LabelFrame(self.tab, text="Inductance Calculations", font=self.ft.myfont_bold)
        lbl_self = tk.Label(lf_ind_calc, text="Self (nH)", font=self.ft.myfont_bold, foreground="blue")
        lbl_eff = tk.Label(lf_ind_calc, text="Effective (nH)", font=self.ft.myfont_bold, foreground="blue")
        lb_legs = tk.Label(lf_ind_calc, text="Legs", font=self.ft.myfont_bold)
        lb_er = tk.Label(lf_ind_calc, text="ER Seg.", font=self.ft.myfont_bold)

        txt_self_legs = my_tk.MyEntry(lf_ind_calc, text=self.results.leg_self, read_only=True, decimals=const.MAX_PRECISION)
        txt_self_er = my_tk.MyEntry(lf_ind_calc, text=self.results.er_self, read_only=True, decimals=const.MAX_PRECISION)
        txt_eff_legs = my_tk.MyEntry(lf_ind_calc, text=self.results.leg_eff[0], read_only=True, decimals=const.MAX_PRECISION)
        txt_eff_er = my_tk.MyEntry(lf_ind_calc, text=self.results.er_eff[0], read_only=True, decimals=const.MAX_PRECISION)

        lbl_self.grid(column=1, row=0, sticky=tk.NSEW, padx=(0, 20), pady=(0, 5))
        lbl_eff.grid(column=2, row=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        lb_legs.grid(column=0, row=1, sticky=tk.NSEW, pady=(0, 10))
        lb_er.grid(column=0, row=2, sticky=tk.NSEW, pady=(0, 10))
        txt_self_legs.grid(column=1, row=1, sticky=tk.NW)
        txt_self_er.grid(column=1, row=2, sticky=tk.NW)
        txt_eff_legs.grid(column=2, row=1, sticky=tk.NW)
        txt_eff_er.grid(column=2, row=2, sticky=tk.NW)

        tk.Grid.columnconfigure(self.tab, 0, weight=0)
        tk.Grid.columnconfigure(self.tab, 3, weight=1)
        lf_ind_calc.grid(column=0, row=0, sticky=tk.NSEW, pady=(5, 5), padx=(5, 0))


class MyResultsTab:
    colors = ["red", "dark orange", "gold", "green", "blue", "purple", "grey", "black"]

    def __init__(self, parent, settings, results):
        self.parent = parent
        self.ft = ft.MyFonts()
        self.settings = settings
        self.results = results

        self.canvas_size = None
        self.canvas_curr = None
        self.canvas_coil = None
        self.tab = ttk.Frame(parent.tab_control)
        self.cap_grid = ttk.Frame(self.tab)  # sub-grid for the capacitor results

        lbl_cap_header = tk.Label(self.cap_grid, text="Calculated Capacitance (pF)", font=self.ft.myfont_bold, foreground="blue")

        self.lbl_cap = [tk.Label(self.cap_grid, text=f"C{i + 1}", font=self.ft.myfont_bold, foreground=self.colors[i]) for i in range(int(const.MAX_LEGS / 4))]
        self.txt_cap_res = [my_tk.MyEntry(self.cap_grid, text=self.results.cap[i], read_only=True, decimals=const.MAX_PRECISION) for i in range(int(const.MAX_LEGS / 4))]

        tk.Grid.columnconfigure(self.tab, 1, weight=0)  # weight of the column width
        tk.Grid.columnconfigure(self.tab, 0, weight=1)
        tk.Grid.columnconfigure(self.tab, 3, weight=1)
        tk.Grid.columnconfigure(self.cap_grid, 2, weight=1)

        self.cap_grid.grid(column=1, row=0, columnspan=2, sticky=tk.NW, pady=(10, 10), padx=(5, 0))
        lbl_cap_header.grid(column=0, row=0, columnspan=3, sticky=tk.NW, pady=(0, 5), padx=(0, 0))
        for i in range(int(const.MAX_LEGS / 4)):
            self.lbl_cap[i].grid(column=0, row=i + 1, sticky=tk.NW, pady=(0, 0), padx=(0, 5))
            self.txt_cap_res[i].grid(column=1, row=i + 1, sticky=tk.NW, pady=(0, 0), padx=(5, 0))

        self.initializeGraphs()

    def initializeGraphs(self):
        # current graph
        self.canvas_size = 200

        frm_curr_plot = tk.LabelFrame(self.tab)
        lbl_curr_plot = tk.Label(frm_curr_plot, text="Current distribution in the legs", font=self.ft.myfont_small_bold, foreground="blue")
        lbl_curr_plot.pack(anchor='nw')
        lbl_curr_plot2 = tk.Label(frm_curr_plot, text="Normalized current intensity", font=self.ft.myfont_small, foreground="black")
        lbl_curr_plot2.pack(anchor='nw')

        self.canvas_curr = tk.Canvas(frm_curr_plot, width=self.canvas_size, height=self.canvas_size, borderwidth=0, highlightbackground="grey")
        self._drawCurrentGraphAxis()
        self.canvas_curr.pack(pady=(10, 10))

        lbl_curr_plot2 = tk.Label(frm_curr_plot, text="Angular position of leg (degree)\nZero beginning at +X direction", font=self.ft.myfont_small, foreground="black")
        lbl_curr_plot2.pack(anchor='nw')

        # capacitor graph
        frm_cap_pos = tk.LabelFrame(self.tab)
        lbl_cap_pos = tk.Label(frm_cap_pos, text="Position of legs and capacitors", font=self.ft.myfont_small_bold, foreground="blue")
        lbl_cap_pos.pack(anchor='nw')
        lbl_curr_plot2 = tk.Label(frm_cap_pos, text="C: Capacitor", font=self.ft.myfont_small, foreground="black")
        lbl_curr_plot2.pack(anchor='nw')

        self.canvas_coil = tk.Canvas(frm_cap_pos, width=self.canvas_size, height=self.canvas_size, borderwidth=1, highlightbackground="grey")
        self._drawCoilGraphAxis()
        self.guiAdjust()
        self.guiClear()
        self.canvas_coil.pack(pady=(10, 10))

        frm_curr_plot.grid(column=1, row=2, sticky=tk.NW, padx=(5, 10))
        frm_cap_pos.grid(column=2, row=2, sticky=tk.NW)

    def _drawCoilGraphAxis(self):
        self.canvas_coil.create_line(self.canvas_size / 2, 0, self.canvas_size / 2, self.canvas_size, fill="blue", width=1)
        self.canvas_coil.create_line(0, self.canvas_size / 2, self.canvas_size, self.canvas_size / 2, fill="blue", width=1)
        self.canvas_coil.create_text(self.canvas_size / 2 + ((self.canvas_size - 40) / 2) - 20, self.canvas_size / 2 + 10, text="+X", font='freemono 9', fill='black')

    def drawCoilGraphShape(self):
        self.canvas_coil.delete("coilshape")
        if self.settings.setting_calc == const.Config.CIRCLE:
            self.canvas_coil.create_oval(20, 20, self.canvas_size - 20, self.canvas_size - 20, outline="green", width=1, tags='coilshape')
        else:
            ratio = self.settings.coil_diameter_short.get() / self.settings.coil_diameter_long.get()
            x_min = 20
            x_max = self.canvas_size - 20
            y_min = self.canvas_size / 2 - ((self.canvas_size / 2 - 20) * ratio)
            y_max = self.canvas_size / 2 + ((self.canvas_size / 2 - 20) * ratio)
            self.canvas_coil.create_oval(x_min, y_min, x_max, y_max, outline="green", width=1, tags='coilshape')

    def _drawCoilGraphLegsCaps(self): #TODO move parts to main program/calculate class
        self.guiAdjust()
        ellipse = self.settings.setting_calc == const.Config.ELLIPSE
        self.canvas_coil.delete("deletable")

        thetas = self.results.thetas
        xcoords = self.results.x_coords
        ycoords = self.results.y_coords
        bc_mode = self.settings.setting_coil_configuration.get()

        r = (self.canvas_size - 40) / 2
        a = self.settings.coil_diameter_long.get()
        b = self.settings.coil_diameter_short.get()
        legs = self.settings.nr_of_legs.get()

        r_hp = r + 6  # radius
        r_lp = r_hp + 4  # radius
        offset = thetas[0]  # rotate the c's to be in between the dots

        if ellipse:
            it = itertools.cycle(itertools.chain(range(0, int(legs / 4)), range(int(legs / 4) - 1, -1, -1)))
            ratio = b / a
            scale = r / (a / 2)
        else:
            ratio = 1
            scale = r / (self.settings.coil_diameter.get() / 2)

        for i, theta in enumerate(thetas[:legs]):
            x = scale * xcoords[i] + self.canvas_size / 2
            y = scale * ycoords[i] + self.canvas_size / 2
            self.canvas_coil.create_oval(x - 4, y - 4, x + 4, y + 4, fill="red", tags='deletable')

            # for i, theta in enumerate(thetas):  # angle and radius to x/y coords
            if ellipse or bc_mode != const.Mode.LOWPASS:  # if const.Mode.HIGHPASS or const.Mode.BANDPASS
                x = r_hp * math.cos(theta - offset) + (self.canvas_size / 2) + 1
                y = (r_hp * math.sin(theta - offset) * ratio) + (self.canvas_size / 2) - 1
            elif bc_mode != const.Mode.HIGHPASS:  # if const.Mode.LOWPASS or const.Mode.BANDPASS
                x = r_lp * math.cos(theta) + (self.canvas_size / 2) + 1
                y = (r_lp * math.sin(theta)) * ratio + (self.canvas_size / 2) - 1

            if ellipse:
                if legs - legs // 4 - 1 < i < legs:
                    self.canvas_coil.create_text(x, y, text=f"C{legs - i}", font=self.ft.myfont_small_bold, fill=self.colors[next(it)], tags='deletable')  # TODO better location of text
                else:
                    next(it)

            else:
                self.canvas_coil.create_text(x, y, text="C", font=self.ft.myfont_small, fill='black', tags='deletable')  # todo change to smaller font size

    def _drawCurrentGraphAxis(self):
        from_edge_l = 10
        from_edge_r = self.canvas_size - 10
        self.canvas_curr.create_line(from_edge_l, self.canvas_size / 2, from_edge_r, self.canvas_size / 2, fill="blue", width=2)  # middle line

        self.canvas_curr.create_line(from_edge_l, self.canvas_size / 2 - 5, from_edge_l, self.canvas_size / 2 + 5, fill="blue", width=2)  # left
        self.canvas_curr.create_line((from_edge_r - from_edge_l) / 4 + from_edge_l, self.canvas_size / 2 - 5, (from_edge_r - from_edge_l) / 4 + from_edge_l, self.canvas_size / 2 + 5, fill="blue", width=2)  # leftmiddle
        self.canvas_curr.create_line((from_edge_r - from_edge_l) / 2 + from_edge_l, self.canvas_size / 2 - 5, (from_edge_r - from_edge_l) / 2 + from_edge_l, self.canvas_size / 2 + 5, fill="blue", width=2)  # middle
        self.canvas_curr.create_line(from_edge_r - (from_edge_r - from_edge_l) / 4, self.canvas_size / 2 - 5, from_edge_r - (from_edge_r - from_edge_l) / 4, self.canvas_size / 2 + 5, fill="blue", width=2)  # rightmiddle
        self.canvas_curr.create_line(from_edge_r, self.canvas_size / 2 - 5, from_edge_r, self.canvas_size / 2 + 5, fill="blue", width=2)  # right

        self.canvas_curr.create_text(from_edge_l + 2, self.canvas_size / 2 + 15, text="0", font='freemono 8')
        self.canvas_curr.create_text((from_edge_r - from_edge_l) / 2 + from_edge_l, self.canvas_size / 2 + 15, text="180", font='freemono 9')
        self.canvas_curr.create_text(self.canvas_size - 10, self.canvas_size / 2 + 15, text="360", font='freemono 9')

    def _drawCurrentPlot(self): #TODO move parts to main program/calculate class
        self.canvas_curr.delete("deletable")

        legcurrs = self.results.leg_currs
        legs = self.settings.nr_of_legs.get()
        offset = 10

        highest_curr = 0
        for curr in legcurrs:
            if abs(curr) > highest_curr:
                highest_curr = abs(curr)
        scale = self.canvas_size / 2 / highest_curr / 1.3

        old_x = 0
        old_y = 0
        for i, curr in enumerate(legcurrs[:legs]):  # create the lines
            x = ((self.canvas_size - 20) / (legs - 1)) * i + offset
            y = -curr * scale + self.canvas_size / 2
            if i > 0:
                self.canvas_curr.create_line(x, y, old_x, old_y, width=1, fill='green', tags='deletable')
            old_x = x
            old_y = y

        for i, curr in enumerate(legcurrs[:legs]):  # create the dots
            x = ((self.canvas_size - 20) / (legs - 1)) * i + offset
            y = -curr * scale + self.canvas_size / 2
            self.canvas_curr.create_oval(x - 4, y - 4, x + 4, y + 4, fill='red', tags="deletable")

    def drawGraphs(self):
        self.drawCoilGraphShape()
        self._drawCoilGraphLegsCaps()
        self._drawCurrentPlot()

    def guiAdjust(self):
        for i in range(int(const.MAX_LEGS / 4)):
            self.lbl_cap[i].grid_remove()
            self.txt_cap_res[i].grid_remove()

        if self.settings.setting_calc == const.Config.ELLIPSE:
            for i in range(int(self.settings.nr_of_legs.get() / 4)):
                self.lbl_cap[i].grid()
                self.txt_cap_res[i].grid()
        else:
            self.txt_cap_res[0].grid()

    def guiClear(self):
        for i in range(int(const.MAX_LEGS / 4)): #TODO move to main program class
            self.txt_cap_res[i].clear()
        self.guiAdjust()

        self.canvas_curr.delete("deletable")
        self.canvas_coil.delete("deletable")


class MySettingsTab:
    def __init__(self, parent, settings, results):
        self.parent = parent
        self.ft = ft.MyFonts()
        self.settings = settings
        self.results = results
        self.tab = ttk.Frame(parent.tab_control)

        self._setGui()

        self.settings.setting_coil_configuration.trace("w", lambda *args: self.guiAdjust())
        self.settings.setting_leg_type.trace("w", lambda *args: self.guiAdjust())
        self.settings.setting_er_type.trace("w", lambda *args: self.guiAdjust())

        self.guiAdjust()

        # self.setDefaults()
        self.settings.reset()

    def linkToResultstab(self): #TODO move to main program class
        self.settings.nr_of_legs.trace("w", lambda *args: self.parent.guiTabResults.guiClear())
        self.settings.coil_diameter_short.trace("w", lambda *args: [self.parent.guiTabResults.guiClear(), self.parent.guiTabResults.drawCoilGraphShape()])
        self.settings.coil_diameter_long.trace("w", lambda *args: [self.parent.guiTabResults.guiClear(), self.parent.guiTabResults.drawCoilGraphShape()])

    def _setGui(self):
        # todo make sub functions for each LabelFrame

        lbl_title = tk.Label(self.tab, text="Circular Birdcage Coil ", font=self.ft.myfont_bold, foreground="blue")

        lf_type_of_legs = tk.LabelFrame(self.tab, text="Type of Leg", font=self.ft.myfont_bold)
        rb_leg_r = tk.Radiobutton(lf_type_of_legs, text='Rect', value=const.Shape.RECT, variable=self.settings.setting_leg_type)
        rb_leg_t = tk.Radiobutton(lf_type_of_legs, text='Tubular', value=const.Shape.TUBE, variable=self.settings.setting_leg_type)
        rb_leg_r.pack(anchor="w")
        rb_leg_t.pack(anchor="w")

        lf_type_of_er = tk.LabelFrame(self.tab, text="Type of ER", font=self.ft.myfont_bold)
        rb_er_r = tk.Radiobutton(lf_type_of_er, text='Rect', value=const.Shape.RECT, variable=self.settings.setting_er_type)
        rb_er_t = tk.Radiobutton(lf_type_of_er, text='Tubular', value=const.Shape.TUBE, variable=self.settings.setting_er_type)
        rb_er_r.pack(anchor="w")
        rb_er_t.pack(anchor="w")

        self.lf_config = tk.LabelFrame(self.tab, text="Configuration", font=self.ft.myfont_bold)
        rb_config_hp = tk.Radiobutton(self.lf_config, text='High-Pass', value=const.Mode.HIGHPASS, variable=self.settings.setting_coil_configuration)
        rb_config_lp = tk.Radiobutton(self.lf_config, text='Low-Pass', value=const.Mode.LOWPASS, variable=self.settings.setting_coil_configuration)
        rb_config_bp = tk.Radiobutton(self.lf_config, text='Band-Pass', value=const.Mode.BANDPASS, variable=self.settings.setting_coil_configuration)
        rb_config_hp.pack(anchor="w")
        rb_config_lp.pack(anchor="w")
        rb_config_bp.pack(anchor="w")

        self.frm_bp = tk.LabelFrame(self.lf_config)
        lb_bp_cap = tk.Label(self.frm_bp, text="Predetermined\ncapacitor (pF)", justify='left', fg='blue')
        txt_bp_cap = my_tk.NumInput(self.frm_bp, text=self.settings.bp_cap, width=5, bg="white", min_value=0.001)
        rb_bp_leg = tk.Radiobutton(self.frm_bp, text='On Leg', font=self.ft.myfont_bold, value=const.Part.LEG, variable=self.settings.setting_bp_cap_location)
        rb_bp_er = tk.Radiobutton(self.frm_bp, text='On ER', font=self.ft.myfont_bold, value=const.Part.ER, variable=self.settings.setting_bp_cap_location)

        lb_bp_cap.grid(row=0, sticky=tk.W, columnspan=2)
        txt_bp_cap.grid(row=1, column=1, rowspan=2, sticky=tk.W)
        rb_bp_leg.grid(row=1, sticky=tk.NW, padx=(0, 5))
        rb_bp_er.grid(row=2, sticky=tk.NW)
        self.frm_bp.pack(anchor="w")

        lf_nr_of_legs = tk.LabelFrame(self.tab, text="Number of Legs", font=self.ft.myfont_bold)
        scale_nr_of_legs = my_tk.MyScale(lf_nr_of_legs, from_=const.MIN_LEGS, to=const.MAX_LEGS, resolution=4, tickinterval=4, orient=tk.HORIZONTAL, length=250,
                                         variable=self.settings.nr_of_legs, command=lambda e: self.settings.nr_of_legs.set(int(scale_nr_of_legs.get())))
        scale_nr_of_legs.pack()

        lf_dimensions = tk.LabelFrame(self.tab, text="Dimensions (cm)", font=self.ft.myfont_bold)

        self.lb_coil_diameter = tk.Label(lf_dimensions, text="Coil Diameter ")
        self.lb_shield_diameter = tk.Label(lf_dimensions, text="RF shield Diameter ")
        self.txt_coil_diameter = my_tk.NumInput(lf_dimensions, text=self.settings.coil_diameter, width=7, bg="white", min_value=0)
        self.txt_shield_diameter = my_tk.NumInput(lf_dimensions, text=self.settings.shield_diameter, width=7, bg="white", min_value=0)

        self.lb_coil_short_diameter = tk.Label(lf_dimensions, text="Coil Diameter Short")
        self.lb_coil_long_diameter = tk.Label(lf_dimensions, text="Coil Diameter Long")
        self.txt_coil_short_diameter = my_tk.NumInput(lf_dimensions, text=self.settings.coil_diameter_short, width=7, bg="white", min_value=0)
        self.txt_coil_long_diameter = my_tk.NumInput(lf_dimensions, text=self.settings.coil_diameter_long, width=7, bg="white", min_value=0)

        lb_leg_length = tk.Label(lf_dimensions, text="Leg Length")
        self.lb_leg_width = tk.Label(lf_dimensions, text="Leg Width")
        self.lb_er_width = tk.Label(lf_dimensions, text="ER Seg. Width")
        txt_leg_length = my_tk.NumInput(lf_dimensions, text=self.settings.leg_length, width=7, bg="white", min_value=0)
        self.txt_leg_width = my_tk.NumInput(lf_dimensions, text=self.settings.leg_width, width=7, bg="white", min_value=0)
        self.txt_er_width = my_tk.NumInput(lf_dimensions, text=self.settings.er_width, width=7, bg="white", min_value=0)

        self.lb_leg_od = tk.Label(lf_dimensions, text="Leg O.D.")
        self.lb_leg_id = tk.Label(lf_dimensions, text="Leg I.D.")
        self.lb_er_od = tk.Label(lf_dimensions, text="ER O.D.")
        self.lb_er_id = tk.Label(lf_dimensions, text="ER I.D.")
        self.txt_leg_od = my_tk.NumInput(lf_dimensions, text=self.settings.leg_od, width=7, bg="white", min_value=0)
        self.txt_leg_id = my_tk.NumInput(lf_dimensions, text=self.settings.leg_id, width=7, bg="white", min_value=0)
        self.txt_er_od = my_tk.NumInput(lf_dimensions, text=self.settings.er_od, width=7, bg="white", min_value=0)
        self.txt_er_id = my_tk.NumInput(lf_dimensions, text=self.settings.er_id, width=7, bg="white", min_value=0)

        # automatic segment length calculation textbox, label
        self.lb_seg_length = tk.Label(lf_dimensions, text="ER Seg. length", foreground='blue')
        self.txt_seg_length = my_tk.MyEntry(lf_dimensions, text=self.results.er_segment_length, fg='grey', read_only=True, decimals=const.MAX_PRECISION)
        self.txt_seg_length.setValue("-")

        # column 1
        self.lb_coil_diameter.grid(column=0, row=0, sticky=tk.W, pady=(0, 10))
        self.txt_coil_diameter.grid(column=1, row=0, sticky=tk.W, pady=(0, 10))

        self.lb_coil_short_diameter.grid(column=0, row=0, sticky=tk.W, pady=(0, 10))
        self.txt_coil_short_diameter.grid(column=1, row=0, sticky=tk.W, pady=(0, 10))

        self.lb_coil_long_diameter.grid(column=0, row=1, sticky=tk.W, pady=(0, 10), padx=(0, 10))
        self.txt_coil_long_diameter.grid(column=1, row=1, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        lb_leg_length.grid(column=0, row=2, sticky=tk.W, pady=(0, 10))
        txt_leg_length.grid(column=1, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_leg_width.grid(column=0, row=3, sticky=tk.W, pady=(0, 10))
        self.txt_leg_width.grid(column=1, row=3, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_leg_od.grid(column=0, row=3, sticky=tk.W, pady=(0, 10))
        self.txt_leg_od.grid(column=1, row=3, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_leg_id.grid(column=0, row=4, sticky=tk.W, pady=(0, 10))
        self.txt_leg_id.grid(column=1, row=4, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        # column 2
        self.lb_shield_diameter.grid(column=2, row=0, sticky=tk.W, pady=(0, 10))
        self.txt_shield_diameter.grid(column=3, row=0, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_er_width.grid(column=2, row=2, sticky=tk.W, pady=(0, 10))
        self.txt_er_width.grid(column=3, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_er_od.grid(column=2, row=2, sticky=tk.W, pady=(0, 10))
        self.txt_er_od.grid(column=3, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_er_id.grid(column=2, row=3, sticky=tk.W, pady=(0, 10))
        self.txt_er_id.grid(column=3, row=3, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        self.lb_seg_length.grid(column=2, row=4, sticky=tk.W, pady=(0, 10))
        self.txt_seg_length.grid(column=3, row=4, sticky=tk.W, pady=(0, 10), padx=(0, 10))

        frm_f0 = tk.Frame(self.tab)
        lb_res_freq = tk.Label(frm_f0, font=self.ft.myfont_bold, text="Resonant\nFreq. (MHz)", justify='left')
        txt_res_freq = my_tk.NumInput(frm_f0, text=self.settings.freq, width=7, bg="white", min_value=0)
        lb_res_freq.grid(row=0, sticky=tk.W)
        txt_res_freq.grid(row=2, sticky=tk.W)

        btn = ttk.Button(self.tab, text="Calculate", command=self.parent.startCalculation)

        tk.Grid.columnconfigure(self.tab, 1, weight=0)
        tk.Grid.columnconfigure(self.tab, 0, weight=100)
        tk.Grid.columnconfigure(self.tab, 3, weight=1)
        tk.Grid.columnconfigure(self.tab, 4, weight=100)
        tk.Grid.rowconfigure(self.tab, 1, weight=1)
        tk.Grid.rowconfigure(self.tab, 10, weight=100)

        lbl_title.grid(column=1, row=0, sticky=tk.N + tk.EW, pady=(5, 10))
        lf_type_of_legs.grid(column=1, row=1, sticky=tk.NSEW, pady=(0, 10), padx=(5, 10))
        lf_type_of_er.grid(column=1, row=2, sticky=tk.NSEW, pady=(0, 10), padx=(5, 10))
        self.lf_config.grid(column=2, row=0, rowspan=2, sticky=tk.NSEW, pady=(0, 10), padx=(0, 10))
        lf_nr_of_legs.grid(column=2, row=2, columnspan=2, sticky=tk.NSEW, pady=(0, 10))
        lf_dimensions.grid(column=1, row=3, columnspan=3, sticky=tk.NSEW, pady=(0, 10), padx=(5, 0))
        frm_f0.grid(column=3, row=0, rowspan=2, sticky=tk.NSEW)
        btn.grid(column=1, row=4, columnspan=3)

    def guiAdjust(self):
        # adjusts the settings tab when clicking radiobuttons
        # try:
        if self.settings.setting_calc == const.Config.ELLIPSE:
            self.lf_config.grid_remove()

            self.lb_coil_diameter.grid_remove()
            self.txt_coil_diameter.grid_remove()

            self.lb_coil_short_diameter.grid()
            self.txt_coil_short_diameter.grid()
            self.lb_coil_long_diameter.grid()
            self.txt_coil_long_diameter.grid()

        else:
            self.lf_config.grid()

            self.lb_coil_diameter.grid()
            self.txt_coil_diameter.grid()

            self.lb_coil_short_diameter.grid_remove()
            self.txt_coil_short_diameter.grid_remove()
            self.lb_coil_long_diameter.grid_remove()
            self.txt_coil_long_diameter.grid_remove()
        # except AttributeError:
        # pass

        if self.settings.setting_leg_type.get() == const.Shape.RECT:
            self.lb_leg_width.grid()
            self.txt_leg_width.grid()

            self.lb_leg_od.grid_remove()
            self.txt_leg_od.grid_remove()
            self.lb_leg_id.grid_remove()
            self.txt_leg_id.grid_remove()
        else:
            self.lb_leg_width.grid_remove()
            self.txt_leg_width.grid_remove()

            self.lb_leg_od.grid()
            self.txt_leg_od.grid()
            self.lb_leg_id.grid()
            self.txt_leg_id.grid()

        if self.settings.setting_er_type.get() == const.Shape.RECT:
            self.lb_er_width.grid()
            self.txt_er_width.grid()

            self.lb_er_od.grid_remove()
            self.txt_er_od.grid_remove()
            self.lb_er_id.grid_remove()
            self.txt_er_id.grid_remove()

            self.lb_seg_length.grid(row=3)
            self.txt_seg_length.grid(row=3)
        else:
            self.lb_er_width.grid_remove()
            self.txt_er_width.grid_remove()

            self.lb_er_od.grid()
            self.txt_er_od.grid()
            self.lb_er_id.grid()
            self.txt_er_id.grid()

            self.lb_seg_length.grid(row=4)
            self.txt_seg_length.grid(row=4)

        if self.settings.setting_coil_configuration.get() == const.Mode.BANDPASS:
            self.frm_bp.pack()
        else:
            self.frm_bp.pack_forget()


class MyAboutWindow:
    def __init__(self, parent):
        self.parent = parent
        self.ft = ft.MyFonts()
        self.top = tk.Toplevel()
        self.top.transient(parent)
        self.top.update_idletasks()
        self.top.withdraw()
        self.top.title(f"About {const.PROGRAM_NAME}")  # {VERSION}")
        self.top.maxsize(400, 450)
        self.top.resizable(0, 0)
        self._setGui()
        self._centerWindow(self.top)
        self.top.deiconify()

    def _setGui(self):
        # logo
        self.top.img = img = tk.PhotoImage(file=const.ICON_FOLDER + "icon32.png")
        self.top.img = img = img.zoom(2)  # needs top.img = to not get garbage collected
        image = tk.Label(self.top, image=img)

        lb_prog = tk.Label(self.top, text=f"{const.PROGRAM_NAME} {const.VERSION}", anchor='w')

        import webbrowser #TODO better placement
        lb_site = tk.Label(self.top, text=f"{const.WEBSITE}", fg="blue", cursor="hand2", anchor='w', font=self.ft.myfont_underlined)
        lb_site.bind("<Button-1>", lambda e: webbrowser.open("http://" + const.WEBSITE, new=0, autoraise=True))

        txt = f"{const.PROGRAM_NAME} is a program to easily determine the ideal capacitor to be used in a birdcage coil design.\n\n" \
              "An acknowledgement goes to PennState Health for the original version and the math used in this program."
        msg = tk.Message(self.top, text=txt, justify='left', anchor='nw')
        msg.bind("<Configure>", lambda e: msg.configure(width=e.width - 10))

        # Buttons
        frm_button = tk.Frame(self.top)
        btn_license = ttk.Button(frm_button, text="License", command=self._showLicense, width=10)
        btn_ok = ttk.Button(frm_button, text="Ok", command=self.top.destroy, width=10)
        btn_license.pack(side="left", padx=(0, 10))
        btn_ok.pack(side="right")

        tk.Grid.columnconfigure(self.top, 1, weight=1)
        tk.Grid.rowconfigure(self.top, 3, weight=1)

        image.grid(column=0, row=0, rowspan=1, sticky=tk.NSEW, padx=(10, 10), pady=(10, 10))
        lb_prog.grid(column=1, row=0, sticky=tk.NSEW)
        lb_site.grid(column=0, row=1, columnspan=2, sticky=tk.NSEW, pady=(0, 10), padx=(10, 10))
        msg.grid(column=0, row=2, columnspan=2, sticky=tk.NSEW, pady=(0, 10), padx=(5, 5))

        frm_button.grid(column=0, row=4, columnspan=2, sticky=tk.N, pady=(10, 10))

    @staticmethod
    def _centerWindow(win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()

        my_tk.centerWindow(win, width, height)

    def _showLicense(self):
        with open("LICENSE.md", 'r') as license_file:
            license_ = license_file.read()

        top = tk.Toplevel()
        top.transient(self.parent)
        top.update_idletasks()
        top.withdraw()
        top.title(f"License")  # {VERSION}")
        top.resizable(0, 0)

        # scrollable textbox
        text = tk.Text(top, wrap=tk.WORD)
        text.insert(tk.INSERT, license_)
        text.pack(side="left", expand=True)
        scroll_y = tk.Scrollbar(top, orient="vertical", command=text.yview)
        scroll_y.pack(side="left", expand=True, fill="y")
        text.configure(yscrollcommand=scroll_y.set, width=80, height=21)
        text.configure(state='disabled')  # make readonly
        text.pack()

        self._centerWindow(top)
        top.deiconify()
