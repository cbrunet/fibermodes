'''
Created on 2014-09-08

@author: cbrunet
'''
import unittest

from fibermodes import Wavelength
from fibermodes.material import Germania


class TestGermania(unittest.TestCase):

    def testIndex(self):
        self.assertAlmostEqual(Germania.n(Wavelength(0.5876e-6)), 1.6085, 4)
        self.assertAlmostEqual(Germania.n(Wavelength(1.55e-6)), 1.5871, 4)
        self.assertAlmostEqual(Germania.n(Wavelength(1.68e-6)), 1.5859, 4)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
