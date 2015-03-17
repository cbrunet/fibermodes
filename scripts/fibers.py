
from fibermodes.material import Silica, SiO2GeO2
from fibermodes.simulator import PSimulator as Simulator
from fibermodes import constants
import numpy


class RCFiber(object):
    wavelength = 1550e-9
    ra = 1.4 / 180  # ratio coeur / gaine
    rho = 0.35  # ratio coeur int / ext
    dn = 0.03

    def __init__(self, name, phiclad, length, delta=1e-4):
        self.name = name
        self.phiclad = phiclad * 1e-6
        self.length = length
        self.delta = delta

        self._a = self.ra * self.phiclad
        self._b = self._a / self.rho

        n2 = Silica.n(self.wavelength)
        n1 = n2 + self.dn
        self.X = SiO2GeO2.xFromN(self.wavelength, n1)

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self._a = value
        self.rho = self._a / self._b
        self.ra = self._a / self.phiclad

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = value
        self.rho = self._a / self._b

    def getSimulator(self):
        sim = Simulator(delta=self.delta)
        sim.setWavelength(self.wavelength)
        sim.setMaterials(Silica, SiO2GeO2, Silica)
        sim.setMaterialParam(1, 0, (self.X, ))
        sim.setRadii((self._a, ), (self._b, ))
        return sim

    def getNg(self, sim=None, modes=None):
        if sim is None:
            sim = self.getSimulator()
        if modes is None:
            modes = sim.findVModes()

        return numpy.array([sim.getNg(m) for m in modes])

    def getDTg(self, sim=None, modes=None):
        ng = self.getNg(sim, modes)
        tg = ng * self.length / constants.c
        # tg0 = min(tg)
        return tg - tg[0]


RCF1 = RCFiber("RCF1", 110, 1500)
RCF2 = RCFiber("RCF2", 125, 1580)
RCF3 = RCFiber("RCF3", 140, 1500)
RCF4 = RCFiber("RCF4", 160, 1130)
RCF5 = RCFiber("RCF5", 180, 1170)

fibers = [RCF1, RCF2, RCF3, RCF4, RCF5]
