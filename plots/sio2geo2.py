"""Plot refractive index as function of concentration and wavelength.

Updated: 2015-10-15

"""

from fibermodes.fiber.material import SiO2GeO2, Silica, Germania
from fibermodes.fiber.material.sio2geo2cm import SiO2GeO2 as SiO2GeO2CM
import numpy
from matplotlib import pyplot


def n_fx():
    pyplot.figure()
    X = numpy.linspace(0, 1)
    wl = 1550e-9
    n = [SiO2GeO2CM.n(wl, x) for x in X]
    pyplot.plot(X, n, c='b', ls=':')
    XR = X[X <= SiO2GeO2CM.XRANGE]
    n = [SiO2GeO2CM.n(wl, x) for x in XR]
    pyplot.plot(XR, n, c='b', ls='-', label="Claussius-Mossotti")

    n = [SiO2GeO2.n(wl, x) for x in X]
    pyplot.plot(X, n, c='g', ls='-', label="Sellmeyer")

    pyplot.axhline(Germania.n(wl), color='r', label="Germania")
    pyplot.axhline(Silica.n(wl), color='m', label="Silica")

    pyplot.legend(loc='best')
    pyplot.title("Wavelength: 1550 nm")
    pyplot.xlabel("Molar concentration")
    pyplot.ylabel("Index")


def n_fw():
    pyplot.figure()
    W = numpy.linspace(0.5e-6, 2.0e-6)
    x = 0.025
    n = [SiO2GeO2CM.n(wl, x) for wl in W]
    pyplot.plot(W*1e6, n, c='b', ls=':')
    WR = W[SiO2GeO2CM.WLRANGE[0] <= W]
    WR = WR[WR <= SiO2GeO2CM.WLRANGE[1]]
    n = [SiO2GeO2CM.n(wl, x) for wl in WR]
    pyplot.plot(WR*1e6, n, c='b', ls='-', label="Claussius-Mossotti")

    n = [SiO2GeO2.n(wl, x) for wl in W]
    pyplot.plot(W*1e6, n, c='g', ls=':')
    WR = W[SiO2GeO2.WLRANGE[0] <= W]
    WR = WR[WR <= SiO2GeO2.WLRANGE[1]]
    n = [SiO2GeO2.n(wl, x) for wl in WR]
    pyplot.plot(WR*1e6, n, c='g', ls='-', label="Sellmeyer")

    pyplot.legend(loc='best')
    pyplot.title("Concentration: 2.5%")
    pyplot.xlabel("Wavelength (um)")
    pyplot.ylabel("Index")

if __name__ == '__main__':
    n_fx()
    n_fw()
    pyplot.show()
