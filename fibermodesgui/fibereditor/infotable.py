from PyQt4 import QtGui, QtCore


class FiberInfoTable(QtGui.QTableWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRowCount(5)
        self.setVerticalHeaderLabels([
            self.tr("Inner radius"),
            self.tr("Outer radius"),
            self.tr("Thickness"),
            self.tr("Min index"),
            self.tr("Max index")])

    def updateInfo(self, fiber, wl):
        self.clearContents()
        nl = len(fiber)
        self.setColumnCount(nl)

        labels = []
        for i in range(nl):
            labels.append(fiber.name(i))

            # Inner radius
            item = QtGui.QTableWidgetItem()
            r1 = fiber.innerRadius(i)
            item.setText("{:.5f} µm".format(r1 * 1e6))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.setItem(0, i, item)

            # Outer radius
            item = QtGui.QTableWidgetItem()
            r2 = fiber.outerRadius(i)
            if r2 < float("inf"):
                item.setText("{:.5f} µm".format(r2 * 1e6))
                item.setTextAlignment(QtCore.Qt.AlignRight)
            else:
                item.setText("∞")
                item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(1, i, item)

            # Thickness
            item = QtGui.QTableWidgetItem()
            rt = fiber.thickness(i)
            if rt < float("inf"):
                item.setText("{:.5f} µm".format(rt * 1e6))
                item.setTextAlignment(QtCore.Qt.AlignRight)
            else:
                item.setText("∞")
                item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(2, i, item)

            # Min index
            item = QtGui.QTableWidgetItem()
            mii = fiber.minIndex(i, wl)
            item.setText("{:.5f}".format(mii))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.setItem(3, i, item)

            # Max index
            item = QtGui.QTableWidgetItem()
            mai = fiber.maxIndex(i, wl)
            item.setText("{:.5f}".format(mai))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.setItem(4, i, item)

        self.setHorizontalHeaderLabels(labels)
