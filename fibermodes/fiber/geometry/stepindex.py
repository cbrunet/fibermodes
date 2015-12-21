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

from fibermodes.fiber.geometry.geometry import Geometry
from fibermodes import constants
from math import sqrt
import numpy
from scipy.special import jn, yn, iv, kn
from scipy.special import j0, y0, i0, k0
from scipy.special import j1, y1, i1, k1
from scipy.special import jvp, yvp, ivp, kvp


class StepIndex(Geometry):

    DEFAULT_PARAMS = []

    def index(self, r, wl):
        if self.ri <= abs(r) <= self.ro:
            return self._m.n(wl, *self._mp)
        else:
            return None

    def minIndex(self, wl):
        return self._m.n(wl, *self._mp)

    def maxIndex(self, wl):
        return self._m.n(wl, *self._mp)

    def u(self, r, neff, wl):
        return wl.k0 * r * sqrt(abs(self.index(r, wl)**2 - neff**2))

    def Psi(self, r, neff, wl, nu, C):
        u = self.u(r, neff, wl)
        if neff < self.maxIndex(wl):
            psi = (C[0] * jn(nu, u) + C[1] * yn(nu, u) if C[1] else
                   C[0] * jn(nu, u))
            psip = u * (C[0] * jvp(nu, u) + C[1] * yvp(nu, u) if C[1] else
                        C[0] * jvp(nu, u))
        else:
            psi = (C[0] * iv(nu, u) + C[1] * kn(nu, u) if C[1] else
                   C[0] * iv(nu, u))
            psip = u * (C[0] * ivp(nu, u) + C[1] * kvp(nu, u) if C[1] else
                        C[0] * ivp(nu, u))
        # if numpy.isnan(psi):
        #     print(neff, self.maxIndex(wl), C, r)
        return psi, psip

    def lpConstants(self, r, neff, wl, nu, A):
        u = self.u(r, neff, wl)
        if neff < self.maxIndex(wl):
            W = constants.pi / 2
            return (W * (u * yvp(nu, u) * A[0] - yn(nu, u) * A[1]),
                    W * (jn(nu, u) * A[1] - u * jvp(nu, u) * A[0]))
        else:
            return ((u * kvp(nu, u) * A[0] - kn(nu, u) * A[1]),
                    (iv(nu, u) * A[1] - u * ivp(nu, u) * A[0]))

    def EH_fields(self, ri, ro, nu, neff, wl, EH, tm=True):
        """

        modify EH in-place (for speed)

        """
        n = self.maxIndex(wl)
        u = self.u(ro, neff, wl)

        if ri == 0:
            if nu == 0:
                if tm:
                    self.C = numpy.array([1., 0., 0., 0.])
                else:
                    self.C = numpy.array([0., 0., 1., 0.])
            else:
                self.C = numpy.zeros((4, 2))
                self.C[0, 0] = 1  # Ez = 1
                self.C[2, 1] = 1  # Hz = alpha
        elif nu == 0:
            self.C = numpy.zeros(4)
            if tm:
                c = constants.Y0 * n * n
                idx = (0, 3)
                self.C[:2] = self.tetmConstants(ri, ro, neff, wl, EH, c, idx)
            else:
                c = -constants.eta0
                idx = (1, 2)
                self.C[2:] = self.tetmConstants(ri, ro, neff, wl, EH, c, idx)
        else:
            self.C = self.vConstants(ri, ro, neff, wl, nu, EH)

        # Compute EH fields
        if neff < n:
            c1 = wl.k0 * ro / u
            F3 = jvp(nu, u) / jn(nu, u)
            F4 = yvp(nu, u) / yn(nu, u)
        else:
            c1 = -wl.k0 * ro / u
            F3 = ivp(nu, u) / iv(nu, u)
            F4 = kvp(nu, u) / kn(nu, u)

        c2 = neff * nu / u * c1
        c3 = constants.eta0 * c1
        c4 = constants.Y0 * n * n * c1

        EH[0] = self.C[0] + self.C[1]
        EH[1] = self.C[2] + self.C[3]
        EH[2] = (c2 * (self.C[0] + self.C[1]) -
                 c3 * (F3 * self.C[2] + F4 * self.C[3]))
        EH[3] = (c4 * (F3 * self.C[0] + F4 * self.C[1]) -
                 c2 * (self.C[2] + self.C[3]))

        return EH

    def vConstants(self, ri, ro, neff, wl, nu, EH):
        a = numpy.zeros((4, 4))
        n = self.maxIndex(wl)
        u = self.u(ro, neff, wl)
        urp = self.u(ri, neff, wl)

        if neff < n:
            B1 = jn(nu, u)
            B2 = yn(nu, u)
            F1 = jn(nu, urp) / B1
            F2 = yn(nu, urp) / B2
            F3 = jvp(nu, urp) / B1
            F4 = yvp(nu, urp) / B2
            c1 = wl.k0 * ro / u
        else:
            B1 = iv(nu, u)
            B2 = kn(nu, u)
            F1 = iv(nu, urp) / B1 if u else 1
            F2 = kn(nu, urp) / B2
            F3 = ivp(nu, urp) / B1 if u else 1
            F4 = kvp(nu, urp) / B2
            c1 = -wl.k0 * ro / u
        c2 = neff * nu / urp * c1
        c3 = constants.eta0 * c1
        c4 = constants.Y0 * n * n * c1

        a[0, 0] = F1
        a[0, 1] = F2
        a[1, 2] = F1
        a[1, 3] = F2
        a[2, 0] = F1 * c2
        a[2, 1] = F2 * c2
        a[2, 2] = -F3 * c3
        a[2, 3] = -F4 * c3
        a[3, 0] = F3 * c4
        a[3, 1] = F4 * c4
        a[3, 2] = -F1 * c2
        a[3, 3] = -F2 * c2

        return numpy.linalg.solve(a, EH)

    def tetmConstants(self, ri, ro, neff, wl, EH, c, idx):
        a = numpy.empty((2, 2))
        n = self.maxIndex(wl)
        u = self.u(ro, neff, wl)
        urp = self.u(ri, neff, wl)

        if neff < n:
            B1 = j0(u)
            B2 = y0(u)
            F1 = j0(urp) / B1
            F2 = y0(urp) / B2
            F3 = -j1(urp) / B1
            F4 = -y1(urp) / B2
            c1 = wl.k0 * ro / u
        else:
            B1 = i0(u)
            B2 = k0(u)
            F1 = i0(urp) / B1
            F2 = k0(urp) / B2
            F3 = i1(urp) / B1
            F4 = -k1(urp) / B2
            c1 = -wl.k0 * ro / u
        c3 = c * c1

        a[0, 0] = F1
        a[0, 1] = F2
        a[1, 0] = F3 * c3
        a[1, 1] = F4 * c3

        return numpy.linalg.solve(a, EH.take(idx))
