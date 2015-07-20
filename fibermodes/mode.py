"""Fiber mode representations, and utility functions."""

from enum import Enum

import numpy
from scipy.special import jn, yn, kn, iv, jvp, yvp, ivp, kvp
from math import sqrt
from fibermodes.constants import eta0

#: Constants for identifying mode family. Can be
#: LP, HE, EH, TE, or TM.
Family = Enum('Family', 'LP HE EH TE TM', module=__name__)


class Mode(object):

    """Fiber mode representation.

    The fiber mode consists of a mode family, and two mode parameters
    (*ν* and *m*).

    """

    def __init__(self, family, nu, m):
        '''
        Constructor
        '''
        if isinstance(family, Family):
            self._family = family
        else:
            self._family = Family[family]
        self._nu = nu
        self._m = m

    def __hash__(self):
        return hash((self._family, self._nu, self._m))

    @property
    def family(self):
        """Mode family.

        .. seealso:: :py:class:`Family`

        """
        return self._family

    @family.setter
    def family(self, fam):
        assert isinstance(fam, Family), "fam must be a Family item"
        self._family = fam

    @property
    def nu(self):
        """*ν* parameter of the mode. It often corresponds to the parameter
        of the radial Bessel functions.

        """
        return self._nu

    ell = nu

    @property
    def m(self):
        """(positive integer) Radial order of the mode.
        It corresponds to the number of concentric rings in the mode fields.

        """
        return self._m

    @m.setter
    def m(self, mparam):
        assert mparam > 0, "m must be a positive integer."
        assert int(mparam) == mparam, "m must be a positive integer."
        self._m = int(mparam)

    def lpEq(self):
        """Equivalent LP mode."""
        if self.family == Family.LP:
            return self
        elif self.family == Family.HE:
            return Mode(Family.LP, self.nu - 1, self.m)
        else:
            return Mode(Family.LP, self.nu + 1, self.m)

    def __str__(self):
        return "{}({},{})".format(self.family.name, self.nu, self.m)

    def __repr__(self):
        return "Mode('{}',{},{})".format(
            self.family.name, self.nu, self.m)

    def __eq__(self, m2):
        s1, s2 = str(self), str(m2)
        # if set((s1, s2)) <= set(('HE(1,1)', 'LP(0,1)')):
        #     return True
        return s1 == s2

    def __ne__(self, m2):
        return not (self == m2)

    def __lt__(self, m2):
        if self.m == m2.m:
            if self.family == m2.family:
                result = self.nu < m2.nu
            else:
                if self.family == Family.HE:
                    nu1 = self.nu - 1
                elif self.family == Family.LP:
                    nu1 = self.nu
                else:
                    nu1 = self.nu + 1
                if m2.family == Family.HE:
                    nu2 = m2.nu - 1
                elif m2.family == Family.LP:
                    nu2 = m2.nu
                else:
                    nu2 = m2.nu + 1
                if nu1 == nu2:
                    fams = [Family.LP, Family.EH, Family.TE,
                            Family.HE, Family.TM]
                    result = fams.index(self.family) < fams.index(m2.family)
                else:
                    result = nu1 < nu2

        else:
            result = self.m < m2.m
        return result

    def __le__(self, m2):
        return (self == m2) or (self < m2)

    def __ge__(self, m2):
        return m2 <= self

    def __gt__(self, m2):
        return m2 < self


# class SMode(Mode):

#     """Solved mode. This is a mode, associated with an effective index."""

#     def __init__(self, fiber, mode, neff):
#         """Build a SMode object, from a Mode and an effective index.

#         Usually, you do not need to call this directly. SMode objects
#         are build using the mode solver.

#         """
#         self._family = mode.family
#         self._nu = mode.nu
#         self._m = mode.m

#         self._fiber = fiber
#         self._neff = neff
#         self._beta = None

#     def beta(self, order=0):
#         if self._beta:
#             return self._beta[order]
#         else:
#             return None

#     @property
#     def bnorm(self):
#         """Normalized propagation constant"""
#         return ((self.neff - self._fiber._n[-1]) /
#                 (max(self._fiber._n) - self._fiber._n[-1]))

#     @property
#     def neff(self):
#         """Effective index of the mode."""
#         return self._neff

#     @property
#     def mode(self):
#         """Return (unsolved) mode object built from this solved mode."""
#         return Mode(self.family, self.nu, self.m)

#     def __eq__(self, m2):
#         if isinstance(m2, SMode):
#             return self.neff == m2.neff
#         else:
#             return self.mode == m2

#     def __ne__(self, m2):
#         return not self == m2

#     def __lt__(self, m2):
#         return self.neff < m2.neff

#     def __le__(self, m2):
#         return self.neff <= m2.neff

#     def __ge__(self, m2):
#         return self.neff >= m2.neff

#     def __gt__(self, m2):
#         return self.neff > m2.neff

#     def rfield(self, R):
#         coefs = self._fiber._constants(self._neff, self)

#         # print(str(self))
#         # for c in coefs:
#         #     print(c)
#         # print()

#         F = numpy.empty((6, 0))
#         for i in range(self._fiber._r.size):
#             rho = self._fiber._r[i]
#             if i == 0:
#                 r = R[R < rho]
#             elif i + 1 < self._fiber._r.size:
#                 r = R[(R >= self._fiber._r[i-1]) & (R < rho)]
#             else:
#                 r = R[R >= rho]

#             A, B, C, D = coefs[4*i:4*i+4]
#             k0 = self._fiber._wl.k0
#             u2 = k0**2 * (self._fiber._n[i]**2 - self._neff**2)
#             u = sqrt(abs(u2))
#             ur = u * r

#             if u2 > 0:
#                 f1 = jn(self._nu, ur)
#                 f2 = yn(self._nu, ur) if i else 0
#                 f1p = jvp(self._nu, ur)
#                 f2p = yvp(self._nu, ur) if i else 0
#             else:
#                 f1 = iv(self._nu, ur)
#                 f2 = kn(self._nu, ur) if i else 0
#                 f1p = ivp(self._nu, ur)
#                 f2p = kvp(self._nu, ur) if i else 0

#             n2 = self._fiber._n[i]**2

#             ez = A * f1 + B * f2
#             hz = C * f1 + D * f2

#             er = k0 / u * (self._neff * (A * f1p + B * f2p) -
#                            eta0 * self._nu / ur * hz)
#             ep = k0 / u * (self._neff * self._nu / ur * ez -
#                            eta0 * (C * f1p + D * f2p))

#             hr = k0 / u * (self._neff * (C * f1p + D * f2p) -
#                            n2 * self._nu / ur / eta0 * ez)
#             hp = k0 / u * (self._neff * self._nu / ur * hz -
#                            n2 / eta0 * (A * f1p + B * f2p))
#             if (u2 < 0):
#                 er *= -1
#                 ep *= -1
#                 hr *= -1
#                 hp *= -1

#             # I = numpy.square(ez) + numpy.square(er) + numpy.square(ep)
#             I = numpy.vstack((ez, er, ep, hz, hr, hp))
#             F = numpy.hstack((F, I))
#         return F


# def sortModes(modes):
#     """Sort :class:`list` of :class:`SMode`, *in-place* (list is modified).

#     Modes are sorted from highest to lowest effective index.
#     *m* parameters of the modes are adjusted.

#     :param modes: Unsorted :class:`list` of :class:`~fibermodes.mode.SMode`
#                   (solved mode) object.
#     :rtype: Sorted :class:`list` of :class:`~fibermodes.mode.SMode`
#             (solved mode) object.

#     """
#     modes.sort(reverse=True)
#     mparams = {}
#     for i, m in enumerate(modes):
#         key = (m.family, m.nu) if m.family != Family.EH else (Family.HE, m.nu)
#         if key[0] == Family.HE:
#             k2 = (Family.EH, m.nu)
#             if mparams.get(key, 0) != mparams.get(k2, 0):
#                 key = k2
#             modes[i].family = key[0]
#         mval = mparams.get(key, 0) + 1
#         modes[i].m = mparams[key] = mval
#     return modes


if __name__ == '__main__':
    m = Mode('HE', 1, 1)
    print(m)
    print(repr(m))
