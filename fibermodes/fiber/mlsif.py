"""Multi-Layers Step-Index Fiber module."""

from .fiber import Fiber
from ..constants import pi

import numpy
from math import log10
from scipy.special import jn, kn, iv, yn, jvp, kvp, ivp, yvp


class MLSIF(Fiber):

    """Multi-Layers Step-Index Fiber class."""

    def _lpceq(self, neff, mode):
        N = self._n.size
        u = self._wl.k0 * self._r * numpy.sqrt(numpy.abs(self._n**2 - neff**2))

        C = numpy.zeros((N, 2))
        C[0, 0] = 1

        for i in range(N - 2):
            u1 = u[i]
            u1r = u1 * self._r[i+1]
            u2r = u[i+1] * self._r[i]
            u2 = u2r / self._r[i+1]

            if neff < self._n[i]:
                F1 = C[i, 0] * jn(mode.nu, u1) + C[i, 1] * yn(mode.nu, u1)
                F1p = C[i, 0] * jvp(mode.nu, u1) + C[i, 1] * yvp(mode.nu, u1)
            else:
                F1 = C[i, 0] * iv(mode.nu, u1) + C[i, 1] * kn(mode.nu, u1)
                F1p = C[i, 0] * ivp(mode.nu, u1) + C[i, 1] * kvp(mode.nu, u1)

            if neff < self._n[i+1]:
                c = pi / (2 * self._r[i+1])
                F2 = jn(mode.nu, u2)
                F2p = jvp(mode.nu, u2)
                F3 = yn(mode.nu, u2)
                F3p = yvp(mode.nu, u2)
            else:
                c = 1 / self._r[i+1]
                F2 = iv(mode.nu, u2)
                F2p = ivp(mode.nu, u2)
                F3 = kn(mode.nu, u2)
                F3p = kvp(mode.nu, u2)

            C[i+1, 0] = c * (u2r * F3p * F1 - u1r * F3 * F1p)
            C[i+1, 1] = c * (u1r * F2 * F1p - u2r * F2p * F1)

        # Last layer (cladding)
        i = N - 2
        u1 = u[i]
        u1r = u1 / self._r[i]
        u2 = u[i+1]
        u2r = u2 / self._r[i+1]

        if neff < self._n[i]:
            F1 = C[i, 0] * jn(mode.nu, u1) + C[i, 1] * yn(mode.nu, u1)
            F1p = u1r * (C[i, 0] * jvp(mode.nu, u1) +
                         C[i, 1] * yvp(mode.nu, u1))
        else:
            F1 = C[i, 0] * iv(mode.nu, u1) + C[i, 1] * kn(mode.nu, u1)
            F1p = u1r * (C[i, 0] * ivp(mode.nu, u1) +
                         C[i, 1] * kvp(mode.nu, u1))

        if neff < self._n[i+1]:  # leaky mode
            F2 = jn(mode.nu, u2)
            F2p = jvp(mode.nu, u2)
            F3 = yn(mode.nu, u2)
            F3p = yvp(mode.nu, u2)

            C[i+1, 0] = pi / 2 * (u2 * F3p * F1 - self._r[i] * F3 * F1p)
            C[i+1, 1] = pi / 2 * (self._r[i] * F2 * F1p - u2 * F2p * F1)

            v = ((C[i+1, 0] * F2 + C[i+1, 1] * F3) * F1p -
                 u2r * (C[i+1, 0] * F2p + C[i+1, 1] * F3p) * F1)
            return v
            # if v > 0:
            #     return log10(v**2)
            # else:
            #     return -float('inf')
        else:  # guided mode
            F2 = 0
            F2p = 0
            F3 = kn(mode.nu, u2)
            F3p = kvp(mode.nu, u2)

            C[i+1, 0] = 0
            C[i+1, 1] = F1 / F3
            return u2r * F3p * F1 - F3 * F1p
            # return log10((u2r * F3p * F1 - F3 * F1p)**2)

    def _teceq(self, neff, mode):
        pass

    def _tmceq(self, neff, mode):
        pass

    def _heceq(self, neff, mode):
        pass

    def _ehceq(self, neff, mode):
        pass
