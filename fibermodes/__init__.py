""" This package provides tools for solving modes in different kind of
optical fibers.

The following classes can be imported directly from fibermodes.
All those classes are imported if using import *

"""

from .wavelength import Wavelength
from .mode import Mode, Family as ModeFamily
from .fiber.factory import FiberFactory
from .simulator.simulator import Simulator
from .simulator.psimulator import PSimulator

__all__ = ['Wavelength',
           'Mode',
           'ModeFamily',
           'FiberFactory',
           'Simulator',
           'PSimulator'
           ]
