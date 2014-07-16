"""Standard Step-Index Fiber module."""

from .fiber import Fiber
from ..mode import Family
from ..wavelength import Wavelength

from math import sqrt
import numpy
from scipy.special import jn, kn, j0, j1, k0, k1, jvp, kvp
from scipy.special import jn_zeros
from scipy.optimize import brentq


class SSIF(Fiber):

    """Standard Step-Index Fiber class.
    See :class:`~fibermodes.fiber.fiber.Fiber`
    for details on available methods.

    """

    @property
    def NA(self):
        """Numerical aperture, given by :math:`NA = \sqrt{n_1^2 - n_2^2}`."""
        return sqrt(self._n[0]*self._n[0] - self._n[1]*self._n[1])

    @property
    def V0(self):
        """Normalized frequency, given by
        :math:`V_0 = k_0 \\rho \sqrt{n_1^2 - n_2^2}`.

        """
        return self._wl.k0 * self._r[0] * self.NA

    def _u(self, neff):
        return self._r[0] * self._wl.k0 * sqrt(self._n[0]**2 - neff**2)

    def _w(self, neff):
        return self._r[0] * self._wl.k0 * sqrt(neff**2 - self._n[1]**2)

    def _lpceq(self, neff, mode):
        u = self._u(neff)
        w = self._w(neff)
        return (u * jn(mode.ell - 1, u) * kn(mode.ell, w) +
                w * jn(mode.ell, u) * kn(mode.ell - 1, w))

    def _teceq(self, neff, mode):
        u = self._u(neff)
        w = self._w(neff)
        return u * j0(u) * k1(w) + w * j1(u) * k0(w)

    def _tmceq(self, neff, mode):
        u = self._u(neff)
        w = self._w(neff)
        return (u * j0(u) * k1(w) * self._n[1]**2 +
                w * j1(u) * k0(w) * self._n[0]**2)

    def _heceq(self, neff, mode):
        u = self._u(neff)
        w = self._w(neff)
        v2 = u*u + w*w
        delta = (1 - self._n[1]**2 / self._n[0]**2) / 2

        return (jvp(mode.nu, u) * w * kn(mode.nu, w) +
                kvp(mode.nu, w) * u * jn(mode.nu, u) * (1 - delta) +
                jn(mode.nu, u) * sqrt((u * kvp(mode.nu, w) * delta)**2 +
                                      ((mode.nu * neff * v2 * kn(mode.nu, w)) /
                                       (self._n[0] * u * w))**2))

    def _ehceq(self, neff, mode):
        u = self._u(neff)
        w = self._w(neff)
        v2 = u*u + w*w
        delta = (1 - self._n[1]**2 / self._n[0]**2) / 2

        return (jvp(mode.nu, u) * w * kn(mode.nu, w) +
                kvp(mode.nu, w) * u * jn(mode.nu, u) * (1 - delta) -
                jn(mode.nu, u) * sqrt((u * kvp(mode.nu, w) * delta)**2 +
                                      ((mode.nu * neff * v2 * kn(mode.nu, w)) /
                                       (self._n[0] * u * w))**2))

    def cutoffV0(self, mode):
        """Give `V0` parameter at cutoff, for given mode.

        :param mode: :class:`~fibermodes.mode.Mode` object

        """
        if mode.family == Family.LP:
            if mode.nu == 0:
                if mode.m == 1:
                    V0 = 0
                else:
                    V0 = jn_zeros(1, mode.m-1)[mode.m-2]
            else:
                V0 = jn_zeros(mode.nu-1, mode.m)[mode.m-1]

        elif mode.family == Family.HE:
            if mode.nu == 1:
                if mode.m == 1:
                    V0 = 0
                else:
                    V0 = jn_zeros(1, mode.m-1)[mode.m-2]
            else:
                V0 = self._cutoffV0HE(mode)
        elif mode.family == Family.EH:
            V0 = jn_zeros(mode.nu, mode.m)[mode.m-1]
        else:
            V0 = jn_zeros(mode.nu, mode.m)[mode.m-1]
        return V0

    def _cutoffHE(self, V0, nu, n02):
        return (1+n02) * jn(nu-2, V0) - (1-n02) * jn(nu, V0)

    def _cutoffV0HE(self, mode):
        """Cutoff for HE(nu,m) modes."""
        z1 = jn_zeros(mode.nu, mode.m)
        z2 = jn_zeros(mode.nu-2, mode.m)
        z = numpy.concatenate((z1, z2))
        z.sort()
        j2 = jn(mode.nu, z)
        j0 = jn(mode.nu-2, z)
        n02 = self._n[0]**2 / self._n[1]**2
        f = (1+n02) * j0 - (1-n02) * j2

        j = 0
        for i in range(len(z)-1):
            a = f[i]
            b = f[i+1]
            if (a > 0 and b < 0) or (a < 0 and b > 0):
                j += 1
            if j == mode.m:
                return brentq(self._cutoffHE, z[i], z[i+1],
                              args=(mode.nu, n02))

    def cutoffWl(self, mode):
        """Return the cutoff wavelength of given mode.

        :param mode: :class:`~fibermodes.mode.Mode` object

        """
        return Wavelength(k0=self.cutoffV0(mode) / self.NA / self._r[0])
