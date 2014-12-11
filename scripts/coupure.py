from fibermodes import Wavelength, Mode, fixedFiber, ModeFamily
from fibermodes.material import Fixed
from fibermodes.simulator import PSimulator as Simulator
import numpy
from matplotlib import pyplot
from operator import mul

from math import sqrt, log10
from scipy.special import jn, yn, jvp, yvp, iv, ivp, kn, kvp
from scipy.special import j0, y0, i0, k0, jn_zeros
from scipy.special import j1, y1, i1, k1
from scipy.optimize import brentq, brent

from fibermodes.constants import eta0


class COFiber(object):
    delta = 1e-3

    @classmethod
    def _params(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        # beta = K0 * cls.n[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]

        if U2[0] > 0:
            u1 = sqrt(U2[0])
            u1r1 = u1 * cls.rho[0]
            g = jn(nu, u1r1)
            gp = -jn(nu+1, u1r1)
        else:
            u1 = sqrt(-U2[0])
            u1r1 = u1 * cls.rho[0]
            g = iv(nu, u1r1)
            gp = -iv(nu+1, u1r1)

        if U2[1] > 0:
            u2 = sqrt(U2[1])
            u2r1 = u2 * cls.rho[0]
            u2r2 = u2 * cls.rho[1]
            F = yn(nu, u2r2) * jn(nu, u2r1) - jn(nu, u2r2) * yn(nu, u2r1)
            Fp = yn(nu, u2r2) * jn(nu+1, u2r1) - jn(nu, u2r2) * yn(nu+1, u2r1)
        else:
            u2 = sqrt(-U2[1])
            u2r1 = u2 * cls.rho[0]
            u2r2 = u2 * cls.rho[1]
            F = kn(nu, u2r2) * iv(nu, u2r1) - iv(nu, u2r2) * kn(nu, u2r1)
            Fp = kn(nu, u2r2) * iv(nu+1, u2r1) + iv(nu, u2r2) * kn(nu+1, u2r1)

        return F, Fp, g, gp, u1r1, u2r1

    @classmethod
    def kappaparams(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(abs(U2[0])) * cls.rho[0]
        u2r1 = sqrt(abs(U2[1])) * cls.rho[0]
        u2r2 = sqrt(abs(U2[1])) * cls.rho[1]
        n1sq, n2sq, n3sq = numpy.square(cls.n)

        if n1sq < n3sq:
            f = ivp(nu, u1r1) / iv(nu, u1r1) / u1r1  # c
        # elif n2sq < n3sq:
        #     f = nu / u1r1**2 + jn(nu+1, u1r1) / jn(nu, u1r1) / u1r1  # a
        else:
            f = jvp(nu, u1r1) / jn(nu, u1r1) / u1r1  # b d

        if U2[0] > 1 and U2[1] > 1:
            # b d
            kappa1 = (n1sq + n2sq) * f / n2sq
            kappa2 = (n1sq * f * f / n2sq -
                      nu**2 * n3sq / n2sq * (1 / u1r1**2 - 1 / u2r1**2)**2)
        else:
            # a c
            kappa1 = -(n1sq + n2sq) * f / n2sq
            kappa2 = (n1sq * f * f / n2sq -
                      nu**2 * n3sq / n2sq * (1 / u1r1**2 + 1 / u2r1**2)**2)

        return kappa1, kappa2, u1r1, u2r1, u2r2

    @classmethod
    def _gammaparams(cls, nu, u1a, u2a):
        n12 = cls.n[0]**2
        n22 = cls.n[1]**2

        if cls.n[0] < cls.n[-1]:
            Inu = iv(nu, u1a)
            Inu1 = iv(nu+1, u1a)
        else:
            Inu = jn(nu, u1a)
            Inu1 = jn(nu+1, u1a)
        f0 = Inu1 / u1a / Inu

        if cls.n[0] < cls.n[-1] or cls.n[1] < cls.n[-1]:
            Gamma0 = u2a / n22 * (2 * nu * n22 / u2a**2 +
                                  nu * (n12 + n22) / u1a**2 +
                                  (n12 + n22) * f0)
            Gamma = u2a**2 / n22 * (f0 * (nu * (n12 + n22) / u2a**2 +
                                          2 * nu * n12 / u1a**2 +
                                          n12 * f0))
        else:
            Gamma0 = u2a / n22 * (2 * nu * n22 / u2a**2 -
                                  nu * (n12 + n22) / u1a**2 +
                                  (n12 + n22) * f0)
            Gamma = u2a**2 / n22 * (f0 * (nu * (n12 + n22) / u2a**2 -
                                          2 * nu * n12 / u1a**2 +
                                          n12 * f0))

        return Gamma0, Gamma

    @classmethod
    def lpcutoff(cls, v0, nu):
        F, Fp, g, gp, u1r1, u2r1 = cls._params(v0, nu-1)
        return Fp / u2r1 * g + F / u1r1 * gp

    @classmethod
    def tecutoff(cls, v0, nu):
        F, Fp, g, gp, u1r1, u2r1 = cls._params(v0, nu)
        return Fp / u2r1 * g + F / u1r1 * gp

    @classmethod
    def tmcutoff(cls, v0, nu):
        F, Fp, g, gp, u1r1, u2r1 = cls._params(v0, nu)
        return cls.n[1]**2 * Fp / u2r1 * g + cls.n[0]**2 * F / u1r1 * gp


    @classmethod
    def ehcutoff2(cls, v0, nu):
        kappa1, kappa2, u1r1, u2r1, u2r2 = cls.kappaparams(v0, nu)

        d = kappa1**2 - 4 * kappa2
        if d > 0:
            if cls.n[1] < cls.n[2]: # a
                f1 = iv(nu+1, u2r1) * kn(nu, u2r2) + kn(nu+1, u2r1) * iv(nu, u2r2)
                f2 = iv(nu, u2r1) * kn(nu, u2r2) - kn(nu, u2r1) * iv(nu, u2r2)
            else: # b c d
                f1 = jn(nu+1, u2r1) * yn(nu, u2r2) - yn(nu+1, u2r1) * jn(nu, u2r2)
                f2 = jn(nu, u2r1) * yn(nu, u2r2) - yn(nu, u2r1) * jn(nu, u2r2)
        else:
            return numpy.nan

        if cls.n[1] > cls.n[0] > cls.n[2]:
            d0 = u2r1 * (nu / u2r1**2 - (kappa1 - sqrt(d)) / 2)  # d
        elif cls.n[1] < cls.n[2]:  # a
            d0 = u2r1 * (-nu / u2r1**2 + (kappa1 + sqrt(d)) / 2)
        else:
            d0 = u2r1 * (nu / u2r1**2 - (kappa1 + sqrt(d)) / 2)

        # print(Delta0 - d0)

        return f1 - d0 * f2


    @classmethod
    def hecutoff2(cls, v0, nu):
        kappa1, kappa2, u1r1, u2r1, u2r2 = cls.kappaparams(v0, nu)
        n1sq, n2sq, n3sq = numpy.square(cls.n)

        d = kappa1**2 - 4 * kappa2
        if d < 0:
            return numpy.nan

        if cls.n[1] > cls.n[0] > cls.n[2]:
            d0 = u2r1 * (nu / u2r1**2 - (kappa1 + sqrt(d)) / 2)  # d
        elif cls.n[1] < cls.n[2]:  # a
            d0 = u2r1 * (-nu / u2r1**2 + (kappa1 - sqrt(d)) / 2)
        else:
            d0 = u2r1 * (nu / u2r1**2 - (kappa1 - sqrt(d)) / 2)

        if nu == 1:
            if cls.n[1] < cls.n[2]:  # a
                f1 = iv(nu+1, u2r1) * kn(nu, u2r2) + kn(nu+1, u2r1) * iv(nu, u2r2)
                f2 = iv(nu, u2r1) * kn(nu, u2r2) - kn(nu, u2r1) * iv(nu, u2r2)
            else:  # b c d
                f1 = jn(nu+1, u2r1) * yn(nu, u2r2) - yn(nu+1, u2r1) * jn(nu, u2r2)
                f2 = jn(nu, u2r1) * yn(nu, u2r2) - yn(nu, u2r1) * jn(nu, u2r2)
            return f1 - d0 * f2

        else:
            n0sq = (n2sq - n3sq) / (n2sq + n3sq)
            if cls.n[1] < cls.n[2]:  # a
                n0sq = (n3sq - n2sq) / (n2sq + n3sq)
                g1 = d0 * iv(nu, u2r1) - iv(nu + 1, u2r1)
                g2 = d0 * kn(nu, u2r1) + kn(nu + 1, u2r1)
                f1 = iv(nu-2, u2r2) * g2 - kn(nu-2, u2r2) * g1
                f2 = iv(nu, u2r2) * g2 - kn(nu, u2r2) * g1

            elif cls.n[0] < cls.n[2]:  # c
                g1 = d0 * jn(nu, u2r1) - jn(nu + 1, u2r1)
                g2 = d0 * yn(nu, u2r1) - yn(nu + 1, u2r1)
                f1 = jn(nu-2, u2r2) * g2 - yn(nu-2, u2r2) * g1
                f2 = jn(nu, u2r2) * g2 - yn(nu, u2r2) * g1

            else:  # b d
                g1 = d0 * jn(nu, u2r1) - jn(nu + 1, u2r1)
                g2 = d0 * yn(nu, u2r1) - yn(nu + 1, u2r1)
                f1 = jn(nu-2, u2r2) * g2 - yn(nu-2, u2r2) * g1
                f2 = jn(nu, u2r2) * g2 - yn(nu, u2r2) * g1

            return f1 + n0sq * f2



class FiberA(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.47, 1.43, 1.44]
    name = "Fiber (a)"

    @classmethod
    def tecutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(U2[0]) * cls.rho[0]
        u2r1 = sqrt(-U2[1]) * cls.rho[0]
        u2r2 = sqrt(-U2[1]) * cls.rho[1]
        return (j0(u1r1) * (iv(2, u2r1) * k0(u2r2) - kn(2, u2r1) * i0(u2r2)) +
                jn(2, u1r1) * (i0(u2r1) * k0(u2r2) - k0(u2r1) * i0(u2r2)))


class FiberB(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.47, 1.45, 1.44]
    name = "Fiber (b)"

    @classmethod
    def lpcutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(U2[0]) * cls.rho[0]
        u2r1 = sqrt(U2[1]) * cls.rho[0]
        u2r2 = sqrt(U2[1]) * cls.rho[1]

        nu -= 1
        Fl1 = jn(nu, u2r1) * yn(nu, u2r2) - yn(nu, u2r1) * jn(nu, u2r2)
        Fl2 = jn(nu+1, u2r1) * yn(nu, u2r2) - yn(nu+1, u2r1) * jn(nu, u2r2)

        return u2r1 * Fl1 * jn(nu+1, u1r1) - u1r1 * Fl2 * jn(nu, u1r1)

    @classmethod
    def tecutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(U2[0]) * cls.rho[0]
        u2r1 = sqrt(U2[1]) * cls.rho[0]
        u2r2 = sqrt(U2[1]) * cls.rho[1]
        jn00 = j0(u2r1) * y0(u2r2) - y0(u2r1) * j0(u2r2)
        return (j0(u1r1) * (jn(2, u2r1) * y0(u2r2) - yn(2, u2r1) * j0(u2r2)) -
                jn(2, u1r1) * jn00)


class FiberC(COFiber):
    rho = [4e-6, 6e-6]
    n = [1.43, 1.47, 1.44]
    name = "Fiber (c)"

    @classmethod
    def tecutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(-U2[0]) * cls.rho[0]
        u2r1 = sqrt(U2[1]) * cls.rho[0]
        return (i0(u1r1) * (-jn(2, u2r1) * y0(v0) + yn(2, u2r1) * j0(v0)) -
                iv(2, u1r1) * (j0(u2r1) * y0(v0) - y0(u2r1) * j0(v0)))


class FiberD(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.45, 1.47, 1.44]
    name = "Fiber (d)"

    @classmethod
    def lpcutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(U2[0]) * cls.rho[0]
        u2r1 = sqrt(U2[1]) * cls.rho[0]
        u2r2 = sqrt(U2[1]) * cls.rho[1]

        nu -= 1
        Fl1 = jn(nu, u2r1) * yn(nu, u2r2) - yn(nu, u2r1) * jn(nu, u2r2)
        Fl2 = jn(nu+1, u2r1) * yn(nu, u2r2) - yn(nu+1, u2r1) * jn(nu, u2r2)

        return u2r1 * Fl1 * jn(nu+1, u1r1) - u1r1 * Fl2 * jn(nu, u1r1)

    @classmethod
    def tecutoff(cls, v0, nu):
        na = sqrt(max(cls.n)**2 - cls.n[-1]**2)
        K0 = v0 / na / cls.rho[-1]
        U2 = [K0**2 * (n**2 - cls.n[-1]**2) for n in cls.n]
        u1r1 = sqrt(U2[0]) * cls.rho[0]
        u2r1 = sqrt(U2[1]) * cls.rho[0]
        jn00 = j0(u2r1) * y0(v0) - y0(u2r1) * j0(v0)
        return (j0(u1r1) * (jn(2, u2r1) * y0(v0) - yn(2, u2r1) * j0(v0)) -
                jn(2, u1r1) * jn00)


class FiberE(COFiber):
    rho = [4e-6, 6e-6]
    n = [1.44, 1.47, 1.44]
    name = "Fiber (e)"

    @classmethod
    def tecutoff(cls, v0, nu):
        u2r1 = v0 * cls.rho[0] / cls.rho[1]
        return jn(2, u2r1) * y0(v0) - yn(2, u2r1) * j0(v0)

    @classmethod
    def tmcutoff(cls, v0, nu):
        u2r1 = v0 * cls.rho[0] / cls.rho[1]
        n02 = cls.n[1]**2 / cls.n[0]**2
        return (j0(v0) * yn(2, u2r1) - y0(v0) * jn(2, u2r1) -
                (1 - n02) / n02 * (j0(v0) * y0(u2r1) - j0(u2r1) * y0(v0)))

    @classmethod
    def hecutoff(cls, v0, nu):
        u2r1 = v0 * cls.rho[0] / cls.rho[1]
        n02 = cls.n[1]**2 / cls.n[0]**2
        if nu == 1:
            return j1(v0) * y1(u2r1) - j1(u2r1) * y1(v0)
        else:
            return (jn(nu-2, v0) * yn(nu, u2r1) - jn(nu, u2r1) * yn(nu-2, v0) -
                    (1 - n02) / (1 + n02) * (jn(nu, v0) * yn(nu, u2r1) -
                                             jn(nu, u2r1) * yn(nu, v0)))

    @classmethod
    def ehcutoff(cls, v0, nu):
        u2r1 = v0 * cls.rho[0] / cls.rho[1]
        n02 = cls.n[1]**2 / cls.n[0]**2
        return (jn(nu+2, u2r1) * yn(nu, v0) - jn(nu, v0) * yn(nu+2, u2r1) +
                (1 - n02) / (1 + n02) * (jn(nu, u2r1) * yn(nu, v0) -
                                         jn(nu, v0) * yn(nu, u2r1)))


def findRoots(fiber, mode, V0):
    nu = mode.nu

    if mode.family == ModeFamily.LP:
        fct = fiber.lpcutoff
    elif mode.family == ModeFamily.TE:
        fct = fiber.tecutoff
    elif mode.family == ModeFamily.TM:
        fct = fiber.tmcutoff
    elif mode.family == ModeFamily.EH:
        fct = fiber.ehcutoff2
    elif mode.family == ModeFamily.HE:
        fct = fiber.hecutoff2

    roots = []
    cf = numpy.fromiter((fct(v0, nu) for v0 in V0),
                        numpy.float,
                        V0.size)

    for i in range(V0.size - 1):
        if (cf[i] > 0 and cf[i+1] < 0) or (cf[i] < 0 and cf[i+1] > 0):
            r = brentq(fct, V0[i], V0[i+1], args=(nu))
            cr = fct(r, nu)
            if (abs(cf[i]) > abs(cr)) and (abs(cf[i+1]) > abs(cr)):
                roots.append(r)
    return roots


def plotProfile(f):
    R = [0]
    for r in f.rho:
        R.append(r)
        R.insert(0, -r)
    R.append(f.rho[-1]*2)
    R.insert(0, -f.rho[-1]*2)

    N = []
    for n in f.n:
        N.append(n)
        N.insert(0, n)
    N.insert(0, f.n[-1])

    pyplot.step(R, N)


def analyseFiber(f):
    print(f.name)
    wl = numpy.linspace(1000e-9, 5000e-9, 100)
    sim = Simulator(delta=f.delta)
    sim.setWavelength(wl)
    sim.setMaterials(*[Fixed] * len(f.n))
    sim.setRadii(*f.rho)
    for i, idx in enumerate(f.n):
        sim.setMaterialParam(i, 0, idx)

    # modes = sim.findLPModes()
    modes = sim.findVModes()
    # modes = [Mode("TM", 0, 1), Mode("TM", 0, 2)]
    # fiber = next(iter(sim))
    V0 = sim.getV0()

    for m in modes:
        # if m.nu != 0:
        #     continue

        # pyplot.plot(V0, sim.getNeff(m), label=str(m))
        pl, = pyplot.plot(V0, sim.getBnorm(m), label=str(m))
        c = pl.get_color()

        # if m.family != ModeFamily.EH:
        #     continue
        roots = findRoots(f, m, V0)[::-1]
        for j, r in enumerate(roots, 1):
            if m.nu == 1 and m.family == ModeFamily.HE and j+1 == m.m:
                pyplot.axvline(r, ls=':', color=c)
                print(str(m), roots[j-1])
            elif (m.nu != 1 or m.family != ModeFamily.HE) and j == m.m:
                pyplot.axvline(r, ls=':', color=c)
                print(str(m), roots[j-1])
        # print(str(m), roots[::-1] if roots else '')

    pyplot.legend()
    pyplot.ylim((0, 1))
    pyplot.xlabel("Normalized frequency ($V_0$)")
    pyplot.ylabel("Normalized propagation constant ($b$)")
    pyplot.title(f.name)


def plotcutoff(f):

    for n in (1.46, 1.48, 1.50):

        if f.n[0] > f.n[1]:
            f.n[0] = n
        else:
            f.n[1] = n

        mu = abs(f.n[2]**2 - f.n[0]**2) / abs(f.n[2]**2 - f.n[1]**2)
        if mu > 1:
            mu = 1 / mu

        rho = numpy.linspace(0, 1)
        v0 = numpy.zeros(rho.shape)
        for i, r in enumerate(rho):
            f.rho[0] = r * f.rho[1]
            roots = findRoots(f, Mode("TE", 0, 1), numpy.linspace(2, 15, 500))
            if roots:
                v0[i] = roots[0]
        v0 = numpy.ma.masked_equal(v0, 0)
        pyplot.plot(v0, rho, label="$\\mu = {:.2f}$".format(mu) if mu else '')

    rj0 = jn_zeros(0, 1)[0]
    pyplot.axvline(rj0, ls='--', color='k')

    pyplot.xlim((2, 6))
    pyplot.ylim((0, 1))
    pyplot.legend(loc='best')
    pyplot.xlabel('Normalized frequency $V_0$')
    pyplot.ylabel('Radii ratio $\\rho$')
    pyplot.title(f.name)


def main():
    for fiber in (
            # FiberA,
            # FiberB,
            # FiberC,
            FiberD,
            # FiberE,
            ):
        # pyplot.figure("profile " + fiber.name)
        # plotProfile(fiber)
        pyplot.figure(fiber.name)
        analyseFiber(fiber)
        # plotcutoff(fiber)


if __name__ == '__main__':
    import timeit
    print(timeit.timeit('main()',
                        setup="from __main__ import main",
                        number=1))

    pyplot.show()

    # import cProfile
    # cProfile.run('main()', 'coupure.stats')
