"""
Description:    Library with the math required to calculate birdcage capacitors.
Author: 		Dimitri Welting
Website: 		http://github.com/dwelting/pyBirdcagebuilder
License: 		Copyright (c) 2020 Dimitri Welting. All rights reserved.
				Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
				This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

import math
from lib.logging import logger


class CalculateBirdcage:
	# All math is copied from the original Birdcage Builder made by PennState Health, and converted to Python

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
		self.parent.guiTabMoreInfo.v_ind_eff_er.set(self.ereff[int(self.nr_of_legs / 4 - 1)] * 1e9)
		self.parent.guiTabMoreInfo.v_ind_eff_legs.set(self.legeff[int(self.nr_of_legs / 4 - 1)] * 1e9)
		self.parent.guiTabSettings.v_er_seg_length.set(self.er_segment_length)

		if self.coil_shape == self.parent.ELLIPSE and not self.shortaxis:  # todo add export multiple C's @ ellipse
			self.parent.guiTabResults.v_cap_res.set(self.cap[int(self.nr_of_legs - 1)])
		else:
			self.parent.guiTabResults.v_cap_res.set(self.cap[int(self.nr_of_legs / 4 - 1)])

		result = f""" Results:
			Result Capacitor: {self.parent.guiTabResults.v_cap_res.get()} pF
			Result ER Segment Length: {self.parent.guiTabSettings.v_er_seg_length.get()} nH
			Result Self Inductance ER: {self.parent.guiTabMoreInfo.v_ind_self_er.get()} nH
			Result Self Inductance Legs: {self.parent.guiTabMoreInfo.v_ind_self_legs.get()} nH
			Result Effective Inductance ER: {self.parent.guiTabMoreInfo.v_ind_eff_er.get()} nH
			Result Effective Inductance Legs: {self.parent.guiTabMoreInfo.v_ind_eff_legs.get()} mm
		"""
		# logger.info(result.replace('\t', ''))
		logger.info(result)
