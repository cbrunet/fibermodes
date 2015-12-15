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

"""This module contains the main window for the fiber mode solver application.

The ModeSolver class should normally be instantiated from modesolverapp.py,
excepted if you want to start the mode solver application from another
Python application.

"""

from PyQt4 import QtGui, QtCore
from fibermodes import ModeFamily
from fibermodesgui.widgets import AppWindow, SLRCWidget
from .solverdocument import SolverDocument
from .fiberselector import FiberSelector
from .fiberslider import FiberSlider
from .wavelengthslider import WavelengthSlider
from .modetable import ModeTableView, ModeTableModel
from .plotframe import PlotFrame
from .simparams import SimParamsDialog
from .chareq import CharEqDialog
from .showhide import ShowHideMode
from fibermodesgui.fieldvisualizer import FieldVisualizer
from fibermodesgui.materialcalculator import MaterialCalculator
from fibermodesgui.wavelengthcalculator import WavelengthCalculator
from fibermodesgui import blockSignals
import os.path
import json
from tempfile import TemporaryFile
from shutil import copyfileobj


def msToStr(ms, displayms=True):
    h = ms // 3600000
    ms -= h * 3600000
    m = ms // 60000
    ms -= m * 60000
    s = ms / 1000
    fmt = "{:d}:{:02d}:{:05.3f}" if displayms else "{:d}:{:02d}:{:02.0f}"
    return fmt.format(h, m, s)


class ModeSolver(AppWindow):

    PARAMETERS = (("cutoff (V)", "cutoff (wavelength)"),
                  ("neff", "b", "vp", "beta0"),
                  ("ng", "vg", "beta1"),
                  ("D", "beta2"),
                  ("S", "beta3"))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.doc = SolverDocument(self)

        self.setWindowTitle(self.tr("Mode Solver"))
        self._initLayout()

        actions = {
            'open': (
                self.tr("&Open"),
                'document-open',
                QtGui.QKeySequence.Open,
                self.actionOpen
            ),
            'save': (
                self.tr("&Save"),
                'document-save',
                QtGui.QKeySequence.Save,
                self.save),
            'exportcur': (
                self.tr("&Export current table"),
                'export',
                [QtGui.QKeySequence("Ctrl+E")],
                self.export_current_table
            ),
            'quit': (
                self.tr("&Quit"),
                None,  # 'application-exit',
                QtGui.QKeySequence.Quit,
                self.close
            ),
            'new': (
                self.tr("&New fiber file"),
                'document-new',
                QtGui.QKeySequence.New,
                self.fiberSelector.editFiber
            ),
            'load': (
                self.tr("&Load fiber file"),
                'document-open',
                QtGui.QKeySequence.Open,
                self.fiberSelector.chooseFiber
            ),
            'edit': (
                self.tr("&Edit fiber"),
                'pen',
                [],
                self.fiberSelector.editFiber
            ),
            'info': (
                self.tr("&Fiber properties"),
                'document-properties',
                [QtGui.QKeySequence("Ctrl+I")],
                self.fiberSelector.fiberProperties
            ),
            'start': (
                self.tr("&Run simulation"),
                'media-playback-start',
                [QtGui.QKeySequence("F5")],
                self.run_simulation
            ),
            'stop': (
                self.tr("&Stop simulation"),
                'media-playback-stop',
                [QtGui.QKeySequence("Ctrl+.")],
                self.stop_simulation
            ),
            'mcalc': (
                self.tr("&Material calculator"),
                'index-calculator',
                [QtGui.QKeySequence("F8")],
                self.toggle_mcalc
            ),
            'wlcalc': (
                self.tr("&Wavelength calculator"),
                'lambda-calculator',
                [QtGui.QKeySequence("F7")],
                self.toggle_wlcalc
            ),
            'plotchareq': (
                self.tr("&Plot characteristic equation"),
                None,
                [],
                self.plot_chareq
            ),
            'clearcaches': (
                self.tr("&Clear all caches"),
                None,
                [],
                self.doc.clear_all_caches
            ),
            'simparams': (
                self.tr("Advanced &Parameters"),
                'document-properties',
                [],
                self.simParams
            ),
            'paramwin': (
                self.tr("&Parameters"),
                'function',
                [QtGui.QKeySequence("F2")],
                self.togglePanes
            ),
            'tablewin': (
                self.tr("&Result table"),
                'table',
                [QtGui.QKeySequence("F3")],
                self.togglePanes
            ),
            'graphwin': (
                self.tr("&Graph"),
                'statistics',
                [QtGui.QKeySequence("F4")],
                self.togglePanes
            ),
            'fullscreen': (
                self.tr("&Fullscreen"),
                'view-fullscreen',
                [QtGui.QKeySequence("F11")],
                self.toggleFullscreen
            ),
            'fields': (
                self.tr("Show &fields"),
                'report',
                [QtGui.QKeySequence("F6")],
                self.plotFields
            )
        }

        menus = [
            (
                self.tr("&File"), [
                    'open',
                    'save',
                    'exportcur',
                    '-',
                    'quit'
                ]
            ),
            (
                self.tr("Fibe&r"), [
                    'new',
                    'load',
                    '-',
                    'edit',
                    'info',
                ]
            ),
            (
                self.tr("&Simulation"), [
                    'start',
                    'stop',
                    '-',
                    'simparams',
                ]
            ),
            (
                self.tr("&Tools"), [
                    'fields',
                    '-',
                    'wlcalc',
                    'mcalc'
                ]
            ),
            (
                self.tr("&Debug"), [
                    'plotchareq',
                    self.logmenu,
                    'clearcaches',
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
            ['open', 'save', 'exportcur'],
            ['start', 'stop'],
            ['fields', '-', 'wlcalc', 'mcalc'],
            ['paramwin', 'tablewin', 'graphwin'],
        ]

        self.initActions(actions)
        self.initMenubars(self.menuBar(), menus)
        self.initToolbars(toolbars)

        self.actions['exportcur'].setEnabled(False)
        self.actions['edit'].setEnabled(False)
        self.actions['info'].setEnabled(False)
        self.actions['start'].setCheckable(True)
        self.actions['stop'].setCheckable(True)
        self.actions['stop'].setChecked(True)
        self.actions['stop'].setEnabled(False)
        self.actions['mcalc'].setCheckable(True)
        self.actions['wlcalc'].setCheckable(True)
        self.actions['paramwin'].setCheckable(True)
        self.actions['paramwin'].setChecked(True)
        self.actions['tablewin'].setCheckable(True)
        self.actions['tablewin'].setChecked(True)
        self.actions['graphwin'].setCheckable(True)
        self.actions['graphwin'].setChecked(True)
        self.actions['fullscreen'].setCheckable(True)
        self.actions['plotchareq'].setEnabled(False)
        self.actions['fields'].setEnabled(False)
        self.wavelengthInput.setValue(1550e-9)
        self.setDirty(False)
        self.closed.connect(self.doc.stop_thread)

        self.mcalc = None
        self.wlcalc = None

    def _initLayout(self):
        self.progressBar = QtGui.QProgressBar()
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
        self.plotFrame.modified.connect(self.setDirty)
        self.modeTableView.selChanged.connect(self.plotFrame.updateModeSel)
        self.modeTableModel.dataChanged.connect(self.plotFrame.updatePlot)
        self.splitter.addWidget(self.plotFrame)
        self.setCentralWidget(self.splitter)

        self.doc.computeStarted.connect(self.initProgressBar)
        self.doc.valueAvailable.connect(self.updateProgressBar)
        self.doc.computeFinished.connect(self.stopProgressBar)

    def _parametersFrame(self):
        self.fiberSelector = FiberSelector(self.doc, self)
        self.fiberSelector.fileLoaded.connect(self.updateFiber)
        self.fiberSelector.fiberEdited.connect(self.updateFiber)

        self.wavelengthInput = SLRCWidget()
        self.wavelengthInput.setSuffix(" nm")
        self.wavelengthInput.setScaleFactor(1e9)
        self.wavelengthInput.setRange(200, 10000)
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
        for row in self.PARAMETERS:
            hlayout = QtGui.QHBoxLayout()
            for param in row:
                box = QtGui.QCheckBox(param)
                box.toggled.connect(self.updateParams)
                hlayout.addWidget(box)
                self.simParamBoxes[param] = box
            hlayout.addStretch(1)
            simParamLayout.addLayout(hlayout)

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
        self.modeTableProxy = QtGui.QSortFilterProxyModel(self)
        self.modeTableProxy.setSourceModel(self.modeTableModel)
        self.modeTableProxy.setSortRole(QtCore.Qt.UserRole)
        self.modeTableProxy.setDynamicSortFilter(True)
        self.modeTableView = ModeTableView(self.modeTableProxy)
        self.modeTableView.selChanged.connect(self.updateUIsel)
        self.modeTableModel.dataChanged.connect(
            self.modeTableView.resizeColumnsToContents)
        self.modeTableModel.modelReset.connect(self.updateUImodes)

        self.fiberSlider = FiberSlider()
        self.fiberSlider.valueChanged.connect(self.setFiber)

        self.wavelengthSlider = WavelengthSlider()
        self.wavelengthSlider.valueChanged.connect(self.setWavelength)

        self.showhidesel = ShowHideMode()
        self.showhidesel.showModes.connect(self.on_show_modes)
        self.showhidesel.hideModes.connect(self.on_hide_modes)

        layout1 = QtGui.QHBoxLayout()
        layout1.addWidget(self.fiberSlider)
        layout1.addWidget(self.wavelengthSlider)

        layout2 = QtGui.QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.showhidesel)
        layout2.addWidget(self.modeTableView, stretch=1)

        frame = QtGui.QFrame()
        frame.setLayout(layout2)

        # Default values
        self.nuMaxInput.setValue(-1)
        self.mMaxInput.setValue(0)

        return frame

    def documentName(self):
        if self.doc.factory:
            fn = self.doc.filename
            p, f = os.path.split(fn)
            b, e = os.path.splitext(f)
            return os.path.join(p, b+".solver")
        return ""

    def actionOpen(self, filename=None):
        if not self._closeDocument():
            return

        if not filename:
            openDialog = QtGui.QFileDialog()
            openDialog.setWindowTitle(self.tr("Open solver..."))
            openDialog.setDirectory(self._dir)
            openDialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            openDialog.setNameFilter(self.tr("Solver (*.solver)"))
            if openDialog.exec_() == QtGui.QFileDialog.Accepted:
                filename = openDialog.selectedFiles()[0]
                self._dir = openDialog.directory()

        if filename:
            if self.load(filename):
                self._dir = os.path.dirname(filename)
                self.setDirty(False)
                self.statusBar().showMessage(self.tr("Solver loaded"), 5000)

    def load(self, filename):
        # Test for fiber file
        p, f = os.path.split(filename)
        b, e = os.path.splitext(f)
        fiberfile = os.path.join(p, b+".fiber")
        if os.path.exists(fiberfile):
            self.doc.filename = fiberfile
            self.fiberSelector.fileLoaded.emit()
        else:
            # Trouver fiberfile...
            print(fiberfile, "not found")
            return False

        self.stop_simulation()
        with open(filename, 'r') as f:
            s = json.load(f)
            self.wavelengthInput.setValue(s['wl'])
            self.modeSelector.setCurrentIndex(int(s['modes']))
            self.doc.params = s['params']
            for p, box in self.simParamBoxes.items():
                with blockSignals(box):
                    box.setChecked(p in self.doc.params)
            self.nuMaxInput.setValue(int(s['numax']))
            self.mMaxInput.setValue(int(s['mmax']))
            self.fiberSlider.fiberInput.setValue(int(s['fnum']))
            self.wavelengthSlider.wavelengthInput.setValue(int(s['wlnum']))
            self.actions['paramwin'].setChecked(s['panes']['params'])
            self.actions['tablewin'].setChecked(s['panes']['modes'])
            self.actions['graphwin'].setChecked(s['panes']['graph'])
            self.togglePanes()
            self.plotFrame.load(s['graph'])
        return True

    def save(self):
        s = {
            'wl': self.wavelengthInput._value,
            'modes': self.modeSelector.currentIndex(),
            'params': self.doc.params,
            'numax': self.doc.numax if self.doc.numax is not None else -1,
            'mmax': self.doc.mmax if self.doc.mmax is not None else -1,
            'fnum': self.fiberSlider.fiberInput.value(),
            'wlnum': self.wavelengthSlider.wavelengthInput.value(),
            'panes': {
                'params': int(self.actions['paramwin'].isChecked()),
                'modes': int(self.actions['tablewin'].isChecked()),
                'graph': int(self.actions['graphwin'].isChecked())},
            'graph': self.plotFrame.save()
        }

        # Use temporary file to prevent overwriting existing file in case
        # of error
        with TemporaryFile(mode="w+") as f:
            json.dump(s, f)
            f.seek(0)
            with open(self.documentName(), 'w') as fd:
                copyfileobj(f, fd)

        self.setDirty(False)
        self.statusBar().showMessage(self.tr("Fiber saved"), 5000)
        super().save()

    def setDirty(self, df=True):
        if 'save' in self.actions:
            if not self.doc.factory:
                self.actions['save'].setEnabled(False)
            else:
                self.actions['save'].setEnabled(df)
        if not self.doc.factory:
            df = False
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
        self.actions['plotchareq'].setEnabled(True)
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
        self.setDirty(True)

    def setMaxNu(self, value):
        self.doc.numax = value
        self.setDirty(True)

    def setMaxM(self, value):
        self.doc.mmax = value
        self.setDirty(True)

    def setFiber(self, value):
        self.modeTableModel.setFiber(value)
        self.plotFrame.setFiber(value)
        self.showVNumber()
        self.setDirty(True)

    def setWavelength(self, value):
        if 0 <= value - 1 < len(self.doc.wavelengths):
            wl = self.doc.wavelengths[value-1]
            self.wavelengthSlider.wlLabel.setText(
                "{:.5f} nm".format(wl * 1e9))
            self.modeTableModel.setWavelength(value)
            self.plotFrame.setWavelength(value)
            self.showVNumber()
            self.setDirty(True)

    def showVNumber(self):
        try:
            wlnum = self.modeTableModel._wl
            fnum = self.modeTableModel._fnum
            wl = self.doc.wavelengths[wlnum]
            fiber = self.doc.fibers[fnum]
            self.wavelengthSlider.vLabel.setText(
                "| V = {:.5f}".format(fiber.V0(wl)))
        except ValueError:
            pass

    def updateParams(self, checked):
        params = []
        for row in self.PARAMETERS:
            for p in row:
                if self.simParamBoxes[p].isChecked():
                    params.append(p)
        self.doc.params = params
        self.plotFrame.updatePMButs()
        self.setDirty(True)

    def initProgressBar(self):
        self.progressBar.setFormat("%v / %m (%p%)")
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)
        self.time.start()
        self.estimation = 0
        self.timer.start(0)
        self.actions['exportcur'].setEnabled(False)

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
        self.actions['exportcur'].setEnabled(True)

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
        self.progressBar.setFormat("")
        self.progressBar.setValue(0)
        self.doc.stop_thread()
        self.doc.ready = False
        self.actions['stop'].setEnabled(False)
        self.actions['start'].setEnabled(True)
        self.actions['start'].setChecked(False)

    def toggle_mcalc(self):
        if self.mcalc is None:
            self.mcalc = MaterialCalculator(self)
            self.mcalc.hidden.connect(self.actions['mcalc'].toggle)

        if self.actions['mcalc'].isChecked():
            self.mcalc.show()
        else:
            with blockSignals(self.mcalc):
                self.mcalc.hide()

    def toggle_wlcalc(self):
        if self.wlcalc is None:
            self.wlcalc = WavelengthCalculator(self)
            self.wlcalc.hidden.connect(self.actions['wlcalc'].toggle)

        if self.actions['wlcalc'].isChecked():
            self.wlcalc.show()
        else:
            with blockSignals(self.wlcalc):
                self.wlcalc.hide()

    def plot_chareq(self):
        sel = self.modeTableView.selectedIndexes()
        try:
            idx = self.modeTableProxy.mapToSource(sel[0])
            mode = self.modeTableModel.modes[idx.row()]
        except IndexError:
            mode = None
        dlg = CharEqDialog(mode, self)
        dlg.show()

    def simParams(self):
        dlg = SimParamsDialog(self.doc)
        dlg.exec_()
        self.doc.numProcs = dlg.numProcs.value()
        self.doc.simulator.delta = float(dlg.delta.text())

    def on_show_modes(self, what, option):
        self._show_hide_modes(True, what, option)

    def on_hide_modes(self, what, option):
        self._show_hide_modes(False, what, option)

    def _show_hide_modes(self, show, what, option):
        nm = self.modeTableModel.rowCount()
        for i in range(nm):
            mode = self.modeTableModel.headerData(i,
                                                  QtCore.Qt.Vertical,
                                                  QtCore.Qt.UserRole)
            if (what == 0 or
                    (what == 1 and mode.family is ModeFamily(option+1)) or
                    (what == 2 and mode.nu == option) or
                    (what == 3 and mode.m == option+1)):
                index = self.modeTableModel.index(i, 0)
                self.modeTableModel.setData(
                    index,
                    QtCore.Qt.Checked if show else QtCore.Qt.Unchecked,
                    QtCore.Qt.CheckStateRole)

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
        self.setDirty(True)

    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def export_current_table(self):
        wlnum = self.modeTableModel._wl
        fnum = self.modeTableModel._fnum

        exportDialog = QtGui.QFileDialog()
        exportDialog.setWindowTitle(self.tr("Export results"))
        exportDialog.setDirectory(self._dir)
        exportDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        exportDialog.setNameFilter(self.tr("Comma Separated Values (*.csv)"))
        exportDialog.setDefaultSuffix('csv')
        if exportDialog.exec_() == QtGui.QFileDialog.Accepted:
            filename = exportDialog.selectedFiles()[0]
            self._dir = exportDialog.directory()
            self.doc.export(filename, wlnum, fnum)

    def updateUIsel(self, modes):
        pass
        # ms = len(modes) > 0
        # self.actions['plotchareq'].setEnabled(ms)

    def updateUImodes(self):
        nm = self.modeTableModel.rowCount()
        self.actions['fields'].setEnabled(nm > 0)
        self.showhidesel.modes = self.modeTableModel.modes

    def plotFields(self):
        fv = FieldVisualizer(self)
        sm = self.modeTableView.selectedModes()
        if sm:
            fv.setModes([[m, 0, 0, 1] for m in sm])
        fv.show()
