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
