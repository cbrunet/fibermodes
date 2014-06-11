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
        self.assertAlmostEqual(he11.neff, 1.4464045, places=5)

        lp01 = fiber.solve(Mode('LP', 0, 1))
        self.assertAlmostEqual(he11.neff, lp01.neff, places=5)

    def testvModes(self):
        wl = Wavelength(800e-9)
        fiber = fixedFiber(wl, [4.5e-6], [1.448918, 1.444418])
        modes = fiber.vModes()

        self.assertEqual(len(modes), 7)

        sols = [('HE(1,1)', 1.4479082),
                ('TE(0,1)', 1.44643),
                ('HE(2,1)', 1.446427),
                ('TM(0,1)', 1.4464268),
                ('EH(1,1)', 1.444673),
                ('HE(3,1)', 1.444669),
                ('HE(1,2)', 1.4444531)]
        for i, (name, neff) in enumerate(sols):
            self.assertEqual(name, str(modes[i]))
            self.assertAlmostEqual(neff, modes[i].neff)

    def testlpModes(self):
        wl = Wavelength(800e-9)
        fiber = fixedFiber(wl, [4.5e-6], [1.448918, 1.444418])
        modes = fiber.lpModes()

        self.assertEqual(len(modes), 4)

    def testvModesFromlpModes(self):
        wl = Wavelength(800e-9)
        fiber = fixedFiber(wl, [4.5e-6], [1.448918, 1.444418])
        lpModes = fiber.lpModes()
        modes = fiber.vModes(lpModes)

        self.assertEqual(len(modes), 7)

        sols = [('HE(1,1)', 1.4479082),
                ('TE(0,1)', 1.44643),
                ('HE(2,1)', 1.446427),
                ('TM(0,1)', 1.4464268),
                ('EH(1,1)', 1.444673),
                ('HE(3,1)', 1.444669),
                ('HE(1,2)', 1.4444531)]
        for i, (name, neff) in enumerate(sols):
            self.assertEqual(name, str(modes[i]))
            self.assertAlmostEqual(neff, modes[i].neff)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
