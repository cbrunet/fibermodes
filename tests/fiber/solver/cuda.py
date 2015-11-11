"""Test suite for fibermodes.fiber.solver.cuda"""

import unittest

try:
    from tests.fiber.solver.tlsif import TestTLSIF
    from fibermodes.fiber.solver import cuda


    @unittest.skip("Implementation not finished")
    class TestCuda(TestTLSIF):

        """Test suite for PSimulator class"""

        def setUp(self):
            super().setUp()
            self.f.setSolvers(neff=cuda.Neff)

except Exception as e:
    class TestCuda(unittest.TestCase):

        @unittest.skip('Missing dependency - ' + str(e))
        def test_fail():
            pass

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCuda)
    unittest.TextTestRunner(verbosity=1).run(suite)
