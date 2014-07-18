"""Annular-core step-index fiber module."""

from .mlsif import MLSIF
from ..wavelength import Wavelength
from ..mode import Family

from math import sqrt
import numpy
from scipy.special import j0, y0, j1, y1, jn, yn, jnyn_zeros
from scipy.optimize import brentq


class ACSIF(MLSIF):

    """Annular-core step-index fiber class."""

    @property
    def NA(self):
        """Numerical aperture, given by :math:`NA = \sqrt{n_1^2 - n_2^2}`."""
        return sqrt(self._n[1]*self._n[1] - self._n[2]*self._n[2])

    @property
    def V0(self):
        """Normalized frequency, given by
        :math:`V_0 = k_0 b \sqrt{n_1^2 - n_2^2}`.

        """
        return self._wl.k0 * self._r[1] * self.NA

    @property
    def rho(self):
        return self._r[0] / self._r[1]

    def _cutoffTE(self, V0, nu, n02):
        ua = self.rho * V0
        return j0(V0) * yn(2, ua) - y0(V0) * jn(2, ua)

    def _cutoffTM(self, V0, nu, n02):
        ua = self.rho * V0
        return (j0(V0) * yn(2, ua) - y0(V0) * jn(2, ua) -
                (1 - n02) / n02 * (j0(V0) * y0(ua) - j0(ua) * y0(V0)))

    def _cutoffHE(self, V0, nu, n02):
        ua = self.rho * V0
        if nu == 1:
            return j1(V0) * y1(ua) - j1(ua) * y1(V0)
        else:
            return (jn(nu-2, V0) * yn(nu, ua) - jn(nu, ua) * yn(nu-2, V0) -
                    (1 - n02) / (1 + n02) * (jn(nu, V0) * yn(nu, ua) -
                                             jn(nu, ua) * yn(nu, V0)))

    def _cutoffEH(self, V0, nu, n02):
        ua = self.rho * V0
        return (jn(nu+2, ua) * yn(nu, V0) - jn(nu, V0) * yn(nu+2, ua) +
                (1 - n02) / (1 + n02) * (jn(nu, ua) * yn(nu, V0) -
                                         jn(nu, V0) * yn(nu, ua)))

    def cutoffV0(self, mode):
        n02 = (self._n[1] * self._n[1]) / (self._n[2] * self._n[2])
        if mode.family == Family.TE:
            zj0, _, zy0, _ = jnyn_zeros(0, mode.m+2)
            zj2, _, zy2, _ = jnyn_zeros(2, mode.m+2)
            fct = self._cutoffTE
            j = 0
        elif mode.family == Family.TM:
            zj0, _, zy0, _ = jnyn_zeros(0, mode.m+2)
            zj2, _, zy2, _ = jnyn_zeros(2, mode.m+2)
            fct = self._cutoffTM
            j = 0
        elif mode.family == Family.HE:
            zj0, _, zy0, _ = jnyn_zeros(mode.nu, mode.m+2)
            if mode.nu == 1:
                if mode.m == 1:
                    return 0
                zj2, zy2 = numpy.ndarray(0), numpy.ndarray(0)
                j = 1
            else:
                zj2, _, zy2, _ = jnyn_zeros(mode.nu-2, mode.m+2)
                j = 0
            fct = self._cutoffHE
        elif mode.family == Family.EH:
            zj0, _, zy0, _ = jnyn_zeros(mode.nu, mode.m+2)
            zj2, _, zy2, _ = jnyn_zeros(mode.nu+2, mode.m+2)
            fct = self._cutoffEH
            j = 0
        z = numpy.concatenate((zj0, zy0, zj2, zy2))
        z.sort()

        b = fct(z[0], mode.nu, n02)
        for i in range(len(z)-1):
            a = b
            b = fct(z[i+1], mode.nu, n02)
            if (a > 0 and b < 0) or (a < 0 and b > 0):
                j += 1
            if j == mode.m:
                return brentq(fct, z[i], z[i+1],
                              args=(mode.nu, n02))

    def cutoffWl(self, mode):
        """Return the cutoff wavelength of given mode.

        :param mode: :class:`~fibermodes.mode.Mode` object

        """
        return Wavelength(k0=self.cutoffV0(mode) / self.NA / self._r[1])
