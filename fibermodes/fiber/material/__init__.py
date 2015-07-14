"""A material describes the refractive index of a layer as function of
:py:class:`~fibermodes.wavelength.Wavelength`.

"""

from .fixed import Fixed
from .air import Air
from .silica import Silica
from .germania import Germania
from .sio2geo2 import SiO2GeO2

__all__ = ["Fixed", "Air", "Silica", "Germania", "SiO2GeO2"]
