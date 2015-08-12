"""Test suite for fiber.factory module"""

import unittest

from fibermodes import FiberFactory


class TestFiberFactory(unittest.TestCase):

    """Test suite for FiberFactory class"""

    def testReadAttributes(self):
        f = FiberFactory('tests/fiber/smf28.fiber')
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
        f = FiberFactory('tests/fiber/smf28.fiber')
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
        f = FiberFactory('tests/fiber/smf28.fiber')
        f.layers[0].radius = [2e-6, 3e-6, 4e-6]

        for i, fiber in enumerate(f):
            self.assertEqual(fiber.outerRadius(0), f.layers[0].radius[i])
            self.assertEqual(f[i].outerRadius(0), f.layers[0].radius[i])

    def testFactoryLayerSetMaterial(self):
        f = FiberFactory('tests/fiber/smf28.fiber')
        f.layers[1].material = "Silica"
        self.assertEqual(len(f.layers[1].mparams), 0)


if __name__ == "__main__":
    import os
    os.chdir("../..")
    unittest.main()
