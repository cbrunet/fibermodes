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

"""Module for fiber materials.

A material gives a refractive index, as function of the wavelength.

"""

from scipy.optimize import brentq
import warnings


class OutOfRangeWarning(UserWarning):

    """Warning raised when a material parameter is out of the allowed range.

    If this warning is raised, it means that results are possibily
    innacurate.

    """
    pass


class Material(object):

    """Material abstract class.

    This gives the interface for the different materials, as well as
    some common functions. All methods in that class are class methods.

    """

    name = "Abstract Material"  # English name for the mateial
    nparams = 0  # Number of material parameters
    info = None  # Info about the material
    url = None  # URL for the reference about the material
    WLRANGE = None  # Acceptable range for the wavelength

    @classmethod
    def _testRange(cls, wl):
        if cls.WLRANGE is None:
            return
        if cls.WLRANGE[0] <= wl <= cls.WLRANGE[1]:
            return

        msg = ("Wavelength {} out of supported range for material {}. "
               "Wavelength should be in the range {} - {}. "
               "Results could be innacurate.").format(
            str(wl),
            cls.name,
            cls.WLRANGE[0],
            cls.WLRANGE[1])
        warnings.warn(msg, OutOfRangeWarning)

    @classmethod
    def n(cls, wl, *args, **kwargs):
        raise NotImplementedError(
            "This method must be implemented in derived class.")

    @classmethod
    def wlFromN(cls, n, *args, **kwargs):
        def f(wl):
            return n - cls.n(wl, *args, **kwargs)

        if cls.WLRANGE is None:
            raise NotImplementedError(
                "This method only works if WLRANGE is defined")

        a = f(cls.WLRANGE[0])
        b = f(cls.WLRANGE[1])
        if a*b > 0:
            warnings.warn("Index {} out of range.".format(n),
                          OutOfRangeWarning)
            return None

        return brentq(f, cls.WLRANGE[0], cls.WLRANGE[1])

    @classmethod
    def str(cls, *args):
        return cls.name

    @classmethod
    def __str__(cls):
        return cls.name

    @classmethod
    def __repr__(cls):
        return "{}()".format(cls.__name__)


if __name__ == '__main__':
    m = Material()
    print(m)
    print(repr(m))
