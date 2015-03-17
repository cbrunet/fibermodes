
from fibermodes.material import SiO2GeO2, Silica, Germania
from fibermodes.material.sio2geo2cm import SiO2GeO2 as SiO2GeO2CM
from fibermodes.material.material import sellmeier
import numpy
from matplotlib import pyplot


if __name__ == '__main__':
    X = numpy.linspace(0, 1)
    wl = 1550e-9
    n = [SiO2GeO2CM.n(wl, x) for x in X]
    pyplot.plot(X, n, label="Claus")

    n = [SiO2GeO2.n(wl, x) for x in X]
    pyplot.plot(X, n, label="Claus")

    n = []
    for x in X:
        b = numpy.array(Silica.B) + x * (numpy.array(Germania.B) - numpy.array(Silica.B))
        c = numpy.array(Silica.C) + x * (numpy.array(Germania.C) - numpy.array(Silica.C))
        n.append(sellmeier(wl, b, c))
    pyplot.plot(X, n, label="Sell")

    pyplot.axhline(Germania.n(wl))
    pyplot.plot([0, 1], [Silica.n(wl), Germania.n(wl)])

    pyplot.legend()
    pyplot.show()
