from .compmaterial import CompMaterial
import numpy
from math import sqrt


class ClaussiusMossotti(CompMaterial):

    nparams = 1
    WLRANGE = (0.6e-6, 1.8e-6)

    A = numpy.array([0.2045154578, 0.06451676258, 0.1311583151])
    B = None
    Z = numpy.array([0.06130807320e-6, 0.1108859848e-6, 8.964441861e-6])

    @classmethod
    def n(cls, wl, x):
        if cls.B is None:
            raise NotImplementedError(
                "This method must be implemented in derived class.")
        cls._testRange(wl)
        cls._testConcentration(x)

        wl2 = wl * wl
        s = numpy.sum((cls.A + cls.B * x) * wl2 / (wl2 - cls.Z * cls.Z))
        return sqrt((2 * s + 1) / (1 - s))
