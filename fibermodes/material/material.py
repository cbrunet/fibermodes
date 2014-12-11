'''
Created on 2014-05-01

@author: cbrunet
'''

import warnings
from math import sqrt
import numpy


class OutOfRangeWarning(UserWarning):
    pass


def sellmeier(wl, b, c):
    x2 = wl * wl * 1e12
    return sqrt(1 + x2 * sum(b[i] / (x2 - c[i]**2) for i in range(3)))


def claussiusMossotti(wl, a, b, z, x):
    """ Claussius-Mossotti interpolation scheme.

    :param wl: Wavelength (in meter)
    :param a: A parameter (3 numbers array) for Silica
    :param b: B parameter (3 numbers array)
    :param z: z parameter (3 numbers array)
    :param x: molar fraction
    :rtype: float

    """
    wl2 = wl * wl
    s = numpy.sum((a + b * x) * wl2 / (wl2 - z * z))
    return sqrt((2 * s + 1) / (1 - s))


class Material(object):

    '''
    classdocs
    '''

    name = "Abstract Material"
    nparams = 0
    URL = None
    WLRANGE = None
    XRANGE = None

    @classmethod
    def _testRange(cls, wl):
        if cls.WLRANGE is None:
            return
        if cls.WLRANGE[0] <= wl <= cls.WLRANGE[1]:
            return

        msg = ("Wavelength {} out of supported range for material {}. "
               "Wavelength should be in the range {} - {}. "
               "Results could be innacurate.").format(
            str(wl),
            cls.name,
            cls.WLRANGE[0],
            cls.WLRANGE[1])
        warnings.warn(msg, OutOfRangeWarning)

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
    def n(cls, wl, *args, **kwargs):
        raise NotImplementedError(
            "This method must be implemented in super class.")

    @classmethod
    def info(cls):
        raise NotImplementedError(
            "This method must be implemented in super class.")

    @classmethod
    def refUrl(cls):
        return cls.URL

    @classmethod
    def __str__(cls):
        return cls.name

    @classmethod
    def __repr__(cls):
        return "{}()".format(cls.__name__)


if __name__ == '__main__':
    m = Material()
    print(m)
    print(repr(m))
