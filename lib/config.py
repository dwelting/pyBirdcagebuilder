"""
Description:    Library with a custom configuraton class.
Author: 	    Dimitri Welting
Website:    	http://github.com/dwelting/
License: 	    Copyright (c) 2020 Dimitri Welting. All rights reserved.
				Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
				This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""


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
