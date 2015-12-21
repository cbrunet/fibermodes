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

