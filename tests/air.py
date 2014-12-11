'''
Created on 2014-09-08

@author: cbrunet
'''
import unittest

from fibermodes import Wavelength
from fibermodes.material import Air


class TestAir(unittest.TestCase):

    def testIndex(self):
        self.assertAlmostEqual(Air.n(Wavelength(0.5876e-6)), 1.00027717)
        self.assertAlmostEqual(Air.n(Wavelength(1.55e-6)), 1.00027326)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
