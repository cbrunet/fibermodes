'''
Created on 2014-05-06

@author: cbrunet
'''
import unittest

from fibermodes import fixedFiber, Wavelength, Mode


class TestACSIF(unittest.TestCase):

    def _compareModes(self, modes, sols):
        self.assertEqual(len(modes), len(sols))

        for i in range(len(sols)):
            self.assertAlmostEqual(modes[i].neff, sols[i][1])
            self.assertEqual(str(modes[i]), sols[i][0])

    def testCase2LP(self):
        """Annular-core fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4444])

        sols = [('LP(0,1)', 1.4472296),
                ('LP(1,1)', 1.4465947),
                ('LP(2,1)', 1.4452985)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase2Vector(self):
        """Annular-core fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4444])

        sols = [('HE(1,1)', 1.4472267686),
                ('TE(0,1)', 1.4465947086),
                ('HE(2,1)', 1.446591650399142),
                ('TM(0,1)', 1.446587672894224),
                ('EH(1,1)', 1.445296246037881),
                ('HE(3,1)', 1.4452944761507711)]
        lpmodes = fiber.lpModes(delta=1e-3)
        vmodes = fiber.vModes(lpmodes, delta=1e-4)
        self._compareModes(vmodes, sols)

    def testCutoffV(self):
        """Values from cutoff acticle, Table III."""
        wl = Wavelength(1.55e-6)
        n1 = 1.474
        n2 = 1.444
        b = 10e-6

        rho = 0.25
        fiber = fixedFiber(wl, [rho*b, b], [n2, n1, n2])
        sols = [(Mode('TE', 0, 1), 2.4161),
                (Mode('HE', 2, 1), 2.4336),
                (Mode('TM', 0, 1), 2.4257),
                (Mode('EH', 1, 1), 3.8330),
                (Mode('HE', 3, 1), 3.8561),
                (Mode('HE', 1, 2), 4.4475),
                (Mode('EH', 2, 1), 5.1359),
                (Mode('HE', 4, 1), 5.1603),
                (Mode('TE', 0, 2), 5.7336),
                (Mode('HE', 2, 2), 5.7418),
                (Mode('TM', 0, 2), 5.7610)]
        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoffV0(mode), V0, 4, msg=str(mode))

        rho = 0.5
        fiber = fixedFiber(wl, [rho*b, b], [n2, n1, n2])
        sols = [(Mode('TE', 0, 1), 2.5544),
                (Mode('HE', 2, 1), 2.5742),
                (Mode('TM', 0, 1), 2.5822),
                (Mode('EH', 1, 1), 3.9294),
                (Mode('HE', 3, 1), 3.9648),
                (Mode('HE', 1, 2), 6.3932),
                (Mode('EH', 2, 1), 5.1976),
                (Mode('HE', 4, 1), 5.2316),
                (Mode('TE', 0, 2), 7.3236),
                (Mode('HE', 2, 2), 7.3337),
                (Mode('TM', 0, 2), 7.3583)]
        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoffV0(mode), V0, 4, msg=str(mode))

        rho = 0.75
        fiber = fixedFiber(wl, [rho*b, b], [n2, n1, n2])
        sols = [(Mode('TE', 0, 1), 3.1663),
                (Mode('HE', 2, 1), 3.1943),
                (Mode('TM', 0, 1), 3.2188),
                (Mode('EH', 1, 1), 4.6458),
                (Mode('HE', 3, 1), 4.7123),
                (Mode('HE', 1, 2), 12.6056),
                (Mode('EH', 2, 1), 5.9360),
                (Mode('HE', 4, 1), 6.0074),
                (Mode('TE', 0, 2), 13.3513),
                (Mode('HE', 2, 2), 13.3631),
                (Mode('TM', 0, 2), 13.3822)]
        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoffV0(mode), V0, 4, msg=str(mode))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
