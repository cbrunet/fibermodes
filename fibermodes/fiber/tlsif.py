"""Three-layers step-index fiber module."""

from .mlsif import MLSIF
from ..mode import Family

import numpy
from scipy.optimize import brentq
from scipy.special import jn, yn, iv, kn, j0, y0, i0, k0, j1, y1, i1, k1
from scipy.special import jvp, ivp
from math import sqrt


class TLSIF(MLSIF):

    """Three-layers step-index fiber class.

    This inherits from :class:`~fibermodes.fiber.mlsif.MLSIF`, adding
    cutoff calculation to it. You usually do not need to instanciate directly
    this class, as :class:`~fibermodes.fiber.factory.Factory` will do it for
    you.

    .. seealso:: Documentation of :class:`~fibermodes.fiber.fiber.Fiber` class.

    """

    @property
    def rho(self):
        """Ratio between first and second layer radius.

        If rho is 0, then the fiber is a standard two-layers step-index fiber.
        If rho approaches 1, then the fiber middle layer thickness approaches
        zero.
        """
        return self._r[0] / self._r[1]

    def _coeq(self, mode):
        """Cutoff equation."""
        M = {Family.LP: self._lpcoeq,
             Family.TE: self._tecoeq,
             Family.TM: self._tmcoeq,
             Family.HE: self._hecoeq,
             Family.EH: self._ehcoeq
             }
        return M[mode.family]

    def cutoffV0(self, mode, V0min=2, V0max=float('inf'), delta=0.25):
        """Gives cutoff of given mode, in term of V0.

        The search begins at V0min, and step-increment by delta until it
        finds a root. By default, the function finds the first root (i.e.
        for m=1, excepted for HE(1,2)). Usually, you find the first root,
        then you specify a higher value for V0min, based on the previous
        root, to find the next root (i.e. cutoff for the next value of m).

        :param mode: :class:`~fibermodes.mode.Mode` object.
        :param V0min: Minimal value for returned V0 (dafault: 2).
        :type V0min: integer
        :param V0max: Maximal value for returned V0 (default: inf).
        :type V0max: integer
        :param delta: Increment used for searching roots (default: 0.25).
                      Decrease it if it is not able to find a given cutoff.
                      Increase it to et faster calculation.
        :type delta: float
        :rtype: float

        """
        nu = mode.nu
        fct = self._coeq(mode)

        v0a = V0min
        fa = fct(v0a, nu)
        v0b = V0min + delta
        fb = fct(v0b, nu)
        while v0b < V0max:
            if (fa > 0 and fb < 0) or (fa < 0 and fb > 0):
                r = brentq(fct, v0a, v0b, args=(nu))
                cr = abs(fct(r, nu))
                if (abs(fa) > cr) and (abs(fb) > cr):
                    return r
            v0a = v0b
            fa = fb
            v0b += delta
            fb = fct(v0b, nu)

    def __params(self, v0):
        r1, r2, _ = self._r
        Nsq = numpy.square(self._n)
        n1sq, n2sq, n3sq = Nsq
        k0 = v0 / (self.na * r2)
        Usq = [k0**2 * (nsq - n3sq) for nsq in Nsq]
        s1, s2, s3 = numpy.sign(Usq)
        u1, u2, u3 = numpy.sqrt(numpy.abs(Usq))
        return u1*r1, u2*r1, u2*r2, s1, s2, n1sq, n2sq, n3sq

    def __delta(self, nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq):
        if s1 < 0:
            f = ivp(nu, u1r1) / iv(nu, u1r1) / u1r1  # c
        else:
            f = jvp(nu, u1r1) / jn(nu, u1r1) / u1r1  # a b d

        if s1 == s2:
            # b d
            kappa1 = -(n1sq + n2sq) * f / n2sq
            kappa2 = (n1sq * f * f / n2sq -
                      nu**2 * n3sq / n2sq * (1 / u1r1**2 - 1 / u2r1**2)**2)
        else:
            # a c
            kappa1 = (n1sq + n2sq) * f / n2sq
            kappa2 = (n1sq * f * f / n2sq -
                      nu**2 * n3sq / n2sq * (1 / u1r1**2 + 1 / u2r1**2)**2)

        d = kappa1**2 - 4 * kappa2
        if d < 0:
            return numpy.nan
        return u2r1 * (nu / u2r1**2 + (kappa1 + s3 * sqrt(d)) * 0.5)

    def _lpcoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)

        if s1 == 0:  # e
            return (jn(nu+1, u2r1) * yn(nu-1, u2r2) -
                    yn(nu+1, u2r1) * jn(nu-1, u2r2))

        (f11a, f11b) = ((jn(nu-1, u1r1), jn(nu, u1r1)) if s1 > 0 else
                        (iv(nu-1, u1r1), iv(nu, u1r1)))
        if s2 > 0:
            f22a, f22b = jn(nu-1, u2r2), yn(nu-1, u2r2)
            f2a = jn(nu, u2r1) * f22b - yn(nu, u2r1) * f22a
            f2b = jn(nu-1, u2r1) * f22b - yn(nu-1, u2r1) * f22a
        else:  # a
            f22a, f22b = iv(nu-1, u2r2), kn(nu-1, u2r2)
            f2a = iv(nu, u2r1) * f22b + kn(nu, u2r1) * f22a
            f2b = iv(nu-1, u2r1) * f22b - kn(nu-1, u2r1) * f22a
        return f11a * f2a * u1r1 - f11b * f2b * u2r1

    def _tecoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)
        (f11a, f11b) = ((j0(u1r1), jn(2, u1r1)) if s1 > 0 else
                        (i0(u1r1), -iv(2, u1r1)))
        if s2 > 0:
            f22a, f22b = j0(u2r2), y0(u2r2)
            f2a = jn(2, u2r1) * f22b - yn(2, u2r1) * f22a
            f2b = j0(u2r1) * f22b - y0(u2r1) * f22a
        else:  # a
            f22a, f22b = i0(u2r2), k0(u2r2)
            f2a = kn(2, u2r1) * f22a - iv(2, u2r1) * f22b
            f2b = i0(u2r1) * f22b - k0(u2r1) * f22a
        return f11a * f2a - f11b * f2b

    def _tmcoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)
        if s1 == 0:  # e
            f11a, f11b = 2, 1
        elif s1 > 0:  # a, b, d
            f11a, f11b = j0(u1r1) * u1r1, j1(u1r1)
        else:  # c
            f11a, f11b = i0(u1r1) * u1r1, i1(u1r1)
        if s2 > 0:
            f22a, f22b = j0(u2r2), y0(u2r2)
            f2a = j1(u2r1) * f22b - y1(u2r1) * f22a
            f2b = j0(u2r1) * f22b - y0(u2r1) * f22a
        else:  # a
            f22a, f22b = i0(u2r2), k0(u2r2)
            f2a = i1(u2r1) * f22b + k1(u2r1) * f22a
            f2b = i0(u2r1) * f22b - k0(u2r1) * f22a
        return f11a * n2sq * f2a - f11b * n1sq * f2b * u2r1

    def _ehcoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)
        if s1 == 0:
            delta0 = (n2sq - n3sq) / (n3sq + n2sq)
        else:
            s3 = 1 if s1 > 0 and u1r1 < u2r1 else -1
            delta0 = self.__delta(nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq)

        if s1 == 0:  # e
            f22a, f22b = jn(nu, u2r2), yn(nu, u2r2)
            f2a = jn(nu+2, u2r1) * f22b - yn(nu+2, u2r1) * f22a
            f2b = jn(nu, u2r1) * f22b - yn(nu, u2r1) * f22a
        elif s2 > 0:  # b c d
            f22a, f22b = jn(nu, u2r2), yn(nu, u2r2)
            f2a = jn(nu+1, u2r1) * f22b - yn(nu+1, u2r1) * f22a
            f2b = jn(nu, u2r1) * f22b - yn(nu, u2r1) * f22a
        else:  # a
            f22a, f22b = iv(nu, u2r2), kn(nu, u2r2)
            f2a = iv(nu+1, u2r1) * f22b + kn(nu+1, u2r1) * f22a
            f2b = -iv(nu, u2r1) * f22b + kn(nu, u2r1) * f22a

        return f2a - delta0 * f2b

    def _hecoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)
        if s1 == 0:  # e
            f21a, f21b = jn(nu, u2r1), yn(nu, u2r1)
        else:
            s3 = -1 if s1 > 0 and u1r1 < u2r1 else 1
            delta0 = self.__delta(nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq)
            if s2 > 0:
                f21a = jn(nu, u2r1) * delta0 - jn(nu+1, u2r1)
                f21b = yn(nu, u2r1) * delta0 - yn(nu+1, u2r1)
            else:
                f21a = iv(nu, u2r1) * delta0 + iv(nu+1, u2r1)
                f21b = kn(nu, u2r1) * delta0 - kn(nu+1, u2r1)
        n0sq = (n3sq - n2sq) / (n2sq + n3sq)

        if s2 > 0:  # a
            f2a = jn(nu-2, u2r2) * f21b - yn(nu-2, u2r2) * f21a
            f2b = jn(nu, u2r2) * f21b - yn(nu, u2r2) * f21a
        else:
            f2a = iv(nu-2, u2r2) * f21b - kn(nu-2, u2r2) * f21a
            f2b = -iv(nu, u2r2) * f21b + kn(nu, u2r2) * f21a

        return f2a - n0sq * f2b
