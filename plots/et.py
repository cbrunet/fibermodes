import numpy
from matplotlib import pyplot


phi = numpy.linspace(-numpy.pi, numpy.pi)
Ep = 1
Er = 2


f = (Er * numpy.sin(phi))**2 + (Ep * numpy.cos(phi))**2

pyplot.plot(phi, f)
pyplot.show()
