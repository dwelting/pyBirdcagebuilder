"""
Description:    Library with customized logging.
Author:     	Dimitri Welting
Website: 	    http://github.com/dwelting/
License: 	    Copyright (c) 2020 Dimitri Welting. All rights reserved.
				Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
				This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

import logging
import logging.config
import os

LOG_CONFIG = os.path.join(os.getcwd(), "conf", "logging.conf")


class MyFormatter(logging.Formatter):
	default_date_fmt = '%Y-%d-%m %H:%M:%S'
	default_fmt = '[%(asctime)s] [%(levelname)-8s] - %(message)s (%(filename)s:%(lineno)s)'
	debug_fmt = '[%(asctime)s] [%(levelname)-8s] - %(message)s (%(filename)s:%(lineno)s, %(funcName)s())'
	info_fmt = '[%(asctime)s] [%(levelname)-8s] - %(message)s'

	def __init__(self, **kwargs):
		if 'fmt' in kwargs.keys():
			self.default_fmt = kwargs['fmt']
			kwargs.pop('fmt')
		if 'format' in kwargs.keys():
			self.default_fmt = kwargs['format']
			kwargs.pop('format')

		if 'datefmt' in kwargs.keys():
			self.default_date_fmt = kwargs['datefmt']
			kwargs.pop('datefmt')

		super().__init__(fmt=self.default_fmt, datefmt=self.default_date_fmt, style='%', **kwargs)

	def format(self, record):
		# Replace the original format with one customized by logging level
		if record.levelno == logging.INFO:
			self._style._fmt = self.info_fmt
		elif record.levelno == logging.DEBUG:
			self._style._fmt = self.debug_fmt
		else:
			self._style._fmt = self.default_fmt

		result = super(MyFormatter, self).format(record)
		return result


class LoggerConfig:
	import json
	import importlib

	def __init__(self, file):
		with open(file, "r") as file:
			self.config_dict = self.json.load(file)
		self._replaceSpecialImport(self.config_dict)

	def _replaceSpecialImport(self, dict_):
		# config file only accepts strings, so convert string to class
		for k in dict_.keys():
			if isinstance(dict_[k], dict):
				nd = dict_[k]
				self._replaceSpecialImport(nd)
			else:
				if k == '()':
					f = dict_[k].rsplit('.', 1)
					mod = self.importlib.import_module(f"{f[0]}")
					att = getattr(mod, f[-1])
					dict_[k] = att



config = LoggerConfig(LOG_CONFIG)
logging.config.dictConfig(config.config_dict)
logger = logging.getLogger('root')

logger.info('---Log Start---')

