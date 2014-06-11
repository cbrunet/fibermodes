"""Standard Step-Index Fiber module."""

from .fiber import Fiber

from math import sqrt
from scipy.special import jn, kn, j0, j1, k0, k1, jvp, kvp


class SSIF(Fiber):

    """Standard Step-Index Fiber class."""

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
