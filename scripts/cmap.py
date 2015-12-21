
from matplotlib import pyplot
import numpy

from fibermodes import Wavelength, Mode, ModeFamily, HE11
from fibermodes.material import Silica, SiO2GeO2
from fibermodes.fiber.ssif import SSIF
from fibermodes.simulator import PSimulator as Simulator
from fibermodes import constants


MODES = [
    HE11,
    Mode(ModeFamily.TE, 0, 1),
    Mode(ModeFamily.HE, 2, 1),
    Mode(ModeFamily.TM, 0, 1),
    Mode(ModeFamily.EH, 1, 1),
    Mode(ModeFamily.HE, 3, 1),
    Mode(ModeFamily.HE, 1, 2),
    ]


def plotCMap(dn):
    V0 = numpy.linspace(2, 5, 50)
    rho = numpy.linspace(0, 1, 50)
    wl = Wavelength(1550e-9)
    n1 = Silica.n(wl)
    n2 = n1 + dn
    X = SiO2GeO2.xFromN(wl, n2)
    b = 6e-6
    a = b * rho

    sim = Simulator(delta=1e-4)
    sim.setWavelength(wl)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setMaterialParam(1, 0, X)
    sim.setRadii(a, (b, ))

    ssif = SSIF(wl, (SiO2GeO2, b, X), (Silica, b))

    cutoffs = {}
    for m in MODES[1:]:
        cutoffs[m] = []
        for i, fiber in enumerate(iter(sim)):
            if i == 0:
                cutoffs[m].append(ssif.cutoffV0(m, 2))
            else:
                if cutoffs[m][i-1] > V0[-1]:
                    cutoffs[m].append(cutoffs[m][i-1])
                else:
                    cutoffs[m].append(fiber.cutoffV0(m, 2))
        pyplot.plot(cutoffs[m], rho, label=str(m))

    wl = constants.tpi * b * ssif.na / V0
    sim.setWavelength(wl)

    neff = {}
    for m in MODES:
        neff[m] = numpy.zeros((rho.size, V0.size))
        for i, r in enumerate(rho):
            if i == 0:
                sim.setMaterials(SiO2GeO2, Silica)
                sim.setMaterialParam(0, 0, X)
                sim.setRadius(0, b)
            else:
                sim.setMaterials(Silica, SiO2GeO2, Silica)
                sim.setMaterialParam(1, 0, X)
                sim.setRadii((a[i], ), (b, ))
            if m in cutoffs and cutoffs[m][i] > V0[-1]:
                continue
            neff[m][i, :] = sim.getNeff(m)

    dneff = numpy.zeros((rho.size, V0.size))
    for i, r in enumerate(rho):
        for j, v in enumerate(V0):
            n = []
            mm = []
            for m in MODES:
                if m in cutoffs and cutoffs[m][i] > v:
                    continue
                if neff[m][i, j]:
                    n.append(neff[m][i, j])
                    mm.append(m)
            if len(n) > 1:
                n = numpy.array(n)
                n.sort()
                dneff[i, j] = min(n[1:] - n[:-1])

    numpy.save('dneff', dneff)

    dneff = numpy.ma.masked_greater(dneff, 1e-3)
    pyplot.imshow(dneff, aspect='auto', extent=(V0[0], V0[-1], 1, 0))

    pyplot.title("$\Delta n = {}$".format(dn))
    pyplot.xlim((V0[0], V0[-1]))
    pyplot.ylim((0, 1))
    pyplot.colorbar()

if __name__ == '__main__':
    plotCMap(0.05)
    pyplot.legend()
    pyplot.show()
