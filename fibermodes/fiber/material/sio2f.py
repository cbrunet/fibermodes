
from .claussiusmossotti import ClaussiusMossotti
import numpy


class SiO2F(ClaussiusMossotti):

    name = "Silica doped with Fluorine (Claussius-Mossotti version)"
    nparams = 1
    XRANGE = 0.02

    B = numpy.array([-0.05413938039, -0.1788588824, -0.07445931332])


# Article (Sunak1989)
# Sunak, H. & Bastien, S.
# Refractive index and material dispersion interpolation of doped silica
# in the 0.6-1.8 mu m wavelength region
# Photonics Technology Letters, IEEE, 1989, 1, 142-145
