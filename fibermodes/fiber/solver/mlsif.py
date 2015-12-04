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
from fibermodes import Wavelength, Mode, ModeFamily
from fibermodes import constants
from math import isnan
import numpy
from scipy.special import kn, kvp, k0, k1, jn, jvp, yn, yvp, iv, ivp


class Neff(FiberSolver):

    def __call__(self, wl, mode, delta, lowbound):
        wl = Wavelength(wl)
        if lowbound is None or isnan(lowbound):
            pm = None
            if mode.family is ModeFamily.HE:
                if mode.m > 1:
                    pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
            elif mode.family is ModeFamily.EH:
                pm = Mode(ModeFamily.HE, mode.nu, mode.m)
            elif mode.m > 1:
                pm = Mode(mode.family, mode.nu, mode.m - 1)

            if pm:
                lowbound = self.fiber.neff(pm, wl, delta)
                if isnan(lowbound):
                    return lowbound
            else:
                lowbound = max(layer.maxIndex(wl)
                               for layer in self.fiber.layers)

            if mode.family is ModeFamily.LP and mode.nu > 0:
                pm = Mode(mode.family, mode.nu - 1, mode.m)
                lb = self.fiber.neff(pm, wl, delta)
                if isnan(lb):
                    return lb
                lowbound = min(lowbound, lb)
        # try:
        #     # Use cutoff information if available
        #     co = self.fiber.cutoff(mode)
        #     if self.fiber.V0(wl) < co:
        #         return float("nan")

        #     nco = max(layer.maxIndex(wl) for layer in self.fiber.layers)
        #     r = self.fiber.innerRadius(-1)

        #     lowbound = min(lowbound, sqrt(nco**2 - (co / (r * wl.k0))**2))
        # except (NotImplementedError):
        #     pass
        # if mode == Mode(ModeFamily.HE, 3, 1):
        #     print('3', lowbound)

        highbound = self.fiber.minIndex(-1, wl)

        fct = {ModeFamily.LP: self._lpceq,
               ModeFamily.TE: self._teceq,
               ModeFamily.TM: self._tmceq,
               ModeFamily.HE: self._heceq,
               ModeFamily.EH: self._heceq
               }

        if lowbound <= highbound:
            print("impossible bound")
            return float("nan")

        if (lowbound - highbound) < 10 * delta:
            delta = (lowbound - highbound) / 10

        return self._findFirstRoot(fct[mode.family], args=(wl, mode.nu),
                                   lowbound=lowbound-1e-15,
                                   highbound=highbound+1e-15,
                                   delta=-delta)

    def _lpfield(self, wl, nu, neff, r):
        N = len(self.fiber)
        C = numpy.array((1, 0))

        for i in range(1, N):
            rho = self.fiber.innerRadius(i)
            if r < rho:
                layer = self.fiber.layers[i-1]
                break
            A = self.fiber.layers[i-1].Psi(rho, neff, wl, nu, C)
            C = self.fiber.layers[i].lpConstants(rho, neff, wl, nu, A)
        else:
            layer = self.fiber.layers[-1]
            u = layer.u(rho, neff, wl)
            C = (0, A[0] / kn(nu, u))

        ex, _ = layer.Psi(r, neff, wl, nu, C)
        hy = neff * constants.Y0 * ex

        return numpy.array((ex, 0, 0)), numpy.array((0, hy, 0))

    def _tefield(self, wl, nu, neff, r):
        pass

    def _tmfield(self, wl, nu, neff, r):
        N = len(self.fiber)
        C = numpy.array((1, 0))
        EH = numpy.zeros(4)
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            layer = self.fiber.layers[i]
            n = layer.maxIndex(wl)
            u = layer.u(ro, neff, wl)

            if i > 0:
                C = layer.tetmConstants(ri, ro, neff, wl, EH,
                                        constants.Y0 * n * n, (0, 3))

            if r < ro:
                break

            if neff < n:
                c1 = wl.k0 * ro / u
                F3 = jvp(nu, u) / jn(nu, u)
                F4 = yvp(nu, u) / yn(nu, u)
            else:
                c1 = -wl.k0 * ro / u
                F3 = ivp(nu, u) / iv(nu, u)
                F4 = kvp(nu, u) / kn(nu, u)

            c4 = constants.Y0 * n * n * c1

            EH[0] = C[0] + C[1]
            EH[3] = c4 * (F3 * C[0] + F4 * C[1])

            ri = ro
        else:
            layer = self.fiber.layers[-1]
            u = layer.u(ro, neff, wl)
            # C =

        return numpy.array((0, ephi, 0)), numpy.array((hr, 0, hz))

    def _hefield(self, wl, nu, neff, r):
        self._heceq(neff, wl, nu)
        for i, rho in enumerate(self.fiber._r):
            if r < rho:
                break
        else:
            i += 1
        layer = self.fiber.layers[i]
        n = layer.maxIndex(wl)
        u = layer.u(rho, neff, wl)
        urp = u * r / rho

        c1 = rho / u
        c2 = wl.k0 * c1
        c3 = nu * c1 / r if r else 0  # To avoid div by 0
        c6 = constants.Y0 * n * n

        if neff < n:
            B1 = jn(nu, u)
            B2 = yn(nu, u)
            F1 = jn(nu, urp) / B1
            F2 = yn(nu, urp) / B2 if i > 0 else 0
            F3 = jvp(nu, urp) / B1
            F4 = yvp(nu, urp) / B2 if i > 0 else 0
        else:
            c2 = -c2
            B1 = iv(nu, u)
            B2 = kn(nu, u)
            F1 = iv(nu, urp) / B1
            F2 = kn(nu, urp) / B2 if i > 0 else 0
            F3 = ivp(nu, urp) / B1
            F4 = kvp(nu, urp) / B2 if i > 0 else 0

        A, B, Ap, Bp = layer.C[:, 0] + layer.C[:, 1] * self.alpha

        Ez = A * F1 + B * F2
        Ezp = A * F3 + B * F4
        Hz = Ap * F1 + Bp * F2
        Hzp = Ap * F3 + Bp * F4

        if r == 0 and nu == 1:
            # Asymptotic expansion of Ez (or Hz):
            # J1(ur/p)/r (r->0) = u/(2p)
            if neff < n:
                f = 1 / (2 * jn(nu, u))
            else:
                f = 1 / (2 * iv(nu, u))
            c3ez = A * f
            c3hz = Ap * f
        else:
            c3ez = c3 * Ez
            c3hz = c3 * Hz

        Er = c2 * (neff * Ezp - constants.eta0 * c3hz)
        Ep = c2 * (neff * c3ez - constants.eta0 * Hzp)

        Hr = c2 * (neff * Hzp - c6 * c3ez)
        Hp = c2 * (-neff * c3hz + c6 * Ezp)

        return numpy.array((Er, Ep, Ez)), numpy.array((Hr, Hp, Hz))

    _ehfield = _hefield

    def _lpceq(self, neff, wl, nu):
        N = len(self.fiber)
        C = numpy.zeros((N-1, 2))
        C[0, 0] = 1

        for i in range(1, N-1):
            r = self.fiber.innerRadius(i)
            A = self.fiber.layers[i-1].Psi(r, neff, wl, nu, C[i-1, :])
            C[i, :] = self.fiber.layers[i].lpConstants(r, neff, wl, nu, A)

        r = self.fiber.innerRadius(-1)
        A = self.fiber.layers[N-2].Psi(r, neff, wl, nu, C[-1, :])
        u = self.fiber.layers[N-1].u(r, neff, wl)
        return u * kvp(nu, u) * A[0] - kn(nu, u) * A[1]

    def _teceq(self, neff, wl, nu):
        N = len(self.fiber)
        EH = numpy.empty(4)
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH, False)
            ri = ro

        # Last layer
        _, Hz, Ep, _ = EH
        u = self.fiber.layers[-1].u(ri, neff, wl)

        F4 = k1(u) / k0(u)
        return Ep + wl.k0 * ri / u * constants.eta0 * Hz * F4

    def _tmceq(self, neff, wl, nu):
        N = len(self.fiber)
        EH = numpy.empty(4)
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH, True)
            ri = ro

        # Last layer
        Ez, _, _, Hp = EH
        u = self.fiber.layers[-1].u(ri, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = k1(u) / k0(u)
        return Hp - wl.k0 * ri / u * constants.Y0 * n * n * Ez * F4

    def _heceq(self, neff, wl, nu):
        N = len(self.fiber)
        EH = numpy.empty((4, 2))
        ri = 0

        for i in range(N-1):
            ro = self.fiber.outerRadius(i)
            try:
                self.fiber.layers[i].EH_fields(ri, ro, nu, neff, wl, EH)
            except ZeroDivisionError:
                return float("inf")
            ri = ro

        # Last layer
        C = numpy.zeros((4, 2))
        C[1, :] = EH[0, :]
        C[3, :] = EH[1, :]
        self.fiber.layers[N-1].C = C

        u = self.fiber.layers[N-1].u(ri, neff, wl)
        n = self.fiber.maxIndex(-1, wl)

        F4 = kvp(nu, u) / kn(nu, u)
        c1 = -wl.k0 * ri / u
        c2 = neff * nu / u * c1
        c3 = constants.eta0 * c1
        c4 = constants.Y0 * n * n * c1

        E = EH[2, :] - (c2 * EH[0, :] - c3 * F4 * EH[1, :])
        H = EH[3, :] - (c4 * F4 * EH[0, :] - c2 * EH[1, :])

        if E[1] != 0:
            self.alpha = -E[0] / E[1]
        else:
            self.alpha = -H[0] / H[1]

        return E[0]*H[1] - E[1]*H[0]

    _ehceq = _heceq
