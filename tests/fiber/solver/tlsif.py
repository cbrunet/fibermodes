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

"""Test suite for fibermodes.fiber.solver.tlsif module."""

import unittest

from fibermodes import FiberFactory, Mode, Wavelength
from math import sqrt


class TestTLSIF(unittest.TestCase):

    """Test suite for three-layers step-index fibers."""

    def setUp(self):
        self.f = FiberFactory()

    def _compareWithCo(self, fiber, mode, neff):
        co = fiber.cutoff(mode)
        wl = Wavelength(1550e-9)
        n = max(l.maxIndex(wl) for l in fiber.layers)
        r = fiber.innerRadius(-1)

        nmax = sqrt(n**2 - (co / (r * wl.k0))**2)
        self.assertLess(neff, nmax)

        ms = Mode(mode.family, mode.nu+1, mode.m)
        co = fiber.cutoff(ms)
        nmin = sqrt(n**2 - (co / (r * wl.k0))**2)
        self.assertGreater(neff, nmin)

    def testCase1LP(self):
        self.f.addLayer(radius=4e-6, index=1.4489)
        self.f.addLayer(radius=10e-6, index=1.4474)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('LP', 0, 1), 1.4472309),
                (Mode('LP', 1, 1), 1.4457064),
                (Mode('LP', 0, 2), 1.4445245)]
        lpmodes = fiber.findLPmodes(wl)

        self.assertEqual(len(lpmodes), len(sols))

        for mode, neff in sols:
            self._compareWithCo(fiber, mode, neff)
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase2LP(self):
        """Annular-core fiber."""
        self.f.addLayer(radius=4e-6, index=1.4444)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('LP', 0, 1), 1.4472296),
                (Mode('LP', 1, 1), 1.4465947),
                (Mode('LP', 2, 1), 1.4452985)]
        lpmodes = fiber.findLPmodes(wl)

        self.assertEqual(len(lpmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-4), neff)

    def testCase3LP(self):
        self.f.addLayer(radius=4e-6, index=1.4474)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('LP', 0, 1), 1.44767716),
                (Mode('LP', 1, 1), 1.44675879),
                (Mode('LP', 2, 1), 1.44534443),
                (Mode('LP', 0, 2), 1.44452950)]
        lpmodes = fiber.findLPmodes(wl)

        self.assertEqual(len(lpmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase4LP(self):
        self.f.addLayer(radius=4e-6, index=1.4444)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4474)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('LP', 0, 1), 1.447761788),
                (Mode('LP', 1, 1), 1.447424556)]
        lpmodes = fiber.findLPmodes(wl)

        self.assertEqual(len(lpmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase5LP(self):
        """W-type fiber."""
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(radius=16e-6, index=1.4444)
        self.f.addLayer(index=1.4474)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('LP', 0, 1), 1.44809)]  # From OptiFiber
        lpmodes = fiber.findLPmodes(wl)

        self.assertEqual(len(lpmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase1Vector(self):
        self.f.addLayer(radius=4e-6, index=1.4489)
        self.f.addLayer(radius=10e-6, index=1.4474)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('HE', 1, 1), 1.44722991),
                (Mode('TE', 0, 1), 1.44570643),
                (Mode('TM', 0, 1), 1.445706197),
                (Mode('HE', 2, 1), 1.445704747),
                (Mode('EH', 1, 1), 1.44452366)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase2Vector(self):
        """Annular-core fiber."""
        self.f.addLayer(radius=4e-6, index=1.4444)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('HE', 1, 1), 1.4472267686),
                (Mode('TE', 0, 1), 1.4465947086),
                (Mode('HE', 2, 1), 1.446591650399142),
                (Mode('TM', 0, 1), 1.446587672894224),
                (Mode('EH', 1, 1), 1.445296246037881),
                (Mode('HE', 3, 1), 1.4452944761507711)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-4), neff)

    def testCase3Vector(self):
        self.f.addLayer(radius=4e-6, index=1.4474)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4444)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('HE', 1, 1), 1.447675825578464),
                (Mode('TE', 0, 1), 1.44675879173106),
                (Mode('HE', 2, 1), 1.4467563516096955),
                (Mode('TM', 0, 1), 1.4467544714182625),
                (Mode('EH', 1, 1), 1.445343017591462),
                (Mode('HE', 3, 1), 1.4453405392005971),
                (Mode('HE', 1, 2), 1.4445293834464685)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase4Vector(self):
        self.f.addLayer(radius=4e-6, index=1.4444)
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(index=1.4474)
        fiber = self.f[0]
        wl = Wavelength(1550e-9)

        sols = [(Mode('HE', 1, 1), 1.4477608163543525),
                (Mode('TE', 0, 1), 1.447424556045192),
                (Mode('HE', 2, 1), 1.4474241401608832),
                (Mode('TM', 0, 1), 1.4474235819526378)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))

        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-5), neff)

    def testCase5Vector(self):
        """Annular-core fiber."""
        self.f.addLayer(radius=10e-6, index=1.4489)
        self.f.addLayer(radius=16e-6, index=1.4444)
        self.f.addLayer(index=1.4474)
        fiber = self.f[0]

        wl = Wavelength(1550e-9)
        sols = [(Mode('HE', 1, 1), 1.448089116517021)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))
        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-6), neff)

        wl = Wavelength(800e-9)
        sols = [(Mode('HE', 1, 1), 1.448638518377151),
                (Mode('TE', 0, 1), 1.4482384223480635),
                (Mode('TM', 0, 1), 1.448237707949158),
                (Mode('EH', 1, 1), 1.4477149),  # Values from OptiFiber
                (Mode('HE', 1, 2), 1.4475354),
                (Mode('HE', 2, 1), 1.4482380),
                (Mode('HE', 3, 1), 1.4477146)]
        vmodes = fiber.findVmodes(wl)
        self.assertEqual(len(vmodes), len(sols))
        for mode, neff in sols:
            self.assertAlmostEqual(fiber.neff(mode, wl, delta=1e-6), neff)

    def _testFiberCutoff(self, rho, n, cutoffs, places=7):
        self.setUp()
        self.f.addLayer(radius=rho[0], index=n[0])
        self.f.addLayer(radius=rho[1], index=n[1])
        self.f.addLayer(index=n[2])
        fiber = self.f[0]

        for mode, co in cutoffs.items():
            self.assertAlmostEqual(fiber.cutoff(mode), co,
                                   places=places,
                                   msg=str(mode))

    def testLPCutoffA(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.43, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): 4.034844259728652,
            Mode('LP', 2, 1): 6.1486114063146005,
            Mode('LP', 3, 1): 8.07126756792508,
            Mode('LP', 4, 1): 9.911798124561814,
            Mode('LP', 0, 2): 6.568180843774973,
            Mode('LP', 1, 2): 8.922361377477307,
            Mode('LP', 2, 2): 11.06585974653044,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffA(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.43, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): 4.034844259728651,
            Mode('HE', 2, 1): 4.071976253449693,
            Mode('TM', 0, 1): 4.058192997221014,
            Mode('EH', 1, 1): 6.158255614959294,
            Mode('HE', 3, 1): 6.189815896708511,
            Mode('EH', 2, 1): 8.080052963422796,
            Mode('HE', 4, 1): 8.115131183786337,
            Mode('EH', 3, 1): 9.91993372343631,
            Mode('HE', 5, 1): 9.957649725258843,
            Mode('HE', 1, 2): 6.589429513136826,
            Mode('TE', 0, 2): 8.922361377477312,
            Mode('HE', 2, 2): 8.948985568829624,
            Mode('TM', 0, 2): 8.953573638542046,
            Mode('EH', 1, 2): 11.078160141775095,
            Mode('HE', 3, 2): 11.09621953195914,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffB(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.45, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): 3.1226096356321893,
            Mode('LP', 2, 1): 5.096112984974791,
            Mode('LP', 3, 1): 6.968066798210773,
            Mode('LP', 4, 1): 8.8012241922413,
            Mode('LP', 5, 1): 10.61168894514904,
            Mode('LP', 0, 2): 4.676313597977374,
            Mode('LP', 1, 2): 6.809117963058563,
            Mode('LP', 2, 2): 8.743801177466404,
            Mode('LP', 3, 2): 10.598944233713851,
            Mode('LP', 0, 3): 8.047306845386878,
            Mode('LP', 1, 3): 9.953012983126248,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffB(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.45, 1.44]
        cutoffs = {
            Mode('TM', 0, 1): 3.111217543593232,
            Mode('TE', 0, 1): 3.122609635632189,
            Mode('HE', 2, 1): 3.1400200936070846,
            Mode('EH', 1, 1): 4.669304720761619,
            Mode('HE', 1, 2): 5.088131872468638,
            Mode('HE', 3, 1): 5.118129406153233,
            Mode('EH', 2, 1): 5.89459696711537,
            Mode('TM', 0, 2): 6.7934897736915065,
            Mode('HE', 2, 2): 6.80880538983052,
            Mode('TE', 0, 2): 6.809117963058563,
            Mode('HE', 4, 1): 6.993124138822584,
            Mode('EH', 3, 1): 7.08470361250189,
            Mode('EH', 1, 2): 8.049518101191492,
            Mode('EH', 4, 1): 8.382115427339519,
            Mode('HE', 1, 3): 8.735885113376382,
            Mode('HE', 3, 2): 8.747374022674864,
            Mode('HE', 5, 1): 8.828714775284547,
            Mode('EH', 2, 2): 9.416036962761297,
            Mode('TE', 0, 3): 9.95301298312625,
            Mode('HE', 2, 3): 9.962177458632713,
            Mode('TM', 0, 3): 9.962228554278012,
            Mode('HE', 4, 2): 10.605263286689778,
            Mode('HE', 6, 1): 10.64128881198123,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffC(self):
        rho = [4e-6, 6e-6]
        n = [1.43, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): 3.010347467577181,
            Mode('LP', 2, 1): 4.404178238529268,
            Mode('LP', 3, 1): 5.631998448700369,
            Mode('LP', 4, 1): 6.7965518925242865,
            Mode('LP', 5, 1): 7.93118037952865,
            Mode('LP', 6, 1): 9.050134813376669,
            Mode('LP', 7, 1): 10.160295215952916,
            Mode('LP', 0, 2): 10.813986300277824,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffC(self):
        rho = [4e-6, 6e-6]
        n = [1.43, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): 3.0103474675771804,
            Mode('TM', 0, 1): 3.0732744029480012,
            Mode('TE', 0, 2): 11.215674035379953,
            Mode('TM', 0, 2): 11.29528661745687,
            Mode('EH', 1, 1): 4.43599929326006,
            Mode('EH', 2, 1): 5.660787662502081,
            Mode('EH', 3, 1): 6.821606789237238,
            Mode('EH', 4, 1): 7.952484494712328,
            Mode('EH', 5, 1): 9.067961694568465,
            Mode('EH', 6, 1): 10.175030484705225,
            Mode('HE', 2, 1): 3.0406851062929734,
            Mode('HE', 3, 1): 4.438962073092406,
            Mode('HE', 4, 1): 5.668294434394004,
            Mode('HE', 5, 1): 6.833174601202006,
            Mode('HE', 6, 1): 7.967602949136493,
            Mode('HE', 7, 1): 9.086138896920177,
            Mode('HE', 8, 1): 10.195817896822504,
            Mode('HE', 1, 2): 10.844609209283163,
            Mode('HE', 2, 2): 11.249595259175186,
            Mode('EH', 1, 2): 11.843142062848772,
            Mode('HE', 3, 2): 11.832900895486063,
            Mode('EH', 2, 2): 12.538738658782329,
            Mode('HE', 4, 2): 12.528230836249172,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffD(self):
        rho = [4e-6, 6e-6]
        n = [1.45, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): 2.702968459636167,
            Mode('LP', 2, 1): 4.150583195855695,
            Mode('LP', 3, 1): 5.430106475704322,
            Mode('LP', 4, 1): 6.636532360901636,
            Mode('LP', 5, 1): 7.804416891196523,
            Mode('LP', 6, 1): 8.949785986163985,
            Mode('LP', 7, 1): 10.080981852288588,
            Mode('LP', 0, 2): 5.640393617621346,
            Mode('LP', 1, 2): 8.008821133207624,
            Mode('LP', 2, 2): 9.679408185385487,
            Mode('LP', 3, 2): 10.97034948328025,
            Mode('LP', 0, 3): 9.684508718046876,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffD(self):
        rho = [4e-6, 6e-6]
        n = [1.45, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): 2.7029684596361676,
            Mode('HE', 2, 1): 2.7228694802366005,
            Mode('TM', 0, 1): 2.727734813318786,
            Mode('EH', 1, 1): 4.1655157193520465,
            Mode('HE', 3, 1): 4.176283860563018,
            Mode('EH', 2, 1): 5.445008118664826,
            Mode('HE', 4, 1): 5.458819017982079,
            Mode('HE', 1, 2): 5.634608766525465,
            Mode('HE', 1, 2): 5.634608766525469,
            Mode('EH', 3, 1): 6.650249935726423,
            Mode('HE', 5, 1): 6.666904206459127,
            Mode('EH', 4, 1): 7.816502257699482,
            Mode('HE', 6, 1): 7.835721155652211,
            Mode('TM', 0, 2): 7.993329888241878,
            Mode('HE', 2, 2): 8.003273407163517,
            Mode('TE', 0, 2): 8.008821133207624,
            Mode('EH', 5, 1): 8.960139011974638,
            Mode('HE', 7, 1): 8.981619572965892,
            Mode('EH', 1, 2): 9.680599063398324,
            Mode('HE', 3, 2): 9.681017840406332,
            Mode('HE', 1, 3): 9.686653009072776,
            Mode('EH', 6, 1): 10.089675701100248,
            Mode('HE', 8, 1): 10.113121418012547,
            Mode('HE', 4, 2): 10.980585429648642,
            Mode('EH', 2, 2): 10.98222290317733,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffE(self):
        rho = [4e-6, 6e-6]
        n = [1.44, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): 2.85904035776636975,
            Mode('LP', 2, 1): 4.2866039225676404,
            Mode('LP', 3, 1): 5.540915061306307,
            Mode('LP', 4, 1): 6.725406031775626,
            Mode('LP', 5, 1): 7.8752953434136135,
            Mode('LP', 6, 1): 9.006117838838101,
            Mode('LP', 7, 1): 10.125608397188888,
            Mode('LP', 0, 2): 9.482807865823602,
            Mode('LP', 1, 2): 10.27844425627377,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffE(self):
        rho = [4e-6, 6e-6]
        n = [1.44, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): 2.859040357765955,
            Mode('HE', 2, 1): 2.8832370027681815,
            Mode('TM', 0, 1): 2.9017337070631224,
            Mode('EH', 1, 1): 4.310052598194367,
            Mode('HE', 3, 1): 4.316477364814478,
            Mode('EH', 2, 1): 5.563044551409131,
            Mode('HE', 4, 1): 5.573271721659564,
            Mode('EH', 3, 1): 6.745115477350213,
            Mode('HE', 5, 1): 6.758852822325253,
            Mode('EH', 4, 1): 7.892295201926296,
            Mode('HE', 6, 1): 7.9091525519850805,
            Mode('EH', 5, 1): 9.020476094070924,
            Mode('HE', 7, 1): 9.040050082529529,
            Mode('EH', 6, 1): 10.137550450462196,
            Mode('HE', 8, 1): 10.159460454232093,
            Mode('HE', 1, 2): 9.482807865823602,
            Mode('TE', 0, 2): 10.278444256273769,
            Mode('HE', 2, 2): 10.289797328577112,
            Mode('TM', 0, 2): 10.310990340988402,
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testCutoffTableIII(self):
        """Values from cutoff acticle, Table III."""
        n = (1.444, 1.474, 1.444)
        b = 10e-6

        rho = (0.25*b, b)
        cutoffs = {
            Mode('TE', 0, 1): 2.4161,
            Mode('HE', 2, 1): 2.4336,
            Mode('TM', 0, 1): 2.4257,
            # Mode('EH', 1, 1): 3.8330,
            Mode('HE', 3, 1): 3.8561,
            Mode('HE', 1, 2): 4.4475,
            # Mode('EH', 2, 1): 5.1359,
            Mode('HE', 4, 1): 5.1603,
            Mode('TE', 0, 2): 5.7336,
            Mode('HE', 2, 2): 5.7418,
            Mode('TM', 0, 2): 5.7610,
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

        rho = (0.5*b, b)
        cutoffs = {
            Mode('TE', 0, 1): 2.5544,
            Mode('HE', 2, 1): 2.5742,
            Mode('TM', 0, 1): 2.5822,
            # Mode('EH', 1, 1): 3.9294,
            Mode('HE', 3, 1): 3.9648,
            Mode('HE', 1, 2): 6.3932,
            # Mode('EH', 2, 1): 5.1976,
            Mode('HE', 4, 1): 5.2316,
            Mode('TE', 0, 2): 7.3236,
            Mode('HE', 2, 2): 7.3337,
            Mode('TM', 0, 2): 7.3583,
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

        rho = (0.75*b, b)
        cutoffs = {
            Mode('TE', 0, 1): 3.1663,
            Mode('HE', 2, 1): 3.1943,
            Mode('TM', 0, 1): 3.2188,
            # Mode('EH', 1, 1): 4.6458,
            Mode('HE', 3, 1): 4.7123,
            Mode('HE', 1, 2): 12.6056,
            # Mode('EH', 2, 1): 5.9360,
            Mode('HE', 4, 1): 6.0074,
            Mode('TE', 0, 2): 13.3513,
            Mode('HE', 2, 2): 13.3631,
            Mode('TM', 0, 2): 13.3822,
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

    def testBuresEx334(self):
        self.f.addLayer(material="SiO2GeO2", radius=4.5e-6,
                        index=1.448918, wl=1550e-9)
        self.f.addLayer(material="Silica", radius=62.5e-6)
        self.f.addLayer(material="Air")
        fiber = self.f[0]

        # Fig 3.31
        wl = Wavelength(900e-9)
        vgc = 1 / fiber.ng(Mode("HE", 1, 1), wl)
        self.assertGreater(vgc, 0.680)
        self.assertLess(vgc, 0.6805)

        vgc = 1 / fiber.ng(Mode("EH", 1, 1), wl)
        self.assertGreater(vgc, 0.6825)
        self.assertLess(vgc, 0.683)

        wl = Wavelength(1600e-9)
        vgc = 1 / fiber.ng(Mode("HE", 1, 1), wl)
        self.assertGreater(vgc, 0.6805)
        self.assertLess(vgc, 0.6815)

        vgc = 1 / fiber.ng(Mode("EH", 1, 1), wl)
        self.assertGreater(vgc, 0.683)
        self.assertLess(vgc, 0.6836)

        # Fig 3.32
        # wl = Wavelength(900e-9)
        # D = fiber.D(Mode("HE", 1, 1), wl)
        # self.assertGreater(D, -80)
        # self.assertLess(D, -60)

        # D = fiber.D(Mode("EH", 1, 1), wl)
        # self.assertGreater(D, -80)
        # self.assertLess(D, -60)

        # wl = Wavelength(1290e-9)
        # D = fiber.D(Mode("HE", 1, 1), wl)
        # self.assertGreater(D, -10)
        # self.assertLess(D, 10)

        # D = fiber.D(Mode("EH", 1, 1), wl)
        # self.assertGreater(D, -10)
        # self.assertLess(D, 10)

        # wl = Wavelength(1550e-9)
        # D = fiber.D(Mode("HE", 1, 1), wl)
        # self.assertGreater(D, 10)
        # self.assertLess(D, 20)

        # wl = Wavelength(1600e-9)
        # D = fiber.D(Mode("HE", 1, 1), wl)
        # self.assertGreater(D, 15)
        # self.assertLess(D, 30)

        # D = fiber.D(Mode("EH", 1, 1), wl)
        # self.assertGreater(D, 15)
        # self.assertLess(D, 30)

if __name__ == "__main__":
    unittest.main()
