# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

"""Test suite for fibermodes.fiber.solver.ssif module."""

import unittest

from fibermodes import Wavelength, Mode, FiberFactory
from math import sqrt


class TestSSIF(unittest.TestCase):

    """Test suite for SSIFSolver class."""

    def testCutoffLP(self):
        f = FiberFactory()
        f.addLayer(radius=1e-5 / 3, index=5)
        f.addLayer(index=4)

        fiber = f[0]

        sols = [(Mode('LP', 0, 1), 0),
                (Mode('LP', 0, 2), 3.8317),
                (Mode('LP', 0, 3), 7.0156),
                (Mode('LP', 1, 1), 2.4048),
                (Mode('LP', 1, 2), 5.5201),
                (Mode('LP', 2, 1), 3.8317)]

        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoff(mode), V0, 4, msg=str(mode))

    def testCutoffV(self):
        """Values from Bures, Table 3.6."""
        delta = 0.3
        V = 5

        wl = Wavelength(1.55e-6)
        n2 = 1.444

        n1 = sqrt(n2**2 / (1 - 2 * delta))
        rho = V / (sqrt(n1**2 - n2**2) * wl.k0)

        f = FiberFactory()
        f.addLayer(radius=rho, index=n1)
        f.addLayer(index=n2)
        fiber = f[0]

        sols = [(Mode('TE', 0, 1), 2.4048),
                (Mode('TM', 0, 1), 2.4048),
                (Mode('HE', 1, 1), 0),
                (Mode('EH', 1, 1), 3.8317),
                (Mode('TE', 0, 2), 5.5201),
                (Mode('TM', 0, 2), 5.5201),
                (Mode('HE', 1, 2), 3.8317),
                (Mode('EH', 1, 2), 7.0156),
                (Mode('HE', 2, 1), 2.8526),
                (Mode('EH', 2, 1), 5.1356),
                (Mode('HE', 3, 1), 4.3423),
                (Mode('EH', 2, 2), 8.4172)]

        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoff(mode), V0, 4, msg=str(mode))

    def testCutoffV2(self):
        """Values from cutoff acticle, Table III."""
        n1 = 1.474
        n2 = 1.444
        rho = 10e-6

        f = FiberFactory()
        f.addLayer(radius=rho, index=n1)
        f.addLayer(index=n2)
        fiber = f[0]

        sols = [(Mode('TE', 0, 1), 2.4048),
                (Mode('HE', 2, 1), 2.4221),
                (Mode('TM', 0, 1), 2.4048),
                (Mode('EH', 1, 1), 3.8317),
                (Mode('HE', 3, 1), 3.8533),
                (Mode('HE', 1, 2), 3.8317),
                (Mode('EH', 2, 1), 5.1356),
                (Mode('HE', 4, 1), 5.1597),
                (Mode('TE', 0, 2), 5.5201),
                (Mode('HE', 2, 2), 5.5277),
                (Mode('TM', 0, 2), 5.5201)]

        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoff(mode), V0, 4, msg=str(mode))

    def testCutoffV3(self):
        """Same index for n1 and n2; therefore this is SSIF."""
        n1 = 1.6
        n2 = 1.6
        n3 = 1.4
        rho1 = 5e-6
        rho2 = 6e-6

        f = FiberFactory()
        f.addLayer(radius=rho1, index=n1)
        f.addLayer(radius=rho2, index=n2)
        f.addLayer(index=n3)
        fiber = f[0]

        sols = [(Mode('TE', 0, 1), 2.4048),
                (Mode('HE', 2, 1), 2.522748641920963),
                (Mode('TM', 0, 1), 2.4048),
                (Mode('EH', 1, 1), 3.8317),
                (Mode('HE', 3, 1), 3.9762622998101453),
                (Mode('HE', 1, 2), 3.8317)]

        for mode, V0 in sols:
            self.assertAlmostEqual(fiber.cutoff(mode), V0, 4, msg=str(mode))

    def testFundamental(self):
        f = FiberFactory()
        f.addLayer(radius=4.5e-6, index=1.448918)
        f.addLayer(index=1.444418)
        fiber = f[0]
        wl = Wavelength(1550e-9)

        neff = fiber.neff(Mode('HE', 1, 1), wl)
        self.assertAlmostEqual(neff, 1.4464045, places=5)

        lp01 = fiber.neff(Mode('LP', 0, 1), wl)
        self.assertAlmostEqual(lp01, neff, places=5)

    def testFindVmodes(self):
        f = FiberFactory()
        f.addLayer(radius=4.5e-6, index=1.448918)
        f.addLayer(index=1.444418)
        fiber = f[0]

        wl = Wavelength(800e-9)
        modes = fiber.findVmodes(wl)

        sols = [(Mode('HE', 1, 1), 1.4479082),
                (Mode('TE', 0, 1), 1.44643),
                (Mode('HE', 2, 1), 1.446427),
                (Mode('TM', 0, 1), 1.4464268),
                (Mode('EH', 1, 1), 1.444673),
                (Mode('HE', 3, 1), 1.444669),
                (Mode('HE', 1, 2), 1.4444531)]
        self.assertEqual(len(modes), len(sols))
        for mode, neff in sols:
            self.assertTrue(mode in modes)
            self.assertAlmostEqual(fiber.neff(mode, wl), neff)

    def testFindLPmodes(self):
        f = FiberFactory()
        f.addLayer(radius=4.5e-6, index=1.448918)
        f.addLayer(index=1.444418)
        fiber = f[0]

        wl = Wavelength(800e-9)
        modes = fiber.findLPmodes(wl)

        self.assertEqual(len(modes), 4)

    def testBures3_6(self):
        delta = 0.3
        V = 5

        wl = Wavelength(1.55e-6)
        n2 = 1.444

        n1 = sqrt(n2**2 / (1 - 2 * delta))
        rho = V / (sqrt(n1**2 - n2**2) * wl.k0)

        f = FiberFactory()
        f.addLayer(radius=rho, index=n1)
        f.addLayer(index=n2)
        fiber = f[0]
        modes = fiber.findVmodes(wl)

        sols = {Mode('HE', 1, 1): 2.119,
                Mode('TE', 0, 1): 3.153,
                Mode('TM', 0, 1): 3.446,
                Mode('HE', 2, 1): 3.377,
                Mode('EH', 1, 1): 4.235,
                Mode('HE', 3, 1): 4.507,
                Mode('HE', 1, 2): 4.638}
        self.assertEqual(len(modes), len(sols))
        for m in modes:
            neff = fiber.neff(m, wl)
            u = wl.k0 * rho * sqrt(n1**2 - neff**2)
            self.assertAlmostEqual(u, sols[m], 3)
        # print(fiber._solver.neff.cache_info())

    def testBures_4_2_8(self):
        n2 = 1.457420
        n1 = 1.462420
        rho = 8.335e-6
        wl = Wavelength(0.6328e-6)

        f = FiberFactory()
        f.addLayer(radius=rho, index=n1)
        f.addLayer(index=n2)
        fiber = f[0]
        modes = fiber.findLPmodes(wl)

        sols = {Mode('LP', 0, 1): 2.1845,
                Mode('LP', 0, 2): 4.9966,
                Mode('LP', 0, 3): 7.7642,
                Mode('LP', 1, 1): 3.4770,
                Mode('LP', 1, 2): 6.3310,
                Mode('LP', 1, 3): 9.0463,
                Mode('LP', 2, 1): 4.6544,
                Mode('LP', 2, 2): 7.5667,
                Mode('LP', 3, 1): 5.7740,
                Mode('LP', 3, 2): 8.7290,
                Mode('LP', 4, 1): 6.8560,
                Mode('LP', 4, 2): 9.8153,
                Mode('LP', 5, 1): 7.9096,
                Mode('LP', 6, 1): 8.9390,
                Mode('LP', 7, 1): 9.9451}
        self.assertEqual(len(modes), len(sols))
        for m in modes:
            neff = fiber.neff(m, wl)
            u = wl.k0 * rho * sqrt(n1**2 - neff**2)
            self.assertAlmostEqual(u, sols[m], 3)

if __name__ == "__main__":
    unittest.main()
