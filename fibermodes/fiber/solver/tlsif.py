
from .solver import FiberSolver
from fibermodes import Mode, ModeFamily
from fibermodes.fiber.material.material import OutOfRangeWarning
from math import sqrt
import numpy
from scipy.special import j0, y0, i0, k0
from scipy.special import j1, y1, i1, k1
from scipy.special import jn, yn, iv, kn
from scipy.special import jvp, ivp
import warnings


class TLSIFSolver(FiberSolver):

    def _cutoff(self, mode):
        delta = 0.25
        fct = {ModeFamily.LP: self._lpcoeq,
               ModeFamily.TE: self._tecoeq,
               ModeFamily.TM: self._tmcoeq,
               ModeFamily.HE: self._hecoeq,
               ModeFamily.EH: self._ehcoeq
               }
        if mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m - 1)
            lowbound = self.cutoff(pm) + delta
        else:
            lowbound = delta
        return self._findFirstRoot(fct[mode.family],
                                   args=(mode.nu,),
                                   lowbound=lowbound,
                                   delta=delta)

    def __params(self, v0):
        with warnings.catch_warnings():
            # ignore OutOfRangeWarning; it will occur elsewhere anyway
            warnings.simplefilter("ignore", category=OutOfRangeWarning)
            wl = self.fiber.toWl(v0)
            r1, r2 = self.fiber._r
            Nsq = numpy.square(numpy.fromiter(
                               (self.fiber.minIndex(i, wl)
                                for i in range(3)), dtype=float, count=3))
            n1sq, n2sq, n3sq = Nsq
            Usq = [wl.k0**2 * (nsq - n3sq) for nsq in Nsq]
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
            delta0 = (n3sq - n2sq) / (n3sq + n2sq)
        else:
            s3 = 1 if s1 > 0 and u1r1 < u2r1 else -1
            if nu == 1 and n1sq > n2sq > n3sq:
                s3 *= -1
            # s3 = 1 if s1 == s2 and nu == 1 else -1
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
            if nu == 1 and n1sq > n2sq > n3sq:
                s3 *= -1
            # s3 = -1 if s1 == s2 and nu == 1 else 1
            delta0 = self.__delta(nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq)
            if s2 > 0:
                f21a = jn(nu, u2r1) * delta0 - jn(nu+1, u2r1)
                f21b = yn(nu, u2r1) * delta0 - yn(nu+1, u2r1)
            else:
                f21a = iv(nu, u2r1) * delta0 + iv(nu+1, u2r1)
                f21b = kn(nu, u2r1) * delta0 - kn(nu+1, u2r1)
        n0sq = (n3sq - n2sq) / (n2sq + n3sq)

        if s2 > 0:
            f2a = jn(nu-2, u2r2) * f21b - yn(nu-2, u2r2) * f21a
            f2b = jn(nu, u2r2) * f21b - yn(nu, u2r2) * f21a
        else:  # a
            f2a = iv(nu-2, u2r2) * f21b - kn(nu-2, u2r2) * f21a
            f2b = -iv(nu, u2r2) * f21b + kn(nu, u2r2) * f21a

        return f2a - n0sq * f2b
