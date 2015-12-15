from PyQt4 import QtGui
import pyqtgraph as pg
import numpy
from math import isinf
import os.path
import csv


class FiberPlot(QtGui.QFrame):

    """

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dataFile = ""
        self.fiberData = None
        toolbar = self.initToolbar()

        self.plot = pg.PlotWidget()
        self.plot.getPlotItem().sigXRangeChanged.connect(self.updateXRange)
        self.plot.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.dataCurve = self.plot.plot()
        self.curve = self.plot.plot()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.plot)
        self.setLayout(layout)

    def initToolbar(self):
        toolbar = QtGui.QToolBar()

        self.foregroundColorButton = pg.ColorButton(color=(255, 255, 255))
        self.foregroundColorButton.sigColorChanged.connect(self.updateCurve)
        self.foregroundColorButton.setToolTip(self.tr("Line color"))
        toolbar.addWidget(self.foregroundColorButton)

        self.backgroundColorButton = pg.ColorButton(color=(0, 0, 0))
        self.backgroundColorButton.sigColorChanged.connect(self.updateBgColor)
        self.backgroundColorButton.setToolTip(self.tr("Background color"))
        toolbar.addWidget(self.backgroundColorButton)

        self.lineWidthSpinBox = QtGui.QDoubleSpinBox()
        self.lineWidthSpinBox.setRange(0, 10)
        self.lineWidthSpinBox.setValue(1)
        self.lineWidthSpinBox.setDecimals(1)
        self.lineWidthSpinBox.setSingleStep(1)
        self.lineWidthSpinBox.valueChanged.connect(self.updateCurve)
        self.lineWidthSpinBox.setToolTip(self.tr("Line width"))
        toolbar.addWidget(self.lineWidthSpinBox)

        toolbar.addSeparator()

        self.selectDataAction = toolbar.addAction(
            QtGui.QIcon.fromTheme('x-office-spreadsheet'),
            self.tr("Import data"),
            self.importData)

        self.dataFgColorButton = pg.ColorButton(color=(0, 255, 0))
        self.dataFgColorButton.sigColorChanged.connect(self.updateDataCurve)
        self.dataFgColorButton.setToolTip(self.tr("Imported data color"))
        self.dataFgColorButton.setEnabled(False)
        toolbar.addWidget(self.dataFgColorButton)

        self.dataLwSpinBox = QtGui.QDoubleSpinBox()
        self.dataLwSpinBox.setRange(0, 10)
        self.dataLwSpinBox.setValue(2)
        self.dataLwSpinBox.setDecimals(1)
        self.dataLwSpinBox.setSingleStep(1)
        self.dataLwSpinBox.valueChanged.connect(self.updateDataCurve)
        self.dataLwSpinBox.setToolTip(self.tr("Imported data line width"))
        self.dataLwSpinBox.setEnabled(False)
        toolbar.addWidget(self.dataLwSpinBox)

        self.deleteDataAction = toolbar.addAction(
            QtGui.QIcon.fromTheme('edit-delete'),
            self.tr("Delete data"),
            self.deleteData)
        self.deleteDataAction.setEnabled(False)

        return toolbar

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

    def updateCurve(self, *args, **kwargs):
        self.curve.setPen(color=self.foregroundColorButton.color(),
                          width=self.lineWidthSpinBox.value())

    def updateDataCurve(self, *args, **kwargs):
        self.dataCurve.setPen(color=self.dataFgColorButton.color(),
                              width=self.dataLwSpinBox.value())

    def updateBgColor(self):
        self.plot.setBackground(self.backgroundColorButton.color())

    def importData(self):
        lastDir = os.path.dirname(self.dataFile)

        filename, selectedFilter = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr("Select data file"),
            dir=lastDir,
            filter=self.tr("Comma Separated Values (*.csv);;"
                           "Tab Separated Values (*.tab)"))
        if not filename:
            return

        self.dataFile = filename
        dialect = 'excel-tab' if "(*.tab)" in selectedFilter else 'excel'

        data = []
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, dialect=dialect)
            for row in reader:
                data.append([float(x.replace(',', '.')) for x in row])
        self.fiberData = numpy.array(data).T

        self.dataCurve.setData(self.fiberData[0], self.fiberData[1])
        self.dataFgColorButton.setEnabled(True)
        self.dataLwSpinBox.setEnabled(True)
        self.deleteDataAction.setEnabled(True)
        self.updateDataCurve()

    def deleteData(self):
        ret = QtGui.QMessageBox.warning(
            self,
            self.tr("Remove fiber data"),
            self.tr("Are you sure you want to remove imported fiber data?"),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.Yes)

        if ret == QtGui.QMessageBox.Yes:
            self.fiberData = None
            self.dataCurve.setData([], [])
            self.dataFgColorButton.setEnabled(False)
            self.dataLwSpinBox.setEnabled(False)
            self.deleteDataAction.setEnabled(False)
