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

""" This package provides tools for solving modes in different kind of
optical fibers.

The following classes can be imported directly from fibermodes.
All those classes are imported if using import *

"""

from .wavelength import Wavelength
from .mode import Mode, HE11, LP01, Family as ModeFamily
from .fiber.factory import FiberFactory
from .simulator.simulator import Simulator
from .simulator.psimulator import PSimulator

__all__ = ['Wavelength',
           'Mode',
           'HE11',
           'LP01',
           'ModeFamily',
           'FiberFactory',
           'Simulator',
           'PSimulator'
           ]
