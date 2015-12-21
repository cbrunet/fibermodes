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


"""Test suite for field module"""

import unittest
import os.path

from fibermodes import FiberFactory, HE11, LP01
from fibermodes.field import Field
import numpy

__dir__, _ = os.path.split(__file__)


class TestField(unittest.TestCase):

    """Test Field class.

    Current test are only to ensure code executes without errors.
    Tests that ensure fields are accurate should be written.

    """

    def setUp(self):
        f = FiberFactory(os.path.join(__dir__, 'fiber/smf28.fiber'))
        fiber = f[0]
        self.field = Field(fiber, HE11, 1550e-9, 50e-6)
        self.lpfield = Field(fiber, LP01, 1550e-9, 50e-6)

    def testFG(self):
        f = self.field.f(0)
        g = self.field.g(0)

        self.assertEqual(f.ndim, 2)
        self.assertEqual(g.ndim, 2)

        self.assertTrue(numpy.all(f <= 1))
        self.assertTrue(numpy.all(f >= -1))
        self.assertTrue(numpy.all(g <= 1))
        self.assertTrue(numpy.all(g >= -1))

    def testEx(self):
        ex = self.field.Ex()
        self.assertEqual(max(ex.ravel()), ex[50, 50])
        self.assertAlmostEqual(ex[0, 0], 0)

    def testEy(self):
        ey = self.field.Ey()
        self.assertTrue(numpy.all(ey < 0.01))
        self.assertTrue(numpy.all(ey < self.field.Ex()))
        self.assertAlmostEqual(ey[0, 0], 0)

    def testEz(self):
        ez = self.field.Ez()
        self.assertAlmostEqual(ez[0, 0], 0)
        self.assertTrue(numpy.all(ez < self.field.Ex()))


if __name__ == "__main__":
    unittest.main()
