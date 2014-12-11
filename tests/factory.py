'''
Created on 2014-05-01

@author: cbrunet
'''
import unittest

from fibermodes.fiber.factory import fixedFiber
from fibermodes.fiber import *
from fibermodes.wavelength import Wavelength


class TestFactory(unittest.TestCase):

    def testFixedFiber(self):
        wl = Wavelength(1550e-9)

        # SSIF
        fiber = fixedFiber(wl, [4e-6], [1.474, 1.444])
        self.assertTrue(isinstance(fiber, SSIF), msg="SSIF")

        # TLSIF
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.444, 1.474, 1.444])
        self.assertTrue(isinstance(fiber, TLSIF), msg="TLSIF")

        # MLSIF
        fiber = fixedFiber(wl, [4e-6, 10e-6, 15e-6],
                           [1.444, 1.474, 1.464, 1.444])
        self.assertTrue(isinstance(fiber, MLSIF), msg="MLSIF")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
