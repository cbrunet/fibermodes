'''
Created on 2014-05-06

@author: cbrunet
'''

import sys
sys.path.insert(0, '..')

if __name__ == '__main__':

    from matplotlib import pyplot
    import numpy

    from fibermodes import fixedFiber, Wavelength

    wl = Wavelength(1550e-9)
    n = numpy.array([1.4444, 1.4489, 1.4474])
    fiber = fixedFiber(wl, [4e-6, 10e-6], n)

    wl = Wavelength(1550e-9)
    n = numpy.array([1.4489, 1.4444, 1.4474])
    fiber = fixedFiber(wl, [10e-6, 16e-6], n)

    lpmodes = fiber.lpModes(delta=1e-3)
    for m in lpmodes:
        print(m, m.neff)
        pyplot.axvline(m.neff, ls='--')

    vmodes = fiber.vModes(delta=1e-4)
    for m in vmodes:
        print(m, m.neff)
        pyplot.axvline(m.neff, ls=':')

    neff = numpy.linspace(n.min(), n.max(), 1000)
    ceq = numpy.zeros(neff.size)
    for m in vmodes:
        for i in range(neff.size):
            ceq[i] = fiber._ceq(m)(neff[i], m)
        pyplot.plot(neff, ceq, label=str(m))

    pyplot.legend()
    pyplot.show()
