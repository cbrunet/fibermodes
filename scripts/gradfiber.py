
import numpy
from matplotlib import pyplot


def n(r, ncl, a, b, c, m=1):
    return ncl + a * numpy.exp(-(((r-b)/c)**(2*m) / 2))


def dn(r, ncl, a, b, c, m=1):
    return -a * numpy.exp(-(((r-b)/c)**(2*m) / 2)) * m * ((r - b) / c)**(2*m-1)


if __name__ == '__main__':
    R = numpy.linspace(0, 15e-6, 1000)
    ncl = 1.444
    a = 0.03
    b = 6e-6
    c = 2e-6
    m = 1

    N = n(R, ncl, a, b, c, m)
    pyplot.plot(R*1e6, N)
    pyplot.ylim((ncl, ncl+a))

    pyplot.figure()
    pyplot.plot(R*1e6, dn(R, ncl, a, b, c, m))
    pyplot.show()
