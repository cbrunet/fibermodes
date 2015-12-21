# This file is part of FiberModes.
#
# FiberModes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FiberModes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FiberModes.  If not, see <http://www.gnu.org/licenses/>.

"""Solver using CUDA (Nvidia GPU)"""

from fibermodes.fiber.solver import mlsif
from fibermodes import Mode, Wavelength, ModeFamily
import numpy
import os
from itertools import cycle

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
assert pycuda.autoinit


class Neff(mlsif.Neff):

    def __init__(self, fiber):
        super().__init__(fiber)

        self.NSOLVERS = 1000  # Number of points for the solver
        self._init_gpu()

    def _init_gpu(self):
        c_src = ""
        c_path = os.path.dirname(os.path.realpath(__file__)) + "/cudasrc/"
        for cfile in ("constf.c", "hypergf.c", "ivf.c",
                      "knf.c", "besseldiff.c", "chareq.c"):
            with open(c_path+cfile) as f:
                c_src += f.read()
        cudamod = SourceModule(c_src)
        self.chareq = cudamod.get_function("chareq")
        self.chareq.prepare("PfPPIPP")

        sof = numpy.dtype(numpy.float32).itemsize
        self.gpu_neff = cuda.mem_alloc(self.NSOLVERS * sof)
        r = numpy.array(self.fiber._r, dtype=numpy.float32)
        self.gpu_r = cuda.mem_alloc(r.nbytes)
        cuda.memcpy_htod(self.gpu_r, r)
        self.gpu_n = cuda.mem_alloc(len(self.fiber) * sof)
        soi = numpy.dtype(numpy.int32).itemsize
        self.gpu_nu = cuda.mem_alloc(soi)
        self.x = numpy.empty((1, self.NSOLVERS), dtype=numpy.float32)
        self.gpu_x = cuda.mem_alloc(self.x.nbytes)

    def __call__(self, wl, mode, delta, lowbound):

        if mode.nu == 0 or mode.family is ModeFamily.LP:
            return super().__call__(wl, mode, delta, lowbound)

        wl = Wavelength(wl)
        nmin = self.fiber.minIndex(-1, wl)
        nmax = max(layer.maxIndex(wl) for layer in self.fiber.layers)
        neff = numpy.linspace(nmin, nmax, self.NSOLVERS).astype(numpy.float32)
        cuda.memcpy_htod(self.gpu_neff, neff)

        n = numpy.fromiter((layer.minIndex(wl) for layer in self.fiber.layers),
                           dtype=numpy.float32,
                           count=len(self.fiber))
        cuda.memcpy_htod(self.gpu_n, n)

        nu = numpy.array([mode.nu], dtype=numpy.int32)
        cuda.memcpy_htod(self.gpu_nu, nu)

        self.chareq.prepared_call(
            (neff.size, nu.size), (5, 4, 2),
            self.gpu_neff, numpy.float32(wl.k0), self.gpu_r,
            self.gpu_n, numpy.uint32(n.size), self.gpu_nu,
            self.gpu_x,
            shared_size=5*4*2*4)

        cuda.memcpy_dtoh(self.x, self.gpu_x)

        sols = []

        for i in range(self.NSOLVERS-1, 0, -1):
            if (abs(self.x[0, i]) > 1e5) or (abs(self.x[0, i-1]) > 1e5):
                continue
            if ((self.x[0, i-1] < 0 and self.x[0, i] > 0) or
                    (self.x[0, i-1] > 0 and self.x[0, i] < 0)):
                sols.append((neff[i-1], neff[i]))
                # sols.append(self._findBetween(
                #     self._heceq, neff[i-1], neff[i], args=(wl, mode.nu)))

        famc = cycle((ModeFamily.HE, ModeFamily.EH))
        m = 1
        for n in sols:
            fam = next(famc)
            self.fiber.set_ne_cache(wl, Mode(fam, mode.nu, m), n)
            if fam == ModeFamily.EH:
                m += 1

        try:
            return self.fiber.ne_cache[wl][mode]
        except KeyError:
            return float("nan")

if __name__ == '__main__':
    from fibermodes import FiberFactory

    f = FiberFactory()
    f.setSolvers(neff=Neff)
    f.addLayer(radius=4e-6, index=1.4489)
    f.addLayer(radius=10e-6, index=1.4474)
    f.addLayer(index=1.4444)
    fiber = f[0]
    wl = 1550e-9
    modes = fiber.findVmodes(wl)
    for mode in modes:
        print(mode, fiber.neff(mode, wl, delta=1e-5))
