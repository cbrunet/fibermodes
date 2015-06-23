
from PySide import QtGui, QtCore
import os


class AppWindow(QtGui.QMainWindow):

    closed = QtCore.Signal()
    saved = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.iconPath = os.path.realpath(os.path.dirname(__file__) +
                                         '/../icons')
        themePaths = QtGui.QIcon.themeSearchPaths()
        themePaths.append(self.iconPath)
        QtGui.QIcon.setThemeSearchPaths(themePaths)
        if not QtGui.QIcon.themeName():
            QtGui.QIcon.setThemeName("tango")

        self.statusBar()

        self.setDocumentName("")
        self._dir = os.getcwd()

    def getIcon(self, iconName):
        icon = QtGui.QIcon.fromTheme(iconName)
        if icon.isNull():
            for subfolder in ("actions", "emblems"):
                for folder in ("16x16", "22x22", "32x32"):
                    filePath = "{}/tango/{}/{}/{}.png".format(
                        self.iconPath, folder, subfolder, iconName)
                if os.path.isfile(filePath):
                    icon.addFile(filePath)
            filePath = "{}/tango/scalable/{}/{}.svg".format(
                    self.iconPath, subfolder, iconName)
            if os.path.isfile(filePath):
                icon.addFile(filePath)
        return icon

    def initActions(self, actions):
        self.actions = {}
        for key, (name, icon, keys, action) in actions.items():
            if icon is None:
                self.actions[key] = QtGui.QAction(name, self)
            else:
                self.actions[key] = QtGui.QAction(
                    self.getIcon(icon), name, self)
            if keys:
                self.actions[key].setShortcuts(keys)
            self.actions[key].triggered.connect(action)

    def initMenubars(self, menubar, menus):
        for name, items in menus:
            menu = menubar.addMenu(name)
            for menuitem in items:
                if isinstance(menuitem, tuple):
                    self.initMenubars(menu, menuitem)
                elif menuitem == '-':
                    menu.addSeparator()
                else:
                    menu.addAction(self.actions[menuitem])

    def initToolbars(self, toolbars):
        for toolbar in toolbars:
            tb = QtGui.QToolBar(self)
            for item in toolbar:
                if item == '-':
                    tb.addSeparator()
                else:
                    tb.addAction(self.actions[item])
            self.addToolBar(tb)

    def setDocumentName(self, name):
        self._documentName = name

    def documentName(self):
        return self._documentName

    def setDirty(self, df=True):
        self._dirty = df

    def dirty(self):
        return self._dirty

    def save(self):
        self.saved.emit(self._documentName)

    def closeEvent(self, event):
        if self._closeDocument():
            event.accept()
            self.closed.emit()
        else:
            event.ignore()

    def _closeDocument(self):
        if self.dirty():
            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr("The document has been modified."))
            msgBox.setInformativeText(
                self.tr("Do you want to save your changes?"))
            msgBox.setStandardButtons(QtGui.QMessageBox.Save |
                                      QtGui.QMessageBox.Discard |
                                      QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Save)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.Save:
                # Save was clicked
                self.save()
            elif ret == QtGui.QMessageBox.Discard:
                # Don't save was clicked
                return True
            elif ret == QtGui.QMessageBox.Cancel:
                # cancel was clicked
                return False
        return True
