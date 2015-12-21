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

"""Module for Germania material."""

from .sellmeier import Sellmeier
from fibermodes.wavelength import Wavelength


class Germania(Sellmeier):

    """Germania material, based on Sellmeier forumla."""

    name = "Germanium dioxide"
    info = "Fused germanium dioxide."
    url = "http://refractiveindex.info/?shelf=main&book=GeO2&page=Fleming"
    WLRANGE = (Wavelength(0.36e-6), Wavelength(4.3e-6))
    B = (0.80686642, 0.71815848, 0.85416831)
    C = (0.068972606, 0.15396605, 11.841931)

# J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
# vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
# http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486
