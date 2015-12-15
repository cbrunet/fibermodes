from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy
from math import ceil


# TODO: optimize for speed. See scatter plot? Pre built objects?


class QuiverWidget(QtGui.QGroupBox):

    def __init__(self, pwin, parent=None):
        super().__init__(parent)

        self.pwin = pwin
        self.__quiver = []

        self.setTitle(self.tr("Polarization (Quiver)"))
        self.setCheckable(True)
        self.setChecked(False)

        layout = QtGui.QFormLayout()

        glabel = QtGui.QLabel(self.tr("Grid Size"))
        self.grid = QtGui.QSpinBox()
        self.grid.setRange(5, 100)
        self.grid.setValue(10)
        self.grid.valueChanged.connect(self.updateGrid)
        glabel.setBuddy(self.grid)
        layout.addRow(glabel, self.grid)

        clabel = QtGui.QLabel(self.tr("Color"))
        self.color = pg.ColorButton(color=(85, 170, 255))
        self.color.sigColorChanging.connect(self.setColor)
        clabel.setBuddy(self.color)
        layout.addRow(clabel, self.color)

        alabel = QtGui.QLabel(self.tr("Arrow Length"))
        self.arrow = QtGui.QSpinBox()
        self.arrow.setRange(2, 100)
        self.arrow.setSingleStep(5)
        self.arrow.setValue(40)
        self.arrow.valueChanged.connect(self.updateArrows)
        alabel.setBuddy(self.arrow)
        layout.addRow(alabel, self.arrow)

        hlabel = QtGui.QLabel(self.tr("Head Length"))
        self.head = QtGui.QSpinBox()
        self.head.setRange(0, 100)
        self.head.setSingleStep(5)
        self.head.setValue(40)
        self.head.setSuffix(" %")
        self.head.valueChanged.connect(self.updateArrows)
        hlabel.setBuddy(self.head)
        layout.addRow(hlabel, self.head)

        self.toggled.connect(self.toggleQuiver)
        self.setLayout(layout)

    def updateFields(self, Emod, Epol):
        self.angles = numpy.degrees(Epol)
        self.lengths = Emod / numpy.max(Emod)
        self.updateGrid()

    def updateGrid(self, value=None):
        npg = self.grid.value()
        npw = self.pwin.options.np.value()

        for q in self.__quiver:
            self.pwin.graph.removeItem(q)
        self.__quiver = []

        d = int(ceil(npw // npg))
        idx = range(d // 2, npw, d)
        r = self.pwin.options.radius.value() * 1e-6
        R = numpy.linspace(-r, r, npw)

        for i in idx:
            for j in idx:
                a = pg.ArrowItem(angle=self.angles[i, j],
                                 pos=(R[i], R[j]),
                                 tailWidth=1)
                self.pwin.graph.addItem(a)
                self.__quiver.append(a)
        self.setColor()
        self.updateArrows()
        self.toggleQuiver(self.isChecked())

    def toggleQuiver(self, show):
        for q in self.__quiver:
            q.setVisible(show)

    def setColor(self):
        pen = pg.mkPen(color=self.color.color())
        brush = pg.mkBrush(color=self.color.color())
        for q in self.__quiver:
            q.setStyle(pen=pen, brush=brush)

    def updateArrows(self):
        npg = self.grid.value()
        npw = self.pwin.options.np.value()
        al = self.arrow.value()
        ap = self.head.value() / 100

        d = int(ceil(npw // npg))
        idx = range(d // 2, npw, d)

        ii = 0
        for i in idx:
            for j in idx:
                self.__quiver[ii].setStyle(
                    headLen=ap*al*self.lengths[i, j],
                    tailLen=(1-ap)*al*self.lengths[i, j])
                ii += 1
