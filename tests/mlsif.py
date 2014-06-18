'''
Created on 2014-05-06

@author: cbrunet
'''
import unittest

from fibermodes import fixedFiber, Wavelength


class TestMLSIF(unittest.TestCase):

    def _compareModes(self, modes, sols):
        self.assertEqual(len(modes), len(sols))

        for i in range(len(sols)):
            self.assertEqual(str(modes[i]), sols[i][0])
            self.assertAlmostEqual(modes[i].neff, sols[i][1])

    def testCase1LP(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4489, 1.4474, 1.4444])
        sols = [('LP(0,1)', 1.4472309),
                ('LP(1,1)', 1.4457064),
                ('LP(0,2)', 1.4445245)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase2LP(self):
        """Annular-core fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4444])

        sols = [('LP(0,1)', 1.4472296),
                ('LP(1,1)', 1.4465947),
                ('LP(2,1)', 1.4452985)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase3LP(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4474, 1.4489, 1.4444])

        sols = [('LP(0,1)', 1.44767716),
                ('LP(1,1)', 1.44675879),
                ('LP(2,1)', 1.44534443),
                ('LP(0,2)', 1.44452950)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase4LP(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4474])

        sols = [('LP(0,1)', 1.447761788),
                ('LP(1,1)', 1.447424556)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase5LP(self):
        """W-type fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [10e-6, 16e-6], [1.4489, 1.4444, 1.4474])

        sols = [('LP(0,1)', 1.44809)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
