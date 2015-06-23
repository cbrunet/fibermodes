
from fibermodes import FiberFactory, Wavelength, Mode


def main():
    wl = Wavelength(1550e-9)

    ff1 = FiberFactory()
    ff1.addLayer(name="core", radius=8e-6, material="Fixed",
                 geometry="StepIndex", index=1.454)
    ff1.addLayer(name="cladding", index=1.444)

    fiber1 = ff1[0]
    neff1 = fiber1.neff(Mode("HE", 1, 1), wl)
    print(neff1)

    ff2 = FiberFactory()
    ff2.addLayer(name="core", radius=8e-6, material="Fixed",
                 geometry="SuperGaussian", tparams=[0, 2e-6, 1],
                 index=1.454)
    ff2.addLayer(name="cladding", index=1.444)

    fiber2 = ff2[0]
    neff2 = fiber2.neff(Mode("HE", 1, 1), wl, lowbound=neff1)
    print(neff2)


if __name__ == '__main__':
    main()
