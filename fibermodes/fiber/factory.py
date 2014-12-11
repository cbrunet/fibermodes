"""Fiber factory module."""

from ..wavelength import Wavelength
from .ssif import SSIF
from .mlsif import MLSIF
from .tlsif import TLSIF
from ..material.fixed import Fixed


class Factory(list):

    """Creates a :py:class:`~fibermodes.fiber.fiber.Fiber` object from given
    arguments.

    The Factory is a :py:class:`list`, and expect to contains
    :py:class:`~fibermodes.material.Material` of each fiber layer,
    begin from the center.

    """

    @property
    def nlayers(self):
        """Number of layers in the fiber."""
        return len(self)

    def __call__(self, wl, *args):
        """
        args are (radius, `*mat_params`)
        """
        assert len(args) == self.nlayers, "Wrong number of arguments"

        if not isinstance(wl, Wavelength):
            wl = Wavelength(wl)

        def n(i):
            return self[i].n(wl, *args[i][1:])

        params = tuple(((self[i],) + tuple(args[i]))
                       for i in range(self.nlayers))

        if self.nlayers == 2 and n(0) > n(1):
            return SSIF(wl, *params)
        elif self.nlayers == 3:
            return TLSIF(wl, *params)
        else:
            return MLSIF(wl, *params)


def fixedFiber(wl, r, n):
    """Build a step-index fiber with fixed indices, from given parameters.

    :param wl: wavelength
    :param r: list of layer radii (from inner to outer)
    :param n: list of layer indices (from inner to outer)
    :rtype: :py:class:`~fibermodes.fiber.fiber.Fiber` object

    """
    ff = Factory()
    params = []
    for i in range(len(n)):
        ff.append(Fixed)
        params.append((r[i], n[i]) if i < len(r) else (r[i - 1], n[i]))
    return ff(wl, *params)
