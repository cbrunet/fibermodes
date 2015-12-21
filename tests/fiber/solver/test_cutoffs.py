#!/usr/bin/env python3

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

import unittest

from fibermodes import FiberFactory, Mode, ModeFamily, HE11
from itertools import zip_longest
from math import isnan


class TestCutoffs(unittest.TestCase):

    """Systematic tests for cutoff values.

    Two things are tested:

    - Order of HE / EH cutoffs
    - Proximity of normalized propagation constant with 0 near cutoff.

    If this test pass, it doesn't mean cutoffs are OK.
    If it fails because of cutoff order, something is wrong.
    If it fails because of "b", it is probably a skipped root.

    """

    def _testFiberCutoffs(self, r, n):
        f = FiberFactory()
        for r_, n_ in zip_longest(r, n):
            f.addLayer(radius=r_, index=n_)
        fiber = f[0]

        for nu in range(1, 5):
            pco = -1
            for m in range(1, 5):
                for fam in (ModeFamily.HE, ModeFamily.EH):
                    mode = Mode(fam, nu, m)
                    co = fiber.cutoff(mode)
                    self.assertGreater(co, pco, "Not greater "+str(mode))

                    if mode != HE11:
                        d = 0.
                        b = float("nan")
                        while isnan(b):
                            d += 0.25
                            wl = fiber.toWl(co + d)
                            b = fiber.b(mode, wl, delta=1e-5)
                        self.assertLess(b, 0.1, "Wrong b "+str(mode))

                    pco = co

    def testProfileA(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.47, 1.43, 1.44])

    def testProfileB_45(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.47, 1.45, 1.44])

    def testProfileB_46(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.47, 1.46, 1.44])

    def testProfileC(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.43, 1.47, 1.44])

    def testProfileD(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.45, 1.47, 1.44])

    def testProfileE(self):
        self._testFiberCutoffs(r=[4e-6, 6e-6], n=[1.44, 1.47, 1.44])

    def testCase1_4474(self):
        self._testFiberCutoffs(r=[4e-6, 10e-6], n=[1.4489, 1.4474, 1.4444])

    def testCase1_4484(self):
        self._testFiberCutoffs(r=[4e-6, 10e-6], n=[1.4489, 1.4484, 1.4444])

    def testCase2(self):
        self._testFiberCutoffs(r=[4e-6, 10e-6], n=[1.4444, 1.4489, 1.4444])

    def testCase3(self):
        self._testFiberCutoffs(r=[4e-6, 10e-6], n=[1.4474, 1.4489, 1.4444])

    def testCase4(self):
        self._testFiberCutoffs(r=[4e-6, 10e-6], n=[1.4444, 1.4489, 1.4474])

    def testCase5(self):
        self._testFiberCutoffs(r=[10e-6, 16e-6], n=[1.4489, 1.4444, 1.4474])


if __name__ == "__main__":
    unittest.main()
