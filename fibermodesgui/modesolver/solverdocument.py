
from PySide import QtCore
from fibermodes import FiberFactory, PSimulator


class SolverDocument(QtCore.QThread):

    computeStarted = QtCore.Signal()
    modesAvailable = QtCore.Signal(int)  # fiber num
    valueAvailable = QtCore.Signal(int, int, object, int)
    computeFinished = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self._filename = None
        self.factory = None
        self._params = []
        # self.numfibers = 0

        self.toCompute = 0
        self.values = {}
        self.modes = []

        self.simulator = PSimulator()
        self.running = False
        self.ready = False

    @property
    def initialized(self):
        return self.simulator.initialized

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value
        self.start()

    @property
    def numax(self):
        return self.simulator.numax

    @numax.setter
    def numax(self, value):
        self.simulator.numax = value if value > -1 else None
        self.start()

    @property
    def mmax(self):
        return self.simulator.mmax

    @mmax.setter
    def mmax(self, value):
        self.simulator.mmax = value if value > 0 else None
        self.start()

    @property
    def modeKind(self):
        if self.simulator.vectorial and self.simulator.scalar:
            return 'both'
        elif self.simulator.vectorial:
            return 'vector'
        else:
            return 'scalar'

    @modeKind.setter
    def modeKind(self, value):
        if value == 'both':
            self.simulator.vectorial = self.simulator.scalar = True
        elif value == 'scalar':
            self.simulator.scalar = True
            self.simulator.vectorial = False
        else:
            self.simulator.vectorial = True
            self.simulator.scalar = False
        self.start()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
        self.factory = FiberFactory(value)
        self.simulator.set_factory(self.factory)
        self.start()

    @property
    def fibers(self):
        return self.simulator.fibers

    @property
    def wavelengths(self):
        return self.simulator.wavelengths

    @wavelengths.setter
    def wavelengths(self, value):
        self.simulator.set_wavelengths(value)
        self.start()

    def start(self):
        if not self.simulator.initialized:
            return

        if not self.ready:
            return

        self.stop_thread()
        super().start()

    def run(self):
        self.modes = []
        self.values = {}
        self.toCompute = 0
        self.running = True
        for fnum, resultf in enumerate(self.simulator.modes()):
            self.modes.append(resultf)
            self.modesAvailable.emit(fnum)
            self.toCompute += sum(len(rw) for rw in resultf)
        self.toCompute *= len(self.params)

        if self.toCompute > 0:
            self.computeStarted.emit()

            for j, p in enumerate(self.params):
                if p == "cutoff":
                    fct = self.simulator.cutoffWl
                else:
                    fct = getattr(self.simulator, p)

                for fnum, resultf in enumerate(fct()):
                    if not self.running:
                        self.simulator.terminate()
                        return
                    for wlnum, resultw in enumerate(resultf):
                        for mode, value in resultw.items():
                            self.values[(fnum, wlnum, mode, j)] = value
                            self.valueAvailable.emit(fnum, wlnum, mode, j)
                            self.toCompute -= 1
            self.computeFinished.emit()

    def stop_thread(self):
        self.running = False
        self.wait()
