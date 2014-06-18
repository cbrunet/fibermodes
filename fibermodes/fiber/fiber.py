"""This module contains the base :class:`~fibermodes.fiber.fiber.Fiber`
class.

"""

import numpy
from scipy.optimize import brentq
from itertools import count

from ..mode import Mode, SMode, Family, sortModes


class Fiber(object):

    """This class represents a Fiber, at a given wavelength.

    This is the basis object used to solve for modes.

    :param wl: :class:`~fibermodes.wavelength.Wavelength` object.
    :param `*args`: variable number of tuples (material, radium, mat_params)

    """

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

    def _findBracket(self, mode, fct,
                     a, b=None, c=None, delta=1e-6):
        if c is None:
            if b is None:
                b = a
                a = self._n.min()
                c = self._n.max()
            else:
                c = b
                b = None

        if b is None:  # From bounds to middle
            s = (fct(c, mode) > 0)
            n = 1
            d = c - a
            sc = (fct(a, mode) > 0)
            while sc == s:
                n *= 2
                d /= 2
                if d < delta:
                    raise OverflowError("Cannot find root in given interval.")
                for i in range(n-1, 0, -2):  # only odd indices, since we
                                             # already tried the others
                    b = a + i * d
                    sc = (fct(b, mode) > 0)
                    if sc != s:
                        a = b
                        c = b + d
                        break
            return (a, c)

        else:  # From point to exterior
            s = (fct(b, mode) > 0)
            d = 0
            for n in count(1):
                d += delta
                if b + d < c:
                    if (fct(b + d, mode) > 0) != s:
                        return (b + d - delta, b + d)
                elif b - d < a:
                    break
                if b - d > a:
                    if (fct(b - d, mode) > 0) != s:
                        return (b - d, b - d + delta)

        raise OverflowError("Cannot find root in given interval.")

    def solve(self, mode, bound=None, delta=1e-6, epsilon=1e-12):
        """Find root of characteristic equation inside given bound.

        It tries to find the first root from the highest index.
        However, it is not guaranteed that the found root is the first root.
        This function does not take into account the *m* parameter of
        the mode. You need to provide the right starting point or interval
        in order to get the right solution.

        :class:`OverflowError` is risen if no root is found.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param bound: hint to help root search. Can be *None*, start,
                      (min, max), or (min, start, max).
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`~fibermodes.mode.SMode` (solved mode) object.
        :raises: :class:`OverflowError`

        """
        fct = self._ceq(mode)

        if bound is None:
            a = self._n.min() + epsilon
            b = None
            c = self._n.max() - epsilon
        else:
            try:
                a = float(bound)
                b = c = None
            except TypeError:
                a = bound[0]
                b = bound[1] if len(bound) > 1 else None
                c = bound[2] if len(bound) > 2 else None
        a, b = self._findBracket(mode, fct, a, b, c, delta=delta)

        neff = brentq(fct, a, b, args=(mode,), xtol=epsilon)
        if a <= neff <= b:
            return SMode(self, mode, neff)
        raise OverflowError("Did not found root in given interval.")

    def solveAll(self, mode, delta=1e-6, epsilon=1e-12, nmax=None,
                 cladding=False):
        """Find all the modes in a given family with a given *ν*.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :param nmax: maximum number of modes to search.
        :param cladding: do we look for cladding modes too?
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.
        """
        modes = []
        n = list(nn for nn in sorted(self._n, reverse=True)
                 if cladding or nn >= self._n[-1])
        bounds = [(n[i+1], n[i]) for i in range(len(n)-1)]
        # bounds = [(self._n.min(), self._n.max())]
        while bounds:
            b = bounds.pop(0)
            try:
                smode = self.solve(mode,
                                   (b[0] + epsilon, b[1] - epsilon),
                                   delta, epsilon)
                modes.append(smode)
                if nmax and len(modes) == nmax:
                    break
                bounds.append((b[0], smode.neff))
                bounds.append((smode.neff, b[1]))
            except OverflowError:
                pass
        return sortModes(modes)

    def csolve(self, mode):
        pass

    def cutoff(self, mode):
        pass

    def lpModes(self, delta=1e-6, epsilon=1e-12, cladding=False):
        """Find all scalar (lp) modes of the fiber.

        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :param cladding: do we look for cladding modes too?
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.

        """
        modes = []
        for nu in count():
            lpModes = self.solveAll(Mode(Family.LP, nu, 1),
                                    delta, epsilon, cladding)
            if not lpModes:
                break
            modes += lpModes
        modes.sort(reverse=True)
        return modes

    def vModes(self, lpModes=None, delta=1e-6, epsilon=1e-12, cladding=False):
        """Find all vector (hybrid) modes of the fiber.

        :param lpModes: :class:`list` of :class:`~fibermodes.mode.SMode`.
                        If set, we look around effective indices of the given
                        LP modes to get an estimation of expected vector modes.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :param cladding: do we look for cladding modes too?
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.

        """
        modes = []
        if lpModes:
            for mode in lpModes:
                try:
                    smode = self.solve(Mode(Family.HE,
                                            mode.nu + 1, mode.m),
                                       mode.neff, delta, epsilon)
                    modes.append(smode)
                except OverflowError:
                    pass
                if mode.nu == 1:
                    try:
                        smode = self.solve(Mode(Family.TE, 0, mode.m),
                                           mode.neff, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                    try:
                        smode = self.solve(Mode(Family.TM, 0, mode.m),
                                           mode.neff, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                elif mode.nu > 1:
                    try:
                        smode = self.solve(Mode(Family.EH,
                                                mode.nu - 1, mode.m),
                                           mode.neff, delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
        else:
            modes += self.solveAll(Mode(Family.TE, 0, 1),
                                   delta, epsilon, cladding)
            modes += self.solveAll(Mode(Family.TM, 0, 1),
                                   delta, epsilon, cladding)
            for nu in count(1):
                heModes = self.solveAll(Mode(Family.HE, nu, 1),
                                        delta, epsilon, cladding)
                if not heModes:
                    break
                modes += heModes
                if nu > 2:
                    ehModes = self.solveAll(Mode(Family.EH, nu-2, 1),
                                            delta, epsilon, cladding)
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
