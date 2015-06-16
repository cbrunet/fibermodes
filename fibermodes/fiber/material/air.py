"""Module for Air material."""

from .material import Material
from fibermodes.wavelength import Wavelength


class Air(Material):

    """Class for Air material."""

    name = "Air"
    nparams = 0
    info = "Dry air, at 15 °C, 101 325 Pa and with 450 ppm CO₂ content."
    url = "http://refractiveindex.info/legacy/?group=GASES&material=Air"
    WLRANGE = (Wavelength(0.23e-6), Wavelength(1.69e-6))

    @classmethod
    def n(cls, wl):
        x2inv = 1 / (wl * wl * 1e12)
        return (1 + 5792105e-8 / (238.0185-x2inv)
                + 167917e-8 / (57.362-x2inv))
