
from PySide import QtGui, QtCore


class ModeTable(QtGui.QTableWidget):

    def __init__(self, doc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._doc = doc

    def setFibers(self, fibers):
        self._fibers = fibers

    def setFiber(self, fnum):
        self._fnum = fnum
        self._updateTable()

    def setWavelength(self, wl):
        self._wl = wl
        self._updateTable()

    def updateParams(self):
        self.setColumnCount(len(self._doc.params) + 1)
        self.setHorizontalHeaderLabels(['Modes'] + self._doc.params)
        self._updateTable()

    def _updateTable(self):
        self.clearContents()
        modes = set()

        if "cutoff" in self._doc.params and self._doc.cutoffs:
            for mode, co in self._doc.cutoffs[self._fnum]:
                if co >= self._wl:
                    modes.add(mode)

        if self._doc.modes and self._wl in self._doc.modes[self._fnum]:
            for mode in self._doc.modes[self._wl]:
                modes.add(mode)

        self.setRowCount(len(modes))
        for i, mode in enumerate(modes):
            item = QtGui.QTableWidgetItem(str(mode))
            self.setItem(i, 0, item)

            for j, prop in enumerate(self._properties, 1):
                if prop == "cutoff":
                    if mode in self._doc.cutoffs[self._fnum]:
                        co = self._doc.cutoffs[self._fnum][mode]
                        item = QtGui.QTableWidgetItem(
                            "{:.5f} nm".format(co * 1e9))
                        self.setItem(i, j, item)
                elif self._wl in self._doc.modes[self._fnum]:
                    if mode in self._doc.modes[self._fnum][self._wl]:
                        if prop in self._doc.modes[self._fnum][self._wl][mode]:
                            p = self._doc.modes[self._fnum][self._wl][mode][prop]
                            item = QtGui.QTableWidgetItem(
                                "{:.5f}".format(p))
                            self.setItem(i, j, item)
