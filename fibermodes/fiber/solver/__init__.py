"""A solver gives the function used to find cutoff and/or effective index
of a given :py:class:`~fibermodes.mode.Mode`
in a given :py:class:`fibermodes.fiber.fiber.Fiber`.

"""

from . import ssif
from . import tlsif
from . import mlsif


__all__ = ['ssif', 'tlsif', 'mlsif']
