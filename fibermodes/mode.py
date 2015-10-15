"""Fiber mode representations, and utility functions."""

from enum import Enum
from colorsys import hsv_to_rgb
from collections import namedtuple


#: Constants for identifying mode family. Can be
#: LP, HE, EH, TE, or TM.
Family = Enum('Family', 'LP HE EH TE TM', module=__name__)


class Mode(namedtuple('Mode', 'family nu m')):

    """Fiber mode representation.

    The fiber mode consists of a mode family, and two mode parameters
    (*ν* and *m*).

    .. py:attribute:: family

        Mode family.

        .. seealso:: :py:class:`Family`

    .. py:attribute:: nu

        *ν* parameter of the mode. It often corresponds to the parameter
        of the radial Bessel functions.

    .. py:attribute:: m

        (positive integer) Radial order of the mode.
        It corresponds to the number of concentric rings in the mode fields.

    """

    def __new__(cls, family, nu, m):
        if not isinstance(family, Family):
            family = Family[family]
        return super(Mode, cls).__new__(cls, family, nu, m)

    def __hash__(self):
        return super().__hash__()

    def lpEq(self):
        """Equivalent LP mode."""
        if self.family is Family.LP:
            return self
        elif self.family is Family.HE:
            return Mode(Family.LP, self.nu - 1, self.m)
        else:
            return Mode(Family.LP, self.nu + 1, self.m)

    def __str__(self):
        return "{}({},{})".format(self.family.name, self.nu, self.m)

    def __repr__(self):
        return "Mode('{}',{},{})".format(
            self.family.name, self.nu, self.m)

    def __eq__(self, m2):
        s1, s2 = str(self), str(m2)
        # if set((s1, s2)) <= set(('HE(1,1)', 'LP(0,1)')):
        #     return True
        return s1 == s2

    def __ne__(self, m2):
        return not (self == m2)

    def __lt__(self, m2):
        """Function used to sort modes.

        The mode order is somewhat arbitrary, but determined:

        1. Modes are sorted by *m* parameter;
        2. Modes of the same family are sorted by *nu* parameter;
        3. Modes of different families are sorted by *ell* parameter,
           where *ell* = *nu* + 1 for EH modes, *nu* - 1 for HE modes,
           1 for TE and TM modes, and *nu* for LP modes.
        4. Modes with same *ell* are sorted by family, in the following
           order: LP, EH, TE, HE, TM.

        """
        if self.m == m2.m:
            if self.family == m2.family:
                result = self.nu < m2.nu
            else:
                if self.family is Family.HE:
                    nu1 = self.nu - 1
                elif self.family is Family.LP:
                    nu1 = self.nu
                else:
                    nu1 = self.nu + 1
                if m2.family is Family.HE:
                    nu2 = m2.nu - 1
                elif m2.family is Family.LP:
                    nu2 = m2.nu
                else:
                    nu2 = m2.nu + 1
                if nu1 == nu2:
                    fams = [Family.LP, Family.EH, Family.TE,
                            Family.HE, Family.TM]
                    result = fams.index(self.family) < fams.index(m2.family)
                else:
                    result = nu1 < nu2

        else:
            result = self.m < m2.m
        return result

    def __le__(self, m2):
        return (self == m2) or (self < m2)

    def __ge__(self, m2):
        return m2 <= self

    def __gt__(self, m2):
        return m2 < self

    def color(self, nn=5, nm=3):
        """Return color (r, g, b) as function of mode.

        LP, HE modes are blue,
        EH modes are red,
        TE modes are green,
        TM modes are yellow.
        For TE and TM modes, m parameter varies hue and value.
        For LP, HE, and EH modes, nu parameter varies hue, and
        m parameter varies saturation.

        Args:
            nn(int): Number of different colors for nu parameter (default: 5).
            nm(int): Number of different colors for m parameter (default: 3).

        Returns:
            (r, g, b) tuple (0 .. 255)
        """
        nu = self.nu-1 if self.family in (Family.EH, Family.HE) else self.nu
        nu %= nn+1

        hd = {Family.LP: 2/3, Family.HE: 2/3, Family.EH: 1,
              Family.TE: 1/3, Family.TM: 1/6}
        h = hd[self.family]

        if self.family in (Family.TE, Family.TM):
            s = 0.8
            dh = (self.m % nm) / (nm * 6)
            v = 1 - dh
        else:
            s = 1 - ((self.m - 1) % nm) / nm
            dh = nu / (nn * 4)
            v = 1
        h -= dh

        r, g, b = hsv_to_rgb(h, s, v)

        # print(str(self), (h, s, v), (r, g, b))
        return (round(r*255), round(g*255), round(b*255))


if __name__ == '__main__':
    m = Mode('HE', 1, 1)
    print(m)
    print(repr(m))
