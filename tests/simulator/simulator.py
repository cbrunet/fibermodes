"""Test suite for fibermodes.simulator module"""

import unittest

from fibermodes import FiberFactory
from fibermodes.simulator import Simulator


class TestSimulator(unittest.TestCase):

    """Test suite for Simulator class"""

    def testUninitializedSimulator(self):
        s = Simulator()

        with self.assertRaises(ValueError):
            s.fibers

        with self.assertRaises(ValueError):
            s.wavelengths

    def testSetWavelengths(self):
        s = Simulator()
        s.set_wavelengths(1550e-9)
        self.assertEqual(len(s.wavelengths), 1)
        self.assertEqual(s.wavelengths[0], 1550e-9)

        s = Simulator(wavelengths=[1550e-9, 1560e-9])
        self.assertEqual(len(s.wavelengths), 2)

        s = Simulator(wavelengths={'start': 1550e-9, 'end': 1580e-9, 'num': 4})
        self.assertEqual(len(s.wavelengths), 4)

        with self.assertRaises(ValueError):
            s.fibers

    def testSetFactory(self):
        s = Simulator()
        s.set_factory('tests/fiber/smf28.fiber')
        self.assertEqual(len(s.fibers), 1)

        f = FiberFactory()
        f.addLayer(radius=[4e-6, 5e-6, 6e-6], index=1.449)
        f.addLayer(index=1.444)
        s = Simulator(factory=f)
        self.assertEqual(len(s.fibers), 3)

        with self.assertRaises(ValueError):
            s.wavelengths

    def testModes(self):
        s = Simulator('tests/fiber/smf28.fiber', 1550e-9)
        modes = s.modes(0, 0)
        self.assertEqual(len(modes), 1)
        self.assertEqual(str(modes.pop()), 'HE(1,1)')

if __name__ == "__main__":
    import os
    os.chdir("../..")
    unittest.main()
