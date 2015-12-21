# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui
import pyqtgraph as pg
import numpy
from fibermodes import Mode, ModeFamily, HE11
from itertools import count
from math import isnan


class CharEqDialog(QtGui.QDialog):

    """Plot characteristic function

    TODO: follow the mouse
    TODO: clear cache button
    TODO: bug with graph scale (sometime change by itself)
    TODO: better scale to important region
    TODO: maximizable window
    TODO: allow to choose log scale

    """

    def __init__(self, mode=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.fnum = parent.fiberSlider.slider.value()
        wlnum = parent.wavelengthSlider.wavelengthInput.value()
        self.wl = parent.doc.wavelengths[wlnum-1]

        self.mode = mode if mode else HE11
        self.fiber = parent.doc.fibers[self.fnum-1]
        self.neffMin = self.fiber.minIndex(-1, self.wl)
        self.neffMax = max(layer.maxIndex(self.wl)
                           for layer in self.fiber.layers)

        self.label = QtGui.QLabel()
        self.plot = pg.PlotWidget()

        self.fType = QtGui.QComboBox()
        self.fType.addItems(["Chareq", "Cutoff"])
        self.fType.setCurrentIndex(0)
        self.fType.currentIndexChanged.connect(self.updateMode)

        self.modeInput = QtGui.QComboBox()
        self.modeInput.addItems(list(m.name for m in ModeFamily))
        self.modeInput.setCurrentIndex(
            self.modeInput.findText(self.mode.family.name))
        self.modeInput.currentIndexChanged.connect(self.updateMode)

        self.nuInput = QtGui.QSpinBox()
        self.nuInput.setValue(self.mode.nu)
        self.nuInput.valueChanged.connect(self.updateMode)

        self.mInput = QtGui.QSpinBox()
        self.mInput.setRange(1, 100)
        self.mInput.setValue(self.mode.m)
        self.mInput.valueChanged.connect(self.updateMode)

        npLabel = QtGui.QLabel(self.tr("# points"))
        self.npInput = QtGui.QSpinBox()
        self.npInput.setRange(50, 10000)
        self.npInput.setValue(50)
        self.npInput.setSingleStep(50)
        self.npInput.valueChanged.connect(self.updateMode)
        npLabel.setBuddy(self.npInput)

        self.zeros = QtGui.QCheckBox(self.tr("Show zeros"))
        self.zeros.toggled.connect(self.showZeros)

        self.points = QtGui.QCheckBox(self.tr("Show points"))
        self.points.toggled.connect(self.showZeros)

        dLabel = QtGui.QLabel(self.tr("∆"))
        deltaValidator = QtGui.QDoubleValidator(bottom=1e-31, top=1)
        self.delta = QtGui.QLineEdit()
        self.delta.setValidator(deltaValidator)
        self.delta.setText("{:e}".format(parent.doc.simulator.delta))
        self.delta.textChanged.connect(self.setDelta)
        dLabel.setBuddy(self.delta)

        hlayout = QtGui.QHBoxLayout()
        if hasattr(self.fiber._cutoff, '_lpcoeq'):
            hlayout.addWidget(self.fType)
        hlayout.addWidget(self.modeInput)
        hlayout.addWidget(self.nuInput)
        hlayout.addWidget(self.mInput)
        hlayout.addSpacing(1)
        hlayout.addWidget(npLabel)
        hlayout.addWidget(self.npInput)
        hlayout.addWidget(self.zeros)
        hlayout.addWidget(self.points)
        hlayout.addWidget(dLabel)
        hlayout.addWidget(self.delta)
        hlayout.addStretch(1)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(hlayout)
        layout.addWidget(self.plot)

        self.setLayout(layout)
        self.__zeros = None
        self.__points = None
        self.updateMode()

    def setTitle(self):
        title = "Fiber: {}  Wavelength: {} nm  Mode: {}".format(
            self.fnum, self.wl * 1e9, self.mode)
        if self.fType.currentIndex() == 0:
            self.setWindowTitle("Characteristic function: " + title)
        else:
            self.setWindowTitle("Cutoff function: " + title)
        self.label.setText(title)

    def updateMode(self):
        fam = self.modeInput.currentText()
        if fam in ("TE", "TM"):
            self.nuInput.setRange(0, 0)
        elif fam == "LP":
            self.nuInput.setRange(0, 99)
        else:
            self.nuInput.setRange(1, 99)

        self.mode = Mode(self.modeInput.currentText(),
                         self.nuInput.value(),
                         self.mInput.value())

        self.setTitle()
        if self.fType.currentIndex() == 0:
            self.plotCharEq()
        else:
            self.plotCutoff()

    def plotCharEq(self):
        Neff = numpy.linspace(self.neffMin, self.neffMax, self.npInput.value())
        y = numpy.empty(Neff.shape)

        Fct = {ModeFamily.LP: self.fiber._neff._lpceq,
               ModeFamily.TE: self.fiber._neff._teceq,
               ModeFamily.TM: self.fiber._neff._tmceq,
               ModeFamily.HE: self.fiber._neff._heceq,
               ModeFamily.EH: self.fiber._neff._ehceq
               }
        fct = Fct[self.mode.family]

        for i, neff in enumerate(Neff):
            try:
                y[i] = fct(neff, self.wl, self.mode.nu)
            except ZeroDivisionError:
                y[i] = numpy.nan

        self.plot.clear()
        self.plot.plot(Neff, y)
        self.plot.addLine(y=0)
        self.showZeros(self.zeros.isChecked(), True)

    def plotCutoff(self):
        V0 = self.fiber.V0(self.wl)
        V = numpy.linspace(0, V0, self.npInput.value())
        y = numpy.empty(V.shape)

        Fct = {ModeFamily.LP: self.fiber._cutoff._lpcoeq,
               ModeFamily.TE: self.fiber._cutoff._tecoeq,
               ModeFamily.TM: self.fiber._cutoff._tmcoeq,
               ModeFamily.HE: self.fiber._cutoff._hecoeq,
               ModeFamily.EH: self.fiber._cutoff._ehcoeq
               }
        fct = Fct[self.mode.family]

        for i, v in enumerate(V):
            try:
                y[i] = fct(v, self.mode.nu)
            except ZeroDivisionError:
                y[i] = numpy.nan

        self.plot.clear()
        self.plot.plot(V, y)
        self.plot.addLine(y=0)
        self.showZeros(self.zeros.isChecked(), True)

    def _get_char_eq_zeros(self):
        x = []
        delta = float(self.delta.text())
        nl = len(self.fiber)
        self.fiber._neff.start_log()
        for m in count(1):
            if self.mode.family is ModeFamily.EH and nl > 2:
                mode = Mode(ModeFamily.HE, self.mode.nu, m)
            else:
                mode = Mode(self.mode.family, self.mode.nu, m)
            neff = self.fiber.neff(mode, self.wl, delta)
            if isnan(neff):
                break
            else:
                x.append(neff)

            if mode.family is ModeFamily.HE and nl > 2:
                mode = Mode(ModeFamily.EH, self.mode.nu, m)
                neff = self.fiber.neff(mode, self.wl, delta)
                if isnan(neff):
                    break
                else:
                    x.append(neff)
        self.fiber._neff.stop_log()
        return x

    def _get_cutoff_eq_zeros(self):
        V0 = self.fiber.V0(self.wl)
        x = []
        self.fiber._cutoff.start_log()
        for m in count(1):
            mode = Mode(self.mode.family, self.mode.nu, m)
            co = self.fiber.cutoff(mode)
            if co < V0:
                x.append(co)
            else:
                break
        self.fiber._cutoff.stop_log()
        return x

    def showZeros(self, checked, reset=False):

        ckzeros = self.zeros.isChecked()
        ckpoints = self.points.isChecked() if ckzeros else False

        self.points.setEnabled(ckzeros)

        if reset:
            if self.__zeros is not None:
                self.plot.removeItem(self.__zeros)
                self.__zeros = None
            if self.__points is not None:
                self.plot.removeItem(self.__points)
                self.__points = None

        if ckzeros:
            if self.__zeros is None:
                if self.fType.currentIndex() == 0:
                    x = self._get_char_eq_zeros()
                else:
                    x = self._get_cutoff_eq_zeros()
                y = [0] * len(x)
                self.__zeros = pg.ScatterPlotItem(x, y, pen='r', brush='r')
            self.plot.addItem(self.__zeros)

            if self.__points is None:
                x, y = [], []
                if self.fType.currentIndex() == 0:
                    if len(self.fiber._neff.log) > 0:
                        x, y = zip(*self.fiber._neff.log)
                else:
                    if len(self.fiber._cutoff.log) > 0:
                        x, y = zip(*self.fiber._cutoff.log)
                self.__points = pg.ScatterPlotItem(x, y, pen='b', brush='b')

            if ckpoints:
                self.plot.addItem(self.__points)
                self.__points.stackBefore(self.__zeros)

        else:
            if self.__zeros is not None:
                self.plot.removeItem(self.__zeros)

        if not ckpoints:
            if self.__points is not None:
                self.plot.removeItem(self.__points)

    def setDelta(self, value):
        self.showZeros(self.zeros.isChecked(), reset=True)
