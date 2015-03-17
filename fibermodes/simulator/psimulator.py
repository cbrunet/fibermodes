"""Parallel simulator module, using multiprocessing. """

from .simulator import Simulator
from ..mode import Mode, Family
import concurrent.futures as cf
import numpy


class PSimulator(Simulator):

    """Parallel simulator class. The interface should be identical to
    :class:`~fibermodes.simulator.simulator.Simulator`.

    :param nproc: Number of processors to use. If ``None``, use all processors.

    """

    def __init__(self, nproc=None, *args, **kwargs):
        if nproc is None:
            import multiprocessing
            nproc = multiprocessing.cpu_count()
        self._nproc = nproc
        super().__init__(*args, **kwargs)

    def _solvefibers(self, fibers, mode):
        smodes = {}
        for fiber in fibers:
            smodes[fiber] = self._solveForMode(fiber, mode)
        return smodes

    def _psolve(self, fibers, mode):
        pm = None
        if mode.family in (Family.TE, Family.TM, Family.LP) and mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m-1)
        elif mode.family == Family.EH:
            pm = Mode(Family.HE, mode.nu, mode.m)
        elif mode.family == Family.HE and mode.m > 1:
            pm = Mode(Family.EH, mode.nu, mode.m-1)

        solvepm = False
        solvem = False
        for fiber in fibers:
            if fiber not in self._modes:
                self._modes[fiber] = {}
            if mode not in self._modes[fiber]:
                if pm is not None:
                    solvepm = True
                solvem = True  # Something missing, so solve for it

        # Recursive parallel solve for previous modes
        if solvepm:
            self._psolve(fibers, pm)

        # Parallel solve for mode
        if solvem:
            futures = {}
            with cf.ProcessPoolExecutor(max_workers=self._nproc) as executor:
                for i in range(self._nproc):
                    ff = fibers[i::self._nproc]
                    futures[executor.submit(self._solvefibers, ff, mode)] = i
                for f in cf.as_completed(futures):
                    for fiber, smode in f.result().items():
                        self._modes[fiber][mode] = smode

    def _getModesAttr(self, mode, attr):
        """Generic function to fetch list of ``attr`` from solved modes.

        """
        fibers = list(iter(self))
        self._psolve(fibers, mode)
        a = numpy.fromiter((self._getModeAttr(fiber, mode, attr, 0)
                            for fiber in fibers),
                           numpy.float,
                           self.__length_hint__())
        a = a.reshape(self.shape())
        return numpy.ma.masked_less_equal(a, 0)
