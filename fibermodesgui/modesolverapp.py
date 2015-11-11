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

# TODO:
# Keep legend position when update plot
# Save results
# Save selection
# Save window position / size
# Save sorting order
# Save modes checked
# Color column
# Two vertical scales
# Debug: plot cutoff eq
# Use dock instead of splitter
