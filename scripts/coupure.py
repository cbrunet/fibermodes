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


def findCutoffs(fiber, nu, V0):
    f = numpy.fromiter((coeq(v0, nu, fiber) for v0 in V0),
                       dtype=float,
                       count=V0.size)
    cutoffs = []
    for i in range(1, f.size):
        if (f[i-1] > 0 and f[i] < 0) or (f[i-1] < 0 and f[i] > 0):
                r = brentq(coeq, V0[i-1], V0[i], args=(nu, fiber))
                cr = abs(coeq(r, nu, fiber))
                if (abs(f[i-1]) > cr) and (abs(f[i]) > cr):
                    cutoffs.append(r)
                    return cutoffs
    return cutoffs


def coeq(v0, nu, fiber):
    r1, r2 = fiber.rho
    n1, n2, n3 = fiber.n

    na = sqrt(max(fiber.n)**2 - n3**2)
    K0 = v0 / (na * r2)
    beta = K0 * n3

    if n1 > n3:
        u1 = K0**2 * (n1**2 - n3**2)
        s1 = 1
    else:
        u1 = K0**2 * (n3**2 - n1**2)
        s1 = -1
    if n2 > n3:
        u2 = K0**2 * (n2**2 - n3**2)
        s2 = 1
    else:
        u2 = K0**2 * (n3**2 - n2**2)
        s2 = -1
    s = -s1 * s2

    u1r1 = u1 * r1
    u2r1 = u2 * r1
    u2r2 = u2 * r2

    X = (u2r1**2 + s * u1r1**2) * nu * beta
    if s1 == 1:
        Y = jvp(nu, u1r1) / jn(nu, u1r1)
    else:
        Y = ivp(nu, u1r1) / iv(nu, u1r1)

    ju2r1 = jn(nu, u2r1) if s2 == 1 else iv(nu, u2r1)
    nu2r1 = yn(nu, u2r1) if s2 == 1 else kn(nu, u2r1)
    jpu2r1 = jvp(nu, u2r1) if s2 == 1 else ivp(nu, u2r1)
    npu2r1 = yvp(nu, u2r1) if s2 == 1 else kvp(nu, u2r1)
    ju2r2 = jn(nu, u2r2) if s2 == 1 else iv(nu, u2r2)
    nu2r2 = yn(nu, u2r2) if s2 == 1 else kn(nu, u2r2)
    j1u2r2 = jn(nu+1, u2r2)
    n1u2r2 = yn(nu+1, u2r2)

    M = numpy.empty((4, 4))
    M[0, 0] = X * ju2r1
    M[0, 1] = X * nu2r1
    M[0, 2] = -K0 * (jpu2r1 * u1r1 + s * Y * ju2r1 * u2r1) * u1r1 * u2r1
    M[0, 3] = -K0 * (npu2r1 * u1r1 + s * Y * nu2r1 * u2r1) * u1r1 * u2r1
    M[1, 0] = -K0 * (n2**2 * jpu2r1 * u1r1 +
                     s * n1**2 * Y * ju2r1 * u2r1) * u1r1 * u2r1
    M[1, 1] = -K0 * (n2**2 * npu2r1 * u1r1 +
                     s * n1**2 * Y * nu2r1 * u2r1) * u1r1 * u2r1
    M[1, 2] = X * ju2r1
    M[1, 3] = X * nu2r1

    D201 = nu * n3 / u2r2 * (j1u2r2 * nu2r2 - ju2r2 * yn(nu+1, u2r2))
    D202 = -((n2**2 + n3**2) * nu * n1u2r2 * nu2r2 / u2r2 +
             n3**2 * nu * nu2r2**2 / (nu - 1))
    D203 = -(n2**2 * nu * ju2r2 * n1u2r2 / u2r2 +
             n3**2 * nu * nu2r2 * j1u2r2 / u2r2 +
             n3**2 * nu * (j1u2r2 * nu2r2 +
                           n1u2r2 * ju2r2) / (2 * (nu - 1)))
    D212 = -(n2**2 * nu * nu2r2 * j1u2r2 / u2r2 +
             n3**2 * nu * ju2r2 * n1u2r2 / u2r2 +
             n3**2 * nu * (n1u2r2 * ju2r2 +
                           j1u2r2 * nu2r2) / (2 * (nu - 1)))
    D213 = -((n2**2 + n3**2) * nu * j1u2r2 * ju2r2 / u2r2 +
             n3**2 * nu * ju2r2**2 / (nu - 1))
    D223 = nu * n2**2 * n3 / u2r2 * (j1u2r2 * nu2r2 - ju2r2 * n1u2r2)

    D30 = M[1, 1] * D201 - M[1, 2] * D202 + M[1, 3] * D203
    D31 = M[1, 0] * D201 - M[1, 2] * D212 + M[1, 3] * D213
    D32 = M[1, 0] * D202 - M[1, 1] * D212 + M[1, 3] * D223
    D33 = M[1, 0] * D203 - M[1, 1] * D213 + M[1, 2] * D223

    return M[0, 0] * D30 - M[0, 1] * D31 + M[0, 2] * D32 - M[0, 3] * D33


class COFiber(object):
    delta = 1e-3


class FiberA(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.47, 1.43, 1.44]
    name = "Fiber (a)"


class FiberB(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.47, 1.45, 1.44]
    name = "Fiber (b)"


class FiberC(COFiber):
    rho = [4e-6, 6e-6]
    n = [1.43, 1.47, 1.44]
    name = "Fiber (c)"


class FiberD(COFiber):
    delta = 1e-4
    rho = [4e-6, 6e-6]
    n = [1.45, 1.47, 1.44]
    name = "Fiber (d)"


class FiberE(COFiber):
    rho = [4e-6, 6e-6]
    n = [1.44, 1.47, 1.44]
    name = "Fiber (e)"


class RCF_ref(COFiber):
    rho = [4e-6, 6e-6]
    n = [1, 1.5, 1]
    # n = [1.5, 2, 1.5]
    name = "RCF (reference)"


class RCF_low(RCF_ref):
    n = [1, 2, 1.5]
    name = "RCF (lower)"


class RCF_high(RCF_ref):
    delta = 1e-4
    n = [1.75, 2, 1.5]
    name = "RCF (higher)"


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
    # wl = numpy.linspace(2100e-9, 2400e-9, 1000)
    wl = numpy.linspace(1500e-9, 5000e-9, 100)
    # wl = numpy.linspace(7000e-9, 20000e-9, 50)
    sim = Simulator(delta=f.delta)
    sim.setWavelength(wl)
    sim.setMaterials(*[Fixed] * len(f.n))
    sim.setRadii(*f.rho)
    for i, idx in enumerate(f.n):
        sim.setMaterialParam(i, 0, idx)

    V0 = sim.getV0()
    # print(V0[0], V0[-1])
    # return

    # modes = sim.findLPModes()
    modes = sim.findVModes()
    # modes = [Mode("TM", 0, 1), Mode("TM", 0, 2)]
    fiber = next(iter(sim))

    for m in modes:
        cutoff = sim.getCutoffV0(fiber, m)
        if cutoff < V0[-1]:
            continue

        # pyplot.plot(V0, sim.getNeff(m), label=str(m))
        pl, = pyplot.plot(V0, sim.getBnorm(m), label=str(m))
        c = pl.get_color()

        if str(m) in ("HE(1,1)", "LP(0,1)"):
            continue

        print(str(m), cutoff)
        pyplot.axvline(cutoff, ls=':', color=c)
        # if m.nu > 1:
        #     cutoffs = findCutoffs(f, m.nu, V0)
        #     for c in cutoffs:
        #         pyplot.axvline(c, ls=':', color='k')

    # pyplot.legend(loc="best")
    pyplot.xlim((2.5, 7))
    # pyplot.ylim((0, 1))
    pyplot.ylim((0, 0.3))
    # pyplot.xlabel("Normalized frequency ($V_0$)")
    # pyplot.ylabel("Normalized propagation constant ($b$)")
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
    for i, fiber in enumerate((
            FiberA,
            FiberB,
            FiberC,
            FiberD,
            FiberE,
            # RCF_ref,
            # , RCF_low, RCF_high
            ), 1):
        # pyplot.figure("profile " + fiber.name)
        # plotProfile(fiber)
        # pyplot.figure(fiber.name)
        pyplot.subplot(5, 1, i)
        analyseFiber(fiber)
        # plotcutoff(fiber)

        if i == 5:
            pyplot.xlabel("Normalized frequency ($V_0$)")
        if i == 3:
            pyplot.ylabel("Normalized propagation constant ($b$)")


if __name__ == '__main__':
    import timeit
    print(timeit.timeit('main()',
                        setup="from __main__ import main",
                        number=1))

    pyplot.show()

    # import cProfile
    # cProfile.run('main()', 'coupure.stats')
