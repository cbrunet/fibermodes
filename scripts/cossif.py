
import numpy
from matplotlib import pyplot
from fibermodes.material import Fixed
from fibermodes.simulator import PSimulator as Simulator
from scipy.special import j0, j1, jn, y0, y1, yn

def plotNeff():
    b = 4e-6
    ncl = 1.444
    nco = ncl + 0.05
    wl = numpy.linspace(1500e-9, 5000e-9, 50)
    V = 2 * numpy.pi / wl * b * numpy.sqrt(nco*nco - ncl*ncl)

    sim = Simulator()
    sim.setWavelength(wl)
    sim.setMaterials(Fixed, Fixed)
    sim.setMaterialParam(0, 0, nco)
    sim.setMaterialParam(1, 0, ncl)
    sim.setRadius(0, b)

    modes = sim.findVModes()

    for m in modes:
        neff = sim.getBnorm(m)
        pyplot.plot(V, neff, label=str(m))

    pyplot.show()


def plotCF():
    ncl = 1.444
    nco = ncl + 0.05
    V = numpy.linspace(1, 7)

    pyplot.plot(V, j0(V))
    pyplot.plot(V, j1(V))
    pyplot.plot(V, jn(2, V))

    n02 = ncl*ncl / (nco * nco)
    a = (1 - n02) / (1 + n02)
    pyplot.plot(V, a * jn(2, V) - j0(V))
    pyplot.plot(V, a * jn(3, V) - j1(V))
    pyplot.plot(V, a * jn(4, V) - jn(2, V))

    pyplot.axhline(0, ls='--', color='k')

    pyplot.show()


def plotrcfte():
    V = numpy.linspace(1, 7)
    rho = 0.5

    f = j0(V) * yn(2, V*rho) - y0(V) * jn(2, rho*V)
    pyplot.plot(V, f)
    pyplot.show()


if __name__ == '__main__':
    plotrcfte()
