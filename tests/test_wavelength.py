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

import unittest

from fibermodes import Wavelength


class TestWavelength(unittest.TestCase):

    def test1550(self):
        w = Wavelength(1550e-9)

        self.assertEqual(w, 1550e-9)
        self.assertEqual(w.wavelength, 1550e-9)
        self.assertEqual(w.wl, 1550e-9)

        self.assertAlmostEqual(w.frequency, 193.41448903225806e12)
        self.assertAlmostEqual(w.v, 193.41448903225806e12)

        self.assertAlmostEqual(w.omega, 1.215259075683131e15)
        self.assertAlmostEqual(w.w, 1.215259075683131e15)

        self.assertAlmostEqual(w.k0, 4053667.940115862)

    def testComp(self):
        w1 = Wavelength(1550e-9)
        w2 = Wavelength(1530e-9)

        self.assertTrue(w1 == w1)
        self.assertFalse(w1 == w2)

        self.assertTrue(w1 > w2)
        self.assertFalse(w2 > w1)

        self.assertTrue(w2 < w1)
        self.assertFalse(w1 < w2)

        self.assertTrue(w1 != w2)
        self.assertFalse(w1 != w1)

        self.assertTrue(w1 >= w2)
        self.assertTrue(w1 >= w1)
        self.assertFalse(w2 >= w1)

        self.assertTrue(w2 <= w1)
        self.assertTrue(w2 <= w2)
        self.assertFalse(w1 <= w2)

    def testInit(self):
        w = Wavelength(1550e-9)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(wl=1550e-9)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(wavelength=1550e-9)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(v=193.41448903225806e12)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(frequency=193.41448903225806e12)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(w=1.215259075683131e15)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(omega=1.215259075683131e15)
        self.assertAlmostEqual(w.wavelength, 1550e-9)

        w = Wavelength(k0=4053667.940115862)
        self.assertAlmostEqual(w.wavelength, 1550e-9)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
