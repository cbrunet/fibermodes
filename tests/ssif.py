'''
Created on 2014-05-06

@author: cbrunet
'''
import unittest

from fibermodes import fixedFiber, Mode, Wavelength


class TestSSIF(unittest.TestCase):

    def testFundamental(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4.5e-6], [1.448918, 1.444418])
        he11 = fiber.solve(Mode('HE', 1, 1))
        self.assertAlmostEqual(he11.neff, 1.4464045, 5)

        lp01 = fiber.solve(Mode('LP', 0, 1))
        self.assertEqual(he11, lp01)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
