"""Annular-core step-index fiber, model 2, module."""

from .acsif import ACSIF
from ..mode import Family

from math import sqrt
import numpy
from scipy.optimize import brentq
from scipy.special import j0, y0, j1, y1, i0, jn, yn, iv, kn
from scipy.special import ivp, jvp, yvp, kvp
from scipy.special import jnyn_zeros


class AC2SIF(ACSIF):

    """Annular-core step-index fiber class."""

    def cutoffV0(self, mode):

        if mode.family == Family.TE:
            fct = self._cutoffTE
            j = 0
        elif mode.family == Family.TM:
            fct = self._cutoffTM
            j = 0
        elif mode.family == Family.EH:
            fct = self._cutoffEH
            j = 0
        else:
            if mode.nu == 1 and mode.m == 1 and mode.family == Family.HE:
                return 0
            j = 0
            fct = self._cutoffEH

        z = 2
        delta = 0.1

        b = fct(z, mode.nu)
        while 1:
            a = b
            b = fct(z + delta, mode.nu)
            if (a > 0 and b < 0) or (a < 0 and b > 0):
                j += 1
                if ((j == mode.m and mode.family in (Family.TE, Family.TM)) or
                        (j % 2 == 0 and 2 * (mode.m - 1) == j and
                         mode.family == Family.HE) or
                        (j % 2 == 1 and 2 * mode.m - 1 == j and
                         mode.family == Family.EH)):
                    return brentq(fct, z, z + delta,
                                  args=(mode.nu))
            z += delta
            if z > 10:
                return -1

    def __getCoParams(self, V0, nu):
        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        n32 = self._n[2] * self._n[2]

        u2a = self.rho * V0
        u1a = u2a * sqrt((n32 - n12) / (n22 - n32))

        i = ivp(nu, u1a) / (u1a * iv(nu, u1a))

        ja = jn(nu, u2a)
        na = yn(nu, u2a)
        jb = jn(nu, V0)
        nb = yn(nu, V0)

        F = ja * nb - jb * na
        Fp = jvp(nu, u2a) * nb - jb * yvp(nu, u2a)

        return i, F, Fp / u2a, u1a, u2a

    def _cutoffTE(self, V0, nu):
        i, f, fp, _, _ = self.__getCoParams(V0, nu)
        return fp + i * f

    def _cutoffTM(self, V0, nu):
        i, f, fp, _, _ = self.__getCoParams(V0, nu)
        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        return n22 * fp + n12 * i * f

    def _cutoffLP(self, V0, ell):
        i, f, fp, u1a, u2a = self.__getCoParams(V0, ell-1)
        return fp + i * f - (u1a**-2 + u2a**-2) * (ell - 1) * f

    def _cutoffEH(self, V0, nu):
        i, f, fp, u1a, u2a = self.__getCoParams(V0, nu)
        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        n32 = self._n[2] * self._n[2]
        return ((fp / f + i) * (n22 * fp / f + n12 * i) -
                (u1a**-2 + u2a**-2)**2 * nu * nu * n32)

    def _cutoffHE(self, V0, nu):
        n12 = self._n[0] * self._n[0]
        n22 = self._n[1] * self._n[1]
        n32 = self._n[2] * self._n[2]

        u2a = self.rho * V0
        u1a = u2a * sqrt((n32 - n12) / (n22 - n32))

        k0 = self._wl.k0
        beta = self._wl.k0 * self._n[2]
        X = (1 / u1a**2 + 1 / u2a**2) * nu * beta
        i = ivp(nu, u1a) / (u1a * iv(nu, u1a))

        ja = jn(nu, u2a)
        jap = jvp(nu, u2a) / u2a
        na = yn(nu, u2a)
        nap = yvp(nu, u2a) / u2a
        jb = jn(nu, V0)
        nb = yn(nu, V0)

        M = numpy.empty((4, 4))
        M[0, 0] = X * ja
        M[0, 1] = X * na
        M[0, 2] = -k0 * (jap + i * ja)
        M[0, 3] = -k0 * (nap + i * na)

        M[1, 0] = -k0 * (n22 * jap + n12 * i * ja)
        M[1, 1] = -k0 * (n22 * nap + n12 * i * na)
        M[1, 2] = X * ja
        M[1, 3] = X * na

        M[2, 0] = ((2 * nu * (nu - 1) * n32 / V0**2 - 2 * n32 + n22) * jb +
                   n22 * jn(nu-2, V0))
        M[2, 1] = ((2 * nu * (nu - 1) * n32 / V0**2 - 2 * n32 + n22) * nb +
                   n22 * yn(nu-2, V0))
        M[2, 2] = ((2 * nu * (nu - 1) * self._n[2] / V0**2 - self._n[2]) * jb -
                   self._n[2] * jn(nu - 2, V0))
        M[2, 3] = ((2 * nu * (nu - 1) * self._n[2] / V0**2 - self._n[2]) * nb -
                   self._n[2] * yn(nu - 2, V0))

        M[3, 0] = ((2 * nu * (nu - 1) * n22 / V0**2 - n32) * jb +
                   n32 * jn(nu-2, V0))
        M[3, 1] = ((2 * nu * (nu - 1) * n32 / V0**2 - n32) * nb +
                   n32 * yn(nu-2, V0))
        M[3, 2] = ((2 * nu * (nu - 1) * n22 * self._n[2] / V0**2 -
                    n22 * self._n[2]) * jb -
                   n22 * self._n[2] * jn(nu - 2, V0))
        M[3, 3] = ((2 * nu * (nu - 1) * self._n[2] / V0**2 - self._n[2]) * nb -
                   self._n[2] * yn(nu - 2, V0))

        return numpy.linalg.det(M)
