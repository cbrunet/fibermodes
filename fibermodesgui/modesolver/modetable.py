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
from math import isnan, isinf


class ModeTableView(QtGui.QTableView):

    selChanged = QtCore.pyqtSignal(list)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setModel(model)
        self.setSortingEnabled(True)
        self.sortByColumn(1, QtCore.Qt.AscendingOrder)

    def selectedModes(self):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(self.model().mapToSource(index).row())

        modes = []
        for row in rows:
            # Use source model, because the proxy model transforms
            # the Mode object into list...
            mode = self.model().sourceModel().headerData(
                row, QtCore.Qt.Vertical, QtCore.Qt.UserRole)
            modes.append(mode)
        return modes

    def selectionChanged(self, selected, deselected):
        self.selChanged.emit(self.selectedModes())
        return super().selectionChanged(selected, deselected)


PARAMS = {
    "cutoff (wavelength)": (1e9, "nm"),
    "vp": (1e-6, "m / s"),
    "vg": (1e-6, "m / us"),
    "D": (1, "ps / (nm km)"),
    "S": (1, "ps / (nm² km)"),
    "beta0": (1e-9, "nm⁻¹"),
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
        return len(self._doc.params) + 1  # plus selection

    def flags(self, index):
        if index.column() == 0:
            f = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        else:
            f = super().flags(index)
        return f

    def data(self, index, role=QtCore.Qt.DisplayRole):
        mode = self.modes[index.row()]
        if index.column() == 0:  # selection
            if role == QtCore.Qt.CheckStateRole:
                sel = self._doc.selection.get(mode, 1)
                return QtCore.Qt.Checked if sel else QtCore.Qt.Unchecked
            else:
                return None

        try:
            v = self._doc.values[(self._fnum,
                                  self._wl,
                                  mode,
                                  index.column()-1)]
        except KeyError:
            v = None

        p = self._doc.params[index.column()-1]
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
                return "{:.5g}{}".format(v*m, u)
        elif role == QtCore.Qt.ToolTipRole:
            if v is None:
                return None
            elif isinf(v):
                return 'infinity'
            else:
                return v*m
        elif role == QtCore.Qt.UserRole:
            return float(v) if v is not None else v

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if index.column() == 0:
            mode = self.modes[index.row()]
            self._doc.selection[mode] = value
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        try:
            if orientation == QtCore.Qt.Horizontal:
                if role == QtCore.Qt.DisplayRole:
                    if section == 0:
                        return ""
                    else:
                        return self._doc.params[section-1]
                elif role == QtCore.Qt.ToolTipRole:
                    if section == 0:
                        return "Plot mode"
            else:
                if role == QtCore.Qt.DisplayRole:
                    return str(self.modes[section])
                elif role == QtCore.Qt.UserRole:
                    return self.modes[section]
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
