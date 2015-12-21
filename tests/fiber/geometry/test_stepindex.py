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

"""Test suite for fiber.geometry.stepindex module"""

import unittest

from fibermodes.fiber.geometry.stepindex import StepIndex


class TestStepIndex(unittest.TestCase):

    """Test suite for StepIndex class"""

    def testIndex(self):
        geom = StepIndex(0, 4e-6, m="Fixed", mp=(1.444,))

        self.assertEqual(geom.index(0, 1550e-9), 1.444)
        self.assertEqual(geom.index(2e-6, 1550e-9), 1.444)
        self.assertEqual(geom.index(-2e-6, 1550e-9), 1.444)
        self.assertIsNone(geom.index(5e-6, 1550e-9))
        self.assertIsNone(geom.index(-5e-6, 1550e-9))

    def testCladding(self):
        geom = StepIndex(4e-6, float("inf"), m="Fixed", mp=(1.444,))

        self.assertEqual(geom.index(4e-6, 1550e-9), 1.444)
        self.assertEqual(geom.index(10e-6, 1550e-9), 1.444)
        self.assertIsNone(geom.index(2e-6, 1550e-9))


if __name__ == "__main__":
    import os
    os.chdir('../..')
    unittest.main()
