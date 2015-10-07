"""Module for material composed of two different materials."""

import warnings
from .material import Material, OutOfRangeWarning
from scipy.optimize import brentq


class CompMaterial(Material):

    """Abstract class for material composed of two materials."""

    XRANGE = None  # Acceptable range for the first parameter
    MATERIALS = None

    @classmethod
    def _testConcentration(cls, x):
        if cls.XRANGE is None:
            return
        if x <= cls.XRANGE:
            return
        msg = ("Concentration {} out of supported range for material {}. "
               "Concentration should be below {}. "
               "Results could be innacurate.").format(
            str(x),
            cls.name,
            cls.XRANGE)
        warnings.warn(msg, OutOfRangeWarning)

    @classmethod
    def xFromN(cls, wl, n):
        if cls.MATERIALS is not None:
            M1, M2 = cls.MATERIALS
            n1 = M1.n(wl)
            n2 = M2.n(wl)
            if n1 < n2:
                assert n1 <= n <= n2
            else:
                assert n2 <= n <= n1

        x = 1 if cls.XRANGE is None else cls.XRANGE
        return brentq(lambda x: cls.n(wl, x)-n, 0, x)

    @classmethod
    def str(cls, x):
        return "{} ({:.2f} %)".format(cls.name, x*100)
