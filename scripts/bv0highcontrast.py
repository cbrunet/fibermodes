
import numpy
from math import sqrt
from matplotlib import pyplot

from fibermodes.simulator import PSimulator as Simulator
from fibermodes import Wavelength, Mode, fixedFiber, ModeFamily
from fibermodes.material import Air, Silica, Fixed


COLORS = {ModeFamily.HE: 'b',
          ModeFamily.EH: 'r',
          ModeFamily.TE: 'm',
          ModeFamily.TM: 'g'}


def bFctV0(n1, n2, rho, b, V0, modes, delta):
    NA = sqrt(n1**2 - n2**2)

    pyplot.figure()
    sim = Simulator(delta=delta)

    sim.setWavelength(Wavelength(k0=(v0 / b / NA)) for v0 in V0)
    sim.setMaterials(Fixed, Fixed, Fixed)
    sim.setRadii((rho * b,), (b,))
    sim.setMaterialsParams((n2,), (n1,), (n2,))

    fiber = fixedFiber(0, [rho * b, b], [n2, n1, n2])

    for m in modes:
        neff = sim.getNeff(m)
        bnorm = (neff - n2) / (n1 - n2)

        pyplot.plot(V0, bnorm, color=COLORS[m.family], label=str(m))

        c = fiber.cutoffV0(m)
        pyplot.axvline(c, color=COLORS[m.family], ls='--')

    pyplot.xlim((0, V0[-1]))
    pyplot.title("$n_1 = {}, n_2 = {}, \\rho = {}$".format(n1, n2, rho))
    pyplot.xlabel("Normalized frequency ($V_0$)")
    pyplot.ylabel("Normalized propagation constant ($\widetilde{\\beta}$)")


if __name__ == '__main__':
    modes = (Mode("HE", 1, 1),
             Mode("TE", 0, 1),
             Mode("TM", 0, 1),
             Mode("HE", 2, 1),
             Mode("EH", 1, 1),
             Mode("HE", 3, 1),
             Mode("HE", 1, 2),
             Mode("EH", 2, 1),
             Mode("HE", 4, 1),
             Mode("TE", 0, 2),
             Mode("HE", 2, 2),
             Mode("TM", 0, 2),
             )
    V0 = numpy.linspace(0, 18, 200)[1:]

    bFctV0(n1=1.474, n2=1.444,
           rho=0.25, b=16e-6, V0=V0,
           modes=modes, delta=1e-4)

    bFctV0(n1=1.444, n2=1,
           rho=0.25, b=16e-6, V0=V0,
           modes=modes, delta=1e-3)

    pyplot.show()
