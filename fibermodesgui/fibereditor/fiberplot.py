from PySide import QtGui
import pyqtgraph as pg
import numpy
from math import isinf


class FiberPlot(QtGui.QFrame):

    """

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.plot = pg.PlotWidget()
        self.plot.getPlotItem().sigXRangeChanged.connect(self.updateXRange)
        self.plot.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.curve = self.plot.plot()
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)

    def autoScale(self):
        r = self.fiber.innerRadius(-1) * 1.5e6
        viewBox = self.plot.getPlotItem().getViewBox()
        viewBox.setXRange(-r, r, 0)
        nmin = self.fiber.minIndex(-1, self.wl)
        nmax = max(layer.maxIndex(self.wl) for layer in self.fiber.layers)
        viewBox.setYRange(nmin, nmax)
        self.updateXRange(viewBox)

    def updateInfo(self, fiber, wl):
        self.fiber = fiber
        self.wl = wl
        self.autoScale()

    def updateXRange(self, viewbox):
        xmin, xmax = viewbox.viewRange()[0]
        xmin *= 1e-6
        xmax *= 1e-6

        R = numpy.empty(0)
        N = numpy.empty(0)

        if xmax > 0:
            for i, layer in enumerate(self.fiber.layers):
                inr = self.fiber.innerRadius(i)
                out = self.fiber.outerRadius(i)
                if inr > xmax and not isinf(out):
                    break
                if out < xmin:
                    continue
                if inr < xmin:
                    inr = xmin
                if out > xmax:
                    out = xmax
                rr = numpy.linspace(inr, out)
                nn = numpy.fromiter((layer.index(r, self.wl) for r in rr),
                                    dtype=float, count=rr.size)
                R = numpy.concatenate((R, rr))
                N = numpy.concatenate((N, nn))
        if xmin < 0:
            for i, layer in enumerate(self.fiber.layers):
                inr = -self.fiber.innerRadius(i)
                out = -self.fiber.outerRadius(i)
                if inr < xmin and not isinf(out):
                    break
                if out > xmax:
                    continue
                if inr > xmax:
                    inr = xmax
                if out < xmin:
                    out = xmin
                rr = numpy.linspace(out, inr)
                nn = numpy.fromiter((layer.index(r, self.wl) for r in rr),
                                    dtype=float, count=rr.size)
                R = numpy.concatenate((rr, R))
                N = numpy.concatenate((nn, N))

        self.curve.setData(R * 1e6, N)

    def mouseClickEvent(self, event):
        if event.double():
            self.autoScale()
