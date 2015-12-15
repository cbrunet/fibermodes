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

from PyQt4 import QtCore, QtGui
from fibermodes import ModeFamily


class ShowHideMode(QtGui.QGroupBox):

    showModes = QtCore.pyqtSignal(int, int)
    hideModes = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Display"))
        self._modes = []

        layout = QtGui.QHBoxLayout()

        self.options = QtGui.QComboBox()

        self.what = QtGui.QComboBox()
        self.what.addItems([self.tr("All"),
                            self.tr("Family"),
                            self.tr("ν parameter"),
                            self.tr("m parameter")])
        self.what.currentIndexChanged.connect(self.updateWhat)
        self.what.setCurrentIndex(0)

        self.bshow = QtGui.QPushButton(self.tr("Show"))
        self.bshow.clicked.connect(self.emitShowModes)
        self.bhide = QtGui.QPushButton(self.tr("Hide"))
        self.bhide.clicked.connect(self.emitHideModes)

        layout.addWidget(self.what)
        layout.addWidget(self.options)
        layout.addWidget(self.bshow)
        layout.addWidget(self.bhide)
        self.setLayout(layout)

    @property
    def modes(self):
        return self._modes

    @modes.setter
    def modes(self, modes):
        self._modes = modes
        self.updateWhat(self.what.currentIndex())

    def updateWhat(self, index):
        self.options.clear()
        if index == 0:  # all
            self.options.setEnabled(False)

        else:
            self.options.setEnabled(True)

            if index == 1:  # family
                ait = set(m.family.name for m in self._modes)
                items = list(f.name for f in ModeFamily)

            elif index == 2:  # nu
                ait = set(str(m.nu) for m in self._modes)
                maxnu = max((m.nu for m in self._modes), default=0)
                items = list(str(n) for n in range(maxnu+1))

            elif index == 3:  # m
                ait = set(str(m.m) for m in self._modes)
                maxm = max((m.m for m in self._modes), default=0)
                items = list(str(m) for m in range(1, maxm+1))

            self.options.addItems(items)
            model = self.options.model()
            for i in range(len(items)):
                if items[i] not in ait:
                    item = model.item(i)
                    item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable |
                                                   QtCore.Qt.ItemIsEnabled))

    def emitShowModes(self):
        self.showModes.emit(self.what.currentIndex(),
                            self.options.currentIndex())

    def emitHideModes(self):
        self.hideModes.emit(self.what.currentIndex(),
                            self.options.currentIndex())
