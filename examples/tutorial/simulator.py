"""This is the examples for the third tutorial: Using Simulator."""


from fibermodes import FiberFactory, Simulator, PSimulator
import numpy
from matplotlib import pyplot


def example1():
    """Counting modes and finding cutoffs."""
    factory = FiberFactory()
    factory.addLayer(radius=10e-6, index=1.474)
    factory.addLayer()

    # Print list of modes
    sim = Simulator(factory, [1550e-9])
    modes = next(sim.modes())[0]  # modes of first wavelength of next fiber
    print(", ".join(str(mode) for mode in sorted(modes)))
    print()

    # Print cutoff (as V number)
    cutoffs = next(sim.cutoff())[0]  # first wavelength of next fiber
    for mode, co in cutoffs.items():
        print(str(mode), co)
    print()

    # Print cutoff (as wavelength)
    cutoffswl = next(sim.cutoffWl())[0]  # first wavelength of next fiber
    for mode, co in cutoffswl.items():
        print(str(mode), str(co))
    print()


def example2():
    """Plotting neff as function of the wavelength"""
    wavelengths = numpy.linspace(1530e-9, 1580e-9, 11)
    factory = FiberFactory()
    factory.addLayer(radius=4e-6, index=1.474)
    factory.addLayer()

    sim = Simulator(factory, wavelengths, delta=1e-5)
    neffiter = sim.neff()
    neffs = next(neffiter)

    for mode in next(sim.modes())[0]:
        neff = []
        for neffwl in neffs:  # for each wavelength
            try:
                neff.append(neffwl[mode])
            except KeyError:  # mode not supported
                neff.append(float("nan"))
        neffma = numpy.ma.masked_invalid(neff)  # mask "nan"
        pyplot.plot(wavelengths*1e9, neffma, label=str(mode))
    pyplot.title("neff as function of wavelength")
    pyplot.xlabel("wavelength (nm)")
    pyplot.ylabel("effective index")
    pyplot.legend()
    pyplot.show()


def example3():
    """Plotting modal map"""
    r2 = 10e-6
    rho = numpy.linspace(0, 0.95)
    r1 = r2 * rho
    Vlim = (2, 6)  # interval where to plot V

    factory = FiberFactory()
    factory.addLayer(radius=r1, index=1.444)
    factory.addLayer(radius=r2, index=1.474)
    factory.addLayer(index=1.444)

    sim = PSimulator(factory, [1550e-9], vectorial=False, scalar=True,
                     numax=6, mmax=2)

    modes = set()
    for ml in sim.modes():
        modes |= ml[0]
    CO = list(sim.cutoff())

    for mode in sorted(modes):
        vco = numpy.fromiter((co[0][mode] if mode in co[0] else float("nan")
                              for co in CO),
                             dtype=float, count=rho.size)
        vco = numpy.ma.masked_invalid(vco)
        if vco.min() < Vlim[1] and vco.max() > Vlim[0]:
            pyplot.plot(vco, rho, label=str(mode))

    pyplot.title("Modal map")
    pyplot.xlabel("V number")
    pyplot.ylabel("r1 / r2")
    pyplot.xlim(Vlim)
    pyplot.ylim((0, 1))
    pyplot.show()

if __name__ == '__main__':
    # example1()
    # example2()
    example3()
