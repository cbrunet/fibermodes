
from fibermodes import Mode, ModeFamily
from fibermodes.material import Fixed
from fibermodes.simulator import PSimulator as Simulator
import numpy
from numpy import ma
from matplotlib import pyplot
from math import sqrt


C = ['b', 'g', 'r', 'm', 'c', 'y', 'k']

FIRSTMODES = (
              Mode(ModeFamily.TE, 0, 1),
              Mode(ModeFamily.HE, 2, 1),
              Mode(ModeFamily.TM, 0, 1),
              Mode(ModeFamily.EH, 1, 1),
              Mode(ModeFamily.HE, 3, 1),
              Mode(ModeFamily.HE, 1, 2),
              # Mode(ModeFamily.HE, 2, 2),
              # Mode(ModeFamily.HE, 1, 3),
              )

MOREMODES = FIRSTMODES + (
                          Mode(ModeFamily.EH, 2, 1),
                          Mode(ModeFamily.HE, 4, 1),
                          Mode(ModeFamily.EH, 3, 1),
                          Mode(ModeFamily.HE, 5, 1),
                          Mode(ModeFamily.EH, 4, 1),
                          Mode(ModeFamily.HE, 6, 1),
                          Mode(ModeFamily.EH, 5, 1),
                          Mode(ModeFamily.HE, 7, 1),
                          Mode(ModeFamily.TE, 0, 2),
                          Mode(ModeFamily.HE, 2, 2),
                          Mode(ModeFamily.TM, 0, 2),
                          Mode(ModeFamily.EH, 1, 2),
                          Mode(ModeFamily.HE, 3, 2),
                          Mode(ModeFamily.HE, 1, 3),
                          Mode(ModeFamily.TE, 0, 3),
                          Mode(ModeFamily.HE, 2, 3),
                          Mode(ModeFamily.TM, 0, 3),
                          Mode(ModeFamily.EH, 1, 3),
                          Mode(ModeFamily.HE, 3, 3),
                          )

HEMODES = (
           Mode(ModeFamily.HE, 2, 1),
           Mode(ModeFamily.HE, 3, 1),
           Mode(ModeFamily.HE, 4, 1),
           Mode(ModeFamily.HE, 1, 2),
           Mode(ModeFamily.HE, 2, 2),
           Mode(ModeFamily.HE, 3, 2),
           Mode(ModeFamily.HE, 1, 3),
           Mode(ModeFamily.HE, 2, 3),
           Mode(ModeFamily.HE, 3, 3),
           )

EHMODES = (Mode(ModeFamily.EH, 1, 1),
           Mode(ModeFamily.EH, 1, 2),
           Mode(ModeFamily.EH, 1, 3),
           Mode(ModeFamily.EH, 2, 1),
           Mode(ModeFamily.EH, 2, 2),
           Mode(ModeFamily.EH, 3, 1),
           )


def maskoutsiders(a, minimum=True):
    if minimum:
        mask = a > numpy.minimum.accumulate(a)
    else:
        mask = a < numpy.maximum.accumulate(a)
    return ma.masked_array(a, mask=mask)


def covsn(N, R, MODES, vp=0, rna=None, ax=[], xlim=None, mask=True, leg=True):
    sim = Simulator()
    sim.setWavelength(1550e-9)
    sim.setRadii(R[0], R[1])
    sim.setMaterials(Fixed, Fixed, Fixed)
    sim.setMaterialsParams((N[0],), (N[1],), (N[2],))
    if rna:
        sim.setV0Param(R[rna[0]] * sqrt(N[rna[1]][0]**2 - N[2]**2))

    NR = len(N[1-vp])

    pyplot.figure()

    for j, mode in enumerate(MODES):
        co = [[] for i in range(NR)]
        for i, fiber in enumerate(iter(sim)):
            co[i % NR].append(sim.getCutoffV0(fiber, mode))
        for i in range(NR):
            c = maskoutsiders(co[i]) if mask else co[i]
            if i == 0:
                pyplot.plot(c, N[vp], label=str(mode), color=C[j % 7])
            else:
                pyplot.plot(c, N[vp], color=C[j % 7])

        for a in ax:
            pyplot.axhline(a, ls='--', color='k')

    pyplot.xlabel("Normalized frequency ($V_0$)")
    pyplot.ylabel("Index of {} layer ($n_{}$)".format(
                  'middle' if vp else 'center', 1 + vp))
    if xlim:
        pyplot.xlim(xlim)
    pyplot.ylim((N[vp][0], N[vp][-1]))
    if leg:
        pyplot.legend()


def varcenter(MODES, xlim=None, leg=True):
    n1 = numpy.linspace(1.2, 1.8, 121)
    n2 = [1.6]

    covsn([n1, n2, 1.4], [4e-6, 5e-6], MODES,
          vp=0, rna=(1, 1), ax=[1.4, 1.6], xlim=xlim, mask=True, leg=leg)


def varboth(MODES):
    n1 = numpy.linspace(1.2, 1.6, 161)
    n2 = numpy.linspace(1.6, 1.8, 5)

    covsn([n1, n2, 1.4], [4e-6, 5e-6], MODES,
          vp=0, ax=[1.4, 1.6], mask=True, leg=True)


def varring(MODES):
    n1 = [1.6]
    n2 = numpy.linspace(1.2, 1.8, 121)

    covsn([n1, n2, 1.4], [4e-6, 5e-6], MODES,
          vp=1, rna=(0, 0), ax=[1.4, 1.6], xlim=(1.5, 5), mask=True, leg=True)


if __name__ == '__main__':
    # varcenter(FIRSTMODES, xlim=(1.5, 7))
    # varring(FIRSTMODES)
    varcenter(MOREMODES, leg=False)
    # varboth(HEMODES)
    pyplot.show()
