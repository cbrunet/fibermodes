"""Unittest for Simulator class."""

import unittest
from fibermodes import Simulator, fixedFiber, Mode, Wavelength
from fibermodes.material import Fixed, Silica, SiO2GeO2
import numpy
from operator import mul
from math import sqrt


class TestSimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = Simulator

    def testLenEmpty(self):
        sim = self.simulator()
        self.assertEqual(len(sim), 0)

    def testLenOne(self):
        sim = self.simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        self.assertEqual(len(sim), 1)

    def testLenOneDim(self):
        sim = self.simulator()
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
        sim = self.simulator()
        sim.setRadii((2e-6, 3e-6, 4e-6), [5e-6, 10e-6])  # 3 * 2 = 6
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((numpy.linspace(1.444, 1.474, 10),),
                               (numpy.arange(1.444, 1.484, 0.01),))  # 10 * 5
        sim.setWavelength(numpy.linspace(800e-9, 1550e-9, 100))  # 100
        self.assertEqual(len(sim), 30000)

    def testIterEmpty(self):
        sim = self.simulator()
        fibers = list(sim)
        self.assertEqual(len(fibers), 0)

    def testIterOne(self):
        sim = self.simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6, 10e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.474,), (1.444,))
        fiber = list(sim)
        self.assertEqual(len(fiber), 1)

        fiber2 = fixedFiber(1550e-9, (4e-6,), (1.474, 1.444))
        self.assertEqual(fiber[0], fiber2)

    def testConstraints(self):
        n = numpy.linspace(1.4, 1.6)
        sim = self.simulator()
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
                          lambda x, y: abs(x - y + 0.2 / 49) < 1e-5,
                          ('material', 0, 0),
                          ('material', 1, 0))
        self.assertEqual(len(sim), 49)

    def testFctParam(self):
        r = numpy.linspace(4e-6, 10e-6)
        sim = self.simulator()
        sim.setWavelength(1550e-9)
        sim.setRadius(1, r)
        sim.setRadiusFct(0, lambda x: .25*x, ('radius', 1))
        sim.setMaterials(Fixed, Fixed, Fixed)
        sim.setMaterialsParams((1.444,), (1.474,), (1.444,))
        radii = numpy.fromiter((f._r[0] for f in sim), numpy.float, len(sim))
        self.assertTrue(numpy.all(radii == .25 * r))
        self.assertEqual(len(sim), sum(1 for _ in sim))

    def testGetDimensions(self):
        sim = self.simulator()
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

    def testGetWavelength(self):
        sim = self.simulator()
        sim.setWavelength(1550e-9)
        sim.setRadii(4e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.454,), (1.444,))
        d = sim.getWavelength()
        self.assertEqual(d.shape, (1,))

        sim.setWavelength(numpy.linspace(800e-9, 1580e-9, 50))
        d = sim.getWavelength()
        self.assertEqual(d.shape, (50,))

        sim.setRadius(0, numpy.linspace(2e-6, 10e-6, 50))
        d = sim.getWavelength()
        self.assertEqual(d.shape, (50, 50))

        sim.setMaterialParam(0, 0, numpy.linspace(1.445, 1.465, 50))
        d = sim.getWavelength()
        self.assertEqual(d.shape, (50, 50, 50))

    def testGetV0(self):
        rho = 0.35
        dn = 0.03
        phiclad = numpy.array([110, 125, 140, 160, 180])
        a = 1.4 * phiclad / phiclad[-1]
        b = a / rho
        wl = Wavelength(1550e-9)
        n2 = Silica.n(wl)
        n1 = n2 + dn
        X = SiO2GeO2.xFromN(wl, n1)

        sim = self.simulator(delta=1e-4)
        sim.setWavelength(wl)
        sim.setMaterials(Silica, SiO2GeO2, Silica)
        sim.setRadius(1, b * 1e-6)
        sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
        sim.setMaterialParam(1, 0, X)

        V0t = wl.k0 * b * 1e-6 * sqrt(n1*n1 - n2*n2)
        V0s = sim.getV0()

        self.assertEqual(V0t.size, V0s.size)
        for va, vb in zip(V0t, V0s):
            self.assertAlmostEqual(va, vb)

    def testShape(self):
        sim = self.simulator()
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
        wl = Wavelength(1550e-9)

        sim = self.simulator(delta=1e-4)
        sim.setWavelength(wl)
        sim.setRadii(4.5e-6)
        sim.setMaterials(Fixed, Fixed)
        sim.setMaterialsParams((1.448918,), (1.444418,))

        modes = sim.findLPModes()
        self.assertEqual(len(modes), 1)
        self.assertTrue(Mode("LP", 0, 1) in modes)

        neff = sim.getNeff(modes[0])
        self.assertAlmostEqual(neff, 1.4464045, places=5)

        beta = sim.getBeta(modes[0])
        self.assertAlmostEqual(float(beta), neff * wl.k0)

        modes = sim.findVModes()
        self.assertEqual(len(modes), 1)
        self.assertTrue(Mode("HE", 1, 1) in modes)

    def testResultArrayOrder(self):
        """Test the order of the resulting array when there are many dimensions

        """
        rho = 0.35
        phiclad = numpy.array([110, 125, 140, 160, 180])
        a = 1.4 * phiclad / phiclad[-1]
        b = a / rho
        wl = numpy.linspace(800e-9, 1600e-9, 9)

        sim = self.simulator(delta=1e-3)
        sim.setWavelength(wl)
        sim.setMaterials(Silica, SiO2GeO2, Silica)
        sim.setRadius(1, b * 1e-6)
        sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
        sim.setMaterialParam(1, 0, 0.19)

        neff = sim.getNeff(Mode("HE", 1, 1))

        for fiber in range(5):
            if fiber:
                for w in range(9):
                    self.assertLess(neff[w, fiber-1], neff[w, fiber])
            for w in range(1, 9):
                self.assertLess(neff[w, fiber], neff[w-1, fiber])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
