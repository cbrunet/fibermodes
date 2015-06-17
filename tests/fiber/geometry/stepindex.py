"""Test suite for fiber.geometry.stepindex module"""

import unittest

from fibermodes.fiber.geometry.stepindex import StepIndex


class TestStepIndex(unittest.TestCase):

    """Test suite for StepIndex class"""

    def testIndex(self):
        geom = StepIndex(0, 4e-6, m="Fixed", mp=(1.444,))

        self.assertEqual(geom.index(0, 1550e-9), 1.444)
        self.assertEqual(geom.index(2e-6, 1550e-9), 1.444)
        self.assertEqual(geom.index(-2e-6, 1550e-9), 1.444)
        self.assertIsNone(geom.index(5e-6, 1550e-9))
        self.assertIsNone(geom.index(-5e-6, 1550e-9))

    def testCladding(self):
        geom = StepIndex(4e-6, float("inf"), m="Fixed", mp=(1.444,))

        self.assertEqual(geom.index(4e-6, 1550e-9), 1.444)
        self.assertEqual(geom.index(10e-6, 1550e-9), 1.444)
        self.assertIsNone(geom.index(2e-6, 1550e-9))


if __name__ == "__main__":
    import os
    os.chdir('../..')
    unittest.main()
