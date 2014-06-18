'''
Created on 2014-05-06

@author: cbrunet
'''

import sys
sys.path.insert(0, '..')

if __name__ == '__main__':

    from matplotlib import pyplot
    import numpy

    from fibermodes import fixedFiber, Wavelength, Mode

    wl = Wavelength(1550e-9)
    n = numpy.array([1.4489, 1.4474, 1.4444])
    fiber = fixedFiber(wl, [4e-6, 10e-6], n)

    neff = numpy.linspace(n.min(), n.max(), 1000)
    ceq = numpy.zeros(neff.size)
    for m in (Mode('LP', 0, 1), Mode('LP', 1, 1)):
        for i in range(neff.size):
            ceq[i] = fiber._ceq(m)(neff[i], m)
        pyplot.plot(neff, ceq, label=str(m))

    lpmodes = fiber.lpModes(delta=1e-5)
    for m in lpmodes:
        print(m, m.neff)
        pyplot.axvline(m.neff, ls='--')

    pyplot.legend()
    pyplot.show()
