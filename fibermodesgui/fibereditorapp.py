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

import sys
from PyQt4 import QtCore, QtGui

from fibermodesgui.fibereditor.mainwindow import FiberEditor


def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName('UTF-8'))
    app.setApplicationName('Fiber Editor')

    win = FiberEditor()
    if len(sys.argv) > 1:
        win.actionOpen(sys.argv[1])
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
