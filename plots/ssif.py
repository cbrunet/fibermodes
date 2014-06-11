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

    n1 = 1.454
    n2 = 1.444
    n1, n2 = (1.448918, 1.444418)

    fiber = fixedFiber(Wavelength(1550e-9), [4e-6], [n1, n2])

    neff = numpy.linspace(n2, n1)
    ceq = numpy.zeros(neff.size)
    for m in (Mode('LP', 0, 1), Mode('HE', 1, 1)):
        for i in range(neff.size):
            ceq[i] = fiber._ceq(m)(neff[i], m)
        pyplot.plot(neff, ceq, label=str(m))

    pyplot.legend()
    pyplot.show()
