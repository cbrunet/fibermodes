"""Test suite for fiber.fiber module"""

import unittest

from fibermodes import FiberFactory


class TestFiber(unittest.TestCase):

    """Test suite for Fiber class"""

    def testFiberProperties(self):
        f = FiberFactory('tests/fiber/rcf.fiber')
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
        f = FiberFactory('tests/fiber/smf28.fiber')
        f.layers[0].material = "SiO2GeO2"
        f.layers[0].mparams = [0.05]
        f.layers[1].material = "Silica"
        fiber = f[0]

        self.assertAlmostEqual(fiber.index(2e-6, 1550e-9),
                               1.451526777142772)
        self.assertAlmostEqual(fiber.index(8e-6, 1550e-9),
                               1.444023621703261)

    def testToWl(self):
        f = FiberFactory('tests/fiber/smf28.fiber')
        fiber = f[0]
        self.assertAlmostEqual(fiber.toWl(fiber.V0(1600e-9)), 1600e-9)

        f.layers[0].material = "Silica"
        f.layers[1].material = "Air"
        fiber = f[0]
        self.assertAlmostEqual(fiber.toWl(fiber.V0(1600e-9)), 1600e-9)


if __name__ == "__main__":
    import os
    os.chdir('../..')
    unittest.main()
