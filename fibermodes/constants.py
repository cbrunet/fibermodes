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


"""Physical constants.

.. codeauthor:: Charles Brunet <charles@cbrunet.net>
"""

from math import sqrt, pi

c = 299792458.0  #: Speed of light in vacuum (m/s).
h = 6.62606957e-34  #: Plank constant (m²kg/s).
mu0 = 1.2566370614359173e-06  #: Vacuum permeability (H/m).
epsilon0 = 8.854187817620389e-12  #: Vacuum permittivity (F/m).
eV = 1.602176565e-19  #: Electron charge (C).

tpi = 2 * pi  #: Two times pi
eta0 = sqrt(mu0 / epsilon0)  #: Impedance of free-space.
Y0 = sqrt(epsilon0 / mu0)  #: Admitance of free-space.
