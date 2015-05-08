
from PySide import QtCore
from multiprocessing import Pool
from fibermodes.fiber.factory import FiberFactory
from fibermodes import Mode


class SolverDocument(QtCore.QObject):

    def __init__(self, parent):
        super().__init__(parent)

        self.filename = None
        self.factory = None
        self.params = []
        self.wavelengths = []
        self.numfibers = 0
        self.modeKind = 'vector'
        self.maxell = 0
        self.maxm = 1

        self.totalTasks = 0
        self.tasksDone = 0
        self.pool = None

        self.cutoffs = []
        self.modes = []

    def load(self):
        """Reset fiber factory data. Reload fiber factory file."""
        self.factory = FiberFactory(self.filename)
        self.numfibers = len(self.factory)
        self.cutoffs = [{} for _ in range(self.numfibers)]
        self.modes = [{} for _ in range(self.numfibers)]

    def start(self):
        self.terminate()

        self._pool = Pool()

        for p in self.params:
            if p == "cutoff":
                self.findCutoffs()

    def terminate(self):
        if self.tasksDone != self.totalTasks:
            self.pool.terminate()
            self.pool.join()
            self.totalTasks = 0
            self.tasksDone = 0

    def findCutoffs(self):
        for mode in self.modeGen():
            print(str(mode))

    def modeGen(self):
        for ell in range(self.maxell+1):
            for m in range(1, self.maxm+1):
                if self.modeKind in ('scalar', 'both'):
                    yield Mode("LP", ell, m)
                if self.modeKind in ('vector', 'both'):
                    if ell == 1:
                        yield Mode("TM", 0, m)
                    if ell >= 2:
                        yield Mode("EH", ell-1, m)
                    yield Mode("HE", ell+1, m)
                    if ell == 1:
                        yield Mode("TE", 0, m)
