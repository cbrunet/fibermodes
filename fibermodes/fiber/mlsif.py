"""Multi-Layers Step-Index Fiber module."""

from .fiber import Fiber
from ..constants import pi, Y0, eta0

import numpy
# from math import log10
from scipy.special import jn, kn, iv, yn, jvp, kvp, ivp, yvp
from scipy.special import j0, j1, k0, k1, i0, i1, y0, y1


class MLSIF(Fiber):

    """Multi-Layers Step-Index Fiber class."""

    def _lpceq(self, neff, mode):
        N = self._n.size
        u = self._wl.k0 * self._r * numpy.sqrt(numpy.abs(self._n**2 - neff**2))

        C = numpy.zeros((N, 2))
        C[0, 0] = 1

        for i in range(N - 2):
            u1 = u[i]
            u1r = u1 * self._r[i+1]
            u2r = u[i+1] * self._r[i]
            u2 = u2r / self._r[i+1]

            if neff < self._n[i]:
                F1 = C[i, 0] * jn(mode.nu, u1) + C[i, 1] * yn(mode.nu, u1)
                F1p = C[i, 0] * jvp(mode.nu, u1) + C[i, 1] * yvp(mode.nu, u1)
            else:
                F1 = C[i, 0] * iv(mode.nu, u1) + C[i, 1] * kn(mode.nu, u1)
                F1p = C[i, 0] * ivp(mode.nu, u1) + C[i, 1] * kvp(mode.nu, u1)

            if neff < self._n[i+1]:
                c = pi / (2 * self._r[i+1])
                F2 = jn(mode.nu, u2)
                F2p = jvp(mode.nu, u2)
                F3 = yn(mode.nu, u2)
                F3p = yvp(mode.nu, u2)
            else:
                c = 1 / self._r[i+1]
                F2 = iv(mode.nu, u2)
                F2p = ivp(mode.nu, u2)
                F3 = kn(mode.nu, u2)
                F3p = kvp(mode.nu, u2)

            C[i+1, 0] = c * (u2r * F3p * F1 - u1r * F3 * F1p)
            C[i+1, 1] = c * (u1r * F2 * F1p - u2r * F2p * F1)

        # Last layer (cladding)
        i = N - 2
        u1 = u[i]
        u1r = u1 / self._r[i]
        u2 = u[i+1]
        u2r = u2 / self._r[i+1]

        if neff < self._n[i]:
            F1 = C[i, 0] * jn(mode.nu, u1) + C[i, 1] * yn(mode.nu, u1)
            F1p = u1r * (C[i, 0] * jvp(mode.nu, u1) +
                         C[i, 1] * yvp(mode.nu, u1))
        else:
            F1 = C[i, 0] * iv(mode.nu, u1) + C[i, 1] * kn(mode.nu, u1)
            F1p = u1r * (C[i, 0] * ivp(mode.nu, u1) +
                         C[i, 1] * kvp(mode.nu, u1))

        if neff < self._n[i+1]:  # leaky mode
            F2 = jn(mode.nu, u2)
            F2p = jvp(mode.nu, u2)
            F3 = yn(mode.nu, u2)
            F3p = yvp(mode.nu, u2)

            C[i+1, 0] = pi / 2 * (u2 * F3p * F1 - self._r[i] * F3 * F1p)
            C[i+1, 1] = pi / 2 * (self._r[i] * F2 * F1p - u2 * F2p * F1)

            v = ((C[i+1, 0] * F2 + C[i+1, 1] * F3) * F1p -
                 u2r * (C[i+1, 0] * F2p + C[i+1, 1] * F3p) * F1)
            return v
            # if v > 0:
            #     return log10(v**2)
            # else:
            #     return -float('inf')
        else:  # guided mode
            F2 = 0
            F2p = 0
            F3 = kn(mode.nu, u2)
            F3p = kvp(mode.nu, u2)

            C[i+1, 0] = 0
            C[i+1, 1] = F1 / F3
            return u2r * F3p * F1 - F3 * F1p
            # return log10((u2r * F3p * F1 - F3 * F1p)**2)

    def _teceq(self, neff, mode):
        N = self._n.size
        C = numpy.zeros((N, 4))
        w = numpy.sqrt(numpy.abs(self._n**2 - neff**2))
        if numpy.any(w == 0):
            return float("inf")
        krhou = 1 / w
        U = self._wl.k0 * self._r * w

        # First layer
        u = U[0]
        rho = self._r[0]
        n = self._n[0]
        if neff < n:
            c1 = krhou[0]
            F3 = -j1(u) / j0(u)
            F4 = 0
            c2 = F3 * c1
        else:
            c1 = -krhou[0]
            F3 = i1(u) / i0(u)
            F4 = 0
            c2 = F3 * c1

        Hz = 1
        Ep = -c2 * eta0
        C[0, :] = [0., 0., 1., 0.]
        a = numpy.empty((2, 2))
        for i in range(1, N-1):
            u = U[i]
            r = self._r[i-1]
            rho = self._r[i]
            urp = u * r / rho
            n = self._n[i]

            if neff < n:
                B1 = j0(u)
                B2 = y0(u)
                F1 = j0(urp) / B1
                F2 = y0(urp) / B2
                F3 = -j1(urp) / B1
                F4 = -y1(urp) / B2
                c1 = krhou[i]
            else:
                B1 = i0(u)
                B2 = k0(u)
                F1 = i0(urp) / B1
                F2 = k0(urp) / B2
                F3 = i1(urp) / B1
                F4 = -k1(urp) / B2
                c1 = -krhou[i]
            c3 = eta0 * c1

            # Second layer
            a[0, 0] = F1
            a[0, 1] = F2
            a[1, 0] = -F3 * c3
            a[1, 1] = -F4 * c3

            C[i, 2:] = numpy.linalg.solve(a, numpy.array((Hz, Ep)))

            if neff < n:
                F3 = -j1(u) / B1
                F4 = -y1(u) / B2
            else:
                F3 = i1(u) / B1
                F4 = -k1(u) / B2

            Hz = C[i, 2] + C[i, 3]
            Ep = -c3 * (F3 * C[i, 2] + F4 * C[i, 3])

        # Third layer
        u = U[-1]
        rho = self._r[-1]
        n = self._n[-1]

        if neff < n:  # leaky mode
            i = N-2
            c5 = neff * c1
            Hr = c5 * (C[i, 2] * F3 + C[i, 3] * F4)

            i = n-1
            B1 = j0(u)
            B2 = y0(u)
            F3 = -j1(u) / B1
            F4 = -y1(u) / B2
            c1 = krhou[i]
            c3 = c1 * eta0
            c5 = neff * c1

            a[0, 0] = 1
            a[0, 1] = 1
            a[1, 0] = F3 * c5
            a[1, 1] = F4 * c5
            C[i, 2:] = numpy.linalg.solve(a, numpy.array((Hz, Hr)))
            val = Ep + c3 * (C[i, 2] * F3 + C[i, 3] * F4)

        else:
            i = N-1
            F4 = k1(u) / k0(u)
            C[i, 3] = Hz
            val = Ep + krhou[i] * eta0 * C[i, 3] * F4
            #return Ep / Hz + F4 * krhou[i] * eta0

        #return math.log10(val*val)
        return val

    def _tmceq(self, neff, mode):
        N = self._n.size
        C = numpy.zeros((N, 4))
        w = numpy.sqrt(numpy.abs(self._n**2 - neff**2))
        if numpy.any(w == 0):
            return float("inf")
        krhou = 1 / w
        U = self._wl.k0 * self._r * w

        # First layer
        u = U[0]
        rho = self._r[0]
        n = self._n[0]
        if neff < n:
            c1 = krhou[0]
            F3 = -j1(u) / j0(u)
            F4 = 0
            c2 = F3 * c1
        else:
            c1 = -krhou[0]
            F3 = i1(u) / i0(u)
            F4 = 0
            c2 = F3 * c1

        Ez = 1
        Hp = c2 * Y0 * n * n
        C[0, :] = [1., 0., 0., 0.]
        a = numpy.empty((2, 2))
        for i in range(1, N-1):
            u = U[i]
            r = self._r[i-1]
            rho = self._r[i]
            urp = u * r / rho
            n = self._n[i]

            if neff < n:
                B1 = j0(u)
                B2 = y0(u)
                F1 = j0(urp) / B1
                F2 = y0(urp) / B2
                F3 = -j1(urp) / B1
                F4 = -y1(urp) / B2
                c1 = krhou[i]
            else:
                B1 = i0(u)
                B2 = k0(u)
                F1 = i0(urp) / B1
                F2 = k0(urp) / B2
                F3 = i1(urp) / B1
                F4 = -k1(urp) / B2
                c1 = -krhou[i]
            c4 = Y0 * n * n * c1

            # Second layer
            a[0, 0] = F1
            a[0, 1] = F2
            a[1, 0] = F3 * c4
            a[1, 1] = F4 * c4

            C[i, :2] = numpy.linalg.solve(a, numpy.array((Ez, Hp)))

            if neff < n:
                F3 = -j1(u) / B1
                F4 = -y1(u) / B2
            else:
                F3 = i1(u) / B1
                F4 = -k1(u) / B2

            Ez = C[i, 0] + C[i, 1]
            Hp = F3 * c4 * C[i, 0] + F4 * c4 * C[i, 1]

        # Third layer
        u = U[-1]
        rho = self._r[-1]
        n = self._n[-1]

        if neff < n:  # leaky mode
            i = N - 2
            c5 = neff * c1
            Er = c5 * (C[i, 0] * F3 + C[i, 1] * F4)

            i = n-1
            B1 = j0(u)
            B2 = y0(u)
            F3 = j1(u) / B1
            F4 = y1(u) / B2
            c1 = krhou[i]
            c5 = neff * c1

            a[0, 0] = 1
            a[0, 1] = 1
            a[1, 0] = F3 * c5
            a[1, 1] = F4 * c5

            C[i, :2] = numpy.linalg.solve(a, numpy.array((Ez, Er)))

            val = Hp - c1 * Y0 * n * n * (C[i, 0] * F3 + C[i, 1] * F4)

        else:
            i = N - 1
            C[i, 1] = Ez
            F4 = k1(u) / k0(u)
            val = Hp - krhou[i] * Y0 * n * n * C[i, 1] * F4
            #return Hp / Ez - F4 * Y0 * n * n * krhou[i]

        #return math.log10(val*val)
        return val

    def _heceq(self, neff, mode):
        N = self._n.size
        w = numpy.sqrt(numpy.abs(self._n**2 - neff**2))
        if numpy.any(w == 0):
            return float("inf")
        krhou = 1 / w
        U = self._wl.k0 * self._r * w
        neffnu = neff * mode.nu

        # First layer
        u = U[0]
        rho = self._r[0]
        n = self._n[0]
        if neff < n:
            c1 = krhou[0]
            F3 = jvp(mode.nu, u) / jn(mode.nu, u)
            F4 = 0
        else:
            c1 = -krhou[0]
            F3 = ivp(mode.nu, u) / iv(mode.nu, u)
            F4 = 0
        c2 = neffnu / u * c1
        c3 = eta0 * c1
        c4 = Y0 * n * n * c1

        EH = numpy.empty((4, 2))
        EH[0, 0] = 1
        EH[0, 1] = 0
        EH[1, 0] = 0
        EH[1, 1] = 1
        EH[2, 0] = c2
        EH[2, 1] = -F3 * c3
        EH[3, 0] = F3 * c4
        EH[3, 1] = -c2

        C = numpy.zeros((N, 4, 2))
        C[0, 0, 0] = 1  # A
        C[0, 2, 1] = 1  # A'
        a = numpy.zeros((4, 4))
        for i in range(1, N-1):
            u = U[i]
            r = self._r[i-1]
            rho = self._r[i]
            urp = u * r / rho
            n = self._n[i]

            if neff < n:
                B1 = jn(mode.nu, u)
                B2 = yn(mode.nu, u)
                F1 = jn(mode.nu, urp) / B1
                F2 = yn(mode.nu, urp) / B2
                F3 = jvp(mode.nu, urp) / B1
                F4 = yvp(mode.nu, urp) / B2
                c1 = krhou[i]
            else:
                B1 = iv(mode.nu, u)
                B2 = kn(mode.nu, u)
                F1 = iv(mode.nu, urp) / B1
                F2 = kn(mode.nu, urp) / B2
                F3 = ivp(mode.nu, urp) / B1
                F4 = kvp(mode.nu, urp) / B2
                c1 = -krhou[i]
            c2 = neff * mode.nu / urp * c1
            c3 = eta0 * c1
            c4 = Y0 * n * n * c1

            # Second layer
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

            C[i, :, :] = numpy.linalg.solve(a, EH)

            if neff < n:
                F3 = jvp(mode.nu, u) / B1
                F4 = yvp(mode.nu, u) / B2
            else:
                F3 = ivp(mode.nu, u) / B1
                F4 = kvp(mode.nu, u) / B2
            c2 = neffnu / u * c1

            EH[0, :] = C[i, 0, :] + C[i, 1, :]
            EH[1, :] = C[i, 2, :] + C[i, 3, :]
            EH[2, :] = (c2 * (C[i, 0, :] + C[i, 1, :]) -
                        c3 * (F3 * C[i, 2, :] + F4 * C[i, 3, :]))
            EH[3, :] = (c4 * (F3 * C[i, 0, :] + F4 * C[i, 1, :]) -
                        c2 * (C[i, 2, :] + C[i, 3, :]))

        # Third layer
        u = U[-1]
        rho = self._r[-1]
        n = self._n[-1]

        if neff < n:
            i = N-2
            c5 = c1 * neff
            Er = (c5 * (C[i, 0, :] * F3 + C[i, 1, :] * F4) -
                  c3 * mode.nu / U[-2] * (C[i, 2, :] + C[i, 3, :]))
            Hr = (c5 * (C[i, 2, :] * F3 + C[i, 3, :] * F4) -
                  c4 * mode.nu * (C[i, 0, :] + C[i, 1, :]))

            i = N-1
            B1 = jn(mode.nu, u)
            B2 = yn(mode.nu, u)
            F3 = jvp(mode.nu, u) / B1
            F4 = yvp(mode.nu, u) / B2
            c1 = krhou[i]
            c3 = eta0 * c1 * mode.nu
            c4 = Y0 * n * n * c1 * mode.nu
            c5 = neff * c1

            a[0, 0] = 1
            a[0, 1] = 1
            a[1, 2] = 1
            a[1, 3] = 1
            a[2, 0] = c5 * F3
            a[2, 1] = c5 * F4
            a[2, 2] = -c3
            a[2, 3] = -c3
            a[3, 0] = -c4
            a[3, 1] = -c4
            a[3, 2] = c5 * F3
            a[3, 3] = c5 * F4

            C[i, :, :] = numpy.linalg.solve(a, [EH[0, :], EH[1, :], Er, Hr])

        else:
            i = N-1
            F3 = 0
            F4 = kvp(mode.nu, u) / kn(mode.nu, u)
            c1 = -krhou[-1]

            C[i, 1, :] = EH[0, :]  # B
            C[i, 3, :] = EH[1, :]  # B'

        c2 = neffnu / u * c1
        c3 = eta0 * c1
        c4 = Y0 * n * n * c1

        E = EH[2, :] - (c2 * (C[i, 0, :] + C[i, 1, :]) -
                        c3 * (F3 * C[i, 2, :] + F4 * C[i, 3, :]))
        H = EH[3, :] - (c4 * (F3 * C[i, 0, :] + F4 * C[i, 1, :]) -
                        c2 * (C[i, 2, :] + C[i, 3, :]))

        # if E[1] != 0:
        #     alpha = -E[0] / E[1]
        # elif H[1] != 0:
        #     alpha = -H[0] / H[1]
        # else:
        #     alpha = 0

        # self.C = C[:, :, 0] + alpha * C[:, :, 1]

        #return math.log10((E[0]*H[1] - E[1]*H[0])**2)
        return E[0]*H[1] - E[1]*H[0]

    _ehceq = _heceq
