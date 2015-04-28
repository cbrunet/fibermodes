from PySide import QtGui, QtCore
from decimal import Decimal


class SLRC(QtGui.QFrame):

    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None, f=0):
        super().__init__(parent, f)

        self._initTypeButton()
        self._initScalarControl()
        self._initListControl()
        self._initRangeControl()
        self._initCodeControl()

        self.innerLayout = QtGui.QHBoxLayout()

        layout = QtGui.QHBoxLayout()
        layout.addLayout(self.innerLayout)
        layout.addWidget(self.typeButton)
        self.setLayout(layout)

        self._type = -1
        self._scale = 1
        self._list = []
        self._code = "return 0"
        self.setScalarLayout()  # default type: scalar
        self.setDecimals(5)

    def _initTypeButton(self):
        self.scalarAction = QtGui.QAction("scalar", self)
        self.scalarAction.triggered.connect(self.setScalarLayout)
        self.listAction = QtGui.QAction("list", self)
        self.listAction.triggered.connect(self.setListLayout)
        self.rangeAction = QtGui.QAction("range", self)
        self.rangeAction.triggered.connect(self.setRangeLayout)
        self.codeAction = QtGui.QAction("code", self)
        self.codeAction.triggered.connect(self.setCodeLayout)

        self.typeMenu = QtGui.QMenu()
        self.typeMenu.addAction(self.scalarAction)
        self.typeMenu.addAction(self.listAction)
        self.typeMenu.addAction(self.rangeAction)
        self.typeMenu.addAction(self.codeAction)

        self.typeButton = QtGui.QToolButton()
        self.typeButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.typeButton.setMenu(self.typeMenu)

    def _setType(self, typenum):
        if typenum == self._type:
            return

        # convert values
        if self._type == 0:
            if typenum == 1:  # scalar to list
                self._list = [self.value()]
            elif typenum == 2:  # scalar to range
                self.rstartInput.setValue(self.value())
                v = self.value() * 10
                self.rendInput.setValue(v if v else 1)
        elif self._type == 1:
            if len(self._list) > 0:
                if typenum == 0:  # list to scalar
                    self.numberInput.setValue(self._list[0])
                elif typenum == 2:  # list to range
                    self.rstartInput.setValue(self._list[0])
                    self.rendInput.setValue(self._list[-1])
                    if len(self._list) >= 2:
                        self.rnumInput.setValue(len(self._list))
        elif self._type == 2:
            if typenum == 0:  # range to scalar
                self.numberInput.setValue(self.rstartInput.value())
            elif typenum == 1:  # range to list
                n = self.rnumInput.value()
                if n > 100:
                    n = 100
                low = self.rstartInput.value()
                high = self.rendInput.value()
                self._list = [low + x*(high-low)/(n-1) for x in range(n)]

        self._type = typenum
        while self.innerLayout.count():  # remove layout items
            layoutItem = self.innerLayout.takeAt(0)
            layoutItem.widget().setParent(None)

        self._emitValueChanged()

    def _initScalarControl(self):
        self.numberInput = QtGui.QDoubleSpinBox()
        self.numberInput.valueChanged.connect(self._emitValueChanged)

    def setScalarLayout(self):
        self._setType(0)
        self.innerLayout.addWidget(self.numberInput)

    def _initListControl(self):
        self.listLabel = QtGui.QLabel()
        self.listButton = QtGui.QPushButton(self.tr("Edit"))
        self.listButton.clicked.connect(self.editList)

    def setListLayout(self):
        self._setType(1)
        self.innerLayout.addWidget(self.listLabel)
        self.innerLayout.addWidget(self.listButton)
        self._updateListCount()

    def _updateListCount(self):
        nitemstext = "{} items" if len(self._list) > 1 else "{} item"
        self.listLabel.setText(self.tr(nitemstext).format(len(self._list)))

    def editList(self):
        ledialog = ListEditor(self._list.copy())
        ret = ledialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            if self._list != ledialog.numlist:
                self._list = ledialog.numlist
                self._updateListCount()
                self._emitValueChanged()

    def _initRangeControl(self):
        self.rstartInput = QtGui.QDoubleSpinBox()
        self.rstartInput.valueChanged.connect(self._emitValueChanged)
        self.rendInput = QtGui.QDoubleSpinBox()
        self.rendInput.valueChanged.connect(self._emitValueChanged)
        self.rnumInput = QtGui.QSpinBox()
        self.rnumInput.setValue(10)
        self.rnumInput.setRange(2, 32000)
        self.rnumInput.valueChanged.connect(self._emitValueChanged)

    def setRangeLayout(self):
        self._setType(2)
        self.innerLayout.addWidget(self.rstartInput)
        self.innerLayout.addWidget(self.rendInput)
        self.innerLayout.addWidget(self.rnumInput)

    def _initCodeControl(self):
        self.codeButton = QtGui.QPushButton(self.tr("Edit code"))
        self.codeButton.clicked.connect(self.editCode)

    def setCodeLayout(self):
        self._setType(3)
        self.innerLayout.addWidget(self.codeButton)

    def editCode(self):
        cedialog = CodeEditor(self._code)
        ret = cedialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            if self._code != cedialog.code:
                self._code = cedialog.code
                self._emitValueChanged()

    def _emitValueChanged(self):
        self.valueChanged.emit(self.value())

    def setValue(self, value):
        if isinstance(value, list):
            self._list = [v * self._scale for v in value]
            self.setListLayout()
        elif isinstance(value, dict):
            self.rstartInput.setValue(value["start"] * self._scale)
            self.rendInput.setValue(value["end"] * self._scale)
            self.rnumInput.setValue(value["num"])
            self.setRangeLayout()
        else:
            try:
                value = float(value) * self._scale
                self.numberInput.setValue(value)
                self.setScalarLayout()
            except ValueError:
                self._code = value
                self.setCodeLayout()

    def value(self):
        if self._type == 0:
            return self.numberInput.value() / self._scale
        elif self._type == 1:
            return [v / self._scale for v in self._list]
        elif self._type == 2:
            return {'start': self.rstartInput.value() / self._scale,
                    'end': self.rendInput.value() / self._scale,
                    'num': self.rnumInput.value()}
        else:
            return self._code

    def setSuffix(self, suffix):
        self.numberInput.setSuffix(suffix)
        self.rstartInput.setSuffix(suffix)
        self.rendInput.setSuffix(suffix)

    def setDecimals(self, prec):
        self.numberInput.setDecimals(prec)
        self.rstartInput.setDecimals(prec)
        self.rendInput.setDecimals(prec)

    def setRange(self, vmin, vmax):
        self.setMinimum(vmin)
        self.setMaximum(vmax)

    def setMinimum(self, vmin):
        self.numberInput.setMinimum(vmin)
        self.rstartInput.setMinimum(vmin)
        self.rendInput.setMinimum(vmin)

    def setMaximum(self, vmax):
        self.numberInput.setMaximum(vmax)
        self.rstartInput.setMaximum(vmax)
        self.rendInput.setMaximum(vmax)

    def setSingleStep(self, val):
        self.numberInput.setSingleStep(val)
        self.rstartInput.setSingleStep(val)
        self.rendInput.setSingleStep(val)

    def setScaleFactor(self, scale):
        self._scale = scale


class ListEditor(QtGui.QDialog):

    def __init__(self, numlist, parent=None, f=0):
        super().__init__(parent, f)
        self.numlist = numlist
        self.setWindowTitle(self.tr("List Editor"))

        self.numbersList = QtGui.QListWidget()
        for n in self.numlist:
            item = QtGui.QListWidgetItem(str(n))
            item.setFlags(QtCore.Qt.ItemIsSelectable |
                          QtCore.Qt.ItemIsEditable |
                          QtCore.Qt.ItemIsEnabled)
            self.numbersList.addItem(item)
        self.numbersList.setCurrentRow(0)
        self.numbersList.setEditTriggers(
            QtGui.QAbstractItemView.AllEditTriggers)
        self.numbersList.itemChanged.connect(self.itemChanged)

        buttonAdd = QtGui.QPushButton(
            QtGui.QIcon.fromTheme('list-add'), "")
        buttonAdd.clicked.connect(self.addItem)
        buttonEdit = QtGui.QPushButton(self.tr("&Edit"))
        buttonEdit.clicked.connect(self.editItem)
        self.buttonRemove = QtGui.QPushButton(
            QtGui.QIcon.fromTheme('list-remove'), "")
        if len(self.numlist) == 1:
            self.buttonRemove.setEnabled(False)
        self.buttonRemove.clicked.connect(self.removeItem)
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                           QtGui.QDialogButtonBox.Cancel)
        buttonBox.addButton(buttonAdd,
                            QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(buttonEdit,
                            QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.buttonRemove,
                            QtGui.QDialogButtonBox.ActionRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.numbersList)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def addItem(self):
        item = QtGui.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable |
                      QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsEnabled)
        row = self.numbersList.currentRow()
        v1 = Decimal(self.numbersList.item(row).text())
        if row + 1 < self.numbersList.count():
            v2 = Decimal(self.numbersList.item(row+1).text())
            item.setText(str((v1 + v2)/2))
            self.numbersList.insertItem(row+1, item)
        elif self.numbersList.count() > 1:
            v2 = Decimal(self.numbersList.item(row-1).text())
            item.setText(str(v1 + (v1 - v2)))
            self.numbersList.addItem(item)
        else:
            item.setText(str(v1 + 1))
            self.numbersList.addItem(item)
        self.numlist.insert(row+1, float(item.text()))
        self.numbersList.setCurrentRow(row+1)
        self.buttonRemove.setEnabled(True)

    def editItem(self):
        item = self.numbersList.currentItem()
        self.numbersList.editItem(item)
        self.numbersList.sortItems()

    def removeItem(self):
        row = self.numbersList.currentRow()
        self.numbersList.takeItem(row)
        del self.numlist[row]
        if self.numbersList.count() == 1:
            self.buttonRemove.setEnabled(False)

    def itemChanged(self, item):
        row = self.numbersList.currentRow()
        try:
            item.setText(str(Decimal(item.text())))
            self.numlist[row] = float(item.text())
            self.numbersList.sortItems()
        except ValueError:
            item.setText(str(self.numlist[row]))


class CodeEditor(QtGui.QDialog):

    def __init__(self, code, parent=None, f=0):
        super().__init__(parent, f)
        self.code = code

        self.codeEditor = QtGui.QPlainTextEdit()
        fixedFont = QtGui.QFont("Monospace")
        fixedFont.setStyleHint(QtGui.QFont.TypeWriter)
        self.codeEditor.setFont(fixedFont)
        self.codeEditor.setPlainText(code)
        self.codeEditor.textChanged.connect(self.onTextChanged)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                           QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("def f(*params):"))
        layout.addWidget(self.codeEditor)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def onTextChanged(self):
        self.code = self.codeEditor.toPlainText()
