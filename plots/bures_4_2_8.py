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

    n2 = 1.457420
    n1 = 1.462420
    rho = 8.335e-6
    wl = Wavelength(0.6328e-6)

    fiber = fixedFiber(wl, [rho], [n1, n2])
    modes = fiber.lpModes(delta=1e-4)

    neff = numpy.linspace(n2, n1, 100)
    ceq = numpy.zeros(neff.size)
    for m in (Mode('LP', 3, 1), Mode('LP', 4, 1)):
        for i in range(neff.size):
            ceq[i] = fiber._ceq(m)(neff[i], m)
        pyplot.plot(neff, ceq, label=str(m))

    lpmodes = fiber.lpModes(delta=1e-5)
    for m in lpmodes:
        if str(m) == 'LP(3,1)':
            print(m, m.neff)
            pyplot.axvline(m.neff, ls='--')

    pyplot.legend()
    pyplot.show()
