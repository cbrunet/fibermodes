from fibermodes import Wavelength, FiberFactory
from fibermodes.simulator import PSimulator
from fibermodes.simulator import Simulator
from scipy.optimize import minimize
from itertools import product
import numpy
import time
import logging
import pickle
from multiprocessing import TimeoutError
from tofcommon import r1, r2, X
import sys


wl = Wavelength(1550e-9)

ff = FiberFactory()
ff.addLayer(name="center", radius=r1, material="Silica")
ff.addLayer(name="ring", radius="return r[0] / 0.35",
            material="SiO2GeO2", x=X)
# ff.addLayer(name="ring", radius=r2,
            # material="SiO2GeO2", index=1.474, wl=wl)
ff.addLayer(name="cladding", material="Silica")

# sim = PSimulator(factory=ff, wavelengths=wl, delta=1e-5)
sim = PSimulator(factory=ff, wavelengths=wl, delta=1e-3)


def deltangs(sim, fnum):
    ng = sorted([ng.get() for ng in sim.ng(fnum, 0).values()])
    dng = [(ng[i] - ng[0])*1e3 for i in range(1, len(ng))]
    return dng


def optimf(params, target):
    # print(params)
    r1, rho, x = params
    r1 *= 1e-6
    r2 = r1 / rho
    ff = FiberFactory()
    ff.addLayer(name="center", radius=r1, material="Silica")
    ff.addLayer(name="ring", radius=r2, material="SiO2GeO2", x=x)
    ff.addLayer(name="cladding", material="Silica")
    sim = PSimulator(factory=ff, wavelengths=wl, delta=1e-3)
    dng = deltangs(sim, 0)
    sim.stop_thread(True)
    if len(dng) != len(target):
        r = 100
        # return float("inf")
    else:
        r = sum((n1 - n2)**2 for (n1, n2) in zip(dng, target)) * 10
    print(params, dng, r)
    return r


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    start = time.perf_counter()

    ng = sim.ng()
    ngm = [[None for _ in X] for _ in r1]
    q = []
    for i, j in product(range(r1.size), range(X.size)):
        ngm[i][j] = []
        for n in next(ng)[0].values():
            # try:
            #     ngm[i][j].append(n.get(1))
            # except TimeoutError:
            #     q.append((i, j, n))
            ngm[i][j].append(n)
        print((i, j), len(ngm[i][j]), end=", ")
        sys.stdout.flush()

    # for i, j, n in q:
    #     ngm[i][j].append(n.get())

    # with open("tofoptim.data", "wb") as f:
    #     pickle.dump(ngm, f)

    # x0 = numpy.array([r1[2]*1e6, 0.35, 0.2])
    # res = minimize(optimf, x0, args=(RCF3,),
    #                bounds=((0.5, 1.5), (0.30, 0.40), (0.17, 0.22)),
    #                callback=print,
    #                options={'disp': True})
    # print(res)

    # sim.stop_thread(True)
    elapsed = time.perf_counter() - start
    print("{:.3f} sec".format(elapsed))
