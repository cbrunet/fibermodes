
from fibermodes import Wavelength, FiberFactory
from math import sqrt


def main():
    delta = 0.3
    V = 5

    wl = Wavelength(1.55e-6)
    n2 = 1.444

    n1 = sqrt(n2**2 / (1 - 2 * delta))
    rho = V / (sqrt(n1**2 - n2**2) * wl.k0)

    f = FiberFactory()
    f.addLayer(radius=rho, index=n1)
    f.addLayer(index=n2)
    fiber = f[0]
    modes = fiber.findVmodes(wl)

    for m in modes:
        neff = fiber.neff(m, wl, delta=1e-5)

if __name__ == '__main__':
    main()
