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


"""Test suite for fiber.factory module"""

import unittest
import os.path

from fibermodes import FiberFactory

__dir__, _ = os.path.split(__file__)


class TestFiberFactory(unittest.TestCase):

    """Test suite for FiberFactory class"""

    def testReadAttributes(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        self.assertEqual(f.name, "smf28")
        self.assertEqual(f.author, "Charles Brunet")
        self.assertEqual(f.description, "Single mode fiber")
        self.assertEqual(len(f.layers), 2)
        self.assertEqual(f.layers[0].name, "core")
        self.assertEqual(f.layers[1].name, "cladding")

    def testSetAttributes(self):
        f = FiberFactory()
        f.name = "smf28"
        f.author = "Charles Brunet"
        f.description = "Single mode fiber"
        f.addLayer()
        f.layers[0].name = "core"
        self.assertEqual(f.name, "smf28")
        self.assertEqual(f.author, "Charles Brunet")
        self.assertEqual(f.description, "Single mode fiber")
        self.assertEqual(f.layers[0].name, "core")

    def testFactoryLen(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        self.assertEqual(len(f), 1)

        f.layers[0].radius = [2e-6, 3e-6, 4e-6]
        self.assertEqual(len(f), 3)

        f.layers[0].mparams[0] = {'start': 1.454,
                                  'end': 1.494,
                                  'num': 5}
        self.assertEqual(len(f), 15)

    def testDefaultLayerAttributes(self):
        f = FiberFactory()
        f.addLayer()

        self.assertEqual(f.layers[0].mparams[0], 1.444)
        self.assertEqual(f.layers[0].material, "Fixed")
        self.assertEqual(f.layers[0].type, "StepIndex")
        self.assertEqual(f.layers[0].radius, 0)

    def testRadiusZero(self):
        f = FiberFactory()
        f.addLayer(radius=0)
        f.addLayer(radius=4e-6, index=1.474)
        f.addLayer()
        fiber = f[0]

        self.assertEqual(len(fiber), 2)

    def testEqualIndexes(self):
        f = FiberFactory()
        f.addLayer(radius=1e-6, index=1.474)
        f.addLayer(radius=4e-6, index=1.474)
        f.addLayer()
        fiber = f[0]

        self.assertEqual(len(fiber), 2)

    @unittest.expectedFailure
    def testImpossibleRadius(self):
        """TODO: not implemented yet"""

        f = FiberFactory()
        f.addLayer(radius=10e-6, index=1.174)
        f.addLayer(radius=4e-6, index=1.444)
        f.addLayer()

        self.assertEqual(len(f), 0)

    def testFactoryGetItem(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        f.layers[0].radius = [2e-6, 3e-6, 4e-6]

        for i, fiber in enumerate(f):
            self.assertEqual(fiber.outerRadius(0), f.layers[0].radius[i])
            self.assertEqual(f[i].outerRadius(0), f.layers[0].radius[i])

    def testFactoryLayerSetMaterial(self):
        f = FiberFactory(os.path.join(__dir__, 'smf28.fiber'))
        f.layers[1].material = "Silica"
        self.assertEqual(len(f.layers[1].mparams), 0)


if __name__ == "__main__":
    unittest.main()
