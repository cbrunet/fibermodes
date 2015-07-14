"""Simulators are used to sweep over different
:py:class:`~fibermodes.fiber.fiber.Fiber` parameters,
and to solve for :py:class:`~fibermodes.mode.Mode` using those parameters.

Main implementation of the simulator is in
:class:`~fibermodes.simulator.simulator.Simulator`. Subclasses can be used
for performing different kind of smulations; e.g. for running simulations
in parallel using multiple processes, or even using MPI.

"""

from .simulator import Simulator
from .psimulator import PSimulator

__all__ = ['Simulator', 'PSimulator']
