"""Parallel simulator module, using multiprocessing. """

from .simulator import Simulator
from ..mode import Family
import numpy
import concurrent.futures as cf


class PSimulator(Simulator):

    """Parallel simulator class. The interface should be identical to
    :class:`~fibermodes.simulator.simulator.Simulator`.

    :param nproc: Number of processors to use. If ``None``, use all processors.

    """

    def __init__(self, nproc=None):
        if nproc is None:
            import multiprocessing
            nproc = multiprocessing.cpu_count()
        self._nproc = nproc
        super().__init__()

    def solveV(self):
        if self._vsolved:
            return
        futures = {}
        with cf.ProcessPoolExecutor(max_workers=self._nproc) as executor:
            for fiber in self:
                lpm = self._lpModes[fiber] if fiber in self._lpModes else None
                if fiber not in self._vModes:
                    futures[executor.submit(fiber.vModes, lpm)] = fiber

            for f in cf.as_completed(futures):
                fiber = futures[f]
                self._vModes[fiber] = {smode.mode: smode
                                       for smode in f.result()}
        self._vsolved = True

    def solveLP(self):
        if self._lpsolved:
            return
        futures = {}
        with cf.ProcessPoolExecutor(max_workers=self._nproc) as executor:
            for fiber in self:
                if fiber not in self._lpModes:
                    futures[executor.submit(fiber.lpModes)] = fiber

            for f in cf.as_completed(futures):
                fiber = futures[f]
                self._lpModes[fiber] = {smode.mode: smode
                                        for smode in f.result()}
        self._lpsolved = True
