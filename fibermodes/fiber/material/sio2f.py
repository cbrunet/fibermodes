# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.


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
