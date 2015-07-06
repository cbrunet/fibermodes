from PySide import QtGui
import pyqtgraph as pg
import numpy
from fibermodes import ModeFamily


class CharEqDialog(QtGui.QDialog):

    """Plot characteristic function

    TODO: localize zeros
    TODO: follow the mouse

    """

    def __init__(self, mode, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        fnum = parent.fiberSlider.slider.value()
        wlnum = parent.wavelengthSlider.wavelengthInput.value()
        self.wl = parent.doc.wavelengths[wlnum-1]

        self.mode = mode
        self.fiber = parent.doc.fibers[fnum-1]
        self.neffMin = self.fiber.minIndex(-1, self.wl)
        self.neffMax = max(layer.maxIndex(self.wl)
                           for layer in self.fiber.layers)

        title = "Fiber: {}  Wavelength: {} nm  Mode: {}".format(
            fnum, self.wl * 1e9, mode)
        self.setWindowTitle("Characteristic function: " + title)

        label = QtGui.QLabel(title)
        self.plot = pg.PlotWidget()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.plot)

        self.setLayout(layout)

        self.plotCharEq()

    def plotCharEq(self):
        Neff = numpy.linspace(self.neffMin, self.neffMax)
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

        self.plot.plot(Neff, y)
        self.plot.addLine(y=0)
