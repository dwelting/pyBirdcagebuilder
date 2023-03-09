"""
Description:    Source file with the math required to calculate birdcage capacitors.
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

from math import sqrt, cos, sin, log, atan, atanh, pi
import src.constants as const


class Calculation:
    # All math is copied from the original Birdcage Builder made by PennState Health, and converted to Python

    def __init__(self, parent, settings, results):
        self.parent = parent
        self.settings = settings
        self.results = results

    def _getValuesFromGui(self):
        # temporary variables with shorter names to minimize code a bit
        self.nr_of_legs = self.settings.nr_of_legs.get()
        self.leg_length = self.settings.leg_length.get()
        self.er_width = self.settings.er_width.get()
        self.leg_width = self.settings.leg_width.get()
        self.er_od = self.settings.er_od.get()
        self.er_id = self.settings.er_id.get()
        self.leg_od = self.settings.leg_od.get()
        self.leg_id = self.settings.leg_id.get()

        self.bp_cap = self.settings.bp_cap.get()

        self.leg_config = self.settings.setting_leg_type.get()
        self.er_config = self.settings.setting_er_type.get()
        self.coil_mode = self.settings.setting_coil_configuration.get()
        self.bp_config = self.settings.setting_bp_cap_location.get()

        self.short_axis = self.settings.setting_coil_axis.get()

        self.shield_radius = self.settings.shield_diameter.get() / 2
        self.coil_radius = self.settings.coil_diameter.get() / 2
        self.coil_shortradius = self.settings.coil_diameter_short.get() / 2

    def _initLocalValues(self, legs: int) -> None:
        # temporary variables with shorter names to minimize code a bit
        self.thetas = [0.0 for _ in range(legs)]
        self.radius = [0.0 for _ in range(legs)]
        self.x_coords = [0.0 for _ in range(legs)]
        self.y_coords = [0.0 for _ in range(legs)]
        self.leg_currs = [0.0 for _ in range(legs)]
        self.er_currs = [0.0 for _ in range(legs)]
        self.leg_eff = [0.0 for _ in range(legs)]
        self.er_eff = [0 for _ in range(legs)]
        self.cap = [0 for _ in range(legs)]
        self.leg_self_ind = 0
        self.er_self_ind = 0
        self.er_segment_length = 0

    def calculate(self):
        self._getValuesFromGui()
        self._initLocalValues(self.nr_of_legs)
        self._calcGeometry(self.nr_of_legs, self.coil_radius, self.coil_shortradius)
        self._calcCurrents(self.nr_of_legs, self.coil_radius, self.coil_shortradius)
        self.er_self_ind = self._calcSelfInductanceEr()
        self.leg_self_ind = self._calcSelfInductanceLeg()
        self._calcEffLeg()
        self._calcEffER(self.nr_of_legs)
        self._calcCapacitance(self.nr_of_legs)
        self._exportResults(self.nr_of_legs)

    def _calcGeometry(self, legs: int, a: float = None, b: float = None) -> None:
        ...

    def _calcCurrents(self, legs: int, a: float = None, b: float = None) -> None:
        ...

    def _calcSelfInductanceEr(self) -> float:
        ...

    def _calcSelfInductanceLeg(self) -> float:
        ...

    def _calcEffLeg(self):
        ...

    def _calcEffER(self, legs: int) -> None:
        ...

    def _calcCapacitance(self, legs: int) -> None:
        ...

    def _exportResults(self, legs: int) -> None:
        # export results to gui
        self.results.radius = self.radius.copy()
        self.results.thetas = self.thetas.copy()
        self.results.x_coords = self.x_coords.copy()
        self.results.y_coords = self.y_coords.copy()
        self.results.leg_currs = self.leg_currs.copy()
        self.results.er_currs = self.er_currs.copy()
        [self.results.cap[i].set(self.cap[i]) for i in range(legs)]
        [self.results.leg_eff[i].set(self.leg_eff[i] * 1e9) for i in range(legs)]  # calculated effective inductance of legs
        [self.results.er_eff[i].set(self.er_eff[i] * 1e9) for i in range(legs)]  # calculated effective inductance of end ring

        self.results.leg_self.set(self.leg_self_ind)  # calculated self inductance of legs
        self.results.er_self.set(self.er_self_ind)  # calculated self inductance of end ring
        self.results.er_segment_length.set(self.er_segment_length)


class CalculateEllipseBirdcage(Calculation):
    # Most math is copied from the original Birdcage Builder made by PennState Health and converted to Python

    def __init__(self, parent, settings, results):
        super().__init__(parent, settings, results)

    def _getValuesFromGui(self):
        super()._getValuesFromGui()
        self.coil_radius = self.settings.coil_diameter_long.get() / 2

    def _calcGeometry(self, legs: int, a: float, b: float) -> None:
        """calculate perimeter of the ellipse"""
        h = (a - b) ** 2 / (a + b) ** 2
        p = pi * (a + b) * (1 + ((3 * h) / (10 + sqrt(4 - 3 * h))))
        self.er_segment_length = p / legs

        """Calculate leg-number of equidistant points on an ellipse"""
        x0 = a
        angle = y0 = x = y = 0
        for i in range(0, legs//4):  # approximate angles and coords
            dist = 0
            while dist < ((self.er_segment_length / 2) if i == 0 else self.er_segment_length):
                angle += 0.0001
                x = a * cos(angle)
                y = b * sin(angle)
                dist += sqrt((x - x0) ** 2 + (y - y0) ** 2)
                x0 = x
                y0 = y
            self.thetas[i] = atan(y / x)
            self.x_coords[i] = x
            self.y_coords[i] = y
            self.radius[i] = sqrt(x ** 2 + y ** 2)

        for i in range(0, int(self.nr_of_legs / 4)):
            self.x_coords[int(self.nr_of_legs / 2 - (i + 1))] = -self.x_coords[i]
            self.x_coords[int(self.nr_of_legs / 2 + i)] = -self.x_coords[i]
            self.x_coords[int(self.nr_of_legs - (i + 1))] = self.x_coords[i]
            self.y_coords[int(self.nr_of_legs / 2 - (i + 1))] = self.y_coords[i]
            self.y_coords[int(self.nr_of_legs / 2 + i)] = -self.y_coords[i]
            self.y_coords[int(self.nr_of_legs - (i + 1))] = -self.y_coords[i]
            self.radius[int(self.nr_of_legs / 2 - (i + 1))] = self.radius[i]
            self.radius[int(self.nr_of_legs / 2 + i)] = self.radius[i]
            self.radius[int(self.nr_of_legs - (i + 1))] = self.radius[i]
            self.thetas[int(self.nr_of_legs / 2 - (i + 1))] = pi - self.thetas[i]
            self.thetas[int(self.nr_of_legs / 2 + i)] = pi + self.thetas[i]
            self.thetas[int(self.nr_of_legs - (i + 1))] = 2 * pi - self.thetas[i]

    def _calcCurrents(self, legs: int, a: float, b: float) -> None:
        """Calc leg/er currents"""
        for i in range(0, legs):
            if self.short_axis:
                self.leg_currs[i] = (b ** 2 * cos(self.thetas[i])) \
                                    / ( (b ** 2 * cos(self.thetas[i]) ** 2) + (a ** 2 * sin(self.thetas[i]) ** 2) )
            else:
                self.leg_currs[i] = (a**2 * sin(self.thetas[i])) \
                                    / ( (b ** 2 * cos(self.thetas[i]) ** 2) + (a ** 2 * sin(self.thetas[i]) ** 2) )

        if not self.short_axis:
            self.er_currs[legs // 4 - 1] = 0
            self.er_currs[3 * legs // 4 - 1] = 0
            self.er_currs[legs // 4 - 1 - 1] = -self.leg_currs[legs // 4 - 1]

            for i in range(1, legs // 4 - 1):
                self.er_currs[legs // 4 - 1 - (i + 1)] = self.er_currs[legs // 4 - 1 - i] - self.leg_currs[legs // 4 - 1 - i]
            self.er_currs[legs - 1] = self.er_currs[0] - self.leg_currs[0]
            self.er_currs[legs // 2 - 1] = -self.er_currs[legs - 1]

            for i in range(0, legs // 4 - 1):
                self.er_currs[legs // 4 + i] = -self.er_currs[legs // 4 - (i + 1) - 1]
                self.er_currs[3 * legs // 4 - (i + 1) - 1] = -self.er_currs[legs // 4 - (i + 1) - 1]
                self.er_currs[3 * legs // 4 + i] = self.er_currs[legs // 4 - (i + 1) - 1]

        else:
            n = 0
            for i in range(0, legs):
                n += self.leg_currs[i]
                self.er_currs[i] = n

            self.er_currs[legs // 2 - 1] = 0
            self.er_currs[legs - 1] = 0

    def _calcSelfInductanceEr(self) -> float:
        er: float
        if self.er_config == const.Shape.RECT:
            er = 2 * self.er_segment_length * (log(2 * self.er_segment_length / self.er_width) + 0.5)
        else:
            n = self.er_id / self.er_od
            if n == 0:
                er = 2 * self.er_segment_length * (log(4 * self.er_segment_length / self.er_od) - 0.75)
            else:
                er = 2 * self.er_segment_length * (log(4 * self.er_segment_length / self.er_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)
        return er

    def _calcSelfInductanceLeg(self) -> float:
        leg: float
        if self.leg_config == const.Shape.RECT:
            leg = 2 * self.leg_length * (log(2 * self.leg_length / self.leg_width) + 0.5)
        else:
            n = self.leg_id / self.leg_od
            if n == 0:
                leg = 2 * self.leg_length * (log(4 * self.leg_length / self.leg_od) - 0.75)
            else:
                leg = 2 * self.leg_length * (log(4 * self.leg_length / self.leg_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)
        return leg

    def _calcEffLeg(self):
        # Calc effective inductance of legs
        for i in range(0, self.nr_of_legs):
            n = 0
            for j in range(0, self.nr_of_legs):
                if i == j:
                    n += self.leg_self_ind
                else:
                    sqrt_ = sqrt((self.x_coords[j] - self.x_coords[i]) ** 2 + (self.y_coords[j] - self.y_coords[i]) ** 2)
                    n += 2 * self.leg_length * (log(self.leg_length / sqrt_ + sqrt(1 + (self.leg_length / sqrt_) ** 2)) - sqrt(1 + (sqrt_ / self.leg_length) ** 2)
                                                + sqrt_ / self.leg_length) * self.leg_currs[j] / self.leg_currs[i]
            self.leg_eff[i] = n * 1e-9

        if self.shield_radius != 0:
            array = [0.0 for _ in range(self.nr_of_legs)]
            array2 = [0.0 for _ in range(self.nr_of_legs)]
            for i in range(0, self.nr_of_legs):
                n = self.shield_radius * self.shield_radius / self.radius[i]
                array[i] = n * cos(self.thetas[i])
                array2[i] = n * sin(self.thetas[i])

            for i in range(0, self.nr_of_legs):
                n = 0
                for j in range(0, self.nr_of_legs):
                    sqrt2 = sqrt((array[j] - self.x_coords[i]) ** 2 + (array2[j] - self.y_coords[i]) ** 2)
                    n += 2 * self.leg_length * (log(self.leg_length / sqrt2 + sqrt(1 + (self.leg_length / sqrt2) ** 2)) - sqrt(1 + (sqrt2 / self.leg_length) ** 2)
                                                + sqrt2 / self.leg_length) * -1 * self.leg_currs[j] / self.leg_currs[i]
                self.leg_eff[i] += n * 1e-9

    def _calcEffER(self, legs: int) -> None:
        # Calc effective inductance of endring
        for i in range(0, legs):
            self.er_eff[i] += self.er_self_ind

        for i in range(0, legs):
            n = self.x_coords[(i + legs // 2) % legs]
            n2 = self.y_coords[(i + legs // 2) % legs]
            n3 = self.x_coords[(i + legs // 2 + 1) % legs]
            n4 = self.y_coords[(i + legs // 2 + 1) % legs]
            n5 = self.x_coords[(i + 1) % legs]
            n6 = self.y_coords[(i + 1) % legs]
            n7 = self.x_coords[i]
            n8 = self.y_coords[i]
            sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt_ = sqrt((n7 - n5) ** 2 + (n8 - n6) ** 2)
            sqrt2 = sqrt((n - n5) ** 2 + (n2 - n6) ** 2)
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                self.er_eff[i] += 2 * sqrt_ * (log(sqrt_ / sqrt2 + sqrt(1 + (sqrt_ / sqrt2) ** 2)) - sqrt(1 + (sqrt2 / sqrt_) ** 2) + sqrt2 / sqrt_)

        for i in range(0, legs):
            n = self.x_coords[i]
            n2 = self.y_coords[i]
            n3 = self.x_coords[(i + 1) % legs]
            n4 = self.y_coords[(i + 1) % legs]
            n5 = self.x_coords[(i + 2) % legs]
            n6 = self.y_coords[(i + 2) % legs]
            sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt2 = sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
            sqrt3 = sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
            abs_ = abs(2 * ((sqrt3 ** 2 + sqrt_ ** 2 - sqrt2 ** 2) / (2 * sqrt3 * sqrt_)) * (sqrt3 * atanh(sqrt_ / (sqrt3 + sqrt2)) + sqrt_ * atanh(sqrt3 / (sqrt_ + sqrt2))))

            n = self.x_coords[(i - 1 + legs) % legs]
            n2 = self.y_coords[(i - 1 + legs) % legs]
            n3 = self.x_coords[i]
            n4 = self.y_coords[i]
            n5 = self.x_coords[(i + 1) % legs]
            n6 = self.y_coords[(i + 1) % legs]
            sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt2 = sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
            sqrt3 = sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
            abs2 = abs(2 * ((sqrt2 ** 2 + sqrt_ ** 2 - sqrt3 ** 2) / (2 * sqrt2 * sqrt_)) * (sqrt2 * atanh(sqrt_ / (sqrt2 + sqrt3)) + sqrt_ * atanh(sqrt2 / (sqrt_ + sqrt3))))
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                self.er_eff[i] += (abs_ * self.er_currs[(i + 1) % legs] + abs2 * self.er_currs[(i - 1 + legs) % legs]) / self.er_currs[i]

        array_ = [0 for _ in range(legs - 3)]
        array2 = [0 for _ in range(legs - 3)]
        for i in range(0, legs):
            n = self.x_coords[i]
            n2 = self.y_coords[i]
            n3 = self.x_coords[(i + 1) % legs]
            n4 = self.y_coords[(i + 1) % legs]
            n5 = n3 - n
            n6 = n4 - n2
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                for j in range(i + 2, i + legs - 1):
                    n7 = self.x_coords[j % legs]
                    n8 = self.y_coords[j % legs]
                    n9 = self.x_coords[(j + 1) % legs]
                    n10 = self.y_coords[(j + 1) % legs]
                    n11 = n9 - n7
                    n12 = n10 - n8

                    if self.er_currs[i] == 0:
                        array2[j - i - 2] = 0
                    elif n5 * n11 + n6 * n12 > 0:
                        array2[j - i - 2] = 1
                    else:
                        array2[j - i - 2] = -1

                    sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
                    sqrt2 = sqrt((n9 - n7) ** 2 + (n10 - n8) ** 2)
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

                    sqrt3 = sqrt(a3)
                    sqrt4 = sqrt(a2)
                    sqrt5 = sqrt(a4)
                    sqrt6 = sqrt(a5)

                    array_[j - i - 2] = n14 * ((n17 + sqrt2) * atanh(sqrt_ / (sqrt6 + sqrt5)) + (n18 + sqrt_) * atanh(sqrt2 / (sqrt6 + sqrt3)) - n17
                                               * atanh(sqrt_ / (sqrt4 + sqrt3)) - n18 * atanh(sqrt2 / (sqrt5 + sqrt4)))

                n19 = 0
                for j in range(0, legs - 3):
                    if j != (legs - 4) / 2:
                        n19 += array_[j] * abs(self.er_currs[(j + i + 2) % legs] / self.er_currs[i]) * array2[j]
                self.er_eff[i] += n19

        for i in range(0, legs):
            self.er_eff[i] *= 1e-9

    def _calcCapacitance(self, legs: int) -> None:
        v = [0.0 for _ in range(legs)]
        omega = 2 * pi * self.settings.freq.get() * 1e6
        for i in range(0, legs):
            v[i] = 0.5 * omega * self.leg_eff[i] * self.leg_currs[i]

        if self.short_axis:
            self.cap[legs // 4 - 1] = self.er_currs[legs // 4 - 1] / (omega * omega * self.er_currs[legs // 4 - 1] * self.er_eff[legs // 4 - 1] + omega * 2.0 * v[legs // 4 - 1]) * 1e12
        else:
            self.cap[legs - 1] = -self.er_currs[legs - 1] / (-omega * omega * self.er_currs[legs - 1] * self.er_eff[legs - 1] + omega * (v[0] - v[legs - 1])) * 1e12

        for j in range(0, legs // 4 - 1):
            self.cap[j] = self.er_currs[j] / (omega * omega * self.er_currs[j] * self.er_eff[j] + omega * (v[j] - v[j + 1])) * 1e12


class CalculateCircleBirdcage(Calculation):
    # All math is copied from the original Birdcage Builder made by PennState Health, and converted to Python

    def __init__(self, parent, settings, results):
        super().__init__(parent, settings, results)

    def _calcGeometry(self, legs: int, a: float = None, b: float = None) -> None:
        self.er_segment_length = (2 * pi * a) / legs

        """Calc helper variables"""
        for i in range(0, legs):
            self.thetas[i] = pi / legs * (2 * i + 1)
            self.x_coords[i] = a * cos(self.thetas[i])
            self.y_coords[i] = a * sin(self.thetas[i])

    def _calcCurrents(self, legs: int, a: float = None, b: float = None) -> None:
        """Calc leg/er currents"""
        for i in range(0, legs):
            self.leg_currs[i] = (a**2 * cos(self.thetas[i])) \
                               / (a**2 * cos(self.thetas[i])**2 + a**2 * sin(self.thetas[i])**2)

        n = 0
        for i in range(0, legs):
            n += self.leg_currs[i]
            self.er_currs[i] = n

        self.er_currs[legs // 2 - 1] = 0
        self.er_currs[legs - 1] = 0

    def _calcSelfInductanceEr(self) -> float:
        er: float
        if self.er_config == const.Shape.RECT:
            er = 2 * self.er_segment_length * (log(2 * self.er_segment_length / self.er_width) + 0.5)
        else:
            n = round(self.er_id / self.er_od)
            if n == 0:
                er = 2 * self.er_segment_length * (log(4 * self.er_segment_length / self.er_od) - 0.75)
            else:
                er = 2 * self.er_segment_length * (log(4 * self.er_segment_length / self.er_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)
        return er

    def _calcSelfInductanceLeg(self) -> float:
        leg: float
        # leg
        if self.leg_config == const.Shape.RECT:
            leg = 2 * self.leg_length * (log(2 * self.leg_length / self.leg_width) + 0.5)
        else:
            n = self.leg_id / self.leg_od
            if round(n == 0):
                leg = 2 * self.leg_length * (log(4 * self.leg_length / self.leg_od) - 0.75)
            else:
                leg = 2 * self.leg_length * (log(4 * self.leg_length / self.leg_od) + (0.1493 * n ** 3 - 0.3606 * n ** 2 - 0.0405 * n + 0.2526) - 1)
        return leg

    def _calcEffLeg(self):
        # Calc effective inductance of legs
        for i in range(0, self.nr_of_legs):
            n = 0
            for j in range(0, self.nr_of_legs):
                if i == j:
                    n += self.leg_self_ind
                else:
                    sqrt_ = sqrt((self.x_coords[j] - self.x_coords[i]) ** 2 + (self.y_coords[j] - self.y_coords[i]) ** 2)
                    n += 2 * self.leg_length * (log(self.leg_length / sqrt_ + sqrt(1 + (self.leg_length / sqrt_) ** 2)) - sqrt(1 + (sqrt_ / self.leg_length) ** 2)
                                                + sqrt_ / self.leg_length) * self.leg_currs[j] / self.leg_currs[i]
            self.leg_eff[i] = n * 1e-9

        if self.shield_radius != 0:
            array = [0.0 for _ in range(self.nr_of_legs)]
            array2 = [0.0 for _ in range(self.nr_of_legs)]
            for i in range(0, self.nr_of_legs):
                n = self.shield_radius**2 / self.coil_radius
                array[i] = n * cos(self.thetas[i])
                array2[i] = n * sin(self.thetas[i])

            for i in range(0, self.nr_of_legs):
                n = 0
                for j in range(0, self.nr_of_legs):
                    sqrt2 = sqrt((array[j] - self.x_coords[i]) ** 2 + (array2[j] - self.y_coords[i]) ** 2)
                    n += 2 * self.leg_length * (log(self.leg_length / sqrt2 + sqrt(1 + (self.leg_length / sqrt2) ** 2)) - sqrt(1 + (sqrt2 / self.leg_length) ** 2)
                                                + sqrt2 / self.leg_length) * -1 * self.leg_currs[j] / self.leg_currs[i]
                self.leg_eff[i] += n * 1e-9

    def _calcEffER(self, legs: int) -> None:
        # Calc effective inductance of end-ring
        for i in range(0, legs):
            self.er_eff[i] += self.er_self_ind

        for i in range(0, legs):
            n = self.x_coords[(i + legs // 2) % legs]
            n2 = self.y_coords[(i + legs // 2) % legs]
            n3 = self.x_coords[(i + legs // 2 + 1) % legs]
            n4 = self.y_coords[(i + legs // 2 + 1) % legs]
            n5 = self.x_coords[(i + 1) % legs]
            n6 = self.y_coords[(i + 1) % legs]
            n7 = self.x_coords[i]
            n8 = self.y_coords[i]
            sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt_ = sqrt((n7 - n5) ** 2 + (n8 - n6) ** 2)
            sqrt2 = sqrt((n - n5) ** 2 + (n2 - n6) ** 2)
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                self.er_eff[i] += 2 * sqrt_ * (log(sqrt_ / sqrt2 + sqrt(1 + (sqrt_ / sqrt2) ** 2)) - sqrt(1 + (sqrt2 / sqrt_) ** 2) + sqrt2 / sqrt_)

        for i in range(0, legs):
            n = self.x_coords[i]
            n2 = self.y_coords[i]
            n3 = self.x_coords[(i + 1) % legs]
            n4 = self.y_coords[(i + 1) % legs]
            n5 = self.x_coords[(i + 2) % legs]
            n6 = self.y_coords[(i + 2) % legs]
            sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt2 = sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
            sqrt3 = sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
            abs_ = abs(2 * ((sqrt3 ** 2 + sqrt_ ** 2 - sqrt2 ** 2) / (2 * sqrt3 * sqrt_)) * (sqrt3 * atanh(sqrt_ / (sqrt3 + sqrt2)) + sqrt_ * atanh(sqrt3 / (sqrt_ + sqrt2))))

            n = self.x_coords[(i - 1 + legs) % legs]
            n2 = self.y_coords[(i - 1 + legs) % legs]
            n3 = self.x_coords[i]
            n4 = self.y_coords[i]
            n5 = self.x_coords[(i + 1) % legs]
            n6 = self.y_coords[(i + 1) % legs]
            sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
            sqrt2 = sqrt((n3 - n5) ** 2 + (n4 - n6) ** 2)
            sqrt3 = sqrt((n5 - n) ** 2 + (n6 - n2) ** 2)
            abs2 = abs(2 * ((sqrt2 ** 2 + sqrt_ ** 2 - sqrt3 ** 2) / (2 * sqrt2 * sqrt_)) * (sqrt2 * atanh(sqrt_ / (sqrt2 + sqrt3)) + sqrt_ * atanh(sqrt2 / (sqrt_ + sqrt3))))
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                self.er_eff[i] += (abs_ * self.er_currs[(i + 1) % legs] + abs2 * self.er_currs[(i - 1 + legs) % legs]) / self.er_currs[i]

        array_ = [0 for _ in range(legs - 3)]
        array2 = [0 for _ in range(legs - 3)]
        for i in range(0, legs):
            n = self.x_coords[i]
            n2 = self.y_coords[i]
            n3 = self.x_coords[(i + 1) % legs]
            n4 = self.y_coords[(i + 1) % legs]
            n5 = n3 - n
            n6 = n4 - n2
            if self.er_currs[i] == 0:
                self.er_eff[i] += 0
            else:
                for j in range(i + 2, i + legs - 1):
                    n7 = self.x_coords[j % legs]
                    n8 = self.y_coords[j % legs]
                    n9 = self.x_coords[(j + 1) % legs]
                    n10 = self.y_coords[(j + 1) % legs]
                    n11 = n9 - n7
                    n12 = n10 - n8

                    if self.er_currs[i] == 0:
                        array2[j - i - 2] = 0
                    elif n5 * n11 + n6 * n12 > 0:
                        array2[j - i - 2] = 1
                    else:
                        array2[j - i - 2] = -1

                    sqrt_ = sqrt((n3 - n) ** 2 + (n4 - n2) ** 2)
                    sqrt2 = sqrt((n9 - n7) ** 2 + (n10 - n8) ** 2)
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

                    sqrt3 = sqrt(a3)
                    sqrt4 = sqrt(a2)
                    sqrt5 = sqrt(a4)
                    sqrt6 = sqrt(a5)

                    array_[j - i - 2] = n14 * ((n17 + sqrt2) * atanh(sqrt_ / (sqrt6 + sqrt5)) + (n18 + sqrt_) * atanh(sqrt2 / (sqrt6 + sqrt3)) - n17
                                               * atanh(sqrt_ / (sqrt4 + sqrt3)) - n18 * atanh(sqrt2 / (sqrt5 + sqrt4)))

                n19 = 0
                for j in range(0, legs - 3):
                    if j != (legs - 4) / 2:
                         n19 += array_[j] * abs(self.er_currs[(j + i + 2) % legs] / self.er_currs[i])
                self.er_eff[i] += n19

        for i in range(0, legs):
            self.er_eff[i] *= 1e-9

    def _calcCapacitance(self, legs: int) -> None:
        array = [0.0 for _ in range(legs)]
        n = 2 * pi * self.settings.freq.get() * 1e6
        for i in range(0, legs):
            array[i] = 0.5 * n * self.leg_eff[i] * self.leg_currs[i]

        if self.coil_mode == const.Mode.HIGHPASS or (self.coil_mode == const.Mode.BANDPASS and self.bp_config == const.Part.LEG):
            n2 = 0
            if self.coil_mode == const.Mode.BANDPASS:
                n2 = -0.5 * (self.leg_currs[legs // 4 - 1] / (n * self.bp_cap)) * 1e12

            self.cap[0] = self.er_currs[legs // 4 - 1] / (
                    n ** 2 * self.er_currs[legs // 4 - 1] * (self.er_eff[legs // 4 - 1]) + n * 2 * (array[legs // 4 - 1] + n2)) * 1e12
        else:
            if self.coil_mode == const.Mode.BANDPASS:
                n3 = -self.er_currs[legs // 4 - 1] * (n ** 2 * self.er_eff[legs // 4 - 1] - 1 / self.bp_cap * 1e12)
                n4 = self.leg_currs[legs // 4 ] * n ** 2 * self.leg_eff[legs // 4 ]
            else:
                n3 = -self.er_currs[legs // 4 - 1] * n ** 2 * self.er_eff[legs // 4 - 1]
                n4 = self.leg_currs[legs // 4 ] * n ** 2 * self.leg_eff[legs // 4 ]

            self.cap[0] = self.leg_currs[legs // 4 ] / (n4 + n3) * 1e12
