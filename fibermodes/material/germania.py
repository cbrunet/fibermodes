'''
Created on 2014-09-08

@author: cbrunet
'''

from .material import Material, sellmeier
from ..wavelength import Wavelength


class Germania(Material):

    '''
    classdocs
    '''

    name = "Germanium dioxide"
    nparams = 0
    URL = "http://refractiveindex.info/?shelf=main&book=GeO2&page=Fleming"
    WLRANGE = (Wavelength(0.36e-6), Wavelength(4.3e-6))
    B = (0.80686642, 0.71815848, 0.85416831)
    C = (0.068972606, 0.15396605, 11.841931)

    @classmethod
    def n(cls, wl):
        return sellmeier(wl, cls.B, cls.C)

    @classmethod
    def info(cls):
        return "Fused germanium dioxide."

# J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
# vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
# http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486
