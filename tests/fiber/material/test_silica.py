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

"""Test suite for fibermodes.fiber.material.silica module"""

import unittest

from fibermodes import Wavelength
from fibermodes.fiber.material import Silica


class TestSilica(unittest.TestCase):

    """Test suite for Silica class."""

    def testIndex(self):
        self.assertAlmostEqual(Silica.n(Wavelength(0.5876e-6)), 1.45846, 5)
        self.assertAlmostEqual(Silica.n(Wavelength(1.55e-6)), 1.44402, 5)


if __name__ == "__main__":
    unittest.main()
