#!/usr/bin/env python3

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

import sys
from fibermodes import Wavelength
from fibermodes.fiber import material
from fibermodesgui import blockSignals
from PyQt4 import QtCore, QtGui


class MaterialCalculator(QtGui.QDialog):

    hidden = QtCore.pyqtSignal()

    def __init__(self, parent=None, f=QtCore.Qt.Widget):
        super().__init__(parent, f)
        self.wl = Wavelength(1550e-9)
        self.conc = 0
        self.index = None
        self.material = None
        self.iscomp = False

        self.setWindowTitle(self.tr("Material Calculator"))

        glayout = QtGui.QGridLayout()
        ilayout = QtGui.QVBoxLayout()

        mlabel = QtGui.QLabel(self.tr("Material"))
        self.matinput = QtGui.QComboBox()
        self.matinput.addItems([m for m in material.__all__ if m != "Fixed"])
        self.matinput.currentIndexChanged.connect(self.selectMaterial)
        mlabel.setBuddy(self.matinput)
        glayout.addWidget(mlabel, 0, 0, alignment=QtCore.Qt.AlignRight)
        glayout.addWidget(self.matinput, 0, 1)

        wlabel = QtGui.QLabel(self.tr("Wavelength"))
        self.winput = QtGui.QDoubleSpinBox()
        self.winput.setDecimals(3)
        self.winput.setRange(1, 50000)
        self.winput.setSingleStep(1)
        self.winput.setValue(self.wl * 1e9)
        self.winput.setSuffix(" nm")
        self.winput.valueChanged.connect(self.wavelengthChanged)
        wlabel.setBuddy(self.winput)
        glayout.addWidget(wlabel, 1, 0, alignment=QtCore.Qt.AlignRight)
        glayout.addWidget(self.winput, 1, 1)

        clabel = QtGui.QLabel(self.tr("Concentration"))
        self.cinput = QtGui.QDoubleSpinBox()
        self.cinput.setDecimals(4)
        self.cinput.setRange(0, 100)
        self.cinput.setSingleStep(1)
        self.cinput.setSuffix(" %")
        self.cinput.setValue(self.conc * 100)
        self.cinput.valueChanged.connect(self.concentrationChanged)
        clabel.setBuddy(self.cinput)
        glayout.addWidget(clabel, 2, 0, alignment=QtCore.Qt.AlignRight)
        glayout.addWidget(self.cinput, 2, 1)

        ilabel = QtGui.QLabel(self.tr("Index"))
        self.iinput = QtGui.QDoubleSpinBox()
        self.iinput.setDecimals(6)
        self.iinput.setRange(1, 10)
        self.iinput.setSingleStep(1e-3)
        self.iinput.valueChanged.connect(self.indexChanged)
        ilabel.setBuddy(self.iinput)
        glayout.addWidget(ilabel, 3, 0, alignment=QtCore.Qt.AlignRight)
        glayout.addWidget(self.iinput, 3, 1)

        # infolabel = QtGui.QLabel(self.tr("<b>Info</b>"))
        # ilayout.addWidget(infolabel)
        self.infotext = QtGui.QTextEdit()
        self.infotext.setReadOnly(True)
        ilayout.addWidget(self.infotext)
        ilayout.addStretch(1)

        layout = QtGui.QHBoxLayout()
        layout.addLayout(glayout)
        layout.addLayout(ilayout)
        self.setLayout(layout)

        self.selectMaterial(0)

    def selectMaterial(self, index):
        materialName = self.matinput.currentText()
        self.material = material.__dict__[materialName]

        self.iscomp = issubclass(self.material,
                                 material.compmaterial.CompMaterial)
        self.cinput.setEnabled(self.iscomp)

        text = "<h1>{}</h1>".format(self.material.name)
        if self.material.info:
            text += "<p>{}</p>".format(self.material.info)
        if self.material.url:
            text += '<p><a href="{url}">{url}</a></p>'.format(
                url=self.material.url)
        self.infotext.setText(text)

        self.index = None
        self._updateInputs()

    def wavelengthChanged(self, value):
        self.wl = Wavelength(value * 1e-9)
        self.index = None
        self._updateInputs()

    def concentrationChanged(self, value):
        self.conc = value * 0.01
        self.index = None
        self._updateInputs()

    def indexChanged(self, value):
        self.index = value
        if self.iscomp:
            self.conc = None
        else:
            self.wl = None
        self._updateInputs()

    def _updateInputs(self):
        if self.index is None:
            args = [self.conc] if self.iscomp else []
            self.index = self.material.n(self.wl, *args)
            with blockSignals(self.iinput):
                self.iinput.setValue(self.index)
        elif self.conc is None:
            self.conc = self.material.xFromN(self.wl, self.index)
            with blockSignals(self.cinput):
                self.cinput.setValue(self.conc * 100)
        elif self.wl is None:
            args = [self.conc] if self.iscomp else []
            self.wl = self.material.wlFromN(self.index, *args)
            if self.wl is None:
                self.wavelengthChanged(self.winput.value())
            else:
                with blockSignals(self.winput):
                    self.winput.setValue(self.wl * 1e9)

    def hideEvent(self, event):
        self.hidden.emit()
        return super().hideEvent(event)


def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName('UTF-8'))
    app.setApplicationName('Material Calculator')

    win = MaterialCalculator()
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
