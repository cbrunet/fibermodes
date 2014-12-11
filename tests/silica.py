'''
Created on 2014-09-08

@author: cbrunet
'''
import unittest

from fibermodes import Wavelength
from fibermodes.material import Silica


class TestSilica(unittest.TestCase):

    def testIndex(self):
        self.assertAlmostEqual(Silica.n(Wavelength(0.5876e-6)), 1.45846, 5)
        self.assertAlmostEqual(Silica.n(Wavelength(1.55e-6)), 1.44402, 5)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
