"""Test suite for fibermodes.fiber.materia.sio2geo2 module"""

import unittest
import warnings

from fibermodes import Wavelength
from fibermodes.fiber.material import Silica, Germania, SiO2GeO2


class TestSiO2GeO2(unittest.TestCase):

    """Test suite for SiO2GeO2 material."""

    def testConcentrationZero(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(Silica.n(Wavelength(0.5876e-6)),
                             SiO2GeO2.n(Wavelength(0.5876e-6), 0))
        self.assertEqual(Silica.n(Wavelength(1.55e-6)),
                         SiO2GeO2.n(Wavelength(1.55e-6), 0))

    def testConcentrationOne(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(Germania.n(Wavelength(0.5876e-6)),
                             SiO2GeO2.n(Wavelength(0.5876e-6), 1))
        self.assertEqual(Germania.n(Wavelength(1.55e-6)),
                         SiO2GeO2.n(Wavelength(1.55e-6), 1))

    def testDopedSilica(self):
        """Warning: test values based on results! It only ensures
        that function works and that results stay the same.
        Please find official tables to compare with.

        """
        self.assertAlmostEqual(SiO2GeO2.n(Wavelength(1.55e-6), 0.05),
                               1.451526777142772)
        self.assertAlmostEqual(SiO2GeO2.n(Wavelength(1.55e-6), 0.1),
                               1.4589885105632852)
        self.assertAlmostEqual(SiO2GeO2.n(Wavelength(1.55e-6), 0.2),
                               1.473791249750968)

    def testXFromN(self):
        self.assertAlmostEqual(
            SiO2GeO2.xFromN(Wavelength(1.55e-6), 1.451526777142772),
                            0.05)


if __name__ == "__main__":
    unittest.main()
