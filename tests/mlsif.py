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
            self.assertAlmostEqual(modes[i].neff, sols[i][1])
            self.assertEqual(str(modes[i]), sols[i][0])

    def testCase1LP(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4489, 1.4474, 1.4444])
        sols = [('LP(0,1)', 1.4472309),
                ('LP(1,1)', 1.4457064),
                ('LP(0,2)', 1.4445245)]
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

    def testCase1Vector(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4489, 1.4474, 1.4444])
        sols = [('HE(1,1)', 1.44722991),
                ('TE(0,1)', 1.44570643),
                ('TM(0,1)', 1.445706197),
                ('HE(2,1)', 1.445704747),
                ('EH(1,1)', 1.44452366)]
        lpmodes = fiber.lpModes(delta=1e-3)
        vmodes = fiber.vModes(lpmodes, delta=1e-4)
        self._compareModes(vmodes, sols)

    def testCase3Vector(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4474, 1.4489, 1.4444])

        sols = [('HE(1,1)', 1.447675825578464),
                ('TE(0,1)', 1.44675879173106),
                ('HE(2,1)', 1.4467563516096955),
                ('TM(0,1)', 1.4467544714182625),
                ('EH(1,1)', 1.445343017591462),
                ('HE(3,1)', 1.4453405392005971),
                ('HE(1,2)', 1.4445293834464685)]
        lpmodes = fiber.lpModes(delta=1e-3)
        vmodes = fiber.vModes(lpmodes, delta=1e-4)
        self._compareModes(vmodes, sols)

    def testCase4Vector(self):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4474])

        sols = [('HE(1,1)', 1.4477608163543525),
                ('TE(0,1)', 1.447424556045192),
                ('HE(2,1)', 1.4474241401608832),
                ('TM(0,1)', 1.4474235819526378)]
        lpmodes = fiber.lpModes(delta=1e-3)
        vmodes = fiber.vModes(lpmodes, delta=1e-5)
        self._compareModes(vmodes, sols)

    def testCase5Vector(self):
        """W-type fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [10e-6, 16e-6], [1.4489, 1.4444, 1.4474])

        sols = [('HE(1,1)', 1.448089116517021)]
        vmodes = fiber.vModes(delta=1e-4)
        self._compareModes(vmodes, sols)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
