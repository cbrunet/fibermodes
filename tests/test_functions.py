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


"""Test suite for fibermodes.functions module"""

import unittest

from fibermodes import functions


class TestFunctions(unittest.TestCase):

    def testCoefficients(self):
        for coefs in functions.A.values():
            self.assertEqual(sum(coefs), 0)

    def testDerivative(self):
        """Test against x**6

        Since error grows with k (derivative order),
        we divide x (closer to 0) and we adjust acceptable
        error. This gives a rough idea whether the test pass or not.

        """
        f = [lambda x: x**6,
             lambda x: 6 * x**5,
             lambda x: 30 * x**4,
             lambda x: 120 * x**3,
             lambda x: 360 * x**2,
             lambda x: 720 * x,
             lambda x: 720,
             lambda x: 0]

        for k in range(1, 7):
            for m in range(max(3, k+1), 7):
                for j in range(m):
                    self.assertEqual(sum(functions.A[(k, m, j)]), 0)
                    minerr = float("inf")
                    maxerr = 0
                    for x in (-2, 0, 1, 1.25):
                        x /= 10**(k)
                        err = abs(
                            functions.derivative(f[0], x, k, m, j, 1e-8) -
                            f[k](x))
                        minerr = min(minerr, err)
                        maxerr = max(maxerr, err)
                        self.assertLessEqual(
                            err, 10**(2*k-11),
                            msg="x={}, k={}, m={}, j={}".format(x, k, m, j))
                    # print(k, m, j, minerr, maxerr)

if __name__ == "__main__":
    unittest.main()
