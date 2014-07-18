"""Unittest for Simulator class."""

import unittest
from fibermodes import Simulator, fixedFiber, Mode
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
        radii = numpy.fromiter((f._r[0] for f in sim), numpy.float, len(sim))
        self.assertTrue(numpy.all(radii == .25 * r))
        self.assertEqual(len(sim), sum(1 for _ in sim))

    def testGetDimensions(self):
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        d = sim.getDimensions()
        self.assertEqual(len(d), 0)

        sim.setWavelength(numpy.linspace(800e-9, 1580e-9))
        d = sim.getDimensions()
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0][0], 'wavelength')

        sim.setRadius(0, numpy.linspace(2e-6, 10e-6))
        d = sim.getDimensions()
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0][0], 'wavelength')
        self.assertEqual(d[1][0], 'radius')
        self.assertEqual(d[1][1], 0)

        sim.setMaterialParam(0, 0, numpy.linspace(1.445, 1.465))
        d = sim.getDimensions()
        self.assertEqual(len(d), 3)
        self.assertEqual(d[0][0], 'wavelength')
        self.assertEqual(d[1][0], 'radius')
        self.assertEqual(d[1][1], 0)
        self.assertEqual(d[2][0], 'material')
        self.assertEqual(d[2][1], 0)
        self.assertEqual(d[2][2], 0)

    def testGetMinMaxParams(self):
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        w, m, r = sim._getMinMaxParams()
        self.assertEqual(w[0], 1550e-9)
        self.assertEqual(r[0][0], 4e-6)
        self.assertEqual(m[0][0][0], 1.454)

        sim.setWavelength(numpy.linspace(800e-9, 1580e-9))
        w, m, r = sim._getMinMaxParams()
        self.assertEqual(w[0], 800e-9)
        self.assertEqual(w[1], 1580e-9)
        self.assertEqual(r[0][0], 4e-6)
        self.assertEqual(m[0][0][0], 1.454)

        sim.setRadius(0, numpy.linspace(2e-6, 10e-6))
        w, m, r = sim._getMinMaxParams()
        self.assertEqual(w[0], 800e-9)
        self.assertEqual(w[1], 1580e-9)
        self.assertEqual(r[0][0], 2e-6)
        self.assertEqual(r[0][1], 10e-6)
        self.assertEqual(m[0][0][0], 1.454)

        sim.setMaterialParam(0, 0, numpy.linspace(1.445, 1.465))
        w, m, r = sim._getMinMaxParams()
        self.assertEqual(w[0], 800e-9)
        self.assertEqual(w[1], 1580e-9)
        self.assertEqual(r[0][0], 2e-6)
        self.assertEqual(r[0][1], 10e-6)
        self.assertEqual(m[0][0][0], 1.445)
        self.assertEqual(m[0][0][1], 1.465)

    def testShape(self):
        sim = Simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        self.assertEqual(sim.shape(), ())

        sim.setWavelength(numpy.linspace(800e-9, 1580e-9))
        self.assertEqual(sim.shape(), (50,))

        sim.setRadius(0, numpy.linspace(2e-6, 10e-6))
        self.assertEqual(sim.shape(), (50, 50))

        sim.setMaterialParam(0, 0, numpy.linspace(1.445, 1.465))
        self.assertEqual(sim.shape(), (50, 50, 50))

    def testSolveLP0(self):
        sim = Simulator(delta=1e-4)
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        sim.solve()

        for f in sim:
            self.assertTrue(f in sim._lpModes)
            self.assertTrue(Mode("LP", 0, 1) in sim._lpModes[f])

        sim.setVectorial(True)
        sim.solve()
        for f in sim:
            self.assertTrue(f in sim._vModes)
            self.assertTrue(Mode("HE", 1, 1) in sim._vModes[f])

    def testSolveLP1(self):
        sim = Simulator(delta=1e-3)
        sim.setWavelength(numpy.linspace(800e-9, 1580e-9))
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        sim.solve()

        for f in sim:
            self.assertTrue(f in sim._lpModes)
            self.assertTrue(Mode("LP", 0, 1) in sim._lpModes[f])

        sim.setVectorial(True)
        sim.solve()
        for f in sim:
            self.assertTrue(f in sim._vModes)
            self.assertTrue(Mode("HE", 1, 1) in sim._vModes[f])

    def testSolveLP2(self):
        sim = Simulator(delta=1e-3)
        sim.setWavelength(numpy.linspace(800e-9, 1580e-9, 10))
        sim.setRadius(0, numpy.linspace(2e-6, 10e-6, 10))
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        sim.solve()

        for f in sim:
            self.assertTrue(f in sim._lpModes)
            self.assertTrue(Mode("LP", 0, 1) in sim._lpModes[f])

        sim.setVectorial(True)
        sim.solve()
        for f in sim:
            self.assertTrue(f in sim._vModes)
            self.assertTrue(Mode("HE", 1, 1) in sim._vModes[f])

    @unittest.skip("Long test")
    def testSolveLP3(self):
        sim = Simulator(delta=1e-3)
        sim.setWavelength(numpy.linspace(800e-9, 1580e-9, 10))
        sim.setRadius(0, numpy.linspace(2e-6, 10e-6, 9))
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((numpy.linspace(1.445, 1.465, 5),), (1.444,))
        sim.solve()

        for f in sim:
            self.assertTrue(f in sim._lpModes)
            self.assertTrue(Mode("LP", 0, 1) in sim._lpModes[f])

        sim.setVectorial(True)
        sim.solve()
        for f in sim:
            self.assertTrue(f in sim._vModes)
            if Mode("HE", 1, 1) not in sim._vModes[f]:
                print(f)
            # self.assertTrue(Mode("HE", 1, 1) in sim._vModes[f])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
