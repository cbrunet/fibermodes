
from .solver import FiberSolver
from fibermodes import Mode, ModeFamily
from math import sqrt
import numpy
from scipy.special import jn, jn_zeros, kn, j0, j1, k0, k1, jvp, kvp


class Cutoff(FiberSolver):

    """Cutoff for standard step-index fiber."""

    def __call__(self, mode, delta):
        nu = mode.nu
        m = mode.m

        if mode.family is ModeFamily.LP:
            if nu == 0:
                    nu = 1
                    m -= 1
            else:
                nu -= 1
        elif mode.family is ModeFamily.HE:
            if nu == 1:
                m -= 1
            else:
                return self._findHEcutoff(mode, delta)

        return jn_zeros(nu, m)[m-1]

    def _cutoffHE(self, V0, nu):
        wl = self.fiber.toWl(V0)
        n02 = self.fiber.maxIndex(0, wl)**2 / self.fiber.minIndex(1, wl)**2
        return (1+n02) * jn(nu-2, V0) - (1-n02) * jn(nu, V0)

    def _findHEcutoff(self, mode, delta):
        if mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m - 1)
            lowbound = self.fiber.cutoff(pm, delta) + delta
        else:
            lowbound = delta
        ipoints = numpy.concatenate((jn_zeros(mode.nu, mode.m),
                                     jn_zeros(mode.nu-2, mode.m)))
        ipoints.sort()
        ipoints = list(ipoints[ipoints > lowbound])
        return self._findFirstRoot(self._cutoffHE,
                                   args=(mode.nu,),
                                   lowbound=lowbound,
                                   ipoints=ipoints,
                                   delta=delta)


class Neff(FiberSolver):

    """neff for standard step-index fiber"""

    def __call__(self, wl, mode, delta, lowbound):
        co = self.fiber.cutoff(mode)
        if self.fiber.V0(wl) < co:
            return float("nan")

        nco = self.fiber.maxIndex(0, wl)
        r = self.fiber.outerRadius(0)
        highbound = sqrt(nco**2 - (co / (r * wl.k0))**2) - delta

        if mode.family is ModeFamily.LP:
            nm = Mode(ModeFamily.LP, mode.nu+1, mode.m)
        elif mode.family is ModeFamily.HE:
            nm = Mode(ModeFamily.LP, mode.nu, mode.m)
        elif mode.family is ModeFamily.EH:
            nm = Mode(ModeFamily.LP, mode.nu+2, mode.m)
        else:
            nm = Mode(ModeFamily.LP, 1, mode.m+1)
        co = self.fiber.cutoff(nm)
        lowbound = max(sqrt(nco**2 - (co / (r * wl.k0))**2) + delta,
                       self.fiber.minIndex(-1, wl) + delta)

        fct = {ModeFamily.LP: self._lpceq,
               ModeFamily.TE: self._teceq,
               ModeFamily.TM: self._tmceq,
               ModeFamily.HE: self._heceq,
               ModeFamily.EH: self._ehceq
               }

        return self._findBetween(fct[mode.family], lowbound, highbound,
                                 args=(wl, mode.nu))

    def _uw(self, wl, neff):
        r = self.fiber.outerRadius(0)
        rk0 = r * wl.k0
        return (rk0 * sqrt(self.fiber.maxIndex(0, wl)**2 - neff**2),
                rk0 * sqrt(neff**2 - self.fiber.minIndex(1, wl)**2))

    def _lpceq(self, neff, wl, nu):
        u, w = self._uw(wl, neff)
        return (u * jn(nu - 1, u) * kn(nu, w) +
                w * jn(nu, u) * kn(nu - 1, w))

    def _teceq(self, neff, wl, nu):
        u, w = self._uw(wl, neff)
        return u * j0(u) * k1(w) + w * j1(u) * k0(w)

    def _tmceq(self, neff, wl, nu):
        u, w = self._uw(wl, neff)
        nco = self.fiber.maxIndex(0, wl)
        ncl = self.fiber.minIndex(1, wl)
        return (u * j0(u) * k1(w) * ncl**2 +
                w * j1(u) * k0(w) * nco**2)

    def _heceq(self, neff, wl, nu):
        u, w = self._uw(wl, neff)
        v2 = u*u + w*w
        nco = self.fiber.maxIndex(0, wl)
        ncl = self.fiber.minIndex(1, wl)
        delta = (1 - ncl**2 / nco**2) / 2
        jnu = jn(nu, u)
        knu = kn(nu, w)
        kp = kvp(nu, w)

        return (jvp(nu, u) * w * knu +
                kp * u * jnu * (1 - delta) +
                jnu * sqrt((u * kp * delta)**2 +
                           ((nu * neff * v2 * knu) /
                            (nco * u * w))**2))

    def _ehceq(self, neff, wl, nu):
        u, w = self._uw(wl, neff)
        v2 = u*u + w*w
        nco = self.fiber.maxIndex(0, wl)
        ncl = self.fiber.minIndex(1, wl)
        delta = (1 - ncl**2 / nco**2) / 2
        jnu = jn(nu, u)
        knu = kn(nu, w)
        kp = kvp(nu, w)

        return (jvp(nu, u) * w * knu +
                kp * u * jnu * (1 - delta) -
                jnu * sqrt((u * kp * delta)**2 +
                           ((nu * neff * v2 * knu) /
                            (nco * u * w))**2))
