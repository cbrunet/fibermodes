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
