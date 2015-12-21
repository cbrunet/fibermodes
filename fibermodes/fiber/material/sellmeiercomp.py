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

"""Module for material based on the composition of two Sellmeier materials."""

from .sellmeier import Sellmeier
from .compmaterial import CompMaterial
import numpy


class SellmeierComp(Sellmeier, CompMaterial):

    """Abstract class for material composed of two Sellmeier materials."""

    nparams = 1

    @classmethod
    def n(cls, wl, x):
        if cls.MATERIALS is None:
            raise NotImplementedError(
                "This method must be implemented in derived class.")
        cls._testRange(wl)
        cls._testConcentration(x)

        M1, M2 = cls.MATERIALS
        B = numpy.array(M1.B)
        Bp = numpy.array(M2.B) - B
        C = numpy.array(M1.C)
        Cp = numpy.array(M2.C) - C
        return cls._n(wl, B + x * Bp, C + x * Cp)
