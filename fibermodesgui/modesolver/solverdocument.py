
from PySide import QtCore
from fibermodes import FiberFactory, PSimulator


class SolverDocument(QtCore.QObject):

    valuesChanged = QtCore.Signal()
    valuesComputed = QtCore.Signal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self._filename = None
        self.factory = None
        self._params = []
        # self.numfibers = 0

        self.toCompute = 0
        self.futures = self.values = {}

        self.simulator = PSimulator()

    @property
    def initialized(self):
        return self.simulator.initialized

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value
        self._computeValues()

    @property
    def numax(self):
        return self.simulator.numax

    @numax.setter
    def numax(self, value):
        self.simulator.numax = value if value > -1 else None
        self._computeValues()

    @property
    def mmax(self):
        return self.simulator.mmax

    @mmax.setter
    def mmax(self, value):
        self.simulator.mmax = value if value > 0 else None
        self._computeValues()

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
        self._computeValues()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
        self.factory = FiberFactory(value)
        self.simulator.set_factory(self.factory)
        self._computeValues()

    @property
    def fibers(self):
        return self.simulator.fibers

    @property
    def wavelengths(self):
        return self.simulator.wavelengths

    @wavelengths.setter
    def wavelengths(self, value):
        self.simulator.set_wavelengths(value)
        self._computeValues()

    def _computeValues(self):
        if not self.simulator.initialized:
            return

        self.simulator.reset_thread()
        self.futures = {}
        self.values = {}
        self.toCompute = 0

        for j, p in enumerate(self.params):
            if p == "cutoff":
                fut = self.simulator.cutoffWl()
            elif p == "neff":
                fut = self.simulator.neff()
            elif p == "ng":
                fut = self.simulator.ng()
            elif p == "D":
                fut = self.simulator.D()
            elif p == "S":
                fut = self.simulator.S()
            else:
                continue  # should not happen...
            for fnum, fiber in enumerate(self.fibers):
                for wlnum, wl in enumerate(self.wavelengths):
                    if j == 0:
                        self.futures[(fnum, wlnum)] = []
                    vals = next(fut)
                    self.futures[(fnum, wlnum)].append(vals)
                    self.toCompute += len(vals)

        if self.toCompute > 0:
            self.valuesChanged.emit()

    def readyValues(self):
        tc = self.toCompute
        rmfut = []
        for (fi, wi), fwfutures in self.futures.items():
            allDone = True
            for j, futures in enumerate(fwfutures):
                rmmod = []
                for m, f in futures.items():
                    if f.ready():
                        rmmod.append(m)
                        v = f.get()
                        self.values[(fi, wi, m, j)] = v
                        self.toCompute -= 1
                        yield (fi, wi, m, j, v)
                    else:
                        allDone = False
                for m in rmmod:
                    del futures[m]
            if allDone:
                rmfut.append((fi, wi))
        for fw in rmfut:
            del self.futures[fw]
        if tc > self.toCompute:
            self.valuesComputed.emit(tc - self.toCompute)
