
from PySide import QtGui, QtCore
from fibermodesgui.widgets import AppWindow, SLRCWidget
from .solverdocument import SolverDocument
from .fiberselector import FiberSelector
from .fiberslider import FiberSlider
from .wavelengthslider import WavelengthSlider
from .modetable import ModeTableView, ModeTableModel
from .plotframe import PlotFrame


def msToStr(ms, displayms=True):
    h = ms // 3600000
    ms -= h * 3600000
    m = ms // 60000
    ms -= m * 60000
    s = ms / 1000
    fmt = "{:d}:{:02d}:{:05.3f}" if displayms else "{:d}:{:02d}:{:02.0f}"
    return fmt.format(h, m, s)


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
            'start': (
                self.tr("&Run simulation"),
                QtGui.QIcon.fromTheme('media-playback-start'),
                [QtGui.QKeySequence("F5")],
                self.run_simulation
            ),
            'stop': (
                self.tr("&Stop simulation"),
                QtGui.QIcon.fromTheme('media-playback-stop'),
                [QtGui.QKeySequence("Ctrl+.")],
                self.stop_simulation
            ),
            'paramwin': (
                self.tr("&Parameters"),
                None,
                [QtGui.QKeySequence("F2")],
                self.togglePanes
            ),
            'tablewin': (
                self.tr("&Result table"),
                None,
                [QtGui.QKeySequence("F3")],
                self.togglePanes
            ),
            'graphwin': (
                self.tr("&Graph"),
                None,
                [QtGui.QKeySequence("F4")],
                self.togglePanes
            ),
            'fullscreen': (
                self.tr("&Fullscreen"),
                QtGui.QIcon.fromTheme('view-fullscreen'),
                [QtGui.QKeySequence("F11")],
                self.toggleFullscreen
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
            ),
            (
                self.tr("&Simulation"), [
                    'start',
                    'stop'
                ]
            ),
            (
                self.tr("&Window"), [
                    'paramwin',
                    'tablewin',
                    'graphwin',
                    '-',
                    'fullscreen',
                ]
            ),
        ]

        toolbars = [
            ['save'],
            ['start', 'stop'],
            ['paramwin', 'tablewin', 'graphwin'],
        ]

        self.initActions(actions)
        self.initMenubars(self.menuBar(), menus)
        self.initToolbars(toolbars)

        self.actions['edit'].setEnabled(False)
        self.actions['info'].setEnabled(False)
        self.actions['start'].setCheckable(True)
        self.actions['stop'].setCheckable(True)
        self.actions['stop'].setChecked(True)
        self.actions['stop'].setEnabled(False)
        self.actions['paramwin'].setCheckable(True)
        self.actions['paramwin'].setChecked(True)
        self.actions['tablewin'].setCheckable(True)
        self.actions['tablewin'].setChecked(True)
        self.actions['graphwin'].setCheckable(True)
        self.actions['graphwin'].setChecked(True)
        self.actions['fullscreen'].setCheckable(True)
        self.wavelengthInput.setValue(1550e-9)
        self.setDirty(False)
        self.closed.connect(self.doc.stop_thread)

    def _initLayout(self):
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setFormat("%v / %m (%p%)")
        self.statusBar().addWidget(self.progressBar, 1)

        self.timeLabel = QtGui.QLabel()
        self.timeLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.timeLabel)
        self.time = QtCore.QTime()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTime)

        self.countLabel = QtGui.QLabel(self.tr("No fiber"))
        self.countLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.countLabel)

        self.splitter = QtGui.QSplitter(self)
        self.splitter.addWidget(self._parametersFrame())
        self.splitter.addWidget(self._modesFrame())
        self.plotFrame = PlotFrame(self)
        self.splitter.addWidget(self.plotFrame)
        self.setCentralWidget(self.splitter)

        self.doc.computeStarted.connect(self.initProgressBar)
        self.doc.valueAvailable.connect(self.updateProgressBar)
        self.doc.computeFinished.connect(self.stopProgressBar)

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

        self.nuMaxInput = QtGui.QSpinBox()
        self.nuMaxInput.valueChanged.connect(self.setMaxNu)
        self.nuMaxInput.setRange(-1, 99)
        self.nuMaxInput.setSpecialValueText(" ")
        self.mMaxInput = QtGui.QSpinBox()
        self.mMaxInput.setRange(0, 100)
        self.mMaxInput.valueChanged.connect(self.setMaxM)
        self.mMaxInput.setSpecialValueText(" ")

        simParamFormLayout = QtGui.QHBoxLayout()
        simParamFormLayout.addWidget(
            QtGui.QLabel(self.tr("l max")), 0, QtCore.Qt.AlignRight)
        simParamFormLayout.addWidget(self.nuMaxInput)
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
        topLayout.addStretch(1)

        topFrame = QtGui.QFrame()
        topFrame.setLayout(topLayout)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(topFrame)

        return splitter

    def _modesFrame(self):
        self.modeTableModel = ModeTableModel(self.doc, self)
        modeTableProxy = QtGui.QSortFilterProxyModel(self)
        modeTableProxy.setSourceModel(self.modeTableModel)
        modeTableProxy.setSortRole(QtCore.Qt.ToolTipRole)
        modeTableProxy.setDynamicSortFilter(True)
        modeTableView = ModeTableView(modeTableProxy)
        self.modeTableModel.dataChanged.connect(
            modeTableView.resizeColumnsToContents)

        self.fiberSlider = FiberSlider()
        self.fiberSlider.valueChanged.connect(self.setFiber)

        self.wavelengthSlider = WavelengthSlider()
        self.wavelengthSlider.valueChanged.connect(self.setWavelength)

        layout1 = QtGui.QHBoxLayout()
        layout1.addWidget(self.fiberSlider)
        layout1.addWidget(self.wavelengthSlider)

        layout2 = QtGui.QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(modeTableView, stretch=1)

        frame = QtGui.QFrame()
        frame.setLayout(layout2)

        # Default values
        self.nuMaxInput.setValue(-1)
        self.mMaxInput.setValue(0)

        return frame

    def setDirty(self, df):
        if not self.doc.factory:
            self.actions['save'].setEnabled(False)
        else:
            self.actions['save'].setEnabled(df)
        super().setDirty(df)

    def _updateFiberCount(self):
        if self.doc.factory:
            nf = len(self.doc.fibers)
            nw = len(self.doc.wavelengths)
            self.countLabel.setText(
                self.tr("{} F x {} W = {}").format(
                    nf, nw, nf*nw))
            self.countLabel.setToolTip(
                self.tr("{} fibers x {} wavelengths = {} combinations".format(
                    nf, nw, nf*nw)))

    def updateFiber(self):
        """New fiber loaded, or fiber modified."""
        self.actions['new'].setEnabled(False)
        self.actions['edit'].setEnabled(True)
        self.actions['info'].setEnabled(True)
        self.fiberSelector.updateFiberName()
        self.fiberSlider.setNum(len(self.doc.fibers))
        self.setDirty(True)
        self._updateFiberCount()
        self.statusBar().showMessage(self.tr("Fiber factory loaded"), 5000)

    def updateWavelengths(self):
        self.doc.wavelengths = self.wavelengthInput
        self.wavelengthSlider.setNum(len(self.doc.wavelengths))
        self.setWavelength(self.wavelengthSlider.value())
        self._updateFiberCount()
        self.setDirty(True)

    def setMode(self, index):
        self.doc.modeKind = self.modeSelector.currentText()

    def setMaxNu(self, value):
        self.doc.numax = value

    def setMaxM(self, value):
        self.doc.mmax = value

    def setFiber(self, value):
        self.modeTableModel.setFiber(value)
        self.plotFrame.setFiber(value)
        self.showVNumber()

    def setWavelength(self, value):
        if 0 <= value - 1 < len(self.doc.wavelengths):
            wl = self.doc.wavelengths[value-1]
            self.wavelengthSlider.wlLabel.setText(
                "{:.5f} nm".format(wl * 1e9))
            self.modeTableModel.setWavelength(value)
            self.plotFrame.setWavelength(value)
            self.showVNumber()

    def showVNumber(self):
        try:
            wlnum = self.modeTableModel._wl
            fnum = self.modeTableModel._fnum
            wl = self.doc.wavelengths[wlnum]
            fiber = self.doc.fibers[fnum]
            self.wavelengthSlider.vLabel.setText(
                "/ V = {:.5f}".format(fiber.V0(wl)))
        except ValueError:
            pass

    def updateParams(self, checked):
        params = []
        for p in self.PARAMETERS:
            if self.simParamBoxes[p].isChecked():
                params.append(p)
        self.doc.params = params

    def initProgressBar(self):
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.time.start()
        self.estimation = 0
        self.timer.start(0)

    def updateProgressBar(self):
        tot = self.progressBar.maximum()
        if tot == 0:
            tot = self.doc.toCompute + 1
            self.progressBar.setMaximum(tot)
        self.progressBar.setValue(self.progressBar.value() + 1)
        elapsed = self.time.elapsed()
        self.estimation = elapsed
        if self.doc.toCompute > 0:
            done = self.progressBar.value()
            if done:
                self.estimation = tot * (elapsed / done)

    def stopProgressBar(self):
        tot = self.progressBar.maximum()
        self.progressBar.setValue(tot)
        self.timer.stop()
        self.updateTime()
        self.plotFrame.updatePlot()

    def updateTime(self):
        elapsed = self.time.elapsed()
        remaining = int(self.estimation - elapsed)
        if remaining > 0:
            self.timeLabel.setText(self.tr("E: {} (R: {})").format(
                msToStr(elapsed), msToStr(remaining, False)))
        else:
            self.timeLabel.setText(self.tr("E: {}").format(
                msToStr(elapsed)))

    def run_simulation(self):
        self.doc.ready = True
        self.doc.start()
        self.actions['start'].setEnabled(False)
        self.actions['stop'].setEnabled(True)
        self.actions['stop'].setChecked(False)

    def stop_simulation(self):
        self.timer.stop()
        self.progressBar.setValue(0)
        self.doc.stop_thread()
        self.doc.ready = False
        self.actions['stop'].setEnabled(False)
        self.actions['start'].setEnabled(True)
        self.actions['start'].setChecked(False)

    def togglePanes(self):
        states = [
            self.actions['paramwin'].isChecked(),
            self.actions['tablewin'].isChecked(),
            self.actions['graphwin'].isChecked()]
        self.splitter.setSizes(states)
        if sum(states) == 1:
            self.actions['paramwin'].setEnabled(not states[0])
            self.actions['tablewin'].setEnabled(not states[1])
            self.actions['graphwin'].setEnabled(not states[2])
        else:
            self.actions['paramwin'].setEnabled(True)
            self.actions['tablewin'].setEnabled(True)
            self.actions['graphwin'].setEnabled(True)

    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
