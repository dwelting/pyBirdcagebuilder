"""
Description:    Library with custom TKinter widgets or useful functions.
Author: 	    Dimitri Welting
Website:    	http://github.com/dwelting/
License: 	    Copyright (c) 2020 Dimitri Welting. All rights reserved.
				Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
				This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

import tkinter as tk
from lib.logging import logger
import os


class MyEntry(tk.Entry):
	def __init__(self, *args, def_value=None, validate_on_focus_loss=False, read_only=False, decimals=None, **kwargs):
		self.def_value = def_value
		self.rounding = decimals
		self.no_update = False
		
		kwargs.setdefault("width", 7)
		kwargs.setdefault("justify", tk.LEFT)
		kwargs.setdefault("bg", "white")
		
		self.var = tk.StringVar()
		self.var_external = None
		if 'text' in kwargs.keys():
			self.var_external = kwargs["text"]
			self.var_external.trace("w", lambda *a: self._setVarFromVarExt())
			kwargs.pop("text")

		super(MyEntry, self).__init__(*args, text=self.var, **kwargs)
		
		if validate_on_focus_loss:
			self.bind("<FocusOut>", self._validate)
		else:
			self.var.trace("w", self._validate)
			self.var.trace("w", lambda *a: self._setVarExtFromVar())
			
		if self.var_external is not None:
			self.bind("<FocusOut>", lambda *a: self._setVarExtFromVar(force=True))
			
		if def_value is not None:
			self.setValue(def_value)
			
		self.var_oldvalue = ""
		
		if read_only:
			self.config(state='readonly', readonlybackground=self.cget('background'))
			
	def _setVarFromVarExt(self):
		if self.no_update:
			return
		
		val = self.var_external.get()
		try:
			if val - int(val) > 0:
				if self.rounding is not None:
					self.var.set(round(val, self.rounding))
				else:
					self.var.set(str(val))
			else:
				self.var.set(int(val))
		except ValueError:
			self.var.set(val)
	
	def _setVarExtFromVar(self, force=False):
		if str(self.var_external.get()) == str(self.var.get()):
			return
		
		self.no_update = True
		
		try:
			ret = self.var_external.get()
			self.var_external.set(type(ret)(self.var.get()))
		except ValueError:
			if force:
				self.var_external.set(type(self.var_external)().get())  # set default value
				self.no_update = False
				self._setVarFromVarExt()
		
		self.no_update = False
		
	def _validate(self, *args, new_value=None):  # override when subclassing
		return True

	def setValue(self, num):  # override when subclassing
		if self._validate(new_value=num):
			self.var.set(str(num))
	
	def getValue(self):
		return self.var.get()

	def clear(self):
		self.var.set("")

	def restoreDefault(self):
		if self.def_value is not None:
			self.setValue(self.def_value)
		else:
			self.var.set("")


class NumInput(MyEntry):
	PASSED = 0
	MIN = -1
	MAX = 1
	
	def __init__(self, *args, min_value=None, max_value=None, **kwargs):
		self.min_value = min_value
		self.max_value = max_value

		super(NumInput, self).__init__(*args, **kwargs)
	
	def _checkMinMAxValue(self, num):
		accept = self.PASSED

		if self.min_value is not None:
			if float(num) < self.min_value:
				accept = self.MIN

		if self.max_value is not None:
			if float(num) > self.max_value:
				accept = self.MAX
		
		if accept is not self.PASSED:
			logger.warning(f"Set value ({num}) not within accepted range")
		
		return accept

	def _validate(self, *args, new_value=None):
		accept_new_value = False
		index_back = False
		
		if new_value is None:
			new_value = self.var.get()  # get the typed-in text/number
			
		try:
			float(new_value)
			is_float = True
		except ValueError:
			is_float = False
		
		if new_value == "":  # if empty just set the value
			accept_new_value = True
		
		elif new_value == "-":  # if negative number symbol, check if negative is allowed
			if self.min_value is None or self.min_value < 0:
				accept_new_value = True
		
		elif str(new_value)[0] == " " or str(new_value)[-1] == " ":  # remove spaces from beginning/end
			index_back = True

		elif is_float:
			minmax = self._checkMinMAxValue(new_value)
			if minmax == self.PASSED:
				accept_new_value = True
			else:
				if minmax == self.MIN:
					new_value = self.min_value
				else:
					new_value = self.max_value
				accept_new_value = True

		if accept_new_value:
			self.var.set(str(new_value))
			self.var_oldvalue = new_value
		else:
			logger.debug(f"Set value ({new_value}) not in an accepted format")
			self.var.set(str(self.var_oldvalue))
			if index_back:
				self.icursor(self.index(tk.INSERT)-1)
				
		return accept_new_value

	def setValue(self, num, rounding=None):
		if self._validate(new_value=num):
			if rounding is None:
				self.var.set(str(num))
			else:
				self.var.set(str(round(float(num), rounding)))


class MyScale(tk.Scale):
	def __init__(self, *args, variable=None, **kwargs):
		super(MyScale, self).__init__(*args, **kwargs)
		if variable is not None:
			variable.trace("w", lambda *a: self.set(variable.get()))  # changes the slider depending on programmatically changed var

		if os.name == 'posix':
			button = '<Button-2>'
		else:
			button = '<Button-3>'
		self.bind('<Button-1>', lambda e: self.event_generate(button, x=e.x, y=e.y))  # makes left-click behave like right-click, making the scale jump instantly to destination


def getScreenDimensions():
	r = tk.Tk()
	r.update_idletasks()
	r.attributes('-fullscreen', True)
	r.state('iconic')
	geometry = r.winfo_geometry()
	r.destroy()

	geometry = geometry.split('x')
	width = geometry[0]
	height = geometry[1].split('+')[0]
	return int(width), int(height)


def centerWindow(win, win_x, win_y):
	import os
	if os.name == 'posix':
		w, h = getScreenDimensions() 	# only way in Linux to get a centered window on the primary screen with dual monitor
	else:
		w = win.winfo_screenwidth()
		h = win.winfo_screenheight()
	x = (w // 2) - (win_x // 2)
	y = (h // 2) - (win_y // 2)
	win.geometry('+%d+%d' % (x, y))
