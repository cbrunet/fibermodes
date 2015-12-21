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

"""Test suite for fibermodes.simulator module"""

import unittest
import os.path

from fibermodes import FiberFactory, Mode, ModeFamily, HE11
from fibermodes.simulator import Simulator

__dir__, _ = os.path.split(__file__)


class TestSimulator(unittest.TestCase):

    """Test suite for Simulator class"""

    @property
    def Simulator(self):
        return Simulator

    def testUninitializedSimulator(self):
        sim = self.Simulator()
        with self.assertRaises(ValueError):
            sim.fibers

        with self.assertRaises(ValueError):
            sim.wavelengths

    def testConstructor(self):
        sim = self.Simulator(
            os.path.join(__dir__, '..', 'fiber', 'smf28.fiber'), 1550e-9)
        self.assertEqual(len(sim.wavelengths), 1)
        self.assertEqual(len(sim.fibers), 1)
        self.assertTrue(sim.initialized)
        self.assertTrue(sim._fsims is not None)

    def testSetWavelengths(self):
        sim = self.Simulator()
        sim.set_wavelengths(1550e-9)
        self.assertEqual(len(sim.wavelengths), 1)
        self.assertEqual(sim.wavelengths[0], 1550e-9)

        sim.set_wavelengths([1550e-9, 1560e-9])
        self.assertEqual(len(sim.wavelengths), 2)

        sim.set_wavelengths({'start': 1550e-9,
                             'end': 1580e-9,
                             'num': 4})
        self.assertEqual(len(sim.wavelengths), 4)

        with self.assertRaises(ValueError):
            sim.fibers
        self.assertFalse(sim.initialized)
        self.assertTrue(sim._fsims is None)

    def testSetFactory(self):
        sim = self.Simulator()
        sim.set_factory(os.path.join(__dir__, '..', 'fiber', 'rcfs.fiber'))
        self.assertEqual(len(sim.fibers), 5)

        f = FiberFactory()
        f.addLayer(radius=[4e-6, 5e-6, 6e-6], index=1.449)
        f.addLayer(index=1.444)
        sim.set_factory(f)
        self.assertEqual(len(sim.fibers), 3)

        with self.assertRaises(ValueError):
            sim.wavelengths
        self.assertFalse(sim.initialized)
        self.assertTrue(sim._fsims is None)

    def testModesSMF(self):
        sim = self.Simulator(
            os.path.join(__dir__, '..', 'fiber', 'smf28.fiber'),
            1550e-9, scalar=True)
        modes = list(sim.modes())
        self.assertEqual(len(modes), 1)
        modesf1 = modes[0]
        self.assertEqual(len(modesf1), 1)
        modeswl1 = modesf1[0]
        self.assertEqual(len(modeswl1), 2)
        self.assertTrue(HE11 in modeswl1)
        self.assertTrue(Mode(ModeFamily.LP, 0, 1) in modeswl1)

    def testModesRCF(self):
        sim = self.Simulator(
            os.path.join(__dir__, '..', 'fiber', 'rcfs.fiber'), 1550e-9)
        modes = list(sim.modes())
        self.assertEqual(len(modes), 5)
        for fmodes, n in zip(modes, (4, 6, 6, 8, 8)):
            self.assertEqual(len(fmodes), 1)
            self.assertEqual(len(fmodes[0]), n)

    def testCutoff(self):
        sim = self.Simulator(
            os.path.join(__dir__, '..', 'fiber', 'rcfs.fiber'), 1550e-9)
        co = list(sim.cutoff())
        self.assertEqual(len(co), 5)
        for fco in co:
            self.assertEqual(len(fco), 1)
            self.assertEqual(fco[0][Mode('HE', 1, 1)], 0)

    def testNeff(self):
        sim = self.Simulator(
            os.path.join(__dir__, '..', 'fiber', 'smf28.fiber'),
            1550e-9, delta=1e-4)
        neff = list(sim.neff())
        self.assertEqual(len(neff), 1)
        self.assertAlmostEqual(neff[0][0][Mode('HE', 1, 1)], 1.446386514937099)

if __name__ == "__main__":
    unittest.main()
