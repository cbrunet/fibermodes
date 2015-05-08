"""Test suite for module fiber.material.air"""

import unittest

from fibermodes import Wavelength
from fibermodes.fiber.material import Air


class TestAir(unittest.TestCase):

    """Test suite for Air class"""

    def testIndex(self):
        self.assertAlmostEqual(Air.n(Wavelength(0.5876e-6)), 1.00027717)
        self.assertAlmostEqual(Air.n(Wavelength(1.55e-6)), 1.00027326)


if __name__ == "__main__":
    unittest.main()
