"""Test suite for fibermodes.fiber.solver.cuda"""

import unittest
from tests.fiber.solver.tlsif import TestTLSIF
from fibermodes.fiber.solver import cuda


class TestCuda(TestTLSIF):

    """Test suite for PSimulator class"""

    def setUp(self):
        super().setUp()
        self.f.setSolvers(neff=cuda.Neff)

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    import os
    os.chdir("../..")
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCuda)
    unittest.TextTestRunner(verbosity=1).run(suite)
