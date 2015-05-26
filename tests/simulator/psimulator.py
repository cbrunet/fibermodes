"""Test suite for fibermodes.simulator.psimulator module"""

import unittest
from fibermodes.simulator import PSimulator
from tests.simulator.simulator import TestSimulator


class TestPSimulator(TestSimulator):

    """Test suite for PSimulator class"""

    def setUp(self):
        self.sim = PSimulator()

    def assertEqual(self, first, second, msg=None):
        try:
            first = first.get()
        except AttributeError:
            pass
        super().assertEqual(first, second, msg)

if __name__ == "__main__":
    import os
    os.chdir("../..")
    unittest.main()
