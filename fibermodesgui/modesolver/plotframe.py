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

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from fibermodesgui import blockSignals
from fibermodesgui.widgets.delegate import ComboItemDelegate
from fibermodes import ModeFamily


FIBERS, WAVELENGTHS, VNUMBER, MODES = range(4)
YAXISLIST = QtCore.Qt.UserRole + 1
MARK = ["None", "Mode", "Circle (o)", "Square (s)", "Triangle (t)",
        "Diamond (d)", "Plus (+)"]
MARKV = [None, "Mode", 'o', 's', 't', 'd', '+']
MARKM = {ModeFamily.HE: 'o', ModeFamily.EH: 's', ModeFamily.TE: 't',
         ModeFamily.TM: 'd', ModeFamily.LP: '+'}
LINES = ['────',
         '...........',
         '-------',
         '_._._._',
         '_.._.._']
LINESV = [QtCore.Qt.SolidLine,
          QtCore.Qt.DotLine,
          QtCore.Qt.DashLine,
          QtCore.Qt.DashDotLine,
          QtCore.Qt.DashDotDotLine]


class PlotOptions(QtGui.QDialog):

    def __init__(self, parent, f=QtCore.Qt.Widget):
        super().__init__(parent, f)
        self.parent = parent

        self.showLegend = QtGui.QCheckBox(self.tr("Show legend"))
        self.showLegend.stateChanged.connect(parent.updatePlot)

        self.showCutoffs = QtGui.QCheckBox(self.tr("Show cutoffs"))
        self.showCutoffs.stateChanged.connect(parent.updatePlot)
        self.showCutoffs.setEnabled(False)

        self.showLayers = QtGui.QCheckBox(self.tr("Show layer boundaries"))
        self.showLayers.stateChanged.connect(parent.updatePlot)

        self.showCurrentFiberWl = QtGui.QCheckBox(
            self.tr("Show current fiber / wavelength"))
        self.showCurrentFiberWl.stateChanged.connect(parent.updatePlot)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.showLegend)
        layout.addWidget(self.showCutoffs)
        layout.addWidget(self.showLayers)
        layout.addWidget(self.showCurrentFiberWl)
        self.setLayout(layout)

    def hideEvent(self, event):
        self.parent.optionsBut.setChecked(False)
        return super().hideEvent(event)

    def save(self):
        return {
            'legend': self.showLegend.isChecked(),
            'cutoffs': self.showCutoffs.isChecked(),
            'layers': self.showLayers.isChecked(),
            'current': self.showCurrentFiberWl.isChecked()
        }

    def load(self, options):
        with blockSignals(self.showLegend):
            self.showLegend.setChecked(options['legend'])
        with blockSignals(self.showCutoffs):
            self.showCutoffs.setChecked(options['cutoffs'])
        with blockSignals(self.showLayers):
            self.showLayers.setChecked(options['layers'])
        with blockSignals(self.showCurrentFiberWl):
            self.showCurrentFiberWl.setChecked(options['current'])
        self.parent.updatePlot()


class PropertyItemDelegate(ComboItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent, role=QtCore.Qt.UserRole)

    def createEditor(self, parent, option, index):
        try:
            self._items, self._values = index.data(role=YAXISLIST)
        except ValueError:
            return None  # results not returned yet
        return super().createEditor(parent, option, index)


class YAxisTableView(QtGui.QTableView):

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setModel(model)

        self.propertyItemDelegate = PropertyItemDelegate(self)
        self.lineStyleItemDelegate = ComboItemDelegate(self, LINES, LINESV,
                                                       QtCore.Qt.UserRole)
        self.markItemDelegate = ComboItemDelegate(self, MARK, MARKV,
                                                  QtCore.Qt.UserRole)
        self.setItemDelegateForColumn(0, self.propertyItemDelegate)
        self.setItemDelegateForColumn(1, self.lineStyleItemDelegate)
        self.setItemDelegateForColumn(2, self.markItemDelegate)

    def removeRow(self):
        rows = set()
        for idx in self.selectedIndexes():
            rows.add(idx.row())
        if len(rows) == 0:
            self.model().removeRow(-1)
        for i in sorted(rows, reverse=True):
            self.model().removeRow(i)


class PlotModel(QtCore.QAbstractTableModel):

    def __init__(self, parent):
        super().__init__(parent)
        self.doc = parent.doc

        self.plots = [[0, hash(QtCore.Qt.SolidLine), None]]

    def rowCount(self, parent=QtCore.QModelIndex):
        return len(self.plots)

    def columnCount(self, parent=QtCore.QModelIndex):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):
        value = self.plots[index.row()][index.column()]

        if index.column() == 0:
            if role == YAXISLIST:
                c = [p[0] for (i, p) in enumerate(self.plots)
                     if i != index.row()]
                params = [(p, i) for (i, p) in enumerate(self.doc.params)
                          if i not in c]
                return zip(*params)
            if role == QtCore.Qt.UserRole:
                return value

            if role == QtCore.Qt.DisplayRole:
                try:
                    return self.doc.params[value]
                except IndexError:
                    return ''

        elif index.column() == 1:  # line style
            if role == QtCore.Qt.UserRole:
                return value
            elif role == QtCore.Qt.DisplayRole:
                return LINES[LINESV.index(value)]

        elif index.column() == 2:  # mark
            if role == QtCore.Qt.UserRole:
                return value
            elif role == QtCore.Qt.DisplayRole:
                return MARK[MARKV.index(value)]

        if role == QtCore.Qt.DisplayRole:
            return value

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        self.plots[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                labels = [self.tr("y axis"),
                          self.tr("Line"),
                          self.tr("Mark")]
                return labels[section]
            else:
                return str(section + 1)

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEditable)

    def save(self):
        data = self.plots.copy()
        # for i, d in enumerate(data):
        #     data[i][1] = hash(d[1])
        return data

    def load(self, data):
        # for i, d in enumerate(data):
        #     data[i][1] = QtCore.Qt.PenStyle(d[1])
        self.plots = data
        self.layoutChanged.emit()

    def addRow(self):
        if len(self.plots) >= len(self.doc.params):
            return
        ci = 0
        c = [p[0] for p in self.plots]
        for i in range(len(self.doc.params)):
            if i not in c:
                ci = i
                break

        i = len(self.plots)
        self.plots.append([ci, QtCore.Qt.SolidLine, None])
        self.rowsInserted.emit(QtCore.QModelIndex(), i, i)

    def removeRow(self, i):
        if len(self.plots) == 1:
            return
        if i < 0:
            i = len(self.plots) + i
        del self.plots[i]
        self.rowsRemoved.emit(QtCore.QModelIndex(), i, i)


class PlotFrame(QtGui.QFrame):

    modified = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.doc = parent.doc
        self._wl = self._fnum = 0
        self._modesel = []

        self.plotOptions = PlotOptions(self)

        self.plot = pg.PlotWidget()
        self.legend = None
        self.plotModel = PlotModel(self)
        self.yAxisTable = YAxisTableView(self.plotModel)
        self.plotModel.dataChanged.connect(self.updatePlot)
        self.plotModel.rowsInserted.connect(self.updatePMButs)
        self.plotModel.rowsRemoved.connect(self.updatePMButs)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(self._xAxisLayout())
        layout.addWidget(self.yAxisTable)
        layout.addWidget(self.plot, stretch=1)
        self.setLayout(layout)

    def _xAxisLayout(self):
        self.xAxisSelector = QtGui.QComboBox()
        self.xAxisSelector.addItem(self.tr("Fibers"))
        self.xAxisSelector.addItem(self.tr("Wavelengths"))
        self.xAxisSelector.addItem(self.tr("V number"))
        # self.xAxisSelector.addItem(self.tr("Modes"))
        self.xAxisSelector.currentIndexChanged.connect(self.updatePlot)
        self.xAxisSelector.setCurrentIndex(VNUMBER)

        self.optionsBut = QtGui.QPushButton(
            QtGui.QIcon.fromTheme('document-properties'),
            self.tr("Options"))
        self.optionsBut.setCheckable(True)
        self.optionsBut.toggled.connect(self.plotOptions.setVisible)

        self.plusBut = QtGui.QPushButton(
            QtGui.QIcon.fromTheme('list-add'), '')
        self.plusBut.setToolTip(self.tr("Add plot parameter"))
        self.plusBut.clicked.connect(self.plotModel.addRow)

        self.minusBut = QtGui.QPushButton(
            QtGui.QIcon.fromTheme('list-remove'), '')
        self.minusBut.setToolTip(self.tr("Remove plot parameter"))
        self.minusBut.clicked.connect(self.yAxisTable.removeRow)
        self.minusBut.setEnabled(False)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel(self.tr("x axis:")))
        layout.addWidget(self.xAxisSelector)
        layout.addWidget(self.optionsBut)
        layout.addWidget(self.plusBut)
        layout.addWidget(self.minusBut)
        layout.addStretch(1)
        return layout

    def setFiber(self, value):
        self._fnum = value - 1
        self.updatePlot()

    def setWavelength(self, value):
        self._wl = value - 1
        self.updatePlot()

    def updateModeSel(self, modes):
        self._modesel = modes
        self.updatePlot()

    def updatePMButs(self, *args, **kwargs):
        self.minusBut.setEnabled(len(self.plotModel.plots) > 1)
        self.plusBut.setEnabled(len(self.plotModel.plots) <
                                len(self.doc.params))

    def updatePlot(self):
        if not self.doc.initialized:
            return

        self.plot.clear()
        if self.plotOptions.showLegend.isChecked():
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
            self.legend = self.plot.addLegend()
        elif self.legend is not None:
            self.legend.scene().removeItem(self.legend)
            self.legend = None

        self._updateXAxis()

        self.miny = float("inf")
        self.maxy = -float("inf")
        for i in range(self.plotModel.rowCount()):
            self.plotGraph(i)
        try:
            viewBox = self.plot.getPlotItem().getViewBox()
            viewBox.setYRange(self.miny, self.maxy)
        except:
            pass

        if (self.plotOptions.showCutoffs.isEnabled() and
                self.plotOptions.showCutoffs.isChecked()):
            self.plotCutoffs()

        if self.plotOptions.showLayers.isChecked():
            self.plotLayers()

    def _updateXAxis(self):
        index = self.xAxisSelector.currentIndex()

        if index == FIBERS:
            self.X = range(1, len(self.doc.fibers)+1)
        elif index == WAVELENGTHS:
            self.X = self.doc.wavelengths
        elif index == VNUMBER:
            fiber = self.doc.fibers[self._fnum]
            self.X = [fiber.V0(w) for w in self.doc.wavelengths[::-1]]
        # elif index == MODES:
        #     self.X = list(self.doc._simulator.modes(self._fnum, self._wl))

        units = 'm' if index == WAVELENGTHS else ''
        self.plot.getPlotItem().setLabel('bottom',
                                         self.xAxisSelector.currentText(),
                                         units)

        if index == WAVELENGTHS and "cutoff (wavelength)" in self.doc.params:
            self.plotOptions.showCutoffs.setEnabled(True)
        elif index == VNUMBER and "cutoff (V)" in self.doc.params:
            self.plotOptions.showCutoffs.setEnabled(True)
        else:
            self.plotOptions.showCutoffs.setEnabled(False)

        if self.plotOptions.showCurrentFiberWl.isChecked():
            if index == FIBERS:
                posx = self._fnum + 1
            elif index == WAVELENGTHS:
                posx = self.doc.wavelengths[self._wl]
            elif index == VNUMBER:
                posx = fiber.V0(self.doc.wavelengths[self._wl])
            self.plot.addLine(x=posx,
                              pen=pg.mkPen(color=(255, 255, 255, 255),
                                           style=QtCore.Qt.DotLine,
                                           width=3))

        viewBox = self.plot.getPlotItem().getViewBox()
        viewBox.setXRange(self.X[0], self.X[-1])
        self.modified.emit()

    def plotGraph(self, row):
        what = self.plotModel.data(self.plotModel.index(row, 0),
                                   QtCore.Qt.UserRole)
        line = self.plotModel.data(self.plotModel.index(row, 1),
                                   role=QtCore.Qt.UserRole)
        line = QtCore.Qt.PenStyle(line)
        mark = self.plotModel.data(self.plotModel.index(row, 2),
                                   QtCore.Qt.UserRole)
        if mark is None and len(self.X) == 1:
            mark = 'o'
        xaxis = self.xAxisSelector.currentIndex()
        nr = self.plotModel.rowCount()
        try:
            nf = self.doc.params[what]
        except IndexError:
            nf = ''

        y = {}
        if xaxis == FIBERS:
            for (f, w, m, j), v in self.doc.values.items():
                if j == what and w == self._wl:
                    if m in y:
                        y[m].append((f+1, v))
                    else:
                        y[m] = [(f+1, v)]
        else:
            for (f, w, m, j), v in self.doc.values.items():
                if j == what and f == self._fnum:
                    if m in y:
                        y[m].append((w, v))
                    else:
                        y[m] = [(w, v)]

        for m, xy in y.items():
            if self.doc.selection.get(m, 1) == 0:
                continue
            X, Y = zip(*sorted(xy))
            if xaxis == VNUMBER:
                X = [self.X[-x-1] for x in X]
            elif xaxis == WAVELENGTHS:
                X = [self.X[x] for x in X]

            col = m.color()
            symb = MARKM[m.family] if mark == 'Mode' else mark
            symbb = col if mark else None
            pen = pg.mkPen(color=col, style=line,
                           width=3 if m in self._modesel else 1)
            spen = pg.mkPen(color='w', width=2 if m in self._modesel else 1)
            name = str(m) if nr == 1 else "{} ({})".format(str(m), nf)
            self.plot.plot(X, Y, pen=pen, symbol=symb,
                           symbolBrush=symbb, symbolPen=spen, name=name)
            miny = min(Y)
            maxy = max(Y)
            self.miny = min(miny, self.miny)
            self.maxy = max(maxy, self.maxy)

    def plotCutoffs(self):
        xaxis = self.xAxisSelector.currentIndex()
        if xaxis == WAVELENGTHS:
            index = self.doc.params.index("cutoff (wavelength)")
        else:
            index = self.doc.params.index("cutoff (V)")
        for (f, w, m, j), v in self.doc.values.items():
            if self.doc.selection.get(m, 1) == 0:
                continue
            if j == index and f == self._fnum and w == 0:
                if self.X[0] < v < self.X[-1]:
                    col = m.color()
                    self.plot.addLine(
                        x=v,
                        pen=pg.mkPen(color=col,
                                     style=QtCore.Qt.DashLine,
                                     width=3 if m in self._modesel else 1))

    def plotLayers(self):
        if self.plotModel.rowCount() == 0:
            return
        what = self.plotModel.data(self.plotModel.index(0, 0),
                                   QtCore.Qt.UserRole)
        p = self.doc.params[what]
        norm = True if p == 'b' else False

        xaxis = self.xAxisSelector.currentIndex()
        if xaxis == FIBERS:
            wl = self.doc.wavelengths[self._wl]
            if norm:
                n1 = [max(layer.maxIndex(wl) for layer in fiber.layers)
                      for fiber in self.doc.fibers]
                n2 = [fiber.maxIndex(-1, wl) for fiber in self.doc.fibers]
            for i in range(len(self.doc.fibers[0])):  # TODO: merged layers...
                n = [fiber.maxIndex(i, wl) if i < len(fiber) else float("nan")
                     for fiber in self.doc.fibers]
                if norm:
                    for i in range(len(n)):
                        n[i] = (n[i]**2 - n2[i]**2) / (n1[i]**2 - n2[i]**2)
                self.plot.plot(self.X, n,
                               pen=pg.mkPen(color='w',
                                            style=QtCore.Qt.DotLine))
        else:
            fiber = self.doc.fibers[self._fnum]
            wls = (self.doc.wavelengths if xaxis == WAVELENGTHS
                   else self.doc.wavelengths[::-1])
            if norm:
                n1 = [max(layer.maxIndex(wl) for layer in fiber.layers)
                      for wl in wls]
                n2 = [fiber.maxIndex(-1, wl) for wl in wls]
            for layer in fiber.layers:
                n = [layer.maxIndex(wl) for wl in wls]
                if norm:
                    for i in range(len(n)):
                        n[i] = (n[i]**2 - n2[i]**2) / (n1[i]**2 - n2[i]**2)
                self.plot.plot(self.X, n,
                               pen=pg.mkPen(color='w',
                                            style=QtCore.Qt.DotLine))

    def save(self):
        return {
            'xaxis': self.xAxisSelector.currentIndex(),
            'options': self.plotOptions.save(),
            'yaxis': self.plotModel.save()
        }

    def load(self, options):
        self.xAxisSelector.setCurrentIndex(int(options['xaxis']))
        self.plotOptions.load(options['options'])
        self.plotModel.load(options['yaxis'])
