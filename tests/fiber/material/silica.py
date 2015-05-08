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
