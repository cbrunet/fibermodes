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

from fibermodes import FiberFactory, Mode, ModeFamily
from fibermodes.field import Field
import numpy

__dir__, _ = os.path.split(__file__)


# TODO: write tests


class TestField(unittest.TestCase):

    def setUp(self):
        f = FiberFactory(os.path.join(__dir__, 'fiber/smf28.fiber'))
        fiber = f[0]
        he11 = Mode(ModeFamily.HE, 1, 1)
        self.field = Field(fiber, he11, 1550e-9, 7e-6)

    def testFG(self):
        f = self.field.f(0)
        g = self.field.g(0)

        self.assertEqual(f.ndim, 2)
        self.assertEqual(g.ndim, 2)

        self.assertTrue(numpy.all(f <= 1))
        self.assertTrue(numpy.all(f >= -1))
        self.assertTrue(numpy.all(g <= 1))
        self.assertTrue(numpy.all(g >= -1))

if __name__ == "__main__":
    unittest.main()
