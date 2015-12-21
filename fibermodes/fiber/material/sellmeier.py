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

"""Sellmeier material module.

"""

from .material import Material
from math import sqrt


class Sellmeier(Material):

    """Material based on Sellmeier formula.

    This is an abstract class for materials like SiO2 and GeO2.

    """

    nparams = 0
    B = None  # List for B parameter
    C = None  # List for C parameter

    @classmethod
    def _n(cls, wl, B, C):
        x2 = wl * wl * 1e12
        return sqrt(abs(1 + x2 * sum(b / (x2 - c**2) for (b, c) in zip(B, C))))

    @classmethod
    def n(cls, wl):
        if cls.B is None or cls.C is None:
            raise NotImplementedError(
                "This method must be implemented in derived class.")
        cls._testRange(wl)
        return cls._n(wl, cls.B, cls.C)
