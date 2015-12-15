from PyQt4 import QtGui, QtCore
from fibermodesgui import blockSignals


class ComboItemDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, items=None, values=None,
                 role=QtCore.Qt.DisplayRole):
        super().__init__(parent)
        self._items = items
        self._values = values
        self._role = role

    def createEditor(self, parent, option, index):
        if self._items:
            combo = QtGui.QComboBox(parent)
            combo.addItems(self._items)
            combo.currentIndexChanged.connect(self.currentIndexChanged)
            return combo
        return None

    def setEditorData(self, editor, index):
        val = index.data(self._role)
        idx = self._values.index(val) if self._values else val
        with blockSignals(editor):
            editor.setCurrentIndex(idx)

    def currentIndexChanged(self, index):
        self.commitData.emit(self.sender())

    def setModelData(self, editor, model, index):
        idx = editor.currentIndex()
        val = self._values[idx] if self._values else idx
        model.setData(index, val, role=self._role)
