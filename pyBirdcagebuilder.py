#!/usr/bin/env python3

"""
Description:    pyBirdcagebuilder is a program that calculates ideal capacitor values for birdcage coil designs.
                This program is based on the original Birdcage Builder program provided by PennState Health.
                (https://research.med.psu.edu/departments/center-for-nmr-research/software/birdcage-builder-web-app/)
Author:         Dimitri Welting
Website:        http://github.com/dwelting/pyBirdcagebuilder
License:        Copyright (c) 2023 Dimitri Welting. All rights reserved.
                Distributed under the MIT license. The full text of the license can be found in the LICENSE file or on the above-mentioned website.
                This code is free to download and use. Any paid service providing this code is not endorsed by the author.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import os

import lib.my_tk as my_tk
import lib.fonts as ft
import src.constants as const
import src.data as data
import src.calculate as calc
import src.gui as gui
from lib.logging import logger
from lib.config import MyConfig


class MainApplication:
    def __init__(self, window):
        self._setWindow(window)
        self.window = window

        self.Config = MyConfig(self)
        self.settings = data.Settings()
        self.results = data.Results()

        # menubar
        self.menuBar = gui.MyMenuBar(self, self.settings, self.results)
        window.config(menu=self.menuBar.menu)

        self.tab_control = ttk.Notebook(window)  # tabs

        self.calcEllipse = calc.CalculateEllipseBirdcage(self, self.settings, self.results)
        self.calcCircle = calc.CalculateCircleBirdcage(self, self.settings, self.results)
        self.guiTabSettings = gui.MySettingsTab(self, self.settings, self.results)
        self.guiTabResults = gui.MyResultsTab(self, self.settings, self.results)
        self.guiTabMoreInfo = gui.MyMoreInfoTab(self, self.settings, self.results)

        self.tab_control.add(self.guiTabSettings.tab, text=' Settings ')
        self.tab_control.add(self.guiTabResults.tab, text=' Results ')
        self.tab_control.add(self.guiTabMoreInfo.tab, text=' More Information ')
        self.tab_control.pack(expand=1, fill='both', padx=(5, 5), pady=(5, 5))

        self.menuBar.initialize()
        self.guiTabSettings.linkToResultstab()

        if os.name == 'posix':
            bg = ttk.Style().lookup('TFrame', 'background')
            self.guiTabSettings.tab.tk_setPalette(background=bg)  # only useful in linux. Hides color inconsistencies between widget bg and frame bg

        logger.info("Program start successfully")

    def _setWindow(self, window):
        window.title(f"{const.PROGRAM_NAME}")  # {VERSION}")

        my_tk.centerWindow(window, const.Window.X, const.Window.Y)
        window.maxsize(const.Window.X, const.Window.Y)
        window.minsize(const.Window.X, const.Window.Y)
        window.resizable(0, 0)

        try:
            if os.name == 'posix':  # windows doesn't like 32px icons
                icon = "icon32.png"
            else:
                icon = "icon16.png"
            window.iconphoto(True, tk.PhotoImage(file=const.ICON_FOLDER + icon))
        except tk.TclError:
            logger.warning("Icon error: no application icon found!")

    def _validateInputs(self):  # TODO move to main program class
        inputs_ = {"Coil shape": "Circle" if self.settings.setting_calc == const.Config.CIRCLE else "Ellipse",
                   "Resonance Frequency": self.settings.freq.get(),
                   "Coil Diameter": self.settings.coil_diameter.get(),
                   "Coil Short Diameter": self.settings.coil_diameter_short.get(),
                   "Coil Long Diameter": self.settings.coil_diameter_long.get(),
                   "Shield Diameter": self.settings.shield_diameter.get(),
                   "Nr Of Legs": self.settings.nr_of_legs.get(),
                   "Leg Length": self.settings.leg_length.get(),
                   "Leg Width": self.settings.leg_width.get(),
                   "Leg OD": self.settings.leg_od.get(),
                   "Leg ID": self.settings.leg_id.get(),
                   "ER Width": self.settings.er_width.get(),
                   "ER OD": self.settings.er_od.get(),
                   "ER ID": self.settings.er_id.get(),
                   "Bandpass Capacitor": self.settings.bp_cap.get()}

        for key, value in inputs_.items():
            if key == "Shield Diameter":  # shield size can be zero (no shield)
                continue
            if value == 0:
                mb.showwarning("Input zero", "One or more inputs are zero.\nPlease input valid values.")
                return False

        if inputs_["Shield Diameter"] == inputs_["Coil Diameter"]:
            mb.showwarning("Zero shield distance", "Shield distance is equal to coil diameter.\nPlease input valid values.")
            return False

        return inputs_

    def startCalculation(self):
        inputs_ = self._validateInputs()
        if not inputs_:
            return
        logger.info("\nCalculation started with values:\n\t" + "\n\t".join("{}: {}".format(k, v) for k, v in inputs_.items()))

        self.guiTabResults.guiAdjust()

        if self.settings.setting_calc == const.Config.CIRCLE:
            self.calcCircle.calculate()
        else:
            self.calcEllipse.calculate() #TODO return results class from function

        self._logResults(self.settings.setting_calc)

        self.guiTabResults.drawGraphs()
        self.tab_control.select(1)  # At end switch tab to results

    def _logResults(self, mode) -> None:
        nr_of_legs = self.settings.nr_of_legs.get()

        result = f"\nResults:"
        if mode == const.Config.CIRCLE:
            result += f"\n\tCapacitor: {self.results.cap[0].get():.2f} pF"
        else:
            for i in range(nr_of_legs // 4):
                result += f"\n\tCapacitor #{i+1}: {self.results.cap[i].get():.2f} pF"

        result += f"\n\tER Segment Length: {self.results.er_segment_length.get():.2f} cm"
        result += f"\n\tSelf Inductance ER: {self.results.er_self.get():.2f} nH"
        result += f"\n\tSelf Inductance Legs: {self.results.leg_self.get():.2f} nH"
        result += f"\n\tEffective Inductance ER: {self.results.er_eff[nr_of_legs // 4 - 1].get():.2f} nH"
        result += f"\n\tEffective Inductance Legs: {self.results.leg_eff[nr_of_legs // 4 - 1].get():.2f} nH"

        logger.info(result)


def main():
    root.withdraw()
    MainApplication(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    ft = ft.MyFonts()
    main()
