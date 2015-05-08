
from . import geometry
from . import solver
from math import sqrt, isnan
from fibermodes import Wavelength, Mode, ModeFamily
from fibermodes import constants
from itertools import count
import warnings
import logging


class MaxIterationsReachedWarning(UserWarning):

    """

    """
    pass


class Fiber(object):

    logger = logging.getLogger(__name__)

    def __init__(self, r, f, fp, m, mp, names):

        self._r = r
        self._names = names

        self.layers = []
        for f_, fp_, m_, mp_ in zip(f, fp, m, mp):
            layer = geometry.__dict__[f_](*fp_, m=m_, mp=mp_)
            self.layers.append(layer)

        self._solver = self._findSolver()

    def __len__(self):
        return len(self.layers)

    def name(self, layer):
        return self._names[layer]

    def _layer(self, r):
        for i, r_ in enumerate(self._r):
            if r < r_:
                return self.layers[i]
        return self.layers[-1]

    def innerRadius(self, layer):
        if layer < 0:
            layer = len(self._r) + layer + 1
        return self._r[layer-1] if layer else 0

    def outerRadius(self, layer):
        return self._r[layer] if layer < len(self._r) else float("inf")

    def thickness(self, layer):
        return self.outerRadius(layer) - self.innerRadius(layer)

    def index(self, r, wl):
        return self._layer(r).index(r, wl)

    def minIndex(self, layer, wl):
        return self.layers[layer].minIndex(wl)

    def maxIndex(self, layer, wl):
        return self.layers[layer].maxIndex(wl)

    def _findSolver(self):
        if all(isinstance(layer, geometry.StepIndex)
               for layer in self.layers):
            nlayers = len(self)
            if nlayers == 2:
                return solver.SSIFSolver(self)
            elif nlayers == 3:
                return solver.TLSIFSolver(self)
        return solver.FiberSolver(self)

    def setSolver(self, solver=None):
        if solver:
            self._solver = solver(self)
        else:
            self._solver = self._findSolver()

    def NA(self, wl):
        n1 = max(layer.maxIndex(wl) for layer in self.layers)
        n2 = self.minIndex(-1, wl)
        return sqrt(n1*n1 - n2*n2)

    def V0(self, wl):
        return Wavelength(wl).k0 * self.innerRadius(-1) * self.NA(wl)

    def toWl(self, V0, maxiter=50, tol=1e-15):
        """Convert V0 number to wavelength.

        An iterative method is used, since the index can be wavelength
        dependant.

        """
        if V0 == 0:
            return float("inf")

        b = self.innerRadius(-1)
        wl0 = 1.55e-6

        for i in range(maxiter):
            wl = constants.tpi / V0 * b * self.NA(wl0)
            if abs(wl - wl0) < tol:
                break
            wl0 = wl
        else:
            warnings.war(("Max number of iterations reached while converting "
                          "V0 to wavelength."), MaxIterationsReachedWarning)

        self.logger.info('toWl converged in {} iterations'.format(i))
        return Wavelength(wl)

    def cutoff(self, mode):
        return self._solver.cutoff(mode)

    def neff(self, mode, wl, delta=1e-6):
        return self._solver.neff(wl, mode, delta)

    def beta(self, mode, wl, p=0):
        return self._solver.beta(wl, mode)

    def b(self, mode, wl):
        """Normalized propagation constant"""
        neff = self._solver.neff(wl, mode)
        nmax = max(layer.maxIndex(wl) for layer in self.layers)
        ncl = self.minIndex(-1, wl)
        ncl2 = ncl*ncl
        return (neff*neff - ncl2) / (nmax*nmax - ncl2)

    def ng(self, mode, wl):
        return self._solver.beta(mode, wl, 1) * constants.c

    def D(self, mode, wl):
        return -(self._solver.beta(mode, wl, 2) *
                 constants.tpi * constants.c * 1e6 / (wl * wl))

    def S(self, mode, wl):
        return (self._solver.beta(mode, wl, 3) *
                (constants.tpi * constants.c / (wl * wl))**2 * 1e-3)

    def findVmodes(self, wl, numax=None, mmax=None):
        families = (ModeFamily.HE, ModeFamily.EH, ModeFamily.TE, ModeFamily.TM)
        return self.findModes(families, wl, numax, mmax)

    def findLPmodes(self, wl, ellmax=None, mmax=None):
        families = (ModeFamily.LP,)
        return self.findModes(families, wl, ellmax, mmax)

    def findModes(self, families, wl, numax=None, mmax=None):
        modes = set()
        v0 = self.V0(wl)
        for fam in families:
            for nu in count(0):
                if (fam is ModeFamily.TE or fam is ModeFamily.TM) and nu > 0:
                    break
                if (fam is ModeFamily.HE or fam is ModeFamily.EH) and nu == 0:
                    continue
                for m in count(1):
                    mode = Mode(fam, nu, m)
                    try:
                        co = self.cutoff(mode)
                        if co > v0:
                            break
                    except NotImplementedError:
                        neff = self.neff(mode, wl)
                        if isnan(neff):
                            break
                    modes.add(mode)
                if m == 1:
                    break
        return modes
