#!/usr/bin/env python3

"""
	Copyright (c) Dimitri Welting. All rights reserved.
	Source code can be found at http://github.com/dwelting/pyBirdcagebuilder
	This program is free to download and use. Any paid service providing this code is not endorsed by the author.

	This program is based on the original Birdcagebuilder program provided by PennState Health.
	(https://research.med.psu.edu/departments/center-for-nmr-research/software/birdcage-builder-web-app/)

	This code is licensed under the MIT License. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
"""

import tkinter as tk
from tkinter import ttk, font
from tkinter import messagebox as mb
import lib.mytk as my_tk
import math
import os
import warnings


PROGRAM_NAME = "pyBirdcagebuilder"
VERSION = "v0.1"
WEBSITE = "github.com/dwelting/pyBirdcagebuilder"

ICON_FOLDER = os.path.join(os.getcwd(), "icon", "")
MAX_PRECISION = 2



class MainApplication:
	WINDOWSIZEx = 500
	WINDOWSIZEy = 550
	
	HIGHPASS = 1
	LOWPASS = 2
	BANDPASS = 3
	RECT = 1
	TUBE = 2
	LEG = 1
	ER = 2
	
	ELLIPSE = 0
	CIRCLE = 1
	SHORT = 1
	LONG = 0

	def __init__(self, window):
		self._setWindow(window)
		self.window = window

		self.Config = MyConfig(self)

		# menubar
		self.menuBar = MyMenuBar(self)
		window.config(menu=self.menuBar.menu)

		self.tab_control = ttk.Notebook(window)  # tabs

		self.calcCapacitance = CalculateBirdcage(self)
		self.guiTabSettings = MySettingsTab(self)
		self.guiTabResults = MyResultsTab(self)
		self.guiTabMoreInfo = MyMoreInfoTab(self)

		self.tab_control.add(self.guiTabSettings.tab, text=' Settings ')
		self.tab_control.add(self.guiTabResults.tab, text=' Results ')
		self.tab_control.add(self.guiTabMoreInfo.tab, text=' More Information ')
		self.tab_control.pack(expand=1, fill='both', padx=(5, 5), pady=(5, 5))
		
		if os.name == 'posix':
			bg = ttk.Style().lookup('TFrame', 'background')
			self.guiTabSettings.tab.tk_setPalette(background=bg)  # only useful in linux. Hides color inconsistencies between widget bg and frame bg
		
	def _setWindow(self, window):
		window.title(f"{PROGRAM_NAME}")  # {VERSION}")

		my_tk.centerWindow(window, self.WINDOWSIZEx, self.WINDOWSIZEy)
		window.maxsize(self.WINDOWSIZEx, self.WINDOWSIZEy)
		window.minsize(self.WINDOWSIZEx, self.WINDOWSIZEy)
		window.resizable(0, 0)

		try:
			if os.name == 'posix':  # windows doesn't like 32px icons
				icon = "icon32.png"
			else:
				icon = "icon16.png"
			window.iconphoto(True, tk.PhotoImage(file=ICON_FOLDER + icon))
		except tk.TclError:
			warnings.warn("Icon error: no application icon found?")

	def startCalculation(self):
		if not self.guiTabSettings.validateInputs():
			return
		
		self.calcCapacitance.calculate()
		self.guiTabResults.drawCapacitors()
		self.guiTabResults.drawGraph()
		self.tab_control.select(1)  # At end switch tab to results


class MyConfig:
	#todo
	def __init__(self, parent):
		self.parent = parent

	def save(self):
		raise NotImplementedError

	def saveAs(self):
		raise NotImplementedError

	def load(self):
		raise NotImplementedError


class MyMenuBar:
	def __init__(self, parent):
		self.parent = parent

		self.coil_shape = tk.BooleanVar()  # selects which coil type
		self.coil_shape.set(True)

		self.menu = tk.Menu(parent.window)
		self._fileMenu()
		# self._optionMenu() #todo add when elliptical is fixed
		self._helpMenu()

	def _optionMenu(self):
		optionmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Options", menu=optionmenu)

		optionmenu.add_checkbutton(label="Circular", onvalue=self.parent.CIRCLE, offvalue=self.parent.ELLIPSE, command=lambda e: print("Not yet implemented"), variable=self.coil_shape)
		optionmenu.add_checkbutton(label="Eliptical", onvalue=self.parent.ELLIPSE, offvalue=self.parent.CIRCLE, command=lambda e: print("Not yet implemented"), variable=self.coil_shape)

	def _helpMenu(self):
		helpmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Help", menu=helpmenu)

		helpmenu.add_command(label=f"About {PROGRAM_NAME}", command=MyAboutWindow)

	def _fileMenu(self):
		filemenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="File", menu=filemenu)

		# filemenu.add_command(label="Save config", command=self.parent.Config.save)
		# filemenu.add_command(label="Save config as...", command=self.parent.Config.saveAs)
		# filemenu.add_command(label="Load config", command=self.parent.Config.load)
		# filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.parent.window.quit)


class MyMoreInfoTab:
	def __init__(self, parent):
		self.parent = parent
		self.tab = ttk.Frame(parent.tab_control)

		self.v_ind_self_legs = tk.DoubleVar()  # calculated self inductance of legs
		self.v_ind_self_er = tk.DoubleVar()  # calculated self inductance of end ring
		self.v_ind_eff_legs = tk.DoubleVar()  # calculated effective inductance of legs
		self.v_ind_eff_er = tk.DoubleVar()  # calculated effective inductance of end ring

		lf_ind_calc = tk.LabelFrame(self.tab, text="Inductance Calculations", font=myfont_bold)
		lbl_self = tk.Label(lf_ind_calc, text="Self (nH)", font=myfont_bold, foreground="blue")
		lbl_eff = tk.Label(lf_ind_calc, text="Effective (nH)", font=myfont_bold, foreground="blue")
		lb_legs = tk.Label(lf_ind_calc, text="Legs", font=myfont_bold)
		lb_er = tk.Label(lf_ind_calc, text="ER Seg.", font=myfont_bold)
	
		txt_self_legs = my_tk.MyEntry(lf_ind_calc, text=self.v_ind_self_legs, read_only=True, decimals=MAX_PRECISION)
		txt_self_er = my_tk.MyEntry(lf_ind_calc, text=self.v_ind_self_er, read_only=True, decimals=MAX_PRECISION)
		txt_eff_legs = my_tk.MyEntry(lf_ind_calc, text=self.v_ind_eff_legs, read_only=True, decimals=MAX_PRECISION)
		txt_eff_er = my_tk.MyEntry(lf_ind_calc, text=self.v_ind_eff_er, read_only=True, decimals=MAX_PRECISION)
	
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
	def __init__(self, parent):
		self.parent = parent
		self.tab = ttk.Frame(parent.tab_control)

		self.v_cap_res = tk.DoubleVar()  # calculated cap value

		lbl_cap = tk.Label(self.tab, text="Calculated Capacitance (pF)", font=myfont_bold, foreground="blue")
		txt_cap_res = my_tk.MyEntry(self.tab, text=self.v_cap_res, read_only=True, decimals=MAX_PRECISION)

		tk.Grid.columnconfigure(self.tab, 1, weight=0)
		tk.Grid.columnconfigure(self.tab, 0, weight=1)
		tk.Grid.columnconfigure(self.tab, 3, weight=1)
		lbl_cap.grid(column=1, row=0, columnspan=2, sticky=tk.NW, pady=(5, 5), padx=(5, 0))
		txt_cap_res.grid(column=1, row=1, sticky=tk.NW, pady=(0, 50), padx=(5, 0))
	
		self._initializeGraphs()
	
	def _initializeGraphs(self):
		# current graph
		self.canvas_size = 200

		frm_curr_plot = tk.LabelFrame(self.tab)
		lbl_curr_plot = tk.Label(frm_curr_plot, text="Current distribution in the legs", font=myfont_small_bold, foreground="blue")
		lbl_curr_plot.pack(anchor='nw')
		lbl_curr_plot2 = tk.Label(frm_curr_plot, text="Normalized current intensity", font=myfont_small, foreground="black")
		lbl_curr_plot2.pack(anchor='nw')

		self.canvas_curr = tk.Canvas(frm_curr_plot, width=self.canvas_size, height=self.canvas_size, borderwidth=0, highlightbackground="grey")
		self._drawGraphAxis()
		self.canvas_curr.pack(pady=(10, 10))

		lbl_curr_plot2 = tk.Label(frm_curr_plot, text="Angular position of leg (degree)\nZero beginning at +X direction", font=myfont_small, foreground="black")
		lbl_curr_plot2.pack(anchor='nw')
	
		# capacitor graph
		frm_cap_pos = tk.LabelFrame(self.tab)
		lbl_cap_pos = tk.Label(frm_cap_pos, text="Position of legs and capacitors", font=myfont_small_bold, foreground="blue")
		lbl_cap_pos.pack(anchor='nw')
		lbl_curr_plot2 = tk.Label(frm_cap_pos, text="C: Capacitor", font=myfont_small, foreground="black")
		lbl_curr_plot2.pack(anchor='nw')

		self.canvas_cap = tk.Canvas(frm_cap_pos, width=self.canvas_size, height=self.canvas_size, borderwidth=1, highlightbackground="grey")
		self._drawCapacitorAxis()
		self.canvas_cap.pack(pady=(10, 10))
	
		frm_curr_plot.grid(column=1, row=2, sticky=tk.NW, padx=(5, 10))
		frm_cap_pos.grid(column=2, row=2, sticky=tk.NW)

	def _drawCapacitorAxis(self):
		if self.parent.menuBar.coil_shape.get() == self.parent.CIRCLE:
			self.canvas_cap.create_oval(20, 20, self.canvas_size-20, self.canvas_size-20, outline="green", width=1)
		else:
			ratio = self.parent.guiTabSettings.v_coil_short_diameter.get() / self.parent.guiTabSettings.v_coil_long_diameter.get()
			x_min = 20
			x_max = self.canvas_size - 20
			y_min = self.canvas_size/2 - ((self.canvas_size/2 - 20) * ratio)
			y_max = self.canvas_size/2 + ((self.canvas_size/2 - 20) * ratio)
			self.canvas_cap.create_oval(x_min, y_min, x_max, y_max, outline="green", width=1)

		self.canvas_cap.create_line(self.canvas_size/2, 0, self.canvas_size/2, self.canvas_size, fill="blue", width=1)
		self.canvas_cap.create_line(0, self.canvas_size/2, self.canvas_size, self.canvas_size/2, fill="blue", width=1)
		self.canvas_cap.create_text(self.canvas_size/2+((self.canvas_size-40)/2)-20, self.canvas_size/2+10, text="+X", font='freemono 9', fill='black')

	def drawCapacitors(self):
		self.canvas_cap.delete("all")
		self._drawCapacitorAxis()
		thetas = self.parent.calcCapacitance.thetas
		bc_mode = self.parent.guiTabSettings.v_rb_config_selected.get()

		# if self.parent.menuBar.coil_shape.get() == ELLIPSE:
		#	ratio = self.parent.guiTabSettings.v_coil_short_diameter.get() / self.parent.guiTabSettings.v_coil_long_diameter.get()
		# else:
		#	ratio = 1

		r = ((self.canvas_size-40)/2)
		for theta in thetas:
			x = r * math.sin(theta) + self.canvas_size/2
			y = r * math.cos(theta) + self.canvas_size/2
			self.canvas_cap.create_oval(x - 4, y - 4, x + 4, y + 4, fill='red')

		r_hp = ((self.canvas_size-40)/2) + 6  # radius
		r_lp = r_hp + 4  # radius
		offset = thetas[0]  # rotate the c's to be in between the dots
		for theta in thetas:  # angle and radius to x/y coords
			if bc_mode != self.parent.LOWPASS:  # if highpass or bandpass
				x = r_hp * math.sin(theta - offset) + (self.canvas_size/2) + 1
				y = r_hp * math.cos(theta - offset) + (self.canvas_size/2) - 1
				self.canvas_cap.create_text(x, y, text="c", fill='blue')

			if bc_mode != self.parent.HIGHPASS:  # if lowpass or bandpass
				x = r_lp * math.sin(theta) + (self.canvas_size/2) + 1
				y = r_lp * math.cos(theta) + (self.canvas_size/2) - 1
				self.canvas_cap.create_text(x, y, text="c", fill='blue')

	def _drawGraphAxis(self):
		from_edge_l = 10
		from_edge_r = self.canvas_size-10
		self.canvas_curr.create_line(from_edge_l, self.canvas_size/2, from_edge_r, self.canvas_size/2, fill="blue", width=2)  # middle line

		self.canvas_curr.create_line(from_edge_l, self.canvas_size/2-5, from_edge_l, self.canvas_size/2+5, fill="blue", width=2)  # left
		self.canvas_curr.create_line((from_edge_r-from_edge_l)/4+from_edge_l, self.canvas_size/2-5, (from_edge_r-from_edge_l)/4+from_edge_l, self.canvas_size/2+5, fill="blue", width=2)  # leftmiddle
		self.canvas_curr.create_line((from_edge_r-from_edge_l)/2+from_edge_l, self.canvas_size/2-5, (from_edge_r-from_edge_l)/2+from_edge_l, self.canvas_size/2+5, fill="blue", width=2)  # middle
		self.canvas_curr.create_line(from_edge_r-(from_edge_r-from_edge_l)/4, self.canvas_size/2-5, from_edge_r-(from_edge_r-from_edge_l)/4, self.canvas_size/2+5, fill="blue", width=2)  # rightmiddle
		self.canvas_curr.create_line(from_edge_r, self.canvas_size/2-5, from_edge_r, self.canvas_size/2+5, fill="blue", width=2)  # right

		self.canvas_curr.create_text(from_edge_l+2, self.canvas_size/2+15, text="0", font='freemono 8')
		self.canvas_curr.create_text((from_edge_r-from_edge_l)/2+from_edge_l, self.canvas_size/2+15, text="180", font='freemono 9')
		self.canvas_curr.create_text(self.canvas_size-10, self.canvas_size/2+15, text="360", font='freemono 9')

	def drawGraph(self):
		self.canvas_curr.delete("all")
		self._drawGraphAxis()

		legcurrs = self.parent.calcCapacitance.legcurrs
		nr_of_legs = self.parent.calcCapacitance.nr_of_legs
		offset = 10

		highest_curr = 0
		for curr in legcurrs:
			if abs(curr) > highest_curr:
				highest_curr = abs(curr)
		scale = self.canvas_size/2 / highest_curr / 1.3

		old_x = 0
		old_y = 0
		for i, curr in enumerate(legcurrs):  # create the lines
			x = ((self.canvas_size-20) / (nr_of_legs-1)) * i + offset
			y = -curr * scale + self.canvas_size/2
			if i > 0:
				self.canvas_curr.create_line(x, y, old_x, old_y, width=1, fill='green')
			old_x = x
			old_y = y

		for i, curr in enumerate(legcurrs):  # create the dots
			x = ((self.canvas_size-20) / (nr_of_legs-1)) * i + offset
			y = -curr * scale + self.canvas_size/2
			self.canvas_curr.create_oval(x - 4, y - 4, x + 4, y + 4, fill='red')


class MySettingsTab:
	def __init__(self, parent):
		self.parent = parent
		self.tab = ttk.Frame(parent.tab_control)

		self.v_res_freq = tk.DoubleVar()  # variable for Resonance frequency
		self.v_rb_legs_selected = tk.IntVar()  # variable for state of radiobuttons
		self.v_rb_er_selected = tk.IntVar()  # variable for state of radiobuttons
		self.v_rb_config_selected = tk.IntVar()  # variable for state of radiobuttons
		self.v_nr_of_legs = tk.IntVar()
		self.v_coil_diameter = tk.DoubleVar()
		self.v_shield_diameter = tk.DoubleVar()
		self.v_bp_cap = tk.DoubleVar()
		self.v_rb_bp = tk.IntVar()
		self.v_leg_length = tk.DoubleVar()
		self.v_er_width = tk.DoubleVar()
		self.v_leg_width = tk.DoubleVar()
		self.v_er_od = tk.DoubleVar()
		self.v_er_id = tk.DoubleVar()
		self.v_leg_od = tk.DoubleVar()
		self.v_leg_id = tk.DoubleVar()

		self.v_coil_shortaxis = tk.IntVar()
		self.v_coil_long_diameter = tk.DoubleVar()
		self.v_coil_short_diameter = tk.DoubleVar()

		self.v_rb_legs_selected.set(self.parent.RECT)
		self.v_rb_er_selected.set(self.parent.RECT)
		self.v_rb_config_selected.set(self.parent.HIGHPASS)
		self.v_rb_bp.set(self.parent.LEG)

		self.v_er_seg_length = tk.DoubleVar()  # Calculated segment length

		self._setGui()

		self.v_rb_config_selected.trace("w", lambda *args: self._guiSettingsAdjust())
		self.v_rb_legs_selected.trace("w", lambda *args: self._guiSettingsAdjust())
		self.v_rb_er_selected.trace("w", lambda *args: self._guiSettingsAdjust())
		self._guiSettingsAdjust()

		self.setDefaults()

	def _setGui(self):
		#todo make sub functions for each gui part

		lbl_title = tk.Label(self.tab, text="Circular Birdcage Coil ", font=myfont_bold, foreground="blue")
	
		lf_type_of_legs = tk.LabelFrame(self.tab, text="Type of Leg", font=myfont_bold)
		rb_leg_r = tk.Radiobutton(lf_type_of_legs, text='Rectangular', value=self.parent.RECT, variable=self.v_rb_legs_selected)
		rb_leg_t = tk.Radiobutton(lf_type_of_legs, text='Tubular', value=self.parent.TUBE, variable=self.v_rb_legs_selected)
		rb_leg_r.pack(anchor="w")
		rb_leg_t.pack(anchor="w")
	
		lf_type_of_er = tk.LabelFrame(self.tab, text="Type of ER", font=myfont_bold)
		rb_er_r = tk.Radiobutton(lf_type_of_er, text='Rectangular', value=self.parent.RECT, variable=self.v_rb_er_selected)
		rb_er_t = tk.Radiobutton(lf_type_of_er, text='Tubular', value=self.parent.TUBE, variable=self.v_rb_er_selected)
		rb_er_r.pack(anchor="w")
		rb_er_t.pack(anchor="w")
	
		lf_config = tk.LabelFrame(self.tab, text="Configuration", font=myfont_bold)
		rb_config_hp = tk.Radiobutton(lf_config, text='High-Pass', value=self.parent.HIGHPASS, variable=self.v_rb_config_selected)
		rb_config_lp = tk.Radiobutton(lf_config, text='Low-Pass', value=self.parent.LOWPASS, variable=self.v_rb_config_selected)
		rb_config_bp = tk.Radiobutton(lf_config, text='Band-Pass', value=self.parent.BANDPASS, variable=self.v_rb_config_selected)
		rb_config_hp.pack(anchor="w")
		rb_config_lp.pack(anchor="w")
		rb_config_bp.pack(anchor="w")

		self.frm_bp = tk.LabelFrame(lf_config)
		lb_bp_cap = tk.Label(self.frm_bp, text="Predetermined\ncapacitor (pF)", justify='left', fg='blue')
		txt_bp_cap = my_tk.NumInput(self.frm_bp, text=self.v_bp_cap, width=5, bg="white", min_value=0.001)
		rb_bp_leg = tk.Radiobutton(self.frm_bp, text='On Leg', font=myfont_bold, value=self.parent.LEG, variable=self.v_rb_bp)
		rb_bp_er = tk.Radiobutton(self.frm_bp, text='On ER', font=myfont_bold, value=self.parent.ER, variable=self.v_rb_bp)
	
		lb_bp_cap.grid(row=0, sticky=tk.W, columnspan=2)
		txt_bp_cap.grid(row=1, column=1, rowspan=2, sticky=tk.W)
		rb_bp_leg.grid(row=1, sticky=tk.NW, padx=(0, 5))
		rb_bp_er.grid(row=2, sticky=tk.NW)
		self.frm_bp.pack(anchor="w")

		lf_nr_of_legs = tk.LabelFrame(self.tab, text="Number of Legs", font=myfont_bold)
		scale_nr_of_legs = my_tk.MyScale(lf_nr_of_legs, from_=8, to=32, resolution=4, tickinterval=4, orient=tk.HORIZONTAL, length=250,
							variable=self.v_nr_of_legs, command=lambda e: self.v_nr_of_legs.set(scale_nr_of_legs.get()))
		scale_nr_of_legs.pack()
	
		lf_dimensions = tk.LabelFrame(self.tab, text="Dimensions (cm)", font=myfont_bold)
		lb_leg_length = tk.Label(lf_dimensions, text="Leg Length")
		lb_coil_radius = tk.Label(lf_dimensions, text="Coil Diameter ")
		lb_shield_radius = tk.Label(lf_dimensions, text="RF shield Diameter ")
		txt_leg_length = my_tk.NumInput(lf_dimensions, text=self.v_leg_length, width=7, bg="white", min_value=0)
		txt_coil_radius = my_tk.NumInput(lf_dimensions, text=self.v_coil_diameter, width=7, bg="white", min_value=0)
		txt_shield_radius = my_tk.NumInput(lf_dimensions, text=self.v_shield_diameter, width=7, bg="white", min_value=0)

		self.lb_leg_width = tk.Label(lf_dimensions, text="Leg Width")
		self.lb_er_width = tk.Label(lf_dimensions, text="ER Seg. Width")
		self.txt_leg_width = my_tk.NumInput(lf_dimensions, text=self.v_leg_width, width=7, bg="white", min_value=0)
		self.txt_er_width = my_tk.NumInput(lf_dimensions, text=self.v_er_width, width=7, bg="white", min_value=0)

		self.lb_leg_od = tk.Label(lf_dimensions, text="Leg O.D.")
		self.lb_leg_id = tk.Label(lf_dimensions, text="Leg I.D.")
		self.lb_er_od = tk.Label(lf_dimensions, text="ER O.D.")
		self.lb_er_id = tk.Label(lf_dimensions, text="ER I.D.")
		self.txt_leg_od = my_tk.NumInput(lf_dimensions, text=self.v_leg_od, width=7, bg="white", min_value=0)
		self.txt_leg_id = my_tk.NumInput(lf_dimensions, text=self.v_leg_id, width=7, bg="white", min_value=0)
		self.txt_er_od = my_tk.NumInput(lf_dimensions, text=self.v_er_od, width=7, bg="white", min_value=0)
		self.txt_er_id = my_tk.NumInput(lf_dimensions, text=self.v_er_id, width=7, bg="white", min_value=0)

		# automatic segment length calculation textbox, label
		self.lb_seg_length = tk.Label(lf_dimensions, text="ER Seg. length", foreground='blue')
		self.txt_seg_length = my_tk.MyEntry(lf_dimensions, text=self.v_er_seg_length, fg='grey', read_only=True, decimals=MAX_PRECISION)
		self.txt_seg_length.setValue("-")
	
		lb_leg_length.grid(column=0, row=1, sticky=tk.W, pady=(0, 10))
		txt_leg_length.grid(column=1, row=1, sticky=tk.W, pady=(0, 10), padx=(0, 10))
		lb_coil_radius.grid(column=0, row=0, sticky=tk.W, pady=(0, 10))
		txt_coil_radius.grid(column=1, row=0, sticky=tk.W, pady=(0, 10))
		lb_shield_radius.grid(column=2, row=0, sticky=tk.W, pady=(0, 10))
		txt_shield_radius.grid(column=3, row=0, sticky=tk.W, pady=(0, 10), padx=(0, 10))
		self.lb_seg_length.grid(column=2, row=3, sticky=tk.W, pady=(0, 10))
		self.txt_seg_length.grid(column=3, row=3, sticky=tk.W, pady=(0, 10), padx=(0, 10))

		self.lb_leg_width.grid(column=0, row=2, sticky=tk.W, pady=(0, 10))
		self.txt_leg_width.grid(column=1, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))
		self.lb_er_width.grid(column=2, row=1, sticky=tk.W, pady=(0, 10))
		self.txt_er_width.grid(column=3, row=1, sticky=tk.W, pady=(0, 10), padx=(0, 10))
	
		self.lb_leg_od.grid(column=0, row=2, sticky=tk.W, pady=(0, 10))
		self.txt_leg_od.grid(column=1, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))
		self.lb_leg_id.grid(column=0, row=3, sticky=tk.W, pady=(0, 10))
		self.txt_leg_id.grid(column=1, row=3, sticky=tk.W, pady=(0, 10), padx=(0, 10))
	
		self.lb_er_od.grid(column=2, row=1, sticky=tk.W, pady=(0, 10))
		self.txt_er_od.grid(column=3, row=1, sticky=tk.W, pady=(0, 10), padx=(0, 10))
		self.lb_er_id.grid(column=2, row=2, sticky=tk.W, pady=(0, 10))
		self.txt_er_id.grid(column=3, row=2, sticky=tk.W, pady=(0, 10), padx=(0, 10))
	
		frm_f0 = tk.Frame(self.tab)
		lb_res_freq = tk.Label(frm_f0, font=myfont_bold, text="Resonant\nFreq. (MHz)", justify='left')
		txt_res_freq = my_tk.NumInput(frm_f0, text=self.v_res_freq, width=7, bg="white", min_value=0)
		lb_res_freq.grid(row=0, sticky=tk.W)
		txt_res_freq.grid(row=2, sticky=tk.W)

		btn = ttk.Button(self.tab, text="Calculate", command=self.parent.startCalculation)

		tk.Grid.columnconfigure(self.tab, 1, weight=0)
		tk.Grid.columnconfigure(self.tab, 0, weight=100)
		tk.Grid.columnconfigure(self.tab, 3, weight=1)
		tk.Grid.columnconfigure(self.tab, 4, weight=100)
		tk.Grid.rowconfigure(self.tab, 1, weight=1)
		tk.Grid.rowconfigure(self.tab, 10, weight=100)
	
		lbl_title.grid(column=1, row=0, sticky=tk.N+tk.EW, pady=(5, 10))
		lf_type_of_legs.grid(column=1, row=1, sticky=tk.NSEW, pady=(0, 10), padx=(5, 10))
		lf_type_of_er.grid(column=1, row=2, sticky=tk.NSEW, pady=(0, 10), padx=(5, 10))
		lf_config.grid(column=2, row=0, rowspan=2, sticky=tk.NSEW, pady=(0, 10), padx=(0, 10))
		lf_nr_of_legs.grid(column=2, row=2, columnspan=2, sticky=tk.NSEW, pady=(0, 10))
		lf_dimensions.grid(column=1, row=3, columnspan=3, sticky=tk.NSEW, pady=(0, 10), padx=(5, 0))
		frm_f0.grid(column=3, row=0, rowspan=2, sticky=tk.NSEW)
		btn.grid(column=1, row=4, columnspan=3)
	
	def validateInputs(self):
		inputs_ = [self.v_coil_diameter.get(),
				   self.v_res_freq.get(),
				   self.v_nr_of_legs.get(),
				   self.v_leg_length.get(),
				   self.v_er_width.get(),
				   self.v_leg_width.get(),
				   self.v_er_od.get(),
				   self.v_er_id.get(),
				   self.v_leg_od.get(),
				   self.v_leg_id.get(),
				   self.v_bp_cap.get(),
				   self.v_coil_long_diameter.get(),
				   self.v_coil_short_diameter.get()]
		for input_ in inputs_:
			if input_ == 0:
				mb.showwarning("Input zero", "One or more inputs are zero.\nPlease input valid values.")
				return False
		
		inputs_.append(self.v_shield_diameter.get())
		if inputs_[0] == inputs_[-1]:
			mb.showwarning("Zero shield distance", "Shield distance is equal to coil diameter.\nPlease input valid values.")
			return False
		
		return True
	
	def setDefaults(self):
		self.v_res_freq.set(120.6)
		self.v_leg_length.set(40)  # 20)
		self.v_leg_width.set(0.5)
		self.v_leg_od.set(1)
		self.v_leg_id.set(0.6)
		self.v_er_width.set(1.1)  # 0.5)
		self.v_er_od.set(1)
		self.v_er_id.set(0.6)
		self.v_coil_diameter.set(60)  # 15)
		self.v_shield_diameter.set(64)  # 17)
		self.v_nr_of_legs.set(24)  # 12)
		self.v_bp_cap.set(56)

		self.v_coil_shortaxis.set(self.parent.SHORT)
		self.v_coil_long_diameter.set(20)
		self.v_coil_short_diameter.set(5)

	def _guiSettingsAdjust(self):
		# adjusts the settings tab when clicking radiobuttons
		if self.v_rb_legs_selected.get() == self.parent.RECT:
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
	
		if self.v_rb_er_selected.get() == self.parent.RECT:
			self.lb_er_width.grid()
			self.txt_er_width.grid()
	
			self.lb_er_od.grid_remove()
			self.txt_er_od.grid_remove()
			self.lb_er_id.grid_remove()
			self.txt_er_id.grid_remove()
	
			self.lb_seg_length.grid(row=2)
			self.txt_seg_length.grid(row=2)
		else:
			self.lb_er_width.grid_remove()
			self.txt_er_width.grid_remove()
	
			self.lb_er_od.grid()
			self.txt_er_od.grid()
			self.lb_er_id.grid()
			self.txt_er_id.grid()
	
			self.lb_seg_length.grid(row=3)
			self.txt_seg_length.grid(row=3)
	
		if self.v_rb_config_selected.get() == self.parent.BANDPASS:
			self.frm_bp.pack()
		else:
			self.frm_bp.pack_forget()


class MyAboutWindow:
	def __init__(self):
		self.top = tk.Toplevel()
		self.top.transient(root)
		self.top.update_idletasks()
		self.top.withdraw()
		self.top.title(f"About {PROGRAM_NAME}")  # {VERSION}")
		self.top.maxsize(400, 450)
		self.top.resizable(0, 0)
		self._setGui()
		self._centerWindow(self.top)
		self.top.deiconify()

		
	def _setGui(self):
		# logo
		self.top.img = img = tk.PhotoImage(file=ICON_FOLDER + "icon32.png")
		self.top.img = img = img.zoom(2)  # needs top.img = to not get garbage collected
		image = tk.Label(self.top, image=img)
	
		lb_prog = tk.Label(self.top, text=f"{PROGRAM_NAME} {VERSION}", anchor='w')
	
		import webbrowser
		myfont_underlined = default_font.copy()
		myfont_underlined.configure(underline=True)
		lb_site = tk.Label(self.top, text=f"{WEBSITE}", fg="blue", cursor="hand2", anchor='w', font=myfont_underlined)
		lb_site.bind("<Button-1>", lambda e: webbrowser.open("http://"+WEBSITE, new=0, autoraise=True))

		txt = f"{PROGRAM_NAME} is a program to easily determine the ideal capacitor to be used in a birdcage coil design.\n\n" \
			"An acknowledgement goes to PennState Health for the original version and the math used in this program."
		msg = tk.Message(self.top, text=txt,  justify='left', anchor='nw')
		msg.bind("<Configure>", lambda e: msg.configure(width=e.width-10))

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
		with open(os.path.join(os.getcwd(), "LICENSE.md"), 'r') as license_file:
			license_ = license_file.read()

		top = tk.Toplevel()
		top.transient(root)
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


class CalculateBirdcage:
	#All math is copied from the original Birdcagebuilder made by PennState Health, and converted to Python

	def __init__(self, parent):
		self.parent = parent

		self._division = 97684  # magic number?

	def calculate(self):
		self._getValuesFromGui()
		self._initLocalValues()

		self._calcGeometry()
		self._calcCurrents()
		self._calcSelfInductances()
		self._calcEffLeg()
		self._calcEffER()
		self._calcCapacitance()
		
		self._exportResults()
	
	def _getValuesFromGui(self):
		self.res_freq = self.parent.guiTabSettings.v_res_freq.get()  # variable for Resonance frequency
		self.nr_of_legs = self.parent.guiTabSettings.v_nr_of_legs.get()
		self.shield_radius = self.parent.guiTabSettings.v_shield_diameter.get() / 2
		self.leg_length = self.parent.guiTabSettings.v_leg_length.get()
		self.er_width = self.parent.guiTabSettings.v_er_width.get()
		self.leg_width = self.parent.guiTabSettings.v_leg_width.get()
		self.er_od = self.parent.guiTabSettings.v_er_od.get()
		self.er_id = self.parent.guiTabSettings.v_er_id.get()
		self.leg_od = self.parent.guiTabSettings.v_leg_od.get()
		self.leg_id = self.parent.guiTabSettings.v_leg_id.get()

		self.bp_cap = self.parent.guiTabSettings.v_bp_cap.get()
		self.leg_config = self.parent.guiTabSettings.v_rb_legs_selected.get()
		self.er_config = self.parent.guiTabSettings.v_rb_er_selected.get()
		self.coil_mode = self.parent.guiTabSettings.v_rb_config_selected.get()
		self.bp_config = self.parent.guiTabSettings.v_rb_bp.get()
		self.coil_shape = self.parent.menuBar.coil_shape.get()

		self.shortaxis = self.parent.guiTabSettings.v_coil_shortaxis.get()
		if self.coil_shape == self.parent.ELLIPSE:
			raise NotImplementedError
			# noinspection PyUnreachableCode
			self.coil_radius = self.parent.guiTabSettings.v_coil_long_diameter.get() / 2
			self.coil_shortradius = self.parent.guiTabSettings.v_coil_short_diameter.get() / 2
		else:
			self.coil_radius = self.parent.guiTabSettings.v_coil_diameter.get() / 2
			self.coil_shortradius = self.coil_radius

	def _initLocalValues(self):
		self.radius = [0.0 for _ in range(self.nr_of_legs)]
		self.thetas = [0.0 for _ in range(self.nr_of_legs)]
		self.xcoords = [0.0 for _ in range(self.nr_of_legs)]
		self.ycoords = [0.0 for _ in range(self.nr_of_legs)]
		self.legcurrs = [0.0 for _ in range(self.nr_of_legs)]
		self.ercurrs = [0.0 for _ in range(self.nr_of_legs)]
		self.legeff = [0.0 for _ in range(self.nr_of_legs)]
		self.ereff = [0 for _ in range(self.nr_of_legs)]
		self.cap = [0.0 for _ in range(int(self.nr_of_legs))]
		self.leg_self_ind = 0
		self.er_self_ind = 0
		self.er_segment_length = 0

		self.delta = self.coil_radius / self._division

	def _calcGeometry(self):
		if self.coil_shape == self.parent.ELLIPSE:
			n = 0
			n2 = 0
			for i in range(0, self._division):
				n2 = i * self.delta
				n += self.delta * math.sqrt(1 + (self.coil_shortradius / self.coil_radius * n2)**2 / (self.coil_radius * self.coil_radius - n2**2))
			self.er_segment_length = n * 4 / self.nr_of_legs

			for i in range(1, int(self.nr_of_legs / 4)+1):
				n4 = 0
				n5 = self.er_segment_length / 2 * (2 * i - 1)
				# for (int n6 = 1; n5 - n4 > 0.0; n4 += self.delta * math.sqrt(1.0 + math.pow(self.coil_shortradius / self.coil_radius * n2, 2.0)
				#	   / (self.coil_radius * self.coil_radius - math.pow(n2, 2.0))), ++n6) { #original
				n6 = 1
				while n5 - n4 > 0:  # todo check if correct, the original for-loop was strange
					n4 += self.delta * math.sqrt(1 + ((self.coil_shortradius / self.coil_radius) * n2)**2 / (self.coil_radius**2 - n2**2))
					n2 = (n6 - 1) * self.delta
					n6 += 1

				self.xcoords[int(self.nr_of_legs / 4 - i)] = n2
				self.ycoords[int(self.nr_of_legs / 4 - i)] = abs(math.sqrt(self.coil_shortradius * self.coil_shortradius * (1.0 - n2 / self.coil_radius * (n2 / self.coil_radius))))
				self.thetas[int(self.nr_of_legs / 4 - i)] = math.atan(self.ycoords[int(self.nr_of_legs / 4 - i)] / self.xcoords[int(self.nr_of_legs / 4 - i)])
				self.radius[int(self.nr_of_legs / 4 - i)] = math.sqrt((self.xcoords[int(self.nr_of_legs / 4 - i)])**2 + (self.ycoords[int(self.nr_of_legs / 4 - i)])**2)
		else:
			self.er_segment_length = 2 * math.pi * (self.coil_radius / self.nr_of_legs)

			# Calc helper variables
			for i in range(0, int(self.nr_of_legs / 4)):
				self.radius[i] = self.coil_radius
				self.thetas[i] = math.pi / self.nr_of_legs * (2 * i + 1)
				self.xcoords[i] = self.coil_radius * math.cos(self.thetas[i])
				self.ycoords[i] = self.coil_radius * math.sin(self.thetas[i])


		for i in range(0, int(self.nr_of_legs / 4)):
			self.xcoords[int(self.nr_of_legs / 2 - (i + 1))] = -self.xcoords[i]
			self.xcoords[int(self.nr_of_legs / 2 + i)] = -self.xcoords[i]
			self.xcoords[int(self.nr_of_legs - (i + 1))] = self.xcoords[i]
			self.ycoords[int(self.nr_of_legs / 2 - (i + 1))] = self.ycoords[i]
			self.ycoords[int(self.nr_of_legs / 2 + i)] = -self.ycoords[i]
			self.ycoords[int(self.nr_of_legs - (i + 1))] = -self.ycoords[i]
			self.radius[int(self.nr_of_legs / 2 - (i + 1))] = self.radius[i]
			self.radius[int(self.nr_of_legs / 2 + i)] = self.radius[i]
			self.radius[int(self.nr_of_legs - (i + 1))] = self.radius[i]
			self.thetas[int(self.nr_of_legs / 2 - (i + 1))] = math.pi - self.thetas[i]
			self.thetas[int(self.nr_of_legs / 2 + i)] = math.pi + self.thetas[i]
			self.thetas[int(self.nr_of_legs - (i + 1))] = 2 * math.pi - self.thetas[i]

	def _calcCurrents(self):
		# Calc leg/er currents
		n = 1
		n2 = 1
		if self.shortaxis or self.coil_shape == self.parent.CIRCLE:
			n2 = 0
		else:
			n = 0

		for i in range(0, self.nr_of_legs):
			self.legcurrs[i] = (n * self.coil_shortradius * self.coil_shortradius * math.cos(self.thetas[i]) + n2 * self.coil_radius * self.coil_radius * math.sin(self.thetas[i])) \
								/ (self.coil_shortradius * self.coil_shortradius * math.cos(self.thetas[i]) * math.cos(self.thetas[i]) + self.coil_radius * self.coil_radius
								* math.sin(self.thetas[i]) * math.sin(self.thetas[i]))

		if (not self.shortaxis) and self.coil_shape == self.parent.ELLIPSE:
			self.ercurrs[int(self.nr_of_legs / 4 - 1)] = 0
			self.ercurrs[int(3 * self.nr_of_legs / 4 - 1)] = 0
			self.ercurrs[int(self.nr_of_legs / 4 - 1 - 1)] = -self.legcurrs[int(self.nr_of_legs / 4 - 1)]

			for i in range(1, int(self.nr_of_legs / 4 - 1)):
				self.ercurrs[int(self.nr_of_legs / 4 - 1 - (i + 1))] = self.ercurrs[int(self.nr_of_legs / 4 - 1 - i)] - self.legcurrs[int(self.nr_of_legs / 4 - 1 - i)]
			self.ercurrs[int(self.nr_of_legs - 1)] = self.ercurrs[0] - self.legcurrs[0]
			self.ercurrs[int(self.nr_of_legs / 2 - 1)] = -self.ercurrs[self.nr_of_legs - 1]

			for i in range(0, int(self.nr_of_legs / 4 - 1)):
				self.ercurrs[int(self.nr_of_legs / 4 + i)] = -self.ercurrs[int(self.nr_of_legs / 4 - (i + 1) - 1)]
				self.ercurrs[int(3 * self.nr_of_legs / 4 - (i + 1) - 1)] = -self.ercurrs[int(self.nr_of_legs / 4 - (i + 1) - 1)]
				self.ercurrs[int(3 * self.nr_of_legs / 4 + i)] = self.ercurrs[int(self.nr_of_legs / 4 - (i + 1) - 1)]

		else:
			n = 0
			for i in range(0, self.nr_of_legs):
				n += self.legcurrs[i]
				self.ercurrs[i] = n

			self.ercurrs[int(self.nr_of_legs / 2 - 1)] = 0
			self.ercurrs[int(self.nr_of_legs - 1)] = 0

	def _calcSelfInductances(self):
		if self.er_config == self.parent.RECT:
			self.er_self_ind = 2 * self.er_segment_length * (math.log(2 * self.er_segment_length / self.er_width) + 0.5)
		else:
			n = self.er_id / self.er_od
			if n == 0:
				self.er_self_ind = 2 * self.er_segment_length * (math.log(4 * self.er_segment_length / self.er_od) - 0.75)
			else:
				self.er_self_ind = 2 * self.er_segment_length * (math.log(4 * self.er_segment_length / self.er_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)

		if self.leg_config == self.parent.RECT:
			self.leg_self_ind = 2 * self.leg_length * (math.log(2 * self.leg_length / self.leg_width) + 0.5)
		else:
			n = self.leg_id / self.leg_od
			if n == 0:
				self.leg_self_ind = 2 * self.leg_length * (math.log(4 * self.leg_length / self.leg_od) - 0.75)
			else:
				self.leg_self_ind = 2 * self.leg_length * (math.log(4 * self.leg_length / self.leg_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)

	def _calcEffLeg(self):
		# Calc effective inductance of legs
		for i in range(0, self.nr_of_legs):
			n = 0
			for j in range(0, self.nr_of_legs):
				if i == j:
					n += self.leg_self_ind
				else:
					sqrt_ = math.sqrt((self.xcoords[j] - self.xcoords[i]) ** 2 + (self.ycoords[j] - self.ycoords[i]) ** 2)
					n += 2 * self.leg_length * (math.log(self.leg_length / sqrt_ + math.sqrt(1 + (self.leg_length / sqrt_) ** 2)) - math.sqrt(1 + (sqrt_ / self.leg_length) ** 2)
							+ sqrt_ / self.leg_length) * self.legcurrs[j] / self.legcurrs[i]
			self.legeff[i] = n * 1e-9

		if self.shield_radius != 0:
			array = [0.0 for _ in range(self.nr_of_legs)]
			array2 = [0.0 for _ in range(self.nr_of_legs)]
			for i in range(0, self.nr_of_legs):
				n = self.shield_radius * self.shield_radius / self.radius[i]
				array[i] = n * math.cos(self.thetas[i])
				array2[i] = n * math.sin(self.thetas[i])

			for i in range(0, self.nr_of_legs):
				n = 0
				for j in range(0, self.nr_of_legs):
					sqrt2 = math.sqrt((array[j] - self.xcoords[i]) ** 2 + (array2[j] - self.ycoords[i]) ** 2)
					n += 2 * self.leg_length * (math.log(self.leg_length / sqrt2 + math.sqrt(1 + (self.leg_length / sqrt2) ** 2)) - math.sqrt(1 + (sqrt2 / self.leg_length) ** 2)
												+ sqrt2 / self.leg_length) * -1 * self.legcurrs[j] / self.legcurrs[i]
				self.legeff[i] += n * 1e-9

	def _calcEffER(self):
		# Calc effective inductance of endring
		for i in range(0, self.nr_of_legs):
			self.ereff[i] += self.er_self_ind

		for i in range(0, self.nr_of_legs):
			n = self.xcoords[int((i + self.nr_of_legs / 2) % self.nr_of_legs)]
			n2 = self.ycoords[int((i + self.nr_of_legs / 2) % self.nr_of_legs)]
			n3 = self.xcoords[int((i + self.nr_of_legs / 2 + 1) % self.nr_of_legs)]
			n4 = self.ycoords[int((i + self.nr_of_legs / 2 + 1) % self.nr_of_legs)]
			n5 = self.xcoords[int((i + 1) % self.nr_of_legs)]
			n6 = self.ycoords[int((i + 1) % self.nr_of_legs)]
			n7 = self.xcoords[i]
			n8 = self.ycoords[i]
			math.sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
			sqrt_ = math.sqrt((n7 - n5) ** 2 + (n8 - n6) ** 2)
			sqrt2 = math.sqrt((n - n5) ** 2 + (n2 - n6) ** 2)
			if self.ercurrs[i] == 0:
				self.ereff[i] += 0
			else:
				self.ereff[i] += 2 * sqrt_ * (math.log(sqrt_ / sqrt2 + math.sqrt(1 + (sqrt_ / sqrt2) ** 2)) - math.sqrt(1 + (sqrt2 / sqrt_) ** 2) + sqrt2 / sqrt_)

		for i in range(0, self.nr_of_legs):
			n = self.xcoords[i]
			n2 = self.ycoords[i]
			n3 = self.xcoords[(i + 1) % self.nr_of_legs]
			n4 = self.ycoords[(i + 1) % self.nr_of_legs]
			n5 = self.xcoords[(i + 2) % self.nr_of_legs]
			n6 = self.ycoords[(i + 2) % self.nr_of_legs]
			sqrt_ = math.sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
			sqrt2 = math.sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
			sqrt3 = math.sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
			abs_ = abs(2 * ((sqrt3 ** 2 + sqrt_ ** 2 - sqrt2 ** 2) / (2 * sqrt3 * sqrt_)) * (sqrt3 * math.atanh(sqrt_ / (sqrt3 + sqrt2)) + sqrt_ * math.atanh(sqrt3 / (sqrt_ + sqrt2))))

			n = self.xcoords[(i - 1 + self.nr_of_legs) % self.nr_of_legs]
			n2 = self.ycoords[(i - 1 + self.nr_of_legs) % self.nr_of_legs]
			n3 = self.xcoords[i]
			n4 = self.ycoords[i]
			n5 = self.xcoords[(i + 1) % self.nr_of_legs]
			n6 = self.ycoords[(i + 1) % self.nr_of_legs]
			sqrt_ = math.sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
			sqrt2 = math.sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
			sqrt3 = math.sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
			abs2 = abs(2 * ((sqrt2 ** 2 + sqrt_ ** 2 - sqrt3 ** 2) / (2 * sqrt2 * sqrt_)) * (sqrt2 * math.atanh(sqrt_ / (sqrt2 + sqrt3)) + sqrt_ * math.atanh(sqrt2 / (sqrt_ + sqrt3))))
			if self.ercurrs[i] == 0:
				self.ereff[i] += 0
			else:
				self.ereff[i] += (abs_ * self.ercurrs[(i + 1) % self.nr_of_legs] + abs2 * self.ercurrs[(i - 1 + self.nr_of_legs) % self.nr_of_legs]) / self.ercurrs[i]

		array_ = [0 for _ in range(self.nr_of_legs - 3)]
		array2 = [0 for _ in range(self.nr_of_legs - 3)]
		for i in range(0, self.nr_of_legs):
			n = self.xcoords[i]
			n2 = self.ycoords[i]
			n3 = self.xcoords[(i + 1) % self.nr_of_legs]
			n4 = self.ycoords[(i + 1) % self.nr_of_legs]
			n5 = n3 - n
			n6 = n4 - n2
			if self.ercurrs[i] == 0:
				self.ereff[i] += 0
			else:
				for j in range(i + 2, i + self.nr_of_legs - 1):
					n7 = self.xcoords[j % self.nr_of_legs]
					n8 = self.ycoords[j % self.nr_of_legs]
					n9 = self.xcoords[(j + 1) % self.nr_of_legs]
					n10 = self.ycoords[(j + 1) % self.nr_of_legs]
					n11 = n9 - n7
					n12 = n10 - n8

					if self.ercurrs[i] == 0:
						array2[j - i - 2] = 0
					elif n5 * n11 + n6 * n12 > 0:
						array2[j - i - 2] = 1
					else:
						array2[j - i - 2] = -1

					sqrt_ = math.sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
					sqrt2 = math.sqrt((n9 - n7) ** 2 + (n10 - n8) ** 2)
					a2 = (n - n7) ** 2 + (n2 - n8) ** 2
					a3 = (n3 - n7) ** 2 + (n4 - n8) ** 2
					a4 = (n - n9) ** 2 + (n2 - n10) ** 2
					a5 = (n3 - n9) ** 2 + (n4 - n10) ** 2
					n13 = a3 - a2 + a4 - a5
					n14 = n13 / (sqrt2 * sqrt_)
					n15 = 4 * sqrt2 * sqrt2 * sqrt_ * sqrt_ - n13 * n13
					n16 = 4 * sqrt2 * sqrt2 * sqrt_ * sqrt_ - n13 * n13

					if n15 == 0:
						n17 = 0
					else:
						n17 = (2 * sqrt_ ** 2 * (a4 - a2 - sqrt2 * sqrt2) + n13 * (a3 - a2 - sqrt_ ** 2)) * sqrt2 / (4 * sqrt2 ** 2 * sqrt_ * sqrt_ - n13 ** 2)

					if n16 == 0:
						n18 = 0
					else:
						n18 = (2 * sqrt2 ** 2 * (a3 - a2 - sqrt_ ** 2) + n13 * (a4 - a2 - sqrt2 ** 2)) * sqrt_ / (4 * sqrt2 ** 2 * sqrt_ * sqrt_ - n13 ** 2)

					sqrt3 = math.sqrt(a3)
					sqrt4 = math.sqrt(a2)
					sqrt5 = math.sqrt(a4)
					sqrt6 = math.sqrt(a5)
					
					array_[j - i - 2] = n14 * ((n17 + sqrt2) * math.atanh(sqrt_ / (sqrt6 + sqrt5)) + (n18 + sqrt_) * math.atanh(sqrt2 / (sqrt6 + sqrt3)) - n17
											* math.atanh(sqrt_ / (sqrt4 + sqrt3)) - n18 * math.atanh(sqrt2 / (sqrt5 + sqrt4)))

				n19 = 0
				for j in range(0, self.nr_of_legs - 3):
					if j != (self.nr_of_legs - 4) / 2:
						if self.coil_shape == self.parent.ELLIPSE:
							n19 += array_[j] * abs(self.ercurrs[(j + i + 2) % self.nr_of_legs] / self.ercurrs[i]) * array2[j]
						else:
							n19 += array_[j] * abs(self.ercurrs[(j + i + 2) % self.nr_of_legs] / self.ercurrs[i])
				self.ereff[i] += n19

		for i in range(0, self.nr_of_legs):
			self.ereff[i] *= 1e-9

	def _calcCapacitance(self):
		array = [0.0 for _ in range(self.nr_of_legs)]
		n = 2 * math.pi * self.res_freq * 1e6
		for i in range(0, self.nr_of_legs):
			array[i] = 0.5 * n * self.legeff[i] * self.legcurrs[i]

		if self.coil_shape == self.parent.ELLIPSE:
			if self.shortaxis:
				self.cap[int(self.nr_of_legs / 4 - 1)] = self.ercurrs[int(self.nr_of_legs / 4 - 1)] / (n * n * self.ercurrs[int(self.nr_of_legs / 4 - 1)]
														* self.ereff[int(self.nr_of_legs / 4 - 1)] + n * 2.0 * array[int(self.nr_of_legs / 4 - 1)]) * 1e12
			else:
				self.cap[self.nr_of_legs - 1] = -self.ercurrs[self.nr_of_legs - 1] / (-n * n * self.ercurrs[self.nr_of_legs - 1] * self.ereff[self.nr_of_legs - 1] + n
												* (array[0] - array[self.nr_of_legs - 1])) * 1e12
			for j in range(0, int(self.nr_of_legs / 4 - 1)):
				self.cap[j] = self.ercurrs[j] / (n * n * self.ercurrs[j] * self.ereff[j] + n * (array[j] - array[j + 1])) * 1e12
		
		else:
			if self.coil_mode == self.parent.HIGHPASS or (self.coil_mode == self.parent.BANDPASS and self.bp_config == self.parent.LEG):
				n2 = 0
				if self.coil_mode == self.parent.BANDPASS:
					n2 = -0.5 * (self.legcurrs[int(self.nr_of_legs / 4 - 1)] / (n * self.bp_cap)) * 1e12
	
				self.cap[int(self.nr_of_legs / 4 - 1)] = self.ercurrs[int(self.nr_of_legs / 4 - 1)] / (
							n ** 2 * self.ercurrs[int(self.nr_of_legs / 4 - 1)] * (self.ereff[int(self.nr_of_legs / 4 - 1)]) + n * 2 * (array[int(self.nr_of_legs / 4 - 1)] + n2)) * 1e12
			else:
				if self.coil_mode == self.parent.BANDPASS:
					n3 = -self.ercurrs[int(self.nr_of_legs / 4 - 1)] * (n ** 2 * self.ereff[int(self.nr_of_legs / 4 - 1)] - 1 / self.bp_cap * 1e12)
					n4 = self.legcurrs[int(self.nr_of_legs / 4)] * n ** 2 * self.legeff[int(self.nr_of_legs / 4)]
				else:
					n3 = -self.ercurrs[int(self.nr_of_legs / 4 - 1)] * n ** 2 * self.ereff[int(self.nr_of_legs / 4 - 1)]
					n4 = self.legcurrs[int(self.nr_of_legs / 4)] * n ** 2 * self.legeff[int(self.nr_of_legs / 4)]
	
				self.cap[int(self.nr_of_legs / 4 - 1)] = self.legcurrs[int(self.nr_of_legs / 4)] / (n4 + n3) * 1e12

	def _exportResults(self):
		# export results to gui
		self.parent.guiTabMoreInfo.v_ind_self_er.set(self.er_self_ind)
		self.parent.guiTabMoreInfo.v_ind_self_legs.set(self.leg_self_ind)
		self.parent.guiTabMoreInfo.v_ind_eff_legs.set(self.legeff[int(self.nr_of_legs / 4 - 1)] * 1e9)
		self.parent.guiTabMoreInfo.v_ind_eff_er.set(self.ereff[int(self.nr_of_legs / 4 - 1)] * 1e9)
		self.parent.guiTabSettings.v_er_seg_length.set(self.er_segment_length)

		if self.coil_shape == self.parent.ELLIPSE and not self.shortaxis:  # todo add export multiple C's @ ellipse
			self.parent.guiTabResults.v_cap_res.set(self.cap[int(self.nr_of_legs - 1)])
		else:
			self.parent.guiTabResults.v_cap_res.set(self.cap[int(self.nr_of_legs / 4 - 1)])


if __name__ == "__main__":
	#todo elliptical:
	# fix the elliptical coil math, something is not right. A practically circular elliptical coil should give same values on all C's?
	# fix elliptical C/leg drawing in the capacitor graph
	# add multiple C results on results tab
	# add the text & b1 image on the results tab
	# when done re-add the Options menu item to be able to switch between circle ellipse

	#todo set focus on tabs when clicking them (switching tabs), instead of widgets in the tab
	#todo add config. Saving/loading the settings for a specific coil
	#todo break the tab gui classes into more methods for readability
	root = tk.Tk()
	root.withdraw()

	default_font = font.nametofont("TkDefaultFont")  # set default font
	default_font.configure(family='freemono', size=11)
	myfont_bold = default_font.copy()  # bold font
	myfont_bold.configure(weight="bold")

	myfont_small_bold = default_font.copy()  # small font
	myfont_small_bold.configure(weight="bold", size=9)
	
	myfont_small = default_font.copy()  # small font
	myfont_small.configure(size=8)

	mygui = MainApplication(root)
	root.deiconify()

	root.mainloop()
