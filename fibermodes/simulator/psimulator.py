"""Parallel simulator module, using multiprocessing. """

from .simulator import Simulator
from ..mode import Mode
import concurrent.futures as cf


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

    def _iterSolve(self, fiter, lpHint=None, vHint=None):
        futures = {}
        with cf.ProcessPoolExecutor(max_workers=self._nproc) as executor:
            for f in fiter:
                futures[executor.submit(self._solveFiber, f,
                                        lpHint, vHint)] = f

            for f in cf.as_completed(futures):
                fiber = futures[f]
                lpModes, vModes = f.result()

                if lpModes:
                    self._lpModes[fiber] = {smode.mode: smode
                                            for smode in lpModes}
                if vModes:
                    self._vModes[fiber] = {smode.mode: smode
                                           for smode in vModes}
