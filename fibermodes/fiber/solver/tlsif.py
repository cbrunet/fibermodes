#!/usr/bin/env python3

# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

from .solver import FiberSolver
from fibermodes import Mode, ModeFamily, Wavelength, HE11
from fibermodes.fiber.material.material import OutOfRangeWarning
from math import sqrt, isinf, isnan
import numpy
from scipy.special import j0, y0, i0, k0
from scipy.special import j1, y1, i1, k1
from scipy.special import jn, yn, iv, kn
from scipy.special import jvp, ivp
import warnings


class Cutoff(FiberSolver):

    def __call__(self, mode):
        fct = {ModeFamily.LP: self._lpcoeq,
               ModeFamily.TE: self._tecoeq,
               ModeFamily.TM: self._tmcoeq,
               ModeFamily.HE: self._hecoeq,
               ModeFamily.EH: self._ehcoeq
               }
        if mode.m > 1:
            if mode.family is ModeFamily.HE:
                pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
            else:
                pm = Mode(mode.family, mode.nu, mode.m - 1)
            if pm == HE11:
                pm = Mode(ModeFamily.TE, 0, 1)
            elif pm == Mode(ModeFamily.LP, 0, 1):
                pm = Mode(ModeFamily.LP, 1, 1)
            lowbound = self.fiber.cutoff(pm)
            delta = 0.05 / lowbound if lowbound > 4 else self._MCD
            lowbound += delta / 100
        elif mode.family is ModeFamily.EH:
            pm = Mode(ModeFamily.HE, mode.nu, mode.m)
            lowbound = self.fiber.cutoff(pm)
            delta = 0.05 / lowbound if lowbound > 4 else self._MCD
            lowbound += delta / 100
        elif mode.nu > 0:
            # TE(0,1) is single-mode condition
            # Roots below TE(0,1) are false-positive
            pm = Mode(ModeFamily.TE, 0, 1)
            lowbound = self.fiber.cutoff(pm)
            delta = 0.05 / lowbound
            lowbound -= delta / 100
        else:
            lowbound = delta = self._MCD
        if isnan(delta):
            print(lowbound)
        return self._findFirstRoot(fct[mode.family],
                                   args=(mode.nu,),
                                   lowbound=lowbound,
                                   delta=delta,
                                   maxiter=int(250/delta))

    def __params(self, v0):
        with warnings.catch_warnings():
            # ignore OutOfRangeWarning; it will occur elsewhere anyway
            warnings.simplefilter("ignore", category=OutOfRangeWarning)
            r1, r2 = self.fiber._r
            wl = self.fiber.toWl(v0)
            if isinf(wl):
                wl = Wavelength(k0=1)  # because it causes troubles if 0
            Nsq = numpy.square(numpy.fromiter(
                               (self.fiber.minIndex(i, wl)
                                for i in range(3)), dtype=float, count=3))
            n1sq, n2sq, n3sq = Nsq
            if wl == 0:
                # Avoid floating point error. But there should be a
                # way to do it better.
                Usq = [float("inf")]*3
            else:
                Usq = [wl.k0**2 * (nsq - n3sq) for nsq in Nsq]
            s1, s2, s3 = numpy.sign(Usq)
            u1, u2, u3 = numpy.sqrt(numpy.abs(Usq))
            return u1*r1, u2*r1, u2*r2, s1, s2, n1sq, n2sq, n3sq

    def __delta(self, nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq):
        """s3 is sign of Delta"""
        if s1 < 0:
            f = ivp(nu, u1r1) / (iv(nu, u1r1) * u1r1)  # c
        else:
            jnnuu1r1 = jn(nu, u1r1)
            if jnnuu1r1 == 0:  # Avoid zero division error
                return float("inf")
            f = jvp(nu, u1r1) / (jnnuu1r1 * u1r1)  # a b d

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
            return self.__fct3(nu, u2r1, u2r2, 2, n2sq, n3sq)
        else:
            s3 = 1 if s1 == s2 else -1

            # if n1sq > n2sq > n3sq:
            #     # s3 = 1 if nu == 1 else -1
            #     return self.__fct2(nu, u1r1, u2r1, u2r2,
            #                        s1, s2, s3,
            #                        n1sq, n2sq, n3sq)
            # else:
            return self.__fct1(nu, u1r1, u2r1, u2r2,
                               s1, s2, s3,
                               n1sq, n2sq, n3sq)

    def _hecoeq(self, v0, nu):
        u1r1, u2r1, u2r2, s1, s2, n1sq, n2sq, n3sq = self.__params(v0)
        if s1 == 0:
            return self.__fct3(nu, u2r1, u2r2, -2, n2sq, n3sq)
        else:
            s3 = -1 if s1 == s2 else 1
            if n1sq > n2sq > n3sq:
                s3 = -1 if nu == 1 else 1
            #     return self.__fct1(nu, u1r1, u2r1, u2r2,
            #                        s1, s2, s3,
            #                        n1sq, n2sq, n3sq)
            # else:
            return self.__fct2(nu, u1r1, u2r1, u2r2,
                               s1, s2, s3,
                               n1sq, n2sq, n3sq)

    def __fct1(self, nu, u1r1, u2r1, u2r2, s1, s2, s3, n1sq, n2sq, n3sq):
        if s2 < 0:  # a
            b11 = iv(nu, u2r1)
            b12 = kn(nu, u2r1)
            b21 = iv(nu, u2r2)
            b22 = kn(nu, u2r2)
            b31 = iv(nu+1, u2r1)
            b32 = kn(nu+1, u2r1)
            f1 = b31*b22 + b32*b21
            f2 = b11*b22 - b12*b21
        else:
            b11 = jn(nu, u2r1)
            b12 = yn(nu, u2r1)
            b21 = jn(nu, u2r2)
            b22 = yn(nu, u2r2)
            if s1 == 0:
                f1 = 0
            else:
                b31 = jn(nu+1, u2r1)
                b32 = yn(nu+1, u2r1)
                f1 = b31*b22 - b32*b21
            f2 = b12*b21 - b11*b22
        if s1 == 0:
            delta = 1
        else:
            delta = self.__delta(nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq)
        return f1 + f2 * delta

    def __fct2(self, nu, u1r1, u2r1, u2r2, s1, s2, s3, n1sq, n2sq, n3sq):
        with numpy.errstate(invalid='ignore'):
            delta = self.__delta(nu, u1r1, u2r1, s1, s2, s3, n1sq, n2sq, n3sq)
            n0sq = (n3sq - n2sq) / (n2sq + n3sq)
            if s2 < 0:  # a
                b11 = iv(nu, u2r1)
                b12 = kn(nu, u2r1)
                b21 = iv(nu, u2r2)
                b22 = kn(nu, u2r2)
                b31 = iv(nu+1, u2r1)
                b32 = kn(nu+1, u2r1)
                b41 = iv(nu-2, u2r2)
                b42 = kn(nu-2, u2r2)
                g1 = b11 * delta + b31
                g2 = b12 * delta - b32
                f1 = b41*g2 - b42*g1
                f2 = b21*g2 - b22*g1
            else:
                b11 = jn(nu, u2r1)
                b12 = yn(nu, u2r1)
                b21 = jn(nu, u2r2)
                b22 = yn(nu, u2r2)
                b31 = jn(nu+1, u2r1)
                b32 = yn(nu+1, u2r1)
                b41 = jn(nu-2, u2r2)
                b42 = yn(nu-2, u2r2)
                g1 = b11 * delta - b31
                g2 = b12 * delta - b32
                f1 = b41*g2 - b42*g1
                f2 = b22*g1 - b21*g2
            return f1 + n0sq*f2

    def __fct3(self, nu, u2r1, u2r2, dn, n2sq, n3sq):
        n0sq = (n3sq - n2sq) / (n2sq + n3sq)
        b11 = jn(nu, u2r1)
        b12 = yn(nu, u2r1)
        b21 = jn(nu, u2r2)
        b22 = yn(nu, u2r2)

        if dn > 0:
            b31 = jn(nu+dn, u2r1)
            b32 = yn(nu+dn, u2r1)
            f1 = b31*b22 - b32*b21
            f2 = b11*b22 - b12*b21
        else:
            b31 = jn(nu+dn, u2r2)
            b32 = yn(nu+dn, u2r2)
            f1 = b31*b12 - b32*b11
            f2 = b12*b21 - b11*b22

        return f1 - n0sq * f2
