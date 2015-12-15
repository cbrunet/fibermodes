from PyQt4 import QtGui, QtCore
from fibermodes import Mode
from fibermodes.field import Field
from fibermodesgui import blockSignals
from fibermodesgui.widgets import AppWindow
from .plotoptions import PlotOptions
import pyqtgraph as pg
import numpy


class FieldVisualizer(AppWindow):

    # TODO: cache field objects. Recompute fields only when needed:
    # - np changed
    # - r changed
    # - (phase, oriendation, amplitude): compute only image

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Field Visualizer"))

        self.doc = parent.doc
        self.fiber = parent.doc.simulator.fibers[
            parent.fiberSlider.fiberInput.value()-1]
        self.wl = parent.doc.simulator.wavelengths[
            parent.wavelengthSlider.wavelengthInput.value()-1]

        actions = {
            'options': (
                self.tr("Show/Hide Plot &Options"),
                'document-properties',
                [QtGui.QKeySequence("F4")],
                self.toggleOptions
            )
        }

        menus = [
            (
                self.tr("&Window"), [
                    'options'
                ]
            ),
        ]

        toolbars = [
            ['options']
        ]

        self.initActions(actions)
        self.initMenubars(self.menuBar(), menus)
        self.initToolbars(toolbars)

        self.actions['options'].setCheckable(True)
        self.actions['options'].setChecked(True)

        self.options = PlotOptions(self)
        self.options.hidden.connect(self.actions['options'].toggle)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.options)

        self.options.plotLayers.toggled.connect(self.plotLayers)
        self.options.cm.sigGradientChanged.connect(self.setImageColor)
        self.options.field.currentIndexChanged.connect(self.updatePlot)
        self.options.np.valueChanged.connect(self.updatePlot)
        self.options.radius.valueChanged.connect(self.updatePlot)

        self.modes = [[Mode("HE", 1, 1), 0, 0, 1]]

        self.__layers = None
        self.__quiver = []
        self.initFields()

        self.graph = pg.PlotWidget()
        self.image = pg.ImageItem()
        self.graph.addItem(self.image)
        self.graph.setAspectLocked(True)
        self.graph.sigRangeChanged.connect(self.updateRange)

        self.setCentralWidget(self.graph)
        self.updatePlot()

    def toggleOptions(self):
        if self.actions['options'].isChecked():
            self.options.show()
        else:
            with blockSignals(self.options):
                self.options.hide()

    def setModes(self, modes):
        self.modes = modes
        self.updatePlot()

    def initFields(self):
        self.__field = {f: None for f in Field.FTYPES}

    def computeFields(self, reset=False, **kwargs):
        if reset:
            self.initFields()

        np = self.options.np.value()
        r = self.options.radius.value() * 1e-6
        for f in Field.FTYPES:
            if kwargs.get(f, False):
                if self.__field[f] is None:
                    self.__field[f] = numpy.zeros((np, np))
                else:
                    kwargs.pop(f)  # Do not recompute if already computed

        for m, p, t, a in self.modes:
            field = self.fiber.field(m, self.wl, r, np)
            for f in Field.FTYPES:
                if kwargs.get(f, False):
                    self.__field[f] += getattr(field, f)(p, t) * a

    def plotLayers(self, state):
        if self.__layers is None:
            vr = self.graph.viewRect()
            r = self.fiber.innerRadius(1)
            pen = pg.mkPen(color=(255, 255, 255, 255),
                           style=QtCore.Qt.DotLine,
                           width=1)
            self.__layers = self.graph.scene().addEllipse(
                -r, -r, 2*r, 2*r, pen=pen)
            self.graph.addItem(self.__layers)

            for i, _ in enumerate(self.fiber.layers[2:], 2):
                r = self.fiber.innerRadius(i)
                c = self.graph.scene().addEllipse(-r, -r, 2*r, 2*r, pen=pen)
                c.setParentItem(self.__layers)
            self.graph.setRange(rect=vr)
        self.__layers.setVisible(state)

    def setImageColor(self):
        self.image.setLookupTable(self.options.cm.getLookupTable(100))

    def updatePlot(self):
        # sbr = self.image.sceneBoundingRect()
        # self.np = int(max(sbr.width(), sbr.height()))

        # else:
        #     vr = self.graph.viewRect()
        #     print(vr)
        #     self.r = max(abs(vr.top()), abs(vr.bottom()),
        #                  abs(vr.left()), abs(vr.right()))

        fname = self.options.field.currentText()
        self.computeFields(reset=True, **{fname: True})
        self.image.setImage(self.__field[fname])
        self.setImageColor()
        r = self.options.radius.value() * 1e-6
        self.image.setRect(QtCore.QRectF(-r, -r, 2*r, 2*r))

        self.computeFields(Emod=True, Epol=True)
        self.options.quiver.updateFields(self.__field['Emod'],
                                         self.__field['Epol'])

    def updateRange(self, view, rgn):
        pass
        print()
        print("view", view.viewRect())
        print("rgn", rgn)
        print("graph", self.graph.viewRect())
        print("image", self.image.viewRect())
        print("image bound", self.image.boundingRect())
        print("scene bounding rect", self.image.sceneBoundingRect())
        print("pixel size", self.image.pixelSize())

    def hideEvent(self, event):
        self.options.hide()
        return super().hideEvent(event)
