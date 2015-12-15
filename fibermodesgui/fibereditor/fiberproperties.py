from PyQt4 import QtGui
from datetime import datetime


class FiberPropertiesWindow(QtGui.QDialog):

    def __init__(self, fibers, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._fibers = fibers
        self.setWindowTitle(self.tr("Fiber Properties"))

        self.nameInput = QtGui.QLineEdit()
        self.authorInput = QtGui.QLineEdit()
        self.crdateLabel = QtGui.QLabel()
        self.tstampLabel = QtGui.QLabel()
        self.descriptionInput = QtGui.QPlainTextEdit()

        formLayout = QtGui.QFormLayout()
        formLayout.addRow(QtGui.QLabel(self.tr("Name")),
                          self.nameInput)
        formLayout.addRow(QtGui.QLabel(self.tr("Author")),
                          self.authorInput)
        formLayout.addRow(QtGui.QLabel(self.tr("Created")),
                          self.crdateLabel)
        formLayout.addRow(QtGui.QLabel(self.tr("Modified")),
                          self.tstampLabel)
        formLayout.addRow(QtGui.QLabel(self.tr("Description")),
                          self.descriptionInput)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                           QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def exec_(self):
        self.nameInput.setText(self._fibers["name"])
        self.authorInput.setText(self._fibers["author"])
        self.crdateLabel.setText(datetime.fromtimestamp(
            self._fibers["crdate"]).strftime('%Y-%m-%d %H:%M:%S'))
        self.tstampLabel.setText(datetime.fromtimestamp(
            self._fibers["tstamp"]).strftime('%Y-%m-%d %H:%M:%S'))
        self.descriptionInput.setPlainText(self._fibers["description"])
        super().exec_()

    def accept(self):
        if self._fibers["name"] != self.nameInput.text():
            self._fibers["name"] = self.nameInput.text()
            self.parent().setDirty(True)
        if self._fibers["author"] != self.authorInput.text():
            self._fibers["author"] = self.authorInput.text()
            self.parent().setDirty(True)
        if self._fibers["description"] != self.descriptionInput.toPlainText():
            self._fibers["description"] = self.descriptionInput.toPlainText()
            self.parent().setDirty(True)
        super().accept()
