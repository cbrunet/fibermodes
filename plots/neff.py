
from fibermodes import Wavelength, Mode, constants
from fibermodes.material import Silica, SiO2GeO2, Fixed
from fibermodes.simulator import PSimulator as Simulator
import numpy
from matplotlib import pyplot


wl = numpy.linspace(800e-9, 1800e-9, 200)
print(wl[1] - wl[0])

sim = Simulator(delta=1e-4, epsilon=1e-12)
sim.setWavelength(wl)
sim.setMaterials(SiO2GeO2, Silica)
sim.setMaterialParam(0, 0, 0.05)
sim.setRadii(4.5e-6)

modes = sim.findVModes()
#modes = [Mode('HE', 1, 2)]

### Neff ###
pyplot.figure()
pyplot.subplot(221)
pyplot.title("Neff")
for m in modes:
    pyplot.plot(wl*1e6, sim.getNeff(m), '-', label=str(m))
n1 = sim.getIndex(0)
n2 = sim.getIndex(1)
pyplot.plot(wl*1e6, n1, ls='--', label="Core")
pyplot.plot(wl*1e6, n2, ls='--', label="Cladding")
pyplot.legend()

### Ng ###
pyplot.subplot(222)
pyplot.title("Ng")
for m in modes:
    pyplot.plot(wl*1e6, sim.getNg(m), '-', label=str(m))

### D ###
pyplot.subplot(223)
pyplot.title("D")
for m in modes:
    pyplot.plot(wl*1e6, sim.getD(m), '-', label=str(m))

### S ###
pyplot.subplot(224)
pyplot.title("S")
for m in modes:
    pyplot.plot(wl*1e6, sim.getS(m), '-', label=str(m))

### Beta0 ###
pyplot.figure()
pyplot.subplot(221)
pyplot.title("Beta0")
for m in modes:
    pyplot.plot(wl*1e6, sim.getBeta(m, 0), '-', label=str(m))
pyplot.legend()

### Beta1 ###
pyplot.subplot(222)
pyplot.title("Beta1")
for m in modes:
    pyplot.plot(wl*1e6, sim.getBeta(m, 1), '-', label=str(m))

### Beta2 ###
pyplot.subplot(223)
pyplot.title("Beta2")
for m in modes:
    pyplot.plot(wl*1e6, sim.getBeta(m, 2), '-', label=str(m))

### Beta3 ###
pyplot.subplot(224)
pyplot.title("Beta3")
for m in modes:
    pyplot.plot(wl*1e6, sim.getBeta(m, 3), '-', label=str(m))

pyplot.show()
