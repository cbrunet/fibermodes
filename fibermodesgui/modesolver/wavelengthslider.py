
from PyQt4 import QtGui, QtCore


class WavelengthSlider(QtGui.QFrame):

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        label = QtGui.QLabel(self.tr("Wavelength"))

        self.wavelengthInput = QtGui.QSpinBox()
        self.wavelengthInput.valueChanged.connect(self.changeValue)

        self.totLabel = QtGui.QLabel()

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self.changeValue)

        self.wlLabel = QtGui.QLabel()
        self.vLabel = QtGui.QLabel()

        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(self.wavelengthInput)
        hlayout.addWidget(self.totLabel)

        h2layout = QtGui.QHBoxLayout()
        h2layout.addWidget(self.wlLabel)
        h2layout.addWidget(self.vLabel)

        vlayout = QtGui.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.slider)
        vlayout.addLayout(h2layout)

        self.setLayout(vlayout)

        self.setNum(0)

    def setNum(self, value):
        mv = 1 if value else 0
        self.totLabel.setText("/ {}".format(value))
        self.wavelengthInput.setRange(mv, value)
        self.slider.setRange(mv, value)

    def value(self):
        return self.wavelengthInput.value()

    def changeValue(self, value):
        if value != self.wavelengthInput.value():
            self.wavelengthInput.setValue(value)
        if value != self.slider.value():
            self.slider.setValue(value)
        self.valueChanged.emit(value)
