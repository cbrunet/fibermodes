
from PySide import QtGui


class FiberEditor(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Fiber Editor"))

        actions = {
            'new': (
                self.tr("&New"),
                QtGui.QIcon.fromTheme('document-new'),
                QtGui.QKeySequence.New,
                self.actionNew
            ),
            'quit': (
                self.tr("&Quit"),
                QtGui.QIcon.fromTheme('application-exit'),
                QtGui.QKeySequence.Quit,
                self.actionQuit
            ),
            'info': (
                self.tr("&Fiber properties"),
                QtGui.QIcon.fromTheme('document-properties'),
                [QtGui.QKeySequence("Ctrl+I")],
                self.actionInfo
            ),
            'add': (
                self.tr("&Add layer"),
                QtGui.QIcon.fromTheme('list-add'),
                [QtGui.QKeySequence("Ctrl+Shift++")],
                self.actionAddLayer
            ),
            'remove': (
                self.tr("&Remove layer"),
                QtGui.QIcon.fromTheme('list-remove'),
                [QtGui.QKeySequence("Ctrl+-")],
                self.actionRemoveLayer
            ),
        }

        menus = [
            (
                self.tr("&File"), [
                    'new',
                    '-',
                    'quit'
                ]
            ),
            (
                self.tr("Fibe&r"), [
                    'info',
                    '-',
                    'add',
                    'remove'
                ]
            )
        ]

        self._initActions(actions)
        self._initMenubars(self.menuBar(), menus)
        self._initLayout()

    def actionNew(self):
        print('New!')

    def actionQuit(self):
        self.close()

    def actionInfo(self):
        pass

    def actionAddLayer(self):
        pass

    def actionRemoveLayer(self):
        pass

    def _initActions(self, actions):
        self.actions = {}
        for key, (name, icon, keys, action) in actions.items():
            self.actions[key] = QtGui.QAction(icon, name, self)
            if keys:
                self.actions[key].setShortcuts(keys)
            self.actions[key].triggered.connect(action)

    def _initMenubars(self, menubar, menus):
        for name, items in menus:
            menu = menubar.addMenu(name)
            for menuitem in items:
                if isinstance(menuitem, tuple):
                    self._initMenubars(menu, menuitem)
                elif menuitem == '-':
                    menu.addSeparator()
                else:
                    menu.addAction(self.actions[menuitem])

    def _initLayout(self):
        layerList = QtGui.QListView()

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(layerList)

        self.setCentralWidget(splitter)

