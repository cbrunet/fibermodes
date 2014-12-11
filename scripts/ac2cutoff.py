
from math import pi, sqrt
import numpy
from scipy.special import j0, y0, j1, y1, jn, yn, i0, i1, iv, jvp, yvp, ivp
from matplotlib import pyplot

wl = 1550e-9
k0 = 2 * pi / wl

n1 = 1
n2 = 2
n3 = 1.444

rho = .25


n32 = n3 * n3
n22 = n2 * n2
n12 = n1 * n1

u1 = k0 * sqrt(n32 - n12)
u2 = k0 * sqrt(n22 - n32)


def cutoffTE(b):
    # EXP: 2.4220557071361126
    a = rho * b
    return (i0(u1*a) * (j0(u2*b) * yn(2, u2*a) - y0(u2*b) * jn(2, u2*a)) -
            iv(2, u1*a) * (j0(u2*a) * y0(u2*b) - y0(u2*a) * j0(u2*b)))


def cutoffTM(b):
    # EXP: 2.604335468618898
    a = rho * b
    return (n22 / n12 * (j0(u2*b) * yn(2, u2*a) - y0(u2*b) * jn(2, u2*a)) +
            (n22 / n12 - 1 + iv(2, u1*a) / i0(u1*a)) *
            (j0(u2*b) * y0(u2*a) - y0(u2*b) * j0(u2*a)))


def fullDet(b, nu):
    a = rho * b
    i = ivp(nu, u1*a) / (u1*a * iv(nu, u1*a))

    if nu == 1:
        k2 = -2
        k = 0
    else:
        k2 = 2 * nu / (u2 * b)**2 - 1 / (nu - 1)
        k = -1

    X = (1 / (u1*a)**2 + 1 / (u2*a)**2)

    P1 = jn(nu, u2*a) * yn(nu, u2*b) - yn(nu, u2*a) * jn(nu, u2*b)
    P2 = (jvp(nu, u2*a) * yn(nu, u2*b) - yvp(nu, u2*a) * jn(nu, u2*b)) / (u2 * a)
    P3 = (jn(nu, u2*a) * yvp(nu, u2*b) - yn(nu, u2*a) * jvp(nu, u2*b)) / (u2 * b)
    P4 = (jvp(nu, u2*a) * yvp(nu, u2*b) - yvp(nu, u2*a) * jvp(nu, u2*b)) / (u2 * a * u2 * b)

    A = (n12 * i**2 - n32 * nu**2 * X**2)

    if nu == 1:
        B = 0
    else:
        B = 2 * n22 * n32 * nu * X * (P1 * P4 - P2 * P3)

    return (n32 * k2 * A * P1**2 +
            (n12 + n22) * n32 * i * k2 * P1 * P2 -
            (n22 + n32) * k * A * P1 * P3 -
            (n12*n32 + n22*n22) * i * k * P1 * P4 +
            n22 * n32 * k2 * P2**2 -
            n22 * (n12 + n32) * i * k * P2 * P3 -
            n22 * (n22 + n32) * k * P2 * P4 -
            B)


def cutoffHE1(b):
    a = rho * b
    i = ivp(1, u1*a) / (u1*a * i1(u1*a))

    X = (1 / (u1*a)**2 + 1 / (u2*a)**2)

    P = j1(u2*a) * y1(u2*b) - y1(u2*a) * j1(u2*b)
    Ps = (jvp(1, u2*a) * y1(u2*b) - yvp(1, u2*a) * j1(u2*b)) / (u2 * a)

    return (i * P + Ps) * (n12 * i * P + n22 * Ps) - n32 * X * X * P * P


def cutoffHE2(b):
    nu = 2
    a = rho * b
    i = ivp(2, u1*a) / (u1*a * iv(2, u1*a))

    X = (1 / (u1*a)**2 + 1 / (u2*a)**2)

    P1 = jn(nu, u2*a) * yn(nu, u2*b) - yn(nu, u2*a) * jn(nu, u2*b)
    P2 = (jvp(nu, u2*a) * yn(nu, u2*b) - yvp(nu, u2*a) * jn(nu, u2*b)) / (u2 * a)
    P3 = (jn(nu, u2*a) * yvp(nu, u2*b) - yn(nu, u2*a) * jvp(nu, u2*b)) / (u2 * b)
    P4 = (jvp(nu, u2*a) * yvp(nu, u2*b) - yvp(nu, u2*a) * jvp(nu, u2*b)) / (u2 * a * u2 * b)

    A = 2 * nu / (u2 * b)**2 - 1 / (nu - 1)

    return (n22 / n32 * (i*P1 + P2) * (n12*i*P3 + n22 * P4) +
            (A * i * P1 + A * P2 + i*P3 + P4) * (n12*i*P1 + n22*P2) -
            n32 * nu**2 * X**2 * P1 * (A * P1 + P3) -
            n22 * nu * X * (nu * X * P1 * P3 + 2 * P1 * P4 - 2 * P2 * P3))

# HE 2,1: ~2.73
# EH 1,1: >3,81
# HE 3,1: ~4.2
# HE 1,2: ~5

if __name__ == '__main__':
    b = numpy.linspace(2e-7, 2e-6, 1001)

    # pyplot.plot(u2 * b, cutoffTE(b), label="TE")
    # pyplot.plot(u2 * b, cutoffTM(b), label="TM")
    # pyplot.plot(u2 * b, cutoffHE1(b), label="HE1")
    # pyplot.plot(u2 * b, fullDet(b, 1), label="HE1 bis")
    pyplot.plot(u2 * b, cutoffHE2(b), label="HE2")
    pyplot.plot(u2 * b, fullDet(b, 2), label="HE2 bis")

    pyplot.axhline(0, ls='--')
    pyplot.ylim((-2, 2))
    pyplot.legend(loc='best')
    pyplot.show()
