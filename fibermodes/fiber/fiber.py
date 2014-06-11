"""This module contains the base :class:`~fibermodes.fiber.fiber.Fiber`
class.

"""

import numpy
from scipy.optimize import brentq
from itertools import count

from ..mode import Mode, SMode, Family, sortModes


class Fiber(object):

    '''
    classdocs
    '''

    def __init__(self, wl, *args):
        '''
        Constructor

        args are: (material, radius, mat_params)
        '''
        n = len(args)

        self._wl = wl
        self._mat = []
        self._r = numpy.empty(n)
        self._n = numpy.empty(n)
        self._params = []

        for i in range(n):
            self._mat.append(args[i][0])
            self._r[i] = args[i][1]
            self._n[i] = args[i][0].n(self._wl, *args[i][2:])
            self._params.append(args[i][2:])

    def solve(self, mode, bound=None, delta=1e-6, epsilon=1e-12):
        """Find root of characteristic equation inside given bound.

        It tries to find the first root from the highest index.
        However, it is not guaranteed that the found root is the first root.
        This function does not take into account the *m* parameter of
        the mode. You need to provide the right interval in order to get
        the right solution.

        :class:`OverflowError` is risen if no root is found.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param bound: interval (min, max) where to search, or *None*.
                      If *None*, it will search between min and max index
                      of the fiber.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`~fibermodes.mode.SMode` (solved mode) object.
        :raises: :class:`OverflowError`

        """
        fct = self._ceq(mode)

        if bound is None:
            bound = [self._n.min() + epsilon, self._n.max() - epsilon]
        else:
            bound = list(bound)

        s = 1 if fct(bound[1], mode) > 0 else -1
        n = 1
        d = bound[1] - bound[0]
        sc = 1 if fct(bound[0], mode) > 0 else -1
        while sc == s:
            n *= 2
            d /= 2
            if d < delta:
                raise OverflowError("Did not found root in given interval.")
            for i in range(n-1, 0, -2):  # only odd indices, since we
                                         # already tried the others
                b = bound[0] + i * d
                sc = 1 if fct(b, mode) > 0 else -1
                if sc != s:
                    bound[0] = b
                    bound[1] = b + d
                    break

        neff = brentq(fct, bound[0], bound[1], args=(mode,), xtol=epsilon)
        if bound[0] < neff < bound[1]:
            return SMode(self, mode, neff)
        raise OverflowError("Did not found root in given interval.")

    def solveAll(self, mode, delta=1e-6, epsilon=1e-12):
        """Find all the modes in a given family with a given *ν*.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.
        """
        modes = []
        bounds = [(self._n.min(), self._n.max())]
        while bounds:
            b = bounds.pop(0)
            try:
                smode = self.solve(mode,
                                   (b[0] + epsilon, b[1] - epsilon),
                                   delta, epsilon)
                modes.append(smode)
                bounds.append((b[0], smode.neff))
                bounds.append((smode.neff, b[1]))
            except OverflowError:
                pass
        return sortModes(modes)

    def csolve(self, mode):
        pass

    def cutoff(self, mode):
        pass

    def lpModes(self, delta=1e-6, epsilon=1e-12):
        """Find all scalar (lp) modes of the fiber.

        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.

        """
        modes = []
        for nu in count():
            lpModes = self.solveAll(Mode(Family.LP, nu, 1), delta, epsilon)
            if not lpModes:
                break
            modes += lpModes
        modes.sort(reverse=True)
        return modes

    def vModes(self, lpModes=None, delta=1e-6, epsilon=1e-12):
        """Find all vector (hybrid) modes of the fiber.

        :param lpModes: :class:`list` of :class:`~fibermodes.mode.SMode`.
                        If set, we look around effective indices of the given
                        LP modes to get an estimation of expected vector modes.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.

        """
        modes = []
        if lpModes:
            for mode in lpModes:
                # 5 is arbitrary. Try to find an optimal algorithm to
                # search for optimal bound
                bound = (mode.neff - 5 * delta, mode.neff + 5 * delta)
                if mode.nu == 0:
                    try:
                        smode = self.solve(Mode(Family.HE, 1, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                elif mode.nu == 1:
                    try:
                        smode = self.solve(Mode(Family.TE, 0, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                    try:
                        smode = self.solve(Mode(Family.TM, 0, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                    try:
                        smode = self.solve(Mode(Family.HE, 2, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                else:
                    try:
                        smode = self.solve(Mode(Family.HE,
                                                mode.nu + 1, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                    try:
                        smode = self.solve(Mode(Family.EH,
                                                mode.nu - 1, mode.m),
                                           bound, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
        else:
            modes += self.solveAll(Mode(Family.TE, 0, 1), delta, epsilon)
            modes += self.solveAll(Mode(Family.TM, 0, 1), delta, epsilon)
            for nu in count(1):
                heModes = self.solveAll(Mode(Family.HE, nu, 1), delta, epsilon)
                if not heModes:
                    break
                modes += heModes
                if nu > 2:
                    ehModes = self.solveAll(Mode(Family.EH, nu-2, 1),
                                            delta, epsilon)
                    if not ehModes:
                        break
                    modes += ehModes
        modes.sort(reverse=True)
        return modes

    def _ceq(self, mode):
        M = {Family.LP: self._lpceq,
             Family.TE: self._teceq,
             Family.TM: self._tmceq,
             Family.HE: self._heceq,
             Family.EH: self._ehceq}
        return M[mode.family]
