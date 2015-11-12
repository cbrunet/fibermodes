from PySide import QtGui
import pyqtgraph as pg
import numpy
from fibermodes import Mode, ModeFamily, Wavelength


class CharEqDialog(QtGui.QDialog):

    """Plot characteristic function

    TODO: localize zeros
    TODO: follow the mouse

    """

    def __init__(self, mode=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.fnum = parent.fiberSlider.slider.value()
        wlnum = parent.wavelengthSlider.wavelengthInput.value()
        self.wl = parent.doc.wavelengths[wlnum-1]

        self.mode = mode if mode else Mode(ModeFamily.HE, 1, 1)
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
        self.mInput.setValue(self.mode.m)
        self.mInput.valueChanged.connect(self.updateMode)

        npLabel = QtGui.QLabel(self.tr("# points"))
        self.npInput = QtGui.QSpinBox()
        self.npInput.setRange(50, 10000)
        self.npInput.setValue(50)
        self.npInput.setSingleStep(50)
        self.npInput.valueChanged.connect(self.updateMode)

        hlayout = QtGui.QHBoxLayout()
        if hasattr(self.fiber._cutoff, '_lpcoeq'):
            hlayout.addWidget(self.fType)
        hlayout.addWidget(self.modeInput)
        hlayout.addWidget(self.nuInput)
        hlayout.addWidget(self.mInput)
        hlayout.addSpacing(1)
        hlayout.addWidget(npLabel)
        hlayout.addWidget(self.npInput)
        hlayout.addStretch(1)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(hlayout)
        layout.addWidget(self.plot)

        self.setLayout(layout)
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
               ModeFamily.EH: self.fiber._neff._heceq
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
