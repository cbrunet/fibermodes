#!/usr/bin/env python3

import sys
from PySide import QtGui

from fibereditor.mainwindow import FiberEditor


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Fiber Editor')

    win = FiberEditor()
    if len(sys.argv) > 1:
        win.actionOpen(sys.argv[1])
    win.show()

    sys.exit(app.exec_())
