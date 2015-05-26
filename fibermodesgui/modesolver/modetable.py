
from PySide import QtGui, QtCore
from math import isnan, isinf


class ModeTableView(QtGui.QTableView):

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.setSortingEnabled(True)


class ModeTableModel(QtCore.QAbstractTableModel):

    def __init__(self, doc, parent=None):
        super().__init__(parent)
        self._doc = doc
        self._fnum = self._wl = 0
        self.modes = []
        doc.valuesChanged.connect(self.updateTable)

    def rowCount(self, parent=QtCore.QModelIndex):
        return len(self.modes)

    def columnCount(self, parent=QtCore.QModelIndex):
        return len(self._doc.params)

    def data(self, index, role):
        mode = self.modes[index.row()]
        try:
            v = self._doc.values[(self._fnum,
                                  self._wl,
                                  mode,
                                  index.column())]
        except KeyError:
            v = None

        if role == QtCore.Qt.DisplayRole:
            if v is None:
                return '...'
            elif isnan(v):
                return '--'
            elif isinf(v):
                return 'oo'
            else:
                if self._doc.params[index.column()] == 'cutoff':
                    return "{:.5f} nm".format(v * 1e9)
                elif self._doc.params[index.column()] == 'D':
                    return "{:.5f} ps / (nm km)".format(v * 1e9)
                else:
                    return "{:.5f}".format(v)
        elif role == QtCore.Qt.ToolTipRole:
            if v is None:
                return None
            elif isinf(v):
                return 'infinity'
            elif self._doc.params[index.column()] == 'cutoff':
                return v * 1e9
            else:
                return v

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._doc.params[section]
            else:
                return str(self.modes[section])

    def setFiber(self, fnum):
        self._fnum = fnum - 1
        self.updateTable()

    def setWavelength(self, wl):
        self._wl = wl - 1
        self.updateTable()

    def updateTable(self):
        """Update displayed values when fiber of wl index change."""
        sim = self._doc.simulator
        if sim.factory is None:
            return

        self.beginResetModel()
        self.modes = list(sim.modes(self._fnum, self._wl))
        self.endResetModel()

        if self._doc.toCompute > 0:
            QtCore.QTimer.singleShot(0, self._updateValues)

    def _updateValues(self):
        for fi, wi, m, j, v in self._doc.readyValues():
            if (fi, wi) == (self._fnum, self._wl):
                i = self.modes.index(m)
                index = self.index(i, j)
                self.setData(index, v)

        if self._doc.futures:
            QtCore.QTimer.singleShot(0, self._updateValues)
