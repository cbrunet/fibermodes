'''
Created on 2014-09-08

@author: cbrunet
'''
import unittest
import warnings

from fibermodes import Wavelength
from fibermodes.material import Silica, SiO2GeO2


class TestSiO2GeO2(unittest.TestCase):

    def testIndex(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertAlmostEqual(Silica.n(Wavelength(0.5876e-6)),
                                   SiO2GeO2.n(Wavelength(0.5876e-6), 0))
        self.assertAlmostEqual(Silica.n(Wavelength(1.55e-6)),
                               SiO2GeO2.n(Wavelength(1.55e-6), 0))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
