
from PySide import QtGui, QtCore
from fibermodesgui.widgets import AppWindow, SLRCWidget
from .solverdocument import SolverDocument
from .fiberselector import FiberSelector
from .fiberslider import FiberSlider
from .wavelengthslider import WavelengthSlider
from .modetable import ModeTable


class ModeSolver(AppWindow):

    PARAMETERS = ("cutoff", "neff", "ng", "D", "S")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.doc = SolverDocument(self)

        self.setWindowTitle(self.tr("Mode Solver"))
        self._initLayout()

        actions = {
            'save': (
                self.tr("&Save results"),
                QtGui.QIcon.fromTheme('document-save'),
                QtGui.QKeySequence.Save,
                self.save),
            'quit': (
                self.tr("&Quit"),
                QtGui.QIcon.fromTheme('application-exit'),
                QtGui.QKeySequence.Quit,
                self.close
            ),
            'new': (
                self.tr("&New fiber file"),
                QtGui.QIcon.fromTheme('document-new'),
                QtGui.QKeySequence.New,
                self.fiberSelector.editFiber
            ),
            'open': (
                self.tr("&Load fiber file"),
                QtGui.QIcon.fromTheme('document-open'),
                QtGui.QKeySequence.Open,
                self.fiberSelector.chooseFiber
            ),
            'edit': (
                self.tr("&Edit fiber"),
                None,
                [],
                self.fiberSelector.editFiber
            ),
            'info': (
                self.tr("&Fiber properties"),
                QtGui.QIcon.fromTheme('document-properties'),
                [QtGui.QKeySequence("Ctrl+I")],
                self.fiberSelector.fiberProperties
            ),
        }

        menus = [
            (
                self.tr("&File"), [
                    'save',
                    '-',
                    'quit'
                ]
            ),
            (
                self.tr("Fibe&r"), [
                    'new',
                    'open',
                    '-',
                    'edit',
                    'info',
                ]
            )
        ]

        toolbars = [
            ['save']
        ]

        self.initActions(actions)
        self.initMenubars(self.menuBar(), menus)
        self.initToolbars(toolbars)

        self.actions['edit'].setEnabled(False)
        self.actions['info'].setEnabled(False)
        self.wavelengthInput.setValue(1550e-9)
        self.setDirty(False)

    def _initLayout(self):
        self.countLabel = QtGui.QLabel()
        self.countLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.countLabel)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(self._parametersFrame())
        splitter.addWidget(self._modesFrame())
        splitter.addWidget(QtGui.QFrame())
        self.setCentralWidget(splitter)

    def _parametersFrame(self):
        self.fiberSelector = FiberSelector(self.doc)
        self.fiberSelector.fileLoaded.connect(self.updateFiber)
        self.fiberSelector.fiberEdited.connect(self.updateFiber)

        self.wavelengthInput = SLRCWidget()
        self.wavelengthInput.setSuffix(" nm")
        self.wavelengthInput.setScaleFactor(1e9)
        self.wavelengthInput.setRange(500, 3000)
        self.wavelengthInput.setSingleStep(1)
        self.wavelengthInput.valueChanged.connect(self.updateWavelengths)

        self.modeSelector = QtGui.QComboBox()
        self.modeSelector.addItems(['vector', 'scalar', 'both'])
        self.modeSelector.currentIndexChanged.connect(self.setMode)

        formLayout = QtGui.QFormLayout()
        formLayout.addRow(
            QtGui.QLabel(self.tr("Wavelength")),
            self.wavelengthInput)
        formLayout.addRow(
            QtGui.QLabel(self.tr("Modes")),
            self.modeSelector)

        self.ellMaxInput = QtGui.QSpinBox()
        self.ellMaxInput.valueChanged.connect(self.setMaxEll)
        self.mMaxInput = QtGui.QSpinBox()
        self.mMaxInput.setRange(1, 100)
        self.mMaxInput.valueChanged.connect(self.setMaxM)

        simParamFormLayout = QtGui.QHBoxLayout()
        simParamFormLayout.addWidget(
            QtGui.QLabel(self.tr("l max")), 0, QtCore.Qt.AlignRight)
        simParamFormLayout.addWidget(self.ellMaxInput)
        simParamFormLayout.addWidget(
            QtGui.QLabel(self.tr("m max")), 0, QtCore.Qt.AlignRight)
        simParamFormLayout.addWidget(self.mMaxInput)

        simParamLayout = QtGui.QVBoxLayout()
        simParamLayout.addLayout(simParamFormLayout)

        self.simParamBoxes = {}
        for param in self.PARAMETERS:
            box = QtGui.QCheckBox(self.tr("Find {}").format(param))
            box.toggled.connect(self.updateParams)
            simParamLayout.addWidget(box)
            self.simParamBoxes[param] = box

        simParamsGroup = QtGui.QGroupBox(self.tr("Simulation Parameters"))
        simParamsGroup.setLayout(simParamLayout)

        topLayout = QtGui.QVBoxLayout()
        topLayout.addWidget(QtGui.QLabel(self.tr("Fiber")))
        topLayout.addWidget(self.fiberSelector)
        topLayout.addLayout(formLayout)
        topLayout.addWidget(simParamsGroup)

        topFrame = QtGui.QFrame()
        topFrame.setLayout(topLayout)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(topFrame)

        return splitter

    def _modesFrame(self):
        self.modeTable = ModeTable(self.doc)

        self.fiberSlider = FiberSlider()
        self.fiberSlider.valueChanged.connect(self.modeTable.setFiber)

        self.wavelengthSlider = WavelengthSlider()
        self.wavelengthSlider.valueChanged.connect(self.setWavelength)

        layout1 = QtGui.QHBoxLayout()
        layout1.addWidget(self.fiberSlider)
        layout1.addWidget(self.wavelengthSlider)

        layout2 = QtGui.QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.modeTable)

        frame = QtGui.QFrame()
        frame.setLayout(layout2)

        return frame

    def setDirty(self, df):
        if self.doc.factory is None:
            self.actions['save'].setEnabled(False)
        else:
            self.actions['save'].setEnabled(df)
        super().setDirty(df)

    def _updateFiberCount(self):
        nf = self.doc.numfibers
        nw = len(self.doc.wavelengths)
        self.countLabel.setText(
            self.tr("{} F x {} W = {}").format(
                nf, nw, nf*nw))

    def updateFiber(self):
        """New fiber loaded, or fiber modified."""
        self.actions['new'].setEnabled(False)
        self.actions['edit'].setEnabled(True)
        self.actions['info'].setEnabled(True)
        self.doc.load()
        self.fiberSelector.updateFiberName()
        self.fiberSlider.setNum(self.doc.numfibers)
        self.setDirty(True)
        self._updateFiberCount()
        self.statusBar().showMessage(self.tr("Fiber factory loaded"), 5000)

    def updateWavelengths(self):
        wl = self.wavelengthInput()
        try:
            wl = [float(wl)]
        except TypeError:
            pass
        self.doc.wavelengths = wl
        self.wavelengthSlider.setNum(len(wl))
        self.setWavelength(self.wavelengthSlider.value())
        self._updateFiberCount()
        self.setDirty(True)

    def setMode(self, index):
        self.doc.modeKind = self.modeSelector.currentText()

    def setMaxEll(self, value):
        self.doc.maxell = value

    def setMaxM(self, value):
        self.doc.maxm = value

    def setWavelength(self, value):
        if 0 <= value - 1 < len(self.doc.wavelengths):
            wl = self.doc.wavelengths[value-1]
            self.wavelengthSlider.wlLabel.setText(
                "{:.5f} nm".format(wl))
            self.modeTable.setWavelength(wl)

    def updateParams(self, checked):
        self.doc.params = []
        for p in self.PARAMETERS:
            if self.simParamBoxes[p].isChecked():
                self.doc.params.append(p)
        self.modeTable.updateParams()
        self.startSolving()

    def startSolving(self):
        self.doc.start()

    def stopSolving(self):
        self.doc.terminate()

    def solvingEnded(self):
        pass
