from fibermodes.material import Silica, Germania, Air
import numpy
from matplotlib import pyplot


def plotMaterial(wl, mat, epsilon=1e-12):
    pyplot.figure()
    n = mat.n(wl*1e-6)
    pyplot.plot(wl, n, label="n")

    np = mat.n(wl*1e-6 + epsilon)
    nm = mat.n(wl*1e-6 - epsilon)
    dn = (np - nm) / (2 * epsilon)
    ng = n - wl * dn * 1e-6
    pyplot.plot(wl, ng, label="ng")

    pyplot.grid()
    pyplot.title(mat.name)
    pyplot.xlim((wl[0], wl[-1]))
    pyplot.legend()

if __name__ == '__main__':
    wl = numpy.linspace(0.5, 1.6)
    plotMaterial(wl, Silica)
    plotMaterial(wl, Germania)
    plotMaterial(wl, Air)
    pyplot.show()
