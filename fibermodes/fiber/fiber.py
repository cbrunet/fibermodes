"""This module contains the base :class:`~fibermodes.fiber.fiber.Fiber`
class.

You should not instanciate it directly. Instead, you should generate
a specialized fiber class using either a
:class:`~fibermodes.fiber.factory.Factory`, or a utility function like
:func:`~fibermodes.fiber.factory.fixedFiber`.

However, you should referer at the documentation of this class,
as it contains all the functions you need to solve for modes.

"""

import numpy
from scipy.optimize import brentq
from itertools import count
from math import sqrt

from ..mode import Mode, SMode, Family, sortModes


class Fiber(object):

    """This class represents a Fiber, at a given wavelength.

    This is the basis object used to solve for modes.

    :param wl: :class:`~fibermodes.wavelength.Wavelength` object.
    :param `*args`: variable number of tuples (material, radius, mat_params)

    """

    def __init__(self, wl, *args):
        '''
        Constructor

        args are: (material, radius, mat_params)
        '''
        hasfct = False

        def niffct(x):
            nonlocal hasfct
            if hasattr(x, '__iter__'):
                hasfct = True
                return None
            return x

        n = len(args)

        # TODO: use a dict for faster get() ?
        self._wl = wl
        self._mat = []
        self._r = numpy.empty(n)
        self._n = numpy.empty(n)
        self._params = []

        for i in range(n):  # For each layer
            self._mat.append(args[i][0])  # Material
            self._r[i] = niffct(args[i][1])  # Radius
            self._n[i] = args[i][0].n(self._wl, *args[i][2:])
            self._params.append(args[i][2:])
        self._r[-1] = self._r[-2]  # last layer radius

        if hasfct:
            # TODO: implement for wl and matparams also
            for i in range(n):
                if numpy.isnan(self._r[i]):
                    fct, *fargs = args[i][1]
                    p = [self.get(*x) for x in fargs]
                    self._r[i] = fct(*p)

    def __hash__(self):
        """Allow to use Fiber as dictionary key."""
        return hash((self._wl.wavelength,) + tuple(self._r[:-1]) +
                    tuple(self._n))

    @property
    def na(self):
        """Numerical aperture.

        NA is only relevant for :class:`~fibermodes.fiber.ssif.SSIF`.
        However, it is useful when calculating
        :attr:`~fibermodes.fiber.fiber.Fiber.V0`. Therefore, we define it
        as :math:`\\text{NA} = \sqrt{n_{\max}^2 - n_{cl}^2}`, where
        :math:`n_{\max}` is the highest refractive index inside the fiber,
        and :math:`n_{cl}` is the refractive index of the cladding.

        """
        return sqrt(max(self._n)**2 - self._n[-1]**2)

    @property
    def V0(self):
        """Normalized frequency.

        We define it as :math:`V_0 = k_0 r_{cl} \\text{NA}`,
        where :math:`r_{cl}` is the inner radius of the cladding.

        """
        return self._wl.k0 * self._r[-1] * self.na

    def get(self, pname, *args):
        """Get fiber parameter from given parameter name.

        Possible names are: 'wavelength', 'radius', 'material', and 'value'.

        For 'wavelength', the optional second parameter is the wavelength
        conversion to apply ('wavelength', 'k0', 'omega', etc. *see*
        :class:`~fibermodes.wavelength.Wavelength`). It the second parameter
        is omitted, wavelength is assumed.

        For 'radius' and 'material', the second parameter is the layer index.

        For 'material', the third parameter is material parameter index.

        For 'value', the second parameter is the value itself.

        :param pname: string representing the parameter ('wavelength',
                      'radius', 'material', or 'value')
        :rtype: float
        :raises: :class:`TypeError`

        """
        if pname == 'wavelength':
            wc = args[0] if args else 'wavelength'
            return getattr(self._wl, wc)
        elif pname == 'radius':
            return self._r[args[0]]
        elif pname == 'material':
            return self._params[args[0]][args[1]]
        elif pname == 'index':
            return self._n[args[0]]
        elif pname == 'value':
            return args[0]
        raise TypeError('pname must be wavelength, radius, '
                        'material or value, not"{}"'.format(pname))

    def __getitem__(self, key):
        return self.get(*key)

    def solve(self, mode, nmin, nmax, delta=1e-6, epsilon=1e-12):
        """Find root of characteristic equation inside given bound.

        It tries to find the first root from the highest index.
        However, it is not guaranteed that the found root is the first root.
        This function does not take into account the *m* parameter of
        the mode. You need to provide the right starting point or interval
        in order to get the right solution.

        :class:`OverflowError` is risen if no root is found.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param bound: hint to help root search. Can be *None*, start,
                      or (min, start, max).
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :rtype: :class:`~fibermodes.mode.SMode` (solved mode) object.
        :raises: :class:`OverflowError`

        """
        fct = self._ceq(mode)

        a = nmax - epsilon
        fa = fct(a, mode)
        while a > nmin + delta + epsilon:
            b, fb = a, fa
            a = b - delta
            fa = fct(a, mode)
            if (fa < 0 and fb > 0) or (fa > 0 and fb < 0):
                neff = brentq(fct, a, b, args=(mode,), xtol=epsilon)
                if a <= neff <= b:  # Detect discontinuity
                    v0 = abs(fct(neff, mode))
                    if (abs(fct(neff-epsilon, mode)) >= v0 and
                            abs(fct(neff+epsilon, mode)) >= v0):
                        return SMode(self, mode, neff)
        else:
            raise OverflowError("Did not found root in given interval.")

    def solveAll(self, mode, delta=1e-6, epsilon=1e-12, nmax=None,
                 cladding=False, idxmax=None):
        """Find all the modes in a given family with a given *ν*.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param delta: minimal interval to look in.
        :type delta: float
        :param epsilon: precision for root finding.
        :type epsilon: float
        :param nmax: maximum number of modes to search.
        :param cladding: do we look for cladding modes too?
        :param idxmax: maximum posible refractive index, or None
        :rtype: :class:`list` of :class:`~fibermodes.mode.SMode`
                (solved mode) object.
                Return empty :class:`list` if no mode is found.
        """
        modes = []
        if idxmax is None:
            idxmax = max(self._n)
        idxmin = min(self._n) if cladding else self._n[-1]
        assert idxmin < idxmax, "min > max"
        n = list(nn for nn in sorted(set(self._n), reverse=True)
                 if idxmin <= nn <= idxmax)
        if n[0] + epsilon < idxmax:
            n.insert(0, idxmax)
        # if n[-1] > idxmin:
        #     print("!")
        #     n.append(idxmin)
        bounds = [(n[i+1], n[i]) for i in range(len(n)-1)]
        while bounds:
            b = bounds.pop(0)
            try:
                smode = self.solve(mode,
                                   b[0], b[1],
                                   delta, epsilon)
                modes.append(smode)
                if nmax and len(modes) == nmax:
                    break
                bounds.append((b[0], smode.neff))
                # bounds.append((smode.neff, b[1]))
            except OverflowError:
                pass
        return sortModes(modes)

    def csolve(self, mode):
        pass

    def cutoffV0(self, mode):
        """Gives cutoff of given mode, in term of V0.

        This is an abstract method, that can be implemented for specific
        fiber layouts.

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param V0min: Minimal value for returned V0 (dafault: 2).
        :type V0min: integer
        :param V0max: Maximal value for returned V0 (default: inf).
        :type V0max: integer
        :param delta: Increment used for searching roots (default: 0.25).
                      Decrease it if it is not able to find a given cutoff.
                      Increase it to et faster calculation.
        :type delta: float
        :rtype: float
        :raise: NotImplementedError

        """
        raise NotImplementedError

    def lpModes(self, delta=1e-6, epsilon=1e-12, cladding=False, nmax=None):
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
        nm = nmax
        for nu in count():
            lpModes = self.solveAll(Mode(Family.LP, nu, 1),
                                    delta, epsilon, nmax=nm,
                                    cladding=cladding)
            if not lpModes:
                break
            modes += lpModes
            if nmax:
                nm = min(nmax, lpModes[-1].m)
        modes.sort(reverse=True)
        return modes

    def _findNear(self, mode, nmin, neff, nmax, delta, epsilon):
        fct = self._ceq(mode)
        n1 = n2 = neff
        f0 = fct(neff, mode)
        if f0 == 0:
            return SMode(self, mode, neff)

        while 1:
            if n2 + delta < nmax:
                n2 += delta
                f2 = fct(n2, mode)
                if (f0 > 0 and f2 < 0) or (f0 < 0 and f2 > 0):
                    try:
                        return self.solve(mode, n2-delta-2*epsilon, n2+epsilon,
                                          delta, epsilon)
                    except:
                        pass

            if n1 - delta > nmin:
                n1 -= delta
                f1 = fct(n1, mode)
                if (f0 > 0 and f1 < 0) or (f0 < 0 and f1 > 0):
                    try:
                        return self.solve(mode, n1-2*epsilon, n1+delta+epsilon,
                                          delta, epsilon)
                    except:
                        pass

            elif n2 + delta > nmax:
                raise OverflowError("Did not found root in given interval.")

    def vModes(self, lpModes=None, delta=1e-6, epsilon=1e-12, cladding=False,
               nmax=None):
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
            lpModes.sort(reverse=True)
            smode = None
            for mode in lpModes:
                try:
                    nmax = smode.neff if smode else max(self._n)
                    nmin = min(self._n) if cladding else self._n[-1]
                    smode = self._findNear(Mode(Family.HE,
                                                mode.nu + 1, mode.m),
                                           nmin, mode.neff, nmax,
                                           delta, epsilon)
                    modes.append(smode)
                except OverflowError:
                    # print(mode, nmin, mode.neff, nmax)
                    pass
                if mode.nu == 1:
                    try:
                        smode = self._findNear(Mode(Family.TE,
                                                    0, mode.m),
                                               nmin, mode.neff, nmax,
                                               delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                    try:
                        smode = self._findNear(Mode(Family.TM,
                                                    0, mode.m),
                                               nmin, mode.neff, nmax,
                                               delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
                elif mode.nu > 1:
                    try:
                        smode = self._findNear(Mode(Family.EH,
                                                    mode.nu - 1, mode.m),
                                               nmin, mode.neff, nmax,
                                               delta, epsilon)
                        modes.append(smode)
                    except OverflowError:
                        pass
        else:
            modes += self.solveAll(Mode(Family.TE, 0, 1),
                                   delta, epsilon, cladding=cladding)
            modes += self.solveAll(Mode(Family.TM, 0, 1),
                                   delta, epsilon, cladding=cladding)
            idxmax = None
            nm = nmax
            for nu in count(1):
                heModes = self.solveAll(Mode(Family.HE, nu, 1),
                                        delta, epsilon, cladding=cladding,
                                        nmax=nmax, idxmax=idxmax)
                if not heModes:
                    break
                modes += heModes
                if nmax:
                    nm = min(heModes[-1].m, nmax)
                if nu > 2 and self._ehceq != self._heceq:
                    ehModes = self.solveAll(Mode(Family.EH, nu-2, 1),
                                            delta, epsilon, cladding=cladding,
                                            nmax=nm, idxmax=idxmax)
                    if ehModes:
                        modes += ehModes
                idxmax = heModes[0].neff
        return sortModes(modes)

    def _ceq(self, mode):
        """Characteristic equation."""
        M = {Family.LP: self._lpceq,
             Family.TE: self._teceq,
             Family.TM: self._tmceq,
             Family.HE: self._heceq,
             Family.EH: self._ehceq}
        return M[mode.family]

    def __eq__(self, fiber):
        return (self._wl == fiber._wl and
                numpy.all(self._r[:-1] == fiber._r[:-1]) and
                numpy.all(self._n == fiber._n))

    def __str__(self):
        mats = []
        for mat, mp in zip(self._mat, self._params):
            mats.append("{}{}".format(mat.__name__, mp))
        return "Fiber({}, {}, [{}])".format(self._wl,
                                            self._r[:-1],
                                            ", ".join(mats))
