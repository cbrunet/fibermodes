#!/usr/bin/env python3

# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

"""Executable script, for the fiber mode solver application.

This is the Python script you should invoke to start the simulator
user interface.
"""

import sys
from PySide import QtCore, QtGui

from modesolver.mainwindow import ModeSolver


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName('UTF-8'))
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
# Select / unselect all / he / eh / te / tm / lp
