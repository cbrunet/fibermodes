"""Module for fixed index material."""

from .material import Material


class Fixed(Material):

    """Fixed index material class.

    A material with a fixed index always have the same refractive index,
    whatever the wavelength is.

    """

    name = "Fixed index"
    info = "Fixed index"
    nparams = 1

    @classmethod
    def n(cls, wl, n):
        return n
