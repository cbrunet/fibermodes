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


"""Test suite for fiber.fiber module"""

import unittest
import os.path

from fibermodes import FiberFactory
from fibermodes.fiber.material.material import OutOfRangeWarning
from math import isinf
import warnings

__dir__, _ = os.path.split(__file__)


class TestFiber(unittest.TestCase):

    """Test suite for Fiber class"""

    def testFiberProperties(self):
        f = FiberFactory(os.path.join(__dir__, 'rcf.fiber'))
        fiber = f[0]
        self.assertEqual(len(fiber), 3)
        self.assertEqual(fiber.name(0), "center")
        self.assertEqual(fiber.name(1), "ring")
        self.assertEqual(fiber.name(2), "cladding")
        self.assertEqual(fiber.innerRadius(1), 4e-6)
        self.assertEqual(fiber.outerRadius(1), 8e-6)
        self.assertEqual(fiber.thickness(1), 4e-6)
        self.assertEqual(fiber.index(6e-6, 1550e-9), 1.454)
        self.assertEqual(fiber.minIndex(1, 1550e-9), 1.454)
        self.assertEqual(fiber.maxIndex(1, 1550e-9), 1.454)

    def testFiberWithMaterials(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        f.layers[0].material = "SiO2GeO2"
        f.layers[0].mparams = [0.05]
        f.layers[1].material = "Silica"
        fiber = f[0]

        self.assertAlmostEqual(fiber.index(2e-6, 1550e-9),
                               1.451526777142772)
        self.assertAlmostEqual(fiber.index(8e-6, 1550e-9),
                               1.444023621703261)

    def testToWl(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        fiber = f[0]
        self.assertAlmostEqual(fiber.toWl(fiber.V0(1600e-9)), 1600e-9)

        f.layers[0].material = "Silica"
        f.layers[1].material = "Air"
        fiber = f[0]
        self.assertAlmostEqual(fiber.toWl(fiber.V0(1600e-9)), 1600e-9)

        self.assertEqual(fiber.toWl(float("inf")), 0)
        self.assertTrue(isinf(fiber.toWl(0)))

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=OutOfRangeWarning)
            f = FiberFactory()
            f.addLayer(radius=10e-6, material="SiO2GeO2", x=0.25)
            f.addLayer(material="Silica")
            fiber = f[0]
            wl = fiber.toWl(2.4)
            self.assertGreater(wl, 10e-6)


if __name__ == "__main__":
    unittest.main()
