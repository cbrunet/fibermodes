#!/usr/bin/env python3

import sys
from fibermodes import Wavelength
from fibermodesgui import blockSignals
from PySide import QtCore, QtGui


class WavelengthCalculator(QtGui.QDialog):

    hidden = QtCore.Signal()

    def __init__(self, parent=None, f=0):
        super().__init__(parent, f)
        self.wl = Wavelength(1550e-9)

        self.setWindowTitle(self.tr("Wavelength Calculator"))
        layout = QtGui.QGridLayout()

        llabel = QtGui.QLabel("λ")
        self.linput = QtGui.QDoubleSpinBox()
        self.linput.setDecimals(3)
        self.linput.setRange(1, 50000)
        self.linput.setSingleStep(1)
        self.linput.setSuffix(" nm")
        self.linput.valueChanged.connect(self.lvalueChanged)
        llabel.setBuddy(self.linput)
        layout.addWidget(llabel, 0, 0, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.linput, 0, 1)

        klabel = QtGui.QLabel("k₀")
        self.kinput = QtGui.QDoubleSpinBox()
        self.kinput.setDecimals(3)
        self.kinput.setRange(125662, 6283185308)
        self.kinput.setSingleStep(1)
        self.kinput.setSuffix(" m⁻¹")
        self.kinput.valueChanged.connect(self.kvalueChanged)
        klabel.setBuddy(self.kinput)
        layout.addWidget(klabel, 0, 2, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.kinput, 0, 3)

        wlabel = QtGui.QLabel("ω")
        self.winput = QtGui.QDoubleSpinBox()
        self.winput.setDecimals(3)
        self.winput.setRange(36, 1883652)
        self.winput.setSingleStep(1)
        self.winput.setSuffix(" Trad/s")
        self.winput.valueChanged.connect(self.wvalueChanged)
        wlabel.setBuddy(self.winput)
        layout.addWidget(wlabel, 1, 0, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.winput, 1, 1)

        flabel = QtGui.QLabel("f")
        self.finput = QtGui.QDoubleSpinBox()
        self.finput.setDecimals(3)
        self.finput.setRange(0, 1e12)
        self.finput.setSingleStep(1)
        self.finput.setSuffix(" THz")
        self.finput.valueChanged.connect(self.fvalueChanged)
        flabel.setBuddy(self.finput)
        layout.addWidget(flabel, 1, 2, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.finput, 1, 3)

        self.band = QtGui.QLabel()
        self.band.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.band, 2, 0, 1, 4,
                         alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)

        self._updateInputs()

    def _updateInputs(self):
        with blockSignals(self.linput):
            self.linput.setValue(self.wl * 1e9)
        with blockSignals(self.kinput):
            self.kinput.setValue(self.wl.k0)
        with blockSignals(self.winput):
            self.winput.setValue(self.wl.omega * 1e-12)
        with blockSignals(self.finput):
            self.finput.setValue(self.wl.frequency * 1e-12)

        if self.wl < 1260e-9:
            self.band.setText("")
        elif self.wl < 1360e-9:
            self.band.setText("O band")
        elif self.wl < 1460e-9:
            self.band.setText("E band")
        elif self.wl < 1530e-9:
            self.band.setText("S band")
        elif self.wl < 1565e-9:
            self.band.setText("C band")
        elif self.wl < 1625e-9:
            self.band.setText("L band")
        elif self.wl <= 1675e-9:
            self.band.setText("U band")
        else:
            self.band.setText("")

    def lvalueChanged(self, value):
        self.wl = Wavelength(value * 1e-9)
        self._updateInputs()

    def kvalueChanged(self, value):
        self.wl = Wavelength(k0=value)
        self._updateInputs()

    def wvalueChanged(self, value):
        self.wl = Wavelength(omega=value*1e12)
        self._updateInputs()

    def fvalueChanged(self, value):
        self.wl = Wavelength(frequency=value*1e12)
        self._updateInputs()

    def hideEvent(self, event):
        self.hidden.emit()
        return super().hideEvent(event)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Wavelength Calculator')

    win = WavelengthCalculator()
    win.show()

    sys.exit(app.exec_())
