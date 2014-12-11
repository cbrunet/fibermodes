"""Annular-core step-index fiber module."""

from .mlsif import MLSIF
from ..wavelength import Wavelength
from ..mode import Family

from math import sqrt
import numpy
from scipy.special import j0, y0, j1, y1, jn, yn, jnyn_zeros, iv, kn
from scipy.special import ivp, jvp, yvp, kvp
from scipy.optimize import brentq
from ..constants import eta0


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

    def _heceq(self, neff, mode):
        a = self._r[0]
        b = self._r[1]

        u = self._wl.k0 * numpy.sqrt(numpy.abs(self._n*self._n - neff*neff))
        nubeta = mode.nu * self._wl.k0 * neff

        if 0 in u:
            return float("inf")

        u1a = u[0] * a
        u2a = u[1] * a
        u2b = u[1] * b
        u3b = u[2] * b

        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        n32 = self._n[2] * self._n[2]

        Xnubeta = (1 / u1a**2 + 1 / u2a**2) * nubeta
        Ynubeta = (1 / u2b**2 + 1 / u3b**2) * nubeta

        M = numpy.empty((4, 4))

        Ju2a = jn(mode.nu, u2a)
        Nu2a = yn(mode.nu, u2a)
        Ju2b = jn(mode.nu, u2b)
        Nu2b = yn(mode.nu, u2b)

        Jpu2a = jvp(mode.nu, u2a) / u2a
        Npu2a = yvp(mode.nu, u2a) / u2a
        Jpu2b = jvp(mode.nu, u2b) / u2b
        Npu2b = yvp(mode.nu, u2b) / u2b

        I = ivp(mode.nu, u1a) / (u1a * iv(mode.nu, u1a))
        K = kvp(mode.nu, u3b) / (u3b * kn(mode.nu, u3b))

        M[0, 0] = Xnubeta * Ju2a
        M[0, 1] = Xnubeta * Nu2a
        M[0, 2] = -self._wl.k0 * (Jpu2a + I * Ju2a)
        M[0, 3] = -self._wl.k0 * (Npu2a + I * Nu2a)
        M[1, 0] = -self._wl.k0 * (n22 * Jpu2a + n12 * I * Ju2a)
        M[1, 1] = -self._wl.k0 * (n22 * Npu2a + n12 * I * Nu2a)
        M[1, 2] = M[0, 0]
        M[1, 3] = M[0, 1]
        M[2, 0] = Ynubeta * Ju2b
        M[2, 1] = Ynubeta * Nu2b
        M[2, 2] = -self._wl.k0 * (Jpu2b + K * Ju2b)
        M[2, 3] = -self._wl.k0 * (Npu2b + K * Nu2b)
        M[3, 0] = -self._wl.k0 * (n22 * Jpu2b + n32 * K * Ju2b)
        M[3, 1] = -self._wl.k0 * (n22 * Npu2b + n32 * K * Nu2b)
        M[3, 2] = M[2, 0]
        M[3, 3] = M[2, 1]

        return numpy.linalg.det(M)

    def _constants(self, neff, mode):
        a = self._r[0]
        b = self._r[1]

        u = self._wl.k0 * numpy.sqrt(numpy.abs(self._n*self._n - neff*neff))
        nubeta = mode.nu * self._wl.k0 * neff

        if 0 in u:
            return float("inf")

        u1a = u[0] * a
        u2a = u[1] * a
        u2b = u[1] * b
        u3b = u[2] * b

        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        n32 = self._n[2] * self._n[2]

        Xnubeta = (1 / u1a**2 + 1 / u2a**2) * nubeta
        Ynubeta = (1 / u2b**2 + 1 / u3b**2) * nubeta

        M = numpy.empty((4, 4))

        Ju2a = jn(mode.nu, u2a)
        Nu2a = yn(mode.nu, u2a)
        Ju2b = jn(mode.nu, u2b)
        Nu2b = yn(mode.nu, u2b)

        Jpu2a = jvp(mode.nu, u2a) / u2a
        Npu2a = yvp(mode.nu, u2a) / u2a
        Jpu2b = jvp(mode.nu, u2b) / u2b
        Npu2b = yvp(mode.nu, u2b) / u2b

        Iu1a = iv(mode.nu, u1a)
        Ku3b = kn(mode.nu, u3b)
        I = ivp(mode.nu, u1a) / (u1a * Iu1a)
        K = kvp(mode.nu, u3b) / (u3b * Ku3b)

        M[0, 0] = Xnubeta * Ju2a
        M[0, 1] = Xnubeta * Nu2a
        M[0, 2] = -self._wl.k0 * (Jpu2a + I * Ju2a)
        M[0, 3] = -self._wl.k0 * (Npu2a + I * Nu2a)
        M[1, 0] = -self._wl.k0 * (n22 * Jpu2a + n12 * I * Ju2a)
        M[1, 1] = -self._wl.k0 * (n22 * Npu2a + n12 * I * Nu2a)
        M[1, 2] = M[0, 0]
        M[1, 3] = M[0, 1]
        M[2, 0] = Ynubeta * Ju2b
        M[2, 1] = Ynubeta * Nu2b
        M[2, 2] = -self._wl.k0 * (Jpu2b + K * Ju2b)
        M[2, 3] = -self._wl.k0 * (Npu2b + K * Nu2b)
        M[3, 0] = -self._wl.k0 * (n22 * Jpu2b + n32 * K * Ju2b)
        M[3, 1] = -self._wl.k0 * (n22 * Npu2b + n32 * K * Nu2b)
        M[3, 2] = M[2, 0]
        M[3, 3] = M[2, 1]

        coefs = numpy.linalg.solve(numpy.dot(M[:, 1:].T, M[:, 1:]),
                                   -numpy.dot(M[:, 1:].T, M[:, 0]))

        C1 = (Ju2a + coefs[0] * Nu2a) / Iu1a
        C2 = (coefs[1] * Ju2a + coefs[2] * Nu2a) / Iu1a / eta0

        D1 = (Ju2b + coefs[0] * Nu2b) / Ku3b
        D2 = (coefs[1] * Ju2b + coefs[2] * Nu2b) / Ku3b / eta0

        return numpy.array([C1, 0, C2, 0,
                            1, coefs[0], coefs[1] / eta0, coefs[2] / eta0,
                            0, D1, 0, D2])

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
