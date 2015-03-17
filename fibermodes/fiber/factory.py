"""Fiber factory module."""

from fibermodes.wavelength import Wavelength
from fibermodes.fiber.ssif import SSIF
from fibermodes.fiber.mlsif import MLSIF
from fibermodes.fiber.tlsif import TLSIF
from fibermodes.material.fixed import Fixed


class Factory(list):

    """Creates a :py:class:`~fibermodes.fiber.fiber.Fiber` object from given
    arguments.

    The Factory is a :py:class:`list`, and expect to contains
    :py:class:`~fibermodes.material.Material` of each fiber layer,
    begin from the center.

    """

    def __init__(self, *args, **kwargs):
        self._rna = None
        super().__init__(*args, **kwargs)

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

        params = [((self[0],) + tuple(args[0]))]
        ln = n0 = n(0)
        n1 = None
        for i in range(1, self.nlayers):
            cn = n(i)
            if cn == ln:
                params[-1] = (self[i],) + tuple(args[i])
            else:
                params.append((self[i],) + tuple(args[i]))
                ln = cn
                if n1 is None:
                    n1 = cn
        nlayers = len(params)

        if nlayers < 2:
            return None

        if nlayers == 2 and n0 > n1:
            return SSIF(wl, *params, rna=self._rna)
        elif nlayers == 3:
            return TLSIF(wl, *params, rna=self._rna)
        else:
            return MLSIF(wl, *params, rna=self._rna)


def fixedFiber(wl, r, n, rna=None):
    """Build a step-index fiber with fixed indices, from given parameters.

    :param wl: wavelength
    :param r: list of layer radii (from inner to outer)
    :param n: list of layer indices (from inner to outer)
    :rtype: :py:class:`~fibermodes.fiber.fiber.Fiber` object

    """
    ff = Factory()
    ff._rna = rna
    params = []
    for i in range(len(n)):
        ff.append(Fixed)
        params.append((r[i], n[i]) if i < len(r) else (r[i - 1], n[i]))
        # TODO: Detect subsequent layers with same n
    return ff(wl, *params)


if __name__ == '__main__':
    fact = Factory((Fixed, Fixed))
    fiber = fact(1550e-9, (4e-6, 1.6), (6e-6, 1.4))
    print(fiber.__class__, fiber)

    fact = Factory((Fixed, Fixed, Fixed))
    fiber = fact(1550e-9, (4e-6, 1.6), (5e-6, 1.6), (6e-6, 1.4))
    print(fiber.__class__, fiber)

    fact = Factory((Fixed, Fixed, Fixed))
    fiber = fact(1550e-9, (4e-6, 1.4), (5e-6, 1.6), (6e-6, 1.4))
    print(fiber.__class__, fiber)
