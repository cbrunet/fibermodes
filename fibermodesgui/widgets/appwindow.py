
from PyQt4 import QtGui, QtCore
import os
from functools import partial
import logging


class AppWindow(QtGui.QMainWindow):

    closed = QtCore.pyqtSignal()
    saved = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        logging.basicConfig()

        self._dirty = False
        self.actions = {}
        actions = {
            'capturewarnings': (
                self.tr("C&apture warnings"),
                None,
                [],
                None
            ),
            'loglevel': {
                'logcritical': (
                    self.tr("Critical"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.CRITICAL)
                ),
                'logerror': (
                    self.tr("Error"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.ERROR)
                ),
                'logwarning': (
                    self.tr("Warning"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.WARNING)
                ),
                'loginfo': (
                    self.tr("Info"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.INFO)
                ),
                'logdebug': (
                    self.tr("Debug"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.DEBUG)
                ),
                'lognotset': (
                    self.tr("Not set"),
                    None,
                    [],
                    partial(logging.root.setLevel, logging.NOTSET)
                ),
            }
        }
        self.initActions(actions)
        self.actions['capturewarnings'].setCheckable(True)
        self.actions['capturewarnings'].toggled.connect(
            logging.captureWarnings)
        self.actions['lognotset'].setChecked(True)
        self.logmenu = (
            self.tr("&Logging"), [
                'lognotset',
                'logdebug',
                'loginfo',
                'logwarning',
                'logerror',
                'logcritical',
                '-',
                'capturewarnings'
            ]
        )

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
        for key, actiondef in actions.items():
            if isinstance(actiondef, dict):
                self.actions[key] = QtGui.QActionGroup(self)
                for gkey, gactiondef in actiondef.items():
                    self.initAction(gkey, gactiondef, self.actions[key])
                    self.actions[gkey].setCheckable(True)
            else:
                self.initAction(key, actiondef, self)

    def initAction(self, key, actiondef, parent):
        name, icon, keys, action = actiondef
        if icon is None:
            self.actions[key] = QtGui.QAction(name, parent)
        else:
            self.actions[key] = QtGui.QAction(
                self.getIcon(icon), name, parent)
        if keys:
            self.actions[key].setShortcuts(keys)
        if action:
            self.actions[key].triggered.connect(action)

    def initMenubars(self, menubar, menus):
        """Create the menu bar.

        :param menubar: instance of QMenuBar
        :param menus: list of tuple. Each tuple contains: name of menu, and
                      list of action names.

        """
        for name, items in menus:
            self.initMenu(menubar, name, items)

    def initMenu(self, menubar, name, items):
        """Add a menu or a submenu to the menu bar.

        :param menubar: instance of QMenuBar or QMenu
        :param name: name of menu
        :param items: list of action names, or '-' for separator,
                      or tuple with name of submenu and items of submenu.

        """
        menu = menubar.addMenu(name)
        for menuitem in items:
            if isinstance(menuitem, tuple):
                self.initMenu(menu, menuitem[0], menuitem[1])
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
