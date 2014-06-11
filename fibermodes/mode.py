'''
Created on 2014-05-01

@author: cbrunet
'''

from enum import Enum

#: Constants for identifying mode family. Can be
#: LP, HE, EH, TE, or TM.
Family = Enum('Family', 'LP HE EH TE TM', module=__name__)


class Mode(object):

    """Fiber mode representation.

    The fiber mode consists of a mode family, and two mode parameters.

    """

    def __init__(self, family, nu, m):
        '''
        Constructor
        '''
        if isinstance(family, Family):
            self._family = family
        else:
            self._family = Family[family]
        self._nu = nu
        self._m = m

    @property
    def family(self):
        """Mode family.

        .. seealso:: :py:class:`Family`

        """
        return self._family

    @property
    def nu(self):
        """ν parameter of the mode. It often corresponds to the parameter
        of the radial Bessel functions.

        """
        return self._nu

    ell = nu

    @property
    def m(self):
        """Radial order of the mode. It corresponds to the number of
        concentric rings in the mode fields.

        """
        return self._m

    def __str__(self):
        return "{}({},{})".format(self.family.name, self.nu, self.m)

    def __repr__(self):
        return "Mode('{}',{},{})".format(
            self.family.name, self.nu, self.m)

    def __eq__(self, m2):
        s1, s2 = str(self), str(m2)
        if set((s1, s2)) <= set(('HE(1,1)', 'LP(0,1)')):
            return True
        return s1 == s2

    def __ne__(self, m2):
        return not self == m2

    def __lt__(self, m2):
        return False

    def __le__(self, m2):
        return self == m2

    def __ge__(self, m2):
        return self == m2

    def __gt__(self, m2):
        return False


class SMode(Mode):

    """Solved mode. This is a mode, associated with an effective index."""

    def __init__(self, fiber, mode, neff):
        """Build a SMode object, from a Mode and an effective index.

        Usually, you do not need to call this directly. SMode objects
        are build using the mode solver.

        """
        self._family = mode.family
        self._nu = mode.nu
        self._m = mode.m

        self._fiber = fiber
        self._neff = neff

    @property
    def neff(self):
        """Effective index of the mode."""
        return self._neff

    @property
    def beta(self):
        """Propagation constant."""
        return self._fiber._wl.k0 * self._neff


if __name__ == '__main__':
    m = Mode('HE', 1, 1)
    print(m)
    print(repr(m))
