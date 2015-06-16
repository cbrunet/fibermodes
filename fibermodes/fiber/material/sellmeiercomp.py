"""Module for material based on the composition of two Sellmeier materials."""

from .sellmeier import Sellmeier
from .compmaterial import CompMaterial
import numpy


class SellmeierComp(Sellmeier, CompMaterial):

    """Abstract class for material composed of two Sellmeier materials."""

    nparams = 1

    @classmethod
    def n(cls, wl, x):
        if cls.MATERIALS is None:
            raise NotImplementedError(
                "This method must be implemented in derived class.")
        cls._testRange(wl)
        cls._testConcentration(x)

        M1, M2 = cls.MATERIALS
        B = numpy.array(M1.B)
        Bp = numpy.array(M2.B) - B
        C = numpy.array(M1.C)
        Cp = numpy.array(M2.C) - C
        return cls._n(wl, B + x * Bp, C + x * Cp)
