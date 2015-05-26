
from fibermodes import Mode, ModeFamily, Wavelength
from fibermodes import constants
from fibermodes.functions import derivative
from itertools import count
from functools import lru_cache
import numpy
from math import isnan, sqrt
from scipy.optimize import brentq
from scipy.special import kn, kvp, k0, k1
import logging


class FiberSolver(object):

    logger = logging.getLogger(__name__)

    def __init__(self, fiber):
        self.fiber = fiber
        self.co_cache = {Mode("HE", 1, 1): 0,
                         Mode("LP", 0, 1): 0}
        self.ne_cache = {}

    def cutoff(self, mode):
        """Give `V0` parameter at cutoff, for given mode.

        :param mode: :class:`~fibermodes.mode.Mode` object

        Cutoff are cached. Cache remains valid, as fiber object is supposed
        to be unmutable.

        """
        try:
            return self.co_cache[mode]
        except KeyError:
            co = self._cutoff(mode)
            self.co_cache[mode] = co
            return co

    def _cutoff(self, mode):
        raise NotImplementedError()

    def set_ne_cache(self, wl, mode, neff):
        try:
            self.ne_cache[wl][mode] = neff
        except KeyError:
            self.ne_cache[wl] = {mode: neff}

    def neff(self, wl, mode, delta, lowbound=None):
        try:
            return self.ne_cache[wl][mode]
        except KeyError:
            neff = self._neff(wl, mode, delta, lowbound)
            self.set_ne_cache(wl, mode, neff)
            return neff

    def _neff(self, wl, mode, delta, lowbound):
        wl = Wavelength(wl)
        if lowbound is None:
            pm = None
            if mode.family is ModeFamily.HE:
                if mode.m > 1:
                    pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
            elif mode.family is ModeFamily.EH:
                pm = Mode(ModeFamily.HE, mode.nu, mode.m)
            elif mode.m > 1:
                pm = Mode(mode.family, mode.nu, mode.m - 1)

            if pm:
                lowbound = self.neff(wl, pm, delta)
                if isnan(lowbound):
                    return lowbound
            else:
                lowbound = max(layer.maxIndex(wl)
                               for layer in self.fiber.layers)

            if mode.family is ModeFamily.LP and mode.nu > 0:
                pm = Mode(mode.family, mode.nu - 1, mode.m)
                lb = self.neff(wl, pm, delta)
                if isnan(lb):
                    return lowbound
                lowbound = min(lowbound, lb)

        try:
            # Use cutoff information if available
            co = self.cutoff(mode)
            if self.fiber.V0(wl) < co:
                return float("nan")

            nco = max(layer.maxIndex(wl) for layer in self.fiber.layers)
            r = self.fiber.innerRadius(-1)

            lowbound = min(lowbound, sqrt(nco**2 - (co / (r * wl.k0))**2))
        except NotImplementedError:
            pass

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
    def beta(self, omega, mode, p=0, delta=1e-6):
        wl = Wavelength(omega=omega)
        if p == 0:
            neff = self.neff(wl, mode, delta)
            # print("b0", omega, wl, neff)
            return neff * wl.k0

        # if p == 1:
        #     neff1 = derivative(self.neff, wl, 1, 3, 1, 1e-9, mode)
        #     return (self.neff(wl, mode) - wl * neff1) / constants.c

        m = 5
        j = (m - 1) // 2
        h = 1e5
        lb = None
        for i in range(m-1, -1, -1):
            # Precompute neff using previous wavelength
            o = omega + (i-j) * h
            wl = Wavelength(omega=o)
            lb = self.neff(wl, mode, delta, lb) + delta * 1.1
            # print("pc", o, float(wl), lb)

        return derivative(self.beta, omega, p, m, j, h, mode, 0, delta)

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
