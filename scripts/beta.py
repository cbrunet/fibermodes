
from fibermodes import Wavelength, Mode, constants
from fibermodes.material import Silica, SiO2GeO2, Fixed
from fibermodes.simulator import PSimulator as Simulator
import numpy


def println(*args):
    for x in args:
        print(x)
    print()

wl = Wavelength(1550e-9)
epsilon = 1e-12

sim = Simulator(delta=1e-4, epsilon=epsilon)
sim.setWavelength(wl)
sim.setMaterials(Silica, SiO2GeO2, Silica)
sim.setRadii(2e-6, 8e-6)
sim.setMaterialParam(1, 0, .2)

mode = Mode("HE", 1, 1)

neff = sim.getNeff(mode)
beta = sim.getBeta(mode, 0)

println("neff", neff)
println("beta", wl.k0 * neff, beta)

wl = [wl + i * epsilon for i in range(-2, 3)]
sim.setWavelength(wl)

neff = sim.getNeff(mode)
print(neff)

dn1 = (neff[3] - neff[1]) / (2 * epsilon)
dn2 = (neff[0] - neff[4] + 8 * neff[3] - 8 * neff[1]) / (12 * epsilon)
println("dn/dl", dn1, dn2)

ng = neff[2] - wl[2] * dn2
println("Ng", ng, sim.getNg(mode)[2])

beta1 = ng / constants.c
println("beta1", beta1, sim.getBeta(mode, 1)[2])

println(sim.getD(mode)[2])
println(sim.getS(mode)[2])
