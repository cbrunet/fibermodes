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

"""Module for material composed of two different materials."""

import warnings
from .material import Material, OutOfRangeWarning
from scipy.optimize import brentq


class CompMaterial(Material):

    """Abstract class for material composed of two materials."""

    XRANGE = None  # Acceptable range for the first parameter
    MATERIALS = None

    @classmethod
    def _testConcentration(cls, x):
        if cls.XRANGE is None:
            return
        if x <= cls.XRANGE:
            return
        msg = ("Concentration {} out of supported range for material {}. "
               "Concentration should be below {}. "
               "Results could be innacurate.").format(
            str(x),
            cls.name,
            cls.XRANGE)
        warnings.warn(msg, OutOfRangeWarning)

    @classmethod
    def xFromN(cls, wl, n):
        if cls.MATERIALS is not None:
            M1, M2 = cls.MATERIALS
            n1 = M1.n(wl)
            n2 = M2.n(wl)
            if n1 < n2:
                assert n1 <= n <= n2
            else:
                assert n2 <= n <= n1

        x = 1 if cls.XRANGE is None else cls.XRANGE
        return brentq(lambda x: cls.n(wl, x)-n, 0, x)

    @classmethod
    def str(cls, x):
        return "{} ({:.2f} %)".format(cls.name, x*100)
