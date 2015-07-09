from .solver import FiberSolver
from fibermodes import Wavelength, Mode, ModeFamily
from fibermodes import constants
from math import isnan, sqrt
import numpy
from scipy.special import kn, kvp, k0, k1


class Neff(FiberSolver):

    def __call__(self, wl, mode, delta, lowbound):
        wl = Wavelength(wl)
        if lowbound is None or isnan(lowbound):
            pm = None
            if mode.family is ModeFamily.HE:
                if mode.m > 1:
                    pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
            elif mode.family is ModeFamily.EH:
                pm = Mode(ModeFamily.HE, mode.nu, mode.m)
            elif mode.m > 1:
                pm = Mode(mode.family, mode.nu, mode.m - 1)

            if pm:
                lowbound = self.fiber.neff(pm, wl, delta)
                if isnan(lowbound):
                    return lowbound
            else:
                lowbound = max(layer.maxIndex(wl)
                               for layer in self.fiber.layers)

            if mode.family is ModeFamily.LP and mode.nu > 0:
                pm = Mode(mode.family, mode.nu - 1, mode.m)
                lb = self.fiber.neff(pm, wl, delta)
                if isnan(lb):
                    return lowbound
                lowbound = min(lowbound, lb)

        try:
            # Use cutoff information if available
            co = self.fiber.cutoff(mode)
            if self.fiber.V0(wl) < co:
                return float("nan")

            nco = max(layer.maxIndex(wl) for layer in self.fiber.layers)
            r = self.fiber.innerRadius(-1)

            lowbound = min(lowbound, sqrt(nco**2 - (co / (r * wl.k0))**2))
        except (NotImplementedError):
            pass

        highbound = self.fiber.minIndex(-1, wl)

        fct = {ModeFamily.LP: self._lpceq,
               ModeFamily.TE: self._teceq,
               ModeFamily.TM: self._tmceq,
               ModeFamily.HE: self._heceq,
               ModeFamily.EH: self._heceq
               }

        if lowbound <= highbound:
            print("impossible bound")
            return float("nan")

        if (lowbound - highbound) < 10 * delta:
            delta = (lowbound - highbound) / 10

        return self._findFirstRoot(fct[mode.family], args=(wl, mode.nu),
                                   lowbound=lowbound-delta,
                                   highbound=highbound+delta,
                                   delta=-delta)

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
        EH = numpy.empty(4)
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH, False)
            ri = ro

        # Last layer
        _, Hz, Ep, _ = EH
        u = self.fiber.layers[-1].u(ri, neff, wl)

        F4 = k1(u) / k0(u)
        return Ep + wl.k0 * ri / u * constants.eta0 * Hz * F4

    def _tmceq(self, neff, wl, nu):
        N = len(self.fiber)
        EH = numpy.empty(4)
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH, True)
            ri = ro

        # Last layer
        Ez, _, _, Hp = EH
        u = self.fiber.layers[-1].u(ri, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = k1(u) / k0(u)
        return Hp - wl.k0 * ri / u * constants.Y0 * n * n * Ez * F4

    def _heceq(self, neff, wl, nu):
        N = len(self.fiber)
        EH = numpy.empty((4, 2))
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH)
            ri = ro

        # Last layer
        u = self.fiber.layers[N-1].u(ri, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = kvp(nu, u) / kn(nu, u)
        c1 = -wl.k0 * ri / u
        c2 = neff * nu / u * c1
        c3 = constants.eta0 * c1
        c4 = constants.Y0 * n * n * c1

        E = EH[2, :] - (c2 * EH[0, :] - c3 * F4 * EH[1, :])
        H = EH[3, :] - (c4 * F4 * EH[0, :] - c2 * EH[1, :])
        return E[0]*H[1] - E[1]*H[0]

    _ehceq = _heceq
