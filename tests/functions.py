"""Test suite for fibermodes.functions module"""

import unittest

from fibermodes import functions


class TestFunctions(unittest.TestCase):

    def testDerivative(self):
        f = [lambda x: x**6,
             lambda x: 6 * x**5,
             lambda x: 30 * x**4,
             lambda x: 120 * x**3,
             lambda x: 360 * x**2,
             lambda x: 720 * x,
             lambda x: 720,
             lambda x: 0]

        for k in range(1, 3):
            for m in range(3, 7):
                for j in range(m):
                    self.assertEqual(sum(functions.A[(k, m, j)]), 0)
                    minerr = float("inf")
                    maxerr = 0
                    for x in (-0.2, 0, 0.1, 0.125):
                        err = abs(
                            functions.derivative(f[0], x, k, m, j, 1e-8) -
                            f[k](x))
                        minerr = min(minerr, err)
                        maxerr = max(maxerr, err)
                        self.assertLessEqual(
                            err, 6e-3,
                            msg="x={}, k={}, m={}, j={}".format(x, k, m, j))
                    # print(k, m, j, minerr, maxerr)

if __name__ == "__main__":
    unittest.main()
