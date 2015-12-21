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

"""Test suite for fiber.material.germania module."""

import unittest

from fibermodes import Wavelength
from fibermodes.fiber.material import Germania


class TestGermania(unittest.TestCase):

    """Test suite for Germania class."""

    def testIndex(self):
        self.assertAlmostEqual(Germania.n(Wavelength(0.5876e-6)), 1.6085, 4)
        self.assertAlmostEqual(Germania.n(Wavelength(1.55e-6)), 1.5871, 4)
        self.assertAlmostEqual(Germania.n(Wavelength(1.68e-6)), 1.5859, 4)


if __name__ == "__main__":
    unittest.main()
