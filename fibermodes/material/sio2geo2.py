'''
Created on 2014-09-08

@author: cbrunet
'''

from .material import Material, claussiusMossotti
from .silica import Silica
from .germania import Germania
from scipy.optimize import brentq
import numpy


class SiO2GeO2(Material):

    '''
    classdocs
    '''

    name = "Silica doped with Germania"
    nparams = 1
    WLRANGE = (0.6e-6, 1.8e-6)
    XRANGE = 0.2

    A = numpy.array([0.2045154578, 0.06451676258, 0.1311583151])
    B = numpy.array([-0.1011783769, 0.1778934999, -0.1064179581])
    Z = numpy.array([0.06130807320e-6, 0.1108859848e-6, 8.964441861e-6])

    @classmethod
    def n(cls, wl, x):
        cls._testRange(wl)
        cls._testConcentration(x)
        return claussiusMossotti(wl, cls.A, cls.B, cls.Z, x)

    @classmethod
    def info(cls):
        return "Silica doped with Germania."

    @classmethod
    def xFromN(cls, wl, n):
        nSi = Silica.n(wl)
        nGe = Germania.n(wl)
        assert nSi <= n <= nGe

        return brentq(lambda x: cls.n(wl, x)-n, 0, cls.XRANGE)

# J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
# vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
# http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486

# Article (Sunak1989)
# Sunak, H. & Bastien, S.
# Refractive index and material dispersion interpolation of doped silica
# in the 0.6-1.8 mu m wavelength region
# Photonics Technology Letters, IEEE, 1989, 1, 142-145
