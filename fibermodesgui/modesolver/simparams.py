from PyQt4 import QtGui


class SimParamsDialog(QtGui.QDialog):

    def __init__(self, doc, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.numProcs = QtGui.QSpinBox()
        self.numProcs.setRange(0, 16)
        self.numProcs.setValue(doc.numProcs)
        self.numProcs.setSpecialValueText("auto")
        self.numProcs.setWhatsThis(self.tr(
            "Set the number of processes used for computing. If 'auto', use "
            "all processors. If '1', use the sequential version of the "
            "simulator.\n\n"
            "Be aware than assigning more processes than the number of "
            "processors could decrease performance."))

        deltaValidator = QtGui.QDoubleValidator(bottom=1e-31, top=1)
        self.delta = QtGui.QLineEdit()
        self.delta.setValidator(deltaValidator)
        self.delta.setText("{:e}".format(doc.simulator.delta))
        self.delta.setWhatsThis(self.tr(
            "Step size used when solving for modes. Smaller number means "
            "increased computation time, while bigger number means more "
            "chances of skipping solutions."))

        flayout = QtGui.QFormLayout()
        flayout.addRow(QtGui.QLabel(self.tr("Number of processes")),
                       self.numProcs)
        flayout.addRow(QtGui.QLabel(self.tr("Delta parameter")),
                       self.delta)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close |
                                           QtGui.QDialogButtonBox.Help)
        buttonBox.rejected.connect(self.close)
        buttonBox.clicked.connect(QtGui.QWhatsThis.enterWhatsThisMode)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(flayout)
        layout.addWidget(buttonBox)

        self.setLayout(layout)
