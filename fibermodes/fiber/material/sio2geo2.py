"""Module for composition of Silica and Germania."""

from .sellmeiercomp import SellmeierComp
from .silica import Silica
from .germania import Germania


class SiO2GeO2(SellmeierComp):

    """Composition of Silica and Germania."""

    name = "Silica doped with Germania"
    info = """J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486
"""
    url = "http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486"
    WLRANGE = (0.6e-6, 1.8e-6)
    XRANGE = 1
    MATERIALS = (Silica, Germania)


# Article (Sunak1989)
# Sunak, H. & Bastien, S.
# Refractive index and material dispersion interpolation of doped silica
# in the 0.6-1.8 mu m wavelength region
# Photonics Technology Letters, IEEE, 1989, 1, 142-145
