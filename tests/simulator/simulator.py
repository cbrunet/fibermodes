"""Test suite for fibermodes.simulator module"""

import unittest

from fibermodes import FiberFactory, Mode
from fibermodes.simulator import Simulator


class TestSimulator(unittest.TestCase):

    """Test suite for Simulator class"""

    def setUp(self):
        self.sim = Simulator()

    def testUninitializedSimulator(self):
        with self.assertRaises(ValueError):
            self.sim.fibers

        with self.assertRaises(ValueError):
            self.sim.wavelengths

    def testSetWavelengths(self):
        self.sim.set_wavelengths(1550e-9)
        self.assertEqual(len(self.sim.wavelengths), 1)
        self.assertEqual(self.sim.wavelengths[0], 1550e-9)

        self.sim.set_wavelengths([1550e-9, 1560e-9])
        self.assertEqual(len(self.sim.wavelengths), 2)

        self.sim.set_wavelengths({'start': 1550e-9,
                                  'end': 1580e-9,
                                  'num': 4})
        self.assertEqual(len(self.sim.wavelengths), 4)

        with self.assertRaises(ValueError):
            self.sim.fibers

    def testSetFactory(self):
        self.sim.set_factory('tests/fiber/smf28.fiber')
        self.assertEqual(len(self.sim.fibers), 1)

        f = FiberFactory()
        f.addLayer(radius=[4e-6, 5e-6, 6e-6], index=1.449)
        f.addLayer(index=1.444)
        self.sim.set_factory(f)
        self.assertEqual(len(self.sim.fibers), 3)

        with self.assertRaises(ValueError):
            self.sim.wavelengths

    def testModes(self):
        self.sim.set_wavelengths(1550e-9)
        self.sim.set_factory('tests/fiber/smf28.fiber')
        modes = self.sim.modes(0, 0)
        self.assertEqual(len(modes), 1)
        self.assertEqual(str(modes.pop()), 'HE(1,1)')

    def testCutoff(self):
        self.sim.set_wavelengths(1550e-9)
        self.sim.set_factory('tests/fiber/smf28.fiber')
        co = self.sim.cutoff(0, 0)
        self.assertEqual(len(co), 1)
        self.assertEqual(co[Mode('HE', 1, 1)], 0)

    def testNeff(self):
        self.sim.set_wavelengths(1550e-9)
        self.sim.set_factory('tests/fiber/smf28.fiber')
        n = self.sim.neff(0, 0)
        self.assertEqual(len(n), 1)
        self.assertEqual(n[Mode('HE', 1, 1)], 1.4463865149370994)

if __name__ == "__main__":
    import os
    os.chdir("../..")
    unittest.main()
