from PyQt4 import QtGui, QtCore
from decimal import Decimal
from fibermodes.slrc import SLRC
from fibermodesgui import blockSignals


class SLRCWidget(QtGui.QFrame, SLRC):

    valueChanged = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, f=QtCore.Qt.Widget):
        QtGui.QFrame.__init__(self, parent, f)
        SLRC.__init__(self)
        self.scale = 1.

        self.innerLayout = QtGui.QHBoxLayout()

        self._initTypeButton()
        layout = QtGui.QHBoxLayout()
        layout.addLayout(self.innerLayout)
        layout.addWidget(self.typeButton)
        self.setLayout(layout)

        self._initScalarControl()
        self._initListControl()
        self._initRangeControl()
        self._initCodeControl()

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

    def _setType(self, kind, check=True):
        if check and kind == self.kind:
            return False

        self.kind = kind

        while self.innerLayout.count():  # remove layout items
            layoutItem = self.innerLayout.takeAt(0)
            layoutItem.widget().setParent(None)

        self._emitValueChanged()
        return True

    def _initScalarControl(self):
        self.numberInput = QtGui.QDoubleSpinBox()
        self.numberInput.valueChanged.connect(self._updateScalarValue)
        self.innerLayout.addWidget(self.numberInput)
        self.numberInput.setValue(self._value * self.scale)

    def _updateScalarValue(self, value):
        self._value = value / self.scale
        self._emitValueChanged()

    def setScalarLayout(self, check=True):
        if self._setType('scalar', check):
            self.innerLayout.addWidget(self.numberInput)
        self.numberInput.setValue(self._value * self.scale)

    def _initListControl(self):
        self.listLabel = QtGui.QLabel()
        self.listButton = QtGui.QPushButton(self.tr("Edit"))
        self.listButton.clicked.connect(self.editList)

    def setListLayout(self, check=True):
        if self._setType('list', check):
            self.innerLayout.addWidget(self.listLabel)
            self.innerLayout.addWidget(self.listButton)
        self._updateListCount()

    def _updateListCount(self):
        nitemstext = "{} items" if len(self) > 1 else "{} item"
        self.listLabel.setText(self.tr(nitemstext).format(len(self)))

    def editList(self):
        oldvals = [v * self.scale for v in self._value]
        ledialog = ListEditor(oldvals.copy())
        ret = ledialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            if oldvals != ledialog.numlist:
                self._value = [v / self.scale for v in ledialog.numlist]
                self._updateListCount()
                self._emitValueChanged()

    def _initRangeControl(self):
        self.rstartInput = QtGui.QDoubleSpinBox()
        self.rstartInput.valueChanged.connect(self._updateRange)
        self.rendInput = QtGui.QDoubleSpinBox()
        self.rendInput.valueChanged.connect(self._updateRange)
        self.rnumInput = QtGui.QSpinBox()
        self.rnumInput.setValue(10)
        self.rnumInput.setRange(1, 32000)
        self.rnumInput.valueChanged.connect(self._updateRange)

    def _updateRange(self, value):
        if self.kind == 'range':
            self._value['start'] = self.rstartInput.value() / self.scale
            self._value['end'] = self.rendInput.value() / self.scale
            self._value['num'] = self.rnumInput.value()
            self._emitValueChanged()

    def setRangeLayout(self, check=True):
        if self._setType('range', check):
            self.innerLayout.addWidget(self.rstartInput)
            self.innerLayout.addWidget(self.rendInput)
            self.innerLayout.addWidget(self.rnumInput)
        with blockSignals(self.rstartInput):
            self.rstartInput.setValue(self._value['start'] * self.scale)
        with blockSignals(self.rendInput):
            self.rendInput.setValue(self._value['end'] * self.scale)
        with blockSignals(self.rnumInput):
            self.rnumInput.setValue(self._value['num'])

    def _initCodeControl(self):
        self.codeButton = QtGui.QPushButton(self.tr("Edit code"))
        self.codeButton.clicked.connect(self.editCode)

    def setCodeLayout(self, check=True):
        if self._setType('code', check):
            self.innerLayout.addWidget(self.codeButton)

    def editCode(self):
        cedialog = CodeEditor(self._value, self.codeParams)
        ret = cedialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            if self._value != cedialog.code:
                self._value = cedialog.code
                self._emitValueChanged()

    def _emitValueChanged(self):
        self.valueChanged.emit(self._value)

    @property
    def value(self):
        return SLRC.value.fget(self)

    @value.setter
    def value(self, value):
        self.setValue(value)

    def setValue(self, value):
        SLRC.value.fset(self, value)
        kind = self.kind

        if kind == 'scalar':
            self.setScalarLayout(False)
        elif kind == 'list':
            self.setListLayout(False)
        elif kind == 'range':
            self.setRangeLayout(False)
        elif kind == 'code':
            self.setCodeLayout(False)

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

    def setScaleFactor(self, value):
        self.scale = value


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

    def __init__(self, code, params, parent=None, f=0):
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

        paramstr = ", ".join(params) if params else "*params"

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("def f({}):".format(paramstr)))
        layout.addWidget(self.codeEditor)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def onTextChanged(self):
        self.code = self.codeEditor.toPlainText()
