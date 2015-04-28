#!/usr/bin/env python3

import sys
from PySide import QtGui

from modesolver.mainwindow import ModeSolver


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Fiber Editor')

    win = ModeSolver()
    win.show()

    sys.exit(app.exec_())
