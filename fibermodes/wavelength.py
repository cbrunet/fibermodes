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

"""Easy wavelength units conversion."""

from fibermodes.constants import c, tpi


class Wavelength(float):

    """Easy wavelength units conversion class.

    This class is inherited from :py:class:`float`. Therefore, it can be
    used wherever you can use floats. Wavelength always is expressed in
    meters.

    Properties can be used to convert wavelength to frequency or wavenumber.

    """

    def __new__(cls, *args, **kwargs):
        """Construct a Wavelength object, using given value.

        You can pass to the constructor any keyword defined in properties
        (k0, omega, w, wl, wavelength, frequency, v, or f).
        If no keyword is given, value is considered to be wavelength.

        """
        nargs = len(args) + len(kwargs)
        if nargs > 1:
            raise TypeError("Wavelength constructor need exactly one "
                            "parameter")
        if nargs == 0:
            wl = 0
        elif len(args) == 1:
            wl = args[0]
        elif 'k0' in kwargs:
            wl = tpi / kwargs['k0']
        elif 'omega' in kwargs:
            wl = c * tpi / kwargs['omega']
        elif 'w' in kwargs:
            wl = c * tpi / kwargs['w']
        elif 'wl' in kwargs:
            wl = kwargs['wl']
        elif 'wavelength' in kwargs:
            wl = kwargs['wavelength']
        elif 'frequency' in kwargs:
            wl = c / kwargs['frequency']
        elif 'v' in kwargs:
            wl = c / kwargs['v']
        elif 'f' in kwargs:
            wl = c / kwargs['f']
        else:
            raise TypeError("Invalid argument")

        return float.__new__(cls, wl)

    @property
    def k0(self):
        """Wave number (:math:`2 \pi / \lambda`)."""
        return tpi / self if self != 0 else float("inf")

    @property
    def omega(self):
        """Angular frequency (in rad/s)."""
        return c * tpi / self if self != 0 else float("inf")

    w = omega

    @property
    def wavelength(self):
        """Wavelength (in meters)."""
        return self

    wl = wavelength

    @property
    def frequency(self):
        """Frequency (in Hertz)."""
        return c / self if self != 0 else float("inf")

    v = frequency
    f = frequency

    def __str__(self):
        """Format wavelength as string (nanometers, 2 digits)"""
        return "{:.2f} nm".format(1e9 * self.wavelength)

    def __repr__(self):
        return "Wavelength({})".format(self.wavelength)


if __name__ == '__main__':
    # Smoke test
    w = Wavelength(1550e-9)
    print(w)
    print(repr(w))
