"""Easy wavelength units conversion."""

from .constants import c, tpi


class Wavelength(object):

    """Easy wavelength units conversion class.

    """

    def __init__(self, wavelength=None, **kwargs):
        """Construct a Wavelength object, using given value.

        You can pass to the constructor any keywork defined in attributes.
        If no keyword is given, value is considered to be wavelength.

        """
        if wavelength is not None:
            self.wavelength = wavelength
        elif 'k0' in kwargs:
            self.k0 = kwargs['k0']
        elif 'omega' in kwargs:
            self.omega = kwargs['omega']
        elif 'w' in kwargs:
            self.omega = kwargs['w']
        elif 'wl' in kwargs:
            self.wavelength = kwargs['wl']
        elif 'frequency' in kwargs:
            self.frequency = kwargs['frequency']
        elif 'v' in kwargs:
            self.frequency = kwargs['v']
        else:
            raise KeyError('Invalid argument')

    @property
    def k0(self):
        """Wave number."""
        return tpi / self._wl

    @k0.setter
    def k0(self, k0):
        self._wl = tpi / k0

    @property
    def omega(self):
        """Radial frequency (in rad/s)."""
        return c * tpi / self._wl

    @omega.setter
    def omega(self, omega):
        self._wl = c * tpi / omega

    w = omega

    @property
    def wavelength(self):
        """Wavelength (in meters)."""
        return self._wl

    @wavelength.setter
    def wavelength(self, wavelength):
        self._wl = wavelength

    wl = wavelength

    @property
    def frequency(self):
        """Frequency (in Hertz)."""
        return c / self._wl

    @frequency.setter
    def frequency(self, frequency):
        self._wl = c / frequency

    v = frequency

    def __call__(self):
        return self.wavelength

    def __str__(self):
        return "{:.2f} nm".format(1e9 * self.wavelength)

    def __repr__(self):
        return "Wavelength({})".format(self.wavelength)

    def __eq__(self, wl2):
        return self.wavelength == wl2.wavelength

    def __ne__(self, wl2):
        return self.wavelength != wl2.wavelength

    def __lt__(self, wl2):
        return self.wavelength < wl2.wavelength

    def __le__(self, wl2):
        return self.wavelength <= wl2.wavelength

    def __ge__(self, wl2):
        return self.wavelength >= wl2.wavelength

    def __gt__(self, wl2):
        return self.wavelength > wl2.wavelength

    def __float__(self):
        return self.wavelength

    def __int__(self):
        return int(self.wavelength)

if __name__ == '__main__':
    # Smoke test
    w = Wavelength(1550e-9)
    print(w)
    print(repr(w))
