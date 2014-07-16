"""Easy wavelength units conversion."""

from .constants import c, tpi


class Wavelength(float):

    """Easy wavelength units conversion class.

    """

    def __new__(cls, *args, **kwargs):
        """Construct a Wavelength object, using given value.

        You can pass to the constructor any keywork defined in attributes.
        If no keyword is given, value is considered to be wavelength.

        """
        if len(args) + len(kwargs) != 1:
            raise TypeError("Wavelength constructor need exactly one "
                            "parameter")

        if len(args) == 1:
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
        else:
            raise TypeError('Invalid argument')

        return float.__new__(cls, wl)

    @property
    def k0(self):
        """Wave number."""
        return tpi / self

    @property
    def omega(self):
        """Radial frequency (in rad/s)."""
        return c * tpi / self

    w = omega

    @property
    def wavelength(self):
        """Wavelength (in meters)."""
        return self

    wl = wavelength

    @property
    def frequency(self):
        """Frequency (in Hertz)."""
        return c / self

    v = frequency

    def __str__(self):
        return "{:.2f} nm".format(1e9 * self.wavelength)

    def __repr__(self):
        return "Wavelength({})".format(self.wavelength)


if __name__ == '__main__':
    # Smoke test
    w = Wavelength(1550e-9)
    print(w)
    print(repr(w))
