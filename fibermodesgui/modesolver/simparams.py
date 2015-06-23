from PySide import QtGui


class SimParamsDialog(QtGui.QDialog):

    def __init__(self, doc, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.numProcs = QtGui.QSpinBox()
        self.numProcs.setRange(0, 16)
        self.numProcs.setValue(doc.numProcs)
        self.numProcs.setSpecialValueText("auto")

        flayout = QtGui.QFormLayout()
        flayout.addRow(QtGui.QLabel(self.tr("Number of processes")),
                       self.numProcs)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close)
        buttonBox.rejected.connect(self.close)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(flayout)
        layout.addWidget(buttonBox)

        self.setLayout(layout)
