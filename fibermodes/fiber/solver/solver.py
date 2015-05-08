
from fibermodes import Mode, ModeFamily
from fibermodes import constants
from fibermodes.functions import derivative
from itertools import count
from functools import lru_cache
import numpy
from math import isnan
from scipy.optimize import brentq
from scipy.special import kn, kvp, k0, k1
import logging


class FiberSolver(object):

    logger = logging.getLogger(__name__)

    def __init__(self, fiber):
        self.fiber = fiber
        self.__cocache = {Mode("HE", 1, 1): 0,
                          Mode("LP", 0, 1): 0}

    def cutoff(self, mode):
        """Give `V0` parameter at cutoff, for given mode.

        :param mode: :class:`~fibermodes.mode.Mode` object

        Cutoff are cached. Cache remains valid, as fiber object is supposed
        to be unmutable.

        """
        try:
            return self.__cocache[mode]
        except KeyError:
            co = self._cutoff(mode)
            self.__cocache[mode] = co
            return co

    def _cutoff(self, mode):
        raise NotImplementedError()

    @lru_cache(maxsize=None)
    def neff(self, wl, mode, delta=1e-6):
        return self._neff(wl, mode, delta)

    def _neff(self, wl, mode, delta):
        pm = None
        if mode.family is ModeFamily.HE:
            if mode.m > 1:
                pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
        elif mode.family is ModeFamily.EH:
            pm = Mode(ModeFamily.HE, mode.nu, mode.m)
        elif mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m - 1)

        if pm:
            lowbound = self.neff(wl, pm)
        else:
            lowbound = max(layer.maxIndex(wl) for layer in self.fiber.layers)

        if mode.family is ModeFamily.LP and mode.nu > 0:
            pm = Mode(mode.family, mode.nu - 1, mode.m)
            lowbound = min(lowbound, self.neff(wl, pm))

        if isnan(lowbound):
            return lowbound

        highbound = self.fiber.minIndex(-1, wl)

        fct = {ModeFamily.LP: self._lpceq,
               ModeFamily.TE: self._teceq,
               ModeFamily.TM: self._tmceq,
               ModeFamily.HE: self._heceq,
               ModeFamily.EH: self._heceq
               }

        return self._findFirstRoot(fct[mode.family], args=(wl, mode.nu),
                                   lowbound=lowbound-delta,
                                   highbound=highbound+delta,
                                   delta=-delta)

    @lru_cache(maxsize=None)
    def beta(self, wl, mode, p=0):
        if p == 0:
            return self.neff(wl, mode) * constants.tpi / wl

        # if p == 1:
        #     neff1 = derivative(self.neff, wl, 1, 3, 1, 1e-9, mode)
        #     return (self.neff(wl, mode) - wl * neff1) / constants.c

        return derivative(self.beta, wl, p, 5, 2, 1e-9, mode, 0)

    def _findFirstRoot(self, fct, args=(), lowbound=0, highbound=None,
                       ipoints=[], delta=0.25):
        a = lowbound
        fa = fct(a, *args)
        if fa == 0:
            return a

        for i in count(1):
            b = ipoints.pop(0) if ipoints else a + delta
            if highbound:
                if ((b > highbound > lowbound) or (b < highbound < lowbound)):
                    self.logger.info("_findFirstRoot: no root found within "
                                     "allowed range")
                    return float("nan")
            fb = fct(b, *args)
            if fb == 0:
                return b

            if (fa > 0 and fb < 0) or (fa < 0 and fb > 0):
                z = brentq(fct, a, b, args=args)
                fz = fct(z, *args)
                if abs(fa) > abs(fz) < abs(fb):  # Skip discontinuities
                    return z

            a, fa = b, fb

    def _findBetween(self, fct, lowbound, highbound, args=()):
        v = [lowbound, highbound]
        s = [fct(lowbound, *args), fct(highbound, *args)]

        for j in count():  # probably not needed...
            for i in range(len(s)-1):
                a, b = v[i], v[i+1]
                fa, fb = s[i], s[i+1]

                if (fa > 0 and fb < 0) or (fa < 0 and fb > 0):
                    z = brentq(fct, a, b, args=args)
                    fz = fct(z, *args)
                    if abs(fa) > abs(fz) < abs(fb):  # Skip discontinuities
                        return z

            ls = len(s)
            for i in range(ls-1):
                a, b = v[2*i], v[2*i+1]
                c = (a + b) / 2
                v.insert(2*i+1, c)
                s.insert(2*i+1, fct(c, *args))

    def _lpceq(self, neff, wl, nu):
        N = len(self.fiber)
        C = numpy.zeros((N-1, 2))
        C[0, 0] = 1

        for i in range(1, N-1):
            r = self.fiber.innerRadius(i)
            A = self.fiber.layers[i-1].Psi(r, neff, wl, nu, C[i-1, :])
            C[i, :] = self.fiber.layers[i].lpConstants(r, neff, wl, nu, A)

        r = self.fiber.innerRadius(-1)
        A = self.fiber.layers[N-2].Psi(r, neff, wl, nu, C[-1, :])
        u = self.fiber.layers[N-1].u(r, neff, wl)
        return u * kvp(nu, u) * A[0] - kn(nu, u) * A[1]

    def _teceq(self, neff, wl, nu):
        N = len(self.fiber)
        C = numpy.zeros((N-1, 4))
        C[0, :] = [0., 0., 1., 0.]

        for i in range(1, N-1):
            r = self.fiber.innerRadius(i)
            ro = self.fiber.outerRadius(i)
            EH = self.fiber.layers[i-1].ehrfields(
                r, neff, wl, nu, C[i-1, :])
            C[i, 2:] = self.fiber.layers[i].tetmConstants(
                r, ro, neff, wl, EH, -constants.eta0, (1, 2))

        # Last layer
        r = self.fiber.innerRadius(-1)
        _, Hz, Ep, _ = self.fiber.layers[N-2].ehrfields(
                r, neff, wl, nu, C[N-2, :])
        u = self.fiber.layers[-1].u(r, neff, wl)

        F4 = k1(u) / k0(u)
        return Ep + wl.k0 * r / u * constants.eta0 * Hz * F4

    def _tmceq(self, neff, wl, nu):
        N = len(self.fiber)
        C = numpy.zeros((N-1, 4))
        C[0, :] = [1., 0., 0., 0.]

        for i in range(1, N-1):
            r = self.fiber.innerRadius(i)
            ro = self.fiber.outerRadius(i)
            EH = self.fiber.layers[i-1].ehrfields(
                r, neff, wl, nu, C[i-1, :])
            n = self.fiber.maxIndex(i, wl)
            C[i, :2] = self.fiber.layers[i].tetmConstants(
                r, ro, neff, wl, EH, constants.Y0 * n * n, (0, 3))

        # Last layer
        r = self.fiber.innerRadius(-1)
        Ez, _, _, Hp = self.fiber.layers[N-2].ehrfields(
                r, neff, wl, nu, C[N-2, :])
        u = self.fiber.layers[-1].u(r, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = k1(u) / k0(u)
        return Hp - wl.k0 * r / u * constants.Y0 * n * n * Ez * F4

    def _heceq(self, neff, wl, nu):
        N = len(self.fiber)
        C = numpy.zeros((N-1, 4, 2))
        C[0, 0, 0] = 1  # A
        C[0, 2, 1] = 1  # A'

        for i in range(1, N-1):
            r = self.fiber.innerRadius(i)
            ro = self.fiber.outerRadius(i)
            EH = self.fiber.layers[i-1].ehrfields(
                r, neff, wl, nu, C[i-1, :, :])
            C[i, :, :] = self.fiber.layers[i].vConstants(
                r, ro, neff, wl, nu, EH)

        # Last layer
        r = self.fiber.innerRadius(-1)
        EH = self.fiber.layers[N-2].ehrfields(r, neff, wl, nu, C[N-2, :, :])
        u = self.fiber.layers[N-1].u(r, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = kvp(nu, u) / kn(nu, u)
        c1 = -wl.k0 * r / u
        c2 = neff * nu / u * c1
        c3 = constants.eta0 * c1
        c4 = constants.Y0 * n * n * c1

        E = EH[2, :] - (c2 * EH[0, :] - c3 * F4 * EH[1, :])
        H = EH[3, :] - (c4 * F4 * EH[0, :] - c2 * EH[1, :])
        return E[0]*H[1] - E[1]*H[0]
