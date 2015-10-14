"""Sellmeier material module.

"""

from .material import Material
from math import sqrt


class Sellmeier(Material):

    """Material based on Sellmeier formula.

    This is an abstract class for materials like SiO2 and GeO2.

    """

    nparams = 0
    B = None  # List for B parameter
    C = None  # List for C parameter

    @classmethod
    def _n(cls, wl, B, C):
        x2 = wl * wl * 1e12
        return sqrt(abs(1 + x2 * sum(b / (x2 - c**2) for (b, c) in zip(B, C))))

    @classmethod
    def n(cls, wl):
        if cls.B is None or cls.C is None:
            raise NotImplementedError(
                "This method must be implemented in derived class.")
        cls._testRange(wl)
        return cls._n(wl, cls.B, cls.C)
