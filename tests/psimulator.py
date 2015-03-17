"""Unittest for PSimulator class."""

import unittest
from tests.simulator import TestSimulator
from fibermodes.simulator import PSimulator


class TestPSimulator(TestSimulator):

    """Run same test than for Simulator, but with parallel simulator,
    to ensure nothing break with the parallelization.

    """

    def setUp(self):
        self.simulator = PSimulator

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
