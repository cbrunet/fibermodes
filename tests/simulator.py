"""Unittest for Simulator class."""

import unittest
from fibermodes import Simulator, fixedFiber
from fibermodes.material import Fixed
import numpy


class TestSimulator(unittest.TestCase):

    def testLenEmpty(self):
        sim = Simulator()
        self.assertEqual(len(sim), 0)

    def testLenOne(self):
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        self.assertEqual(len(sim), 1)

    def testLenOneDim(self):
        sim = Simulator()
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        sim.setWavelength(numpy.linspace(800e-9, 1550e-9, 100))
        self.assertEqual(len(sim), 100)

        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6, numpy.linspace(4e-6, 10e-6, 50))
        self.assertEqual(len(sim), 50)

        sim.setRadii(4e-6, 10e-6)
        sim.setMaterialsParams((numpy.linspace(1.444, 1.474, 25),), (1.444,))
        self.assertEqual(len(sim), 25)

    def testLenMultiDim(self):
        sim = Simulator()
        sim.setRadii((2e-6, 3e-6, 4e-6), [5e-6, 10e-6])  # 3 * 2 = 6
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((numpy.linspace(1.444, 1.474, 10),),
                               (numpy.arange(1.444, 1.484, 0.01),))  # 10 * 5
        sim.setWavelength(numpy.linspace(800e-9, 1550e-9, 100))  # 100
        self.assertEqual(len(sim), 30000)

    def testIterEmpty(self):
        sim = Simulator()
        fibers = list(sim)
        self.assertEqual(len(fibers), 0)

    def testIterOne(self):
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        fiber = list(sim)
        self.assertEqual(len(fiber), 1)

        fiber2 = fixedFiber(1550e-9, (4e-6,), (1.474, 1.444))
        self.assertEqual(fiber[0], fiber2)

    def testGetParam(self):
        wl = numpy.linspace(800e-9, 1550e-9)
        sim = Simulator()
        sim.setWavelength(wl)
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        self.assertTrue(numpy.all(sim.getParam('wavelength') == wl))

    def testConstraints(self):
        n = numpy.linspace(4e-6, 10e-6)
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((n,), (n,))
        self.assertEqual(len(sim), 2500)

        sim.addConstraint('index',
                          lambda x, y: x > y,
                          ('material', 0, 0),
                          ('material', 1, 0))
        self.assertEqual(len(sim), 1225)

        sim.delConstraint('index')
        self.assertEqual(len(sim), 2500)

        sim.addConstraint('equal',
                          lambda x, y: x == y,
                          ('material', 0, 0),
                          ('material', 1, 0))
        self.assertEqual(len(sim), 50)

    def testFctParam(self):
        r = numpy.linspace(4e-6, 10e-6)
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadius(1, r)
        sim.setRadiusFct(0, lambda x: .25*x, ('radius', 1))
        sim.setMaterials(Fixed, Fixed, Fixed)
        sim.setMaterialsParams((1.444,), (1.474,), (1.444,))
        self.assertTrue(numpy.all(sim.getParam('radius', 0) == .25 * r))
        self.assertEqual(len(sim), sum(1 for _ in sim))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
