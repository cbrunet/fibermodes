'''
Created on 2014-05-01

@author: cbrunet
'''

import warnings
from numpy import sqrt


class OutOfRangeWarning(UserWarning):

    def __init__(self, wl, material):
        self.wl = wl
        self.material = material

    def __str__(self):
        return ("Wavelength {} out of supported range for material {}. "
                "Wavelength should be in the range {} - {}. "
                "Results could be innacurate.").format(
                    str(self.wl),
                    str(self.material),
                    self.material.WLRANGE[0],
                    self.material.WLRANGE[1])


def sellmeier(wl, b, c):
    x2 = wl * wl * 1e12
    return sqrt(1 + x2 * sum(b[i] / (x2 - c[i]**2) for i in range(3)))


class Material(object):

    '''
    classdocs
    '''

    name = "Abstract Material"
    nparams = 0
    URL = None
    WLRANGE = None

    @classmethod
    def _testRange(cls, wl):
        if cls.WLRANGE is None:
            return
        if cls.WLRANGE[0] <= wl <= cls.WLRANGE[1]:
            return
        warnings.warn(wl, cls)

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
