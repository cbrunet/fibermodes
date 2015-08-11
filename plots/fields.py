from fibermodes import FiberFactory, Wavelength, Mode, ModeFamily
from matplotlib import pyplot
from matplotlib.patches import Circle
import numpy
from scipy import io


def fromVDelta(V, Delta, wl):
    """To match Bures examples

    params(3.9, 0.26, wl)  # Bures 3.25

    """
    nco = numpy.sqrt(1.444**2 / (1 - Delta*2))
    rho = V / wl.k0 / numpy.sqrt(nco**2 - 1.444**2)

    f = FiberFactory()
    f.addLayer(name="core", radius=rho, index=nco)
    f.addLayer(name="cladding", index=1.444)
    fiber = f[0]
    print(fiber)
    return fiber


def SMF28():
    f = FiberFactory()
    f.addLayer(name="core", radius=4.5e-6, index=1.449)
    f.addLayer(name="cladding", radius=62.5e-6, index=1.444)
    f.addLayer(name="air", index=1)
    return f[0]


def RCF2():
    x = 0.19
    r1 = 125 * 1.4 / 180 * 1e-6
    r2 = 125 * 4 / 180 * 1e-6

    f = FiberFactory()
    f.addLayer(name="center", radius=r1, material="Silica")
    f.addLayer(name="ring", radius=r2, material="SiO2GeO2", x=x)
    f.addLayer(name="cladding", material="Silica")
    fiber = f[0]
    print(fiber)
    return fiber


def ACF():
    f = FiberFactory()
    f.addLayer(name="air", radius=9.1e-6, material="Air")
    f.addLayer(name="ring", radius=11.3e-6, material="SiO2GeO2", x=0.192)
    f.addLayer(name="trench", radius=16.2e-6, material="SiO2F", x=0.013)
    f.addLayer(name="cladding", material="Silica")
    fiber = f[0]
    print(fiber)
    return fiber


def plotFiber(ax, fiber):
    for i in range(1, len(fiber)):
        r = fiber.innerRadius(i)
        c = Circle((0, 0), radius=r*1e6,
                   linestyle='dashed', color='k', fill=False)
        ax.add_patch(c)


def plotFields(fields):
    extent = [r*1e6 for r in fields.xlim + fields.ylim]
    fig = pyplot.figure()
    for i, F in enumerate(("Ex", "Ey", "Ez",
                           "Er", "Ephi", "Ez",
                           "Et", "Epol", "Emod"), 1):
        ax = fig.add_subplot(3, 3, i)
        ax.set_title(F)
        if F in ("Et", "Emod"):
            cmap = 'Reds'
        elif F in ("Epol"):
            cmap = 'hsv'
        else:
            cmap = 'seismic'
        ax.imshow(getattr(fields, F)(), aspect='equal', extent=extent,
                  cmap=cmap)
        plotFiber(ax, fiber)


def plotExProfile(fiber, mode, wl, r=10e-6, np=101):

    def plotLayers(ax):
        for i in range(1, len(fiber)):
            ax.axvline(-fiber.innerRadius(i) * 1e6, ls="--")
            ax.axvline(fiber.innerRadius(i) * 1e6, ls="--")

    fig = pyplot.figure()
    # fields = fiber.field(mode, wl, 10e-6)
    R = numpy.linspace(-r, r, np)
    E = numpy.zeros((R.size, 3))
    H = numpy.zeros((R.size, 3))
    for i, r_ in enumerate(R):
        E[i, :], H[i, :] = fiber._rfield(mode, wl, abs(r_))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(str(mode))
    ax.set_xlabel("r (µm)")
    ax.plot(R*1e6, E[:, 0], label="Ex")
    plotLayers(ax)


def plotEHProfile(fiber, mode, wl, r=10e-6, np=101):
    def plotLayers(ax):
        for i in range(1, len(fiber)):
            ax.axvline(-fiber.innerRadius(i) * 1e6, ls="--")
            ax.axvline(fiber.innerRadius(i) * 1e6, ls="--")

    fig = pyplot.figure()
    R = numpy.linspace(-r, r, np)
    E = numpy.zeros((R.size, 3))
    H = numpy.zeros((R.size, 3))
    for i, r_ in enumerate(R):
        E[i, :], H[i, :] = fiber._rfield(mode, wl, abs(r_))
    # E
    ax = fig.add_subplot(2, 1, 1)
    ax.set_title(str(mode))
    ax.set_xlabel("r (µm)")
    ax.plot(R*1e6, E[:, 0], label="Er")
    ax.plot(R*1e6, E[:, 1], label="Ephi")
    ax.plot(R*1e6, E[:, 2], label="Ez")
    ax.legend()
    ax.set_xlim((-r*1e6, r*1e6))
    plotLayers(ax)
    # H
    ax = fig.add_subplot(2, 1, 2)
    ax.set_title(str(mode))
    ax.set_xlabel("r (µm)")
    ax.plot(R*1e6, H[:, 0], label="Hr")
    ax.plot(R*1e6, H[:, 1], label="Hphi")
    ax.plot(R*1e6, H[:, 2], label="Hz")
    ax.legend()
    ax.set_xlim((-r*1e6, r*1e6))
    plotLayers(ax)


def Alberto():
    # R = 25e-6
    R = 20e-6
    NP = 201
    wl = Wavelength(1550e-9)
    # fiber = ACF()
    fiber = RCF2()
    for i in range(len(fiber)):
        print(fiber.maxIndex(i, wl))

    modes = fiber.findVmodes(wl)
    # modes = (Mode("HE", 1, 1),)
    for mode in modes:
        if mode.family not in (ModeFamily.HE, ModeFamily.EH):
            continue
        # mode = Mode("LP", 0, 1)
        print()
        print(str(mode))
        fields = fiber.field(mode, wl, R, np=NP)

        Er = numpy.zeros(((NP-1)//2+1, 3))
        Hr = numpy.zeros(Er.shape)
        for i, r in enumerate(numpy.linspace(0, R, Er.shape[0])):
            Er[i, :], Hr[i, :] = fiber._rfield(mode, wl, r)

        mdict = {
            'name': str(mode),
            'neff': fiber.neff(mode, wl),
            'Aeff': fields.Aeff(),
            'Nm': fields.N(),
            'Im': fields.I(),
            'Er': Er,
            'Hr': Hr,
        }

        print("neff: {:.4f}".format(mdict['neff']))
        print("Aeff: {:.4f} µm²".format(mdict['Aeff'] * 1e12))
        print("Nm: {:.4g}".format(mdict['Nm']))
        print("Im: {:.4g}".format(mdict['Im']))
        print()

        io.savemat(str(mode), mdict)

        plotEHProfile(fiber, mode, wl, R, NP)
        pyplot.savefig(str(mode)+'.pdf')


def Bures328():
    fiber = SMF28()
    wl = Wavelength(1550e-9)
    mode = Mode("HE", 1, 1)

    plotEHProfile(fiber, mode, wl, np=201)

if __name__ == '__main__':
    Alberto()

    pyplot.show()
