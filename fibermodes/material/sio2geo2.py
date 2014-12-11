'''
Created on 2014-09-08

@author: cbrunet
'''

from .material import Material, sellmeier
from .silica import Silica
from .germania import Germania
from scipy.optimize import brentq


class SiO2GeO2(Material):

    '''
    classdocs
    '''

    name = "Silica doped with Germania"
    nparams = 1
    WLRANGE = (max(Silica.WLRANGE[0], Germania.WLRANGE[0]),
               min(Silica.WLRANGE[1], Germania.WLRANGE[1]))

    @classmethod
    def n(cls, wl, x):
        B = tuple(Silica.B[i] + x * (Germania.B[i] - Silica.B[i])
                  for i in range(3))
        C = tuple(Silica.C[i] + x * (Germania.C[i] - Silica.C[i])
                  for i in range(3))
        return sellmeier(wl, B, C)

    @classmethod
    def info(cls):
        return "Silica doped with Germania."

    @classmethod
    def xFromN(cls, wl, n):
        nSi = Silica.n(wl)
        nGe = Germania.n(wl)
        assert nSi <= n <= nGe

        return brentq(lambda x: cls.n(wl, x)-n, 0, 1)

# J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
# vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
# http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486
