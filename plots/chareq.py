from fibermodes import Wavelength, fixedFiber, HE11
import numpy
from matplotlib import pyplot

if __name__ == '__main__':
    wl = Wavelength(1550e-9)
    r = [4e-6, 10e-6]
    n = [1.4474, 1.4489, 1.4444]
    N = 1000
    mode = HE11

    fiber = fixedFiber(wl, r, n)
    neff = numpy.linspace(n[-1], max(n), N)

    x = [fiber._heceq(n, mode) for n in neff]

    pyplot.plot(neff[1:-1], x[1:-1])
    # pyplot.ylim((-1e5, 1e5))


    pyplot.show()
