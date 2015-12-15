
from PyQt4 import QtGui, QtCore
import os
from datetime import datetime
from string import Template
from fibermodesgui.fibereditor.mainwindow import FiberEditor


class FiberSelector(QtGui.QFrame):

    fileLoaded = QtCore.pyqtSignal()
    fiberEdited = QtCore.pyqtSignal()

    def __init__(self, doc, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._doc = doc
        self._editWin = None

        self.fiberName = QtGui.QLabel(self.tr("<i>Select fiber...</i>"))
        self.fiberName.setTextFormat(QtCore.Qt.RichText)

        self.chooseButton = QtGui.QPushButton(
            parent.getIcon('document-open'),
            self.tr("Choose"))
        self.chooseButton.clicked.connect(self.chooseFiber)

        self.editButton = QtGui.QPushButton(parent.getIcon('document-new'),
                                            self.tr("New"))
        self.editButton.clicked.connect(self.editFiber)

        self.propButton = QtGui.QPushButton(
            parent.getIcon('info'),
            "")
        self.propButton.setEnabled(False)
        self.propButton.clicked.connect(self.fiberProperties)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.fiberName)
        layout.addWidget(self.chooseButton)
        layout.addWidget(self.editButton)
        layout.addWidget(self.propButton)
        self.setLayout(layout)

        self.editIcon = parent.getIcon('pen')

    def updateFiberName(self):
        name = self._doc.factory.name
        if not name:
            name = os.path.basename(self._doc.filename)
        self.fiberName.setText(name)
        self.editButton.setText(self.tr("Edit"))
        self.editButton.setIcon(self.editIcon)
        self.propButton.setEnabled(True)

    def chooseFiber(self):
        dirname = (os.path.dirname(self._doc.filename)
                   if self._doc.filename
                   else os.getcwd())

        openDialog = QtGui.QFileDialog()
        openDialog.setWindowTitle(self.tr("Open fiber..."))
        openDialog.setDirectory(dirname)
        openDialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        openDialog.setNameFilter(self.tr("Fibers (*.fiber)"))
        if openDialog.exec_() == QtGui.QFileDialog.Accepted:
            self._doc.filename = openDialog.selectedFiles()[0]
            self.fileLoaded.emit()

    def editFiber(self):
        if self._editWin is None:
            self._editWin = FiberEditor(self)
            self._editWin.closed.connect(self.editorClosed)
            if self._doc.filename:
                self._editWin.actionOpen(self._doc.filename)
            # self._editWin.setWindowModality(QtCore.Qt.WindowModal)
            self._editWin.saved.connect(self.updateFiber)
        self._editWin.show()
        self._editWin.raise_()

    def updateFiber(self, filename):
        self._doc.filename = filename
        self.fiberEdited.emit()

    def fiberProperties(self):
        propTemplate = Template(self.tr("""<table>
<tr><th align="right">Filename: </th><td>$filename</td></tr>
<tr><th align="right">Name: </th><td>$name</td></tr>
<tr><th align="right">Author: </th><td>$author</td></tr>
<tr><th align="right">Creation date: </th><td>$crdate</td></tr>
<tr><th align="right">Modification date: </th><td>$tstamp</td></tr>
<tr><th align="right">Description: </th><td>$description</td></tr>
</table>
""")).substitute(filename=os.path.relpath(self._doc.filename),
                 name=self._doc.factory.name,
                 author=self._doc.factory.author,
                 crdate=datetime.fromtimestamp(
                    self._doc.factory.crdate).strftime('%Y-%m-%d %H:%M:%S'),
                 tstamp=datetime.fromtimestamp(
                    self._doc.factory.tstamp).strftime('%Y-%m-%d %H:%M:%S'),
                 description=self._doc.factory.description)

        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle(self.tr("Fiber Properties"))
        msgBox.setText(propTemplate)
        msgBox.exec_()

    def editorClosed(self):
        self._editWin = None
