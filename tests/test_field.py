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


"""Test suite for field module"""

import unittest
import os.path

from fibermodes import FiberFactory, HE11
from fibermodes.field import Field
import numpy

__dir__, _ = os.path.split(__file__)


class TestField(unittest.TestCase):

    """Test Field class.

    Current test are only to ensure code executes without errors.
    Tests that ensure fields are accurate should be written.

    """

    def setUp(self):
        f = FiberFactory(os.path.join(__dir__, 'fiber/smf28.fiber'))
        fiber = f[0]
        self.field = Field(fiber, HE11, 1550e-9, 50e-6)

    def testFG(self):
        f = self.field.f(0)
        g = self.field.g(0)

        self.assertEqual(f.ndim, 2)
        self.assertEqual(g.ndim, 2)

        self.assertTrue(numpy.all(f <= 1))
        self.assertTrue(numpy.all(f >= -1))
        self.assertTrue(numpy.all(g <= 1))
        self.assertTrue(numpy.all(g >= -1))

    def testEx(self):
        ex = self.field.Ex()
        self.assertEqual(max(ex.ravel()), ex[50, 50])
        self.assertAlmostEqual(ex[0, 0], 0)

    def testEy(self):
        ey = self.field.Ey()
        self.assertTrue(numpy.all(ey < 0.01))
        self.assertTrue(numpy.all(ey < self.field.Ex()))
        self.assertAlmostEqual(ey[0, 0], 0)

    def testEz(self):
        ez = self.field.Ez()
        self.assertAlmostEqual(ez[0, 0], 0)
        self.assertTrue(numpy.all(ez < self.field.Ex()))

    def testEr(self):
        # TODO: add test
        er = self.field.Er()

    def testEphi(self):
        # TODO: add test
        ephi = self.field.Ephi()

    def testEt(self):
        ex = self.field.Ex()
        et = self.field.Et()
        self.assertTrue(numpy.all(numpy.abs(ex-et) < 1e-5))

    def testEpol(self):
        epol = self.field.Epol()
        self.assertTrue(numpy.all(numpy.abs(epol) < 1e-2))

    def testEmod(self):
        emod = self.field.Emod()
        self.assertTrue(numpy.all(emod > 0))

    def testHx(self):
        pass

    def testHy(self):
        pass

    def testHz(self):
        # TODO: add test
        hz = self.field.Hz()

    def testHr(self):
        # TODO: add test
        hr = self.field.Hr()

    def testHphi(self):
        # TODO: add test
        hphi = self.field.Hphi()

    def testHt(self):
        # TODO: add test
        ht = self.field.Ht()

    def testHpol(self):
        # TODO: add test
        hpol = self.field.Hpol()

    def testHmod(self):
        hmod = self.field.Hmod()
        self.assertTrue(numpy.all(hmod > 0))

    def testAeff(self):
        # TODO: add test
        aeff = self.field.Aeff()
        self.assertGreater(aeff, 0)


if __name__ == "__main__":
    unittest.main()
