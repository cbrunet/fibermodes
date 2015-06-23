
from PySide import QtGui, QtCore
from math import isnan, isinf


class ModeTableView(QtGui.QTableView):

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.setSortingEnabled(True)


PARAMS = {
    "cutoff (wavelength": (1e9, "nm"),
    "vp": (1e-6, "m / s"),
    "vg": (1e-6, "m / us"),
    "D": (1, "ps / (nm km)"),
    "S": (1, "ps / (nm² km)"),
    "beta0": (1e-9, "1 / nm"),
    "beta1": (1e3, "ps / nm"),
    "beta2": (1e15, "ps² / nm"),
    "beta3": (1e27, "ps³ / nm"),
}


class ModeTableModel(QtCore.QAbstractTableModel):

    def __init__(self, doc, parent=None):
        super().__init__(parent)
        self._doc = doc
        self._fnum = self._wl = 0
        self.modes = []

        doc.modesAvailable.connect(self.updateModes)
        doc.valueAvailable.connect(self.updateValue)

    def rowCount(self, parent=QtCore.QModelIndex):
        return len(self.modes)

    def columnCount(self, parent=QtCore.QModelIndex):
        return len(self._doc.params)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        mode = self.modes[index.row()]
        try:
            v = self._doc.values[(self._fnum,
                                  self._wl,
                                  mode,
                                  index.column())]
        except KeyError:
            v = None

        p = self._doc.params[index.column()]
        m, u = PARAMS.get(p, (1, ""))
        if role == QtCore.Qt.DisplayRole:
            if v is None:
                return '...'
            elif isnan(v):
                return '--'
            elif isinf(v):
                return 'oo'
            else:
                if u:
                    u = " "+u
                return "{:.5f}{}".format(v*m, u)
        elif role == QtCore.Qt.ToolTipRole:
            if v is None:
                return None
            elif isinf(v):
                return 'infinity'
            else:
                return v*m

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            try:
                if orientation == QtCore.Qt.Horizontal:
                    return self._doc.params[section]
                else:
                    return str(self.modes[section])
            except IndexError:
                return None

    def setFiber(self, fnum):
        self._fnum = fnum - 1
        self.updateTable()

    def setWavelength(self, wl):
        self._wl = wl - 1
        self.updateTable()

    def updateModes(self, fnum):
        if fnum == self._fnum:
            self.updateTable()

    def updateTable(self):
        """Update displayed values when fiber of wl index change."""
        sim = self._doc.simulator
        if sim.factory is None:
            return

        self.beginResetModel()
        try:
            self.modes = list(self._doc.modes[self._fnum][self._wl])
        except IndexError:
            pass
        self.endResetModel()

    def updateValue(self, fnum, wl, mode, j):
        if (fnum, wl) == (self._fnum, self._wl):
            i = self.modes.index(mode)
            index = self.index(i, j)
            self.dataChanged.emit(index, index)
