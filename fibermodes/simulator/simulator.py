"""The simulator allows to link fibers with wavelengths, to simulate
an array of parameters.

"""

from itertools import repeat, product
from functools import lru_cache
from fibermodes import FiberFactory, Wavelength
from fibermodes.slrc import SLRC


class Simulator(object):

    """Simulator class."""

    def __init__(self, factory=None, wavelengths=None,
                 numax=None, mmax=None, vectorial=True, scalar=False,
                 delta=1e-6):
        self._fibers = None
        self._wavelengths = None

        self.numax = numax
        self.mmax = mmax
        self.vectorial = vectorial
        self.scalar = scalar
        self.delta = delta

        self.set_factory(factory)
        if wavelengths:
            self.set_wavelengths(wavelengths)

    def set_wavelengths(self, value):
        self._wavelengths = tuple(Wavelength(w) for w in iter(SLRC(value)))

    def set_factory(self, factory):
        if isinstance(factory, str):
            factory = FiberFactory(factory)
        self.factory = factory
        if factory is not None:
            self._fibers = tuple(iter(factory))

    @property
    def fibers(self):
        if self._fibers is None:
            raise ValueError("Object not initialized. You must call "
                             "set_factory first.")
        return self._fibers

    @property
    def wavelengths(self):
        if self._wavelengths is None:
            raise ValueError("Object not initialized. You must call "
                             "set_wavelengths first.")
        return self._wavelengths

    @property
    def initialized(self):
        return not (self._fibers is None or self.factory is None)

    def _idx_iter(self, fidx, wlidx):
        if wlidx is None:
            wlidx = range(len(self.wavelengths))
        if isinstance(fidx, int):
            if isinstance(wlidx, int):
                yield (fidx, wlidx)
            else:
                yield from zip(repeat(fidx), wlidx)
        else:
            if fidx is None:
                fidx = range(len(self.fibers))
            if isinstance(wlidx, int):
                yield from zip(fidx, repeat(wlidx))
            else:
                yield from product(fidx, wlidx)

    def _apply(self, fct, fidx, wlidx):
        if isinstance(fidx, int) and isinstance(wlidx, int):
            return fct((fidx, wlidx))
        return map(fct, self._idx_iter(fidx, wlidx))

    def _apply_cutoff_to_modes(self, fct, idx):
        modes = self._modes(idx)
        return {mode: fct(mode) for mode in modes}

    def _apply_to_modes(self, fct, idx):
        modes = self._modes(idx)
        wl = self.wavelengths[idx[1]]
        return {mode: fct(mode, wl, delta=self.delta) for mode in modes}

    @lru_cache()
    def _modes(self, arg):
        fidx, wlidx = arg
        modes = set()
        if self.vectorial:
            modes |= self.fibers[fidx].findVmodes(
                self.wavelengths[wlidx], self.numax, self.mmax)
        if self.scalar:
            modes |= self.fibers[fidx].findLPmodes(
                self.wavelengths[wlidx], self.numax, self.mmax)
        return modes

    def modes(self, fidx=None, wlidx=None):
        return self._apply(self._modes, fidx, wlidx)

    def _cutoff(self, arg):
        return self._apply_cutoff_to_modes(self.fibers[arg[0]].cutoff, arg)

    def cutoff(self, fidx=None, wlidx=None):
        return self._apply(self._cutoff, fidx, wlidx)

    def _cutoffWl(self, arg):
        return self._apply_cutoff_to_modes(self.fibers[arg[0]].cutoffWl, arg)

    def cutoffWl(self, fidx=None, wlidx=None):
        return self._apply(self._cutoffWl, fidx, wlidx)

    def _neff(self, arg):
        return self._apply_to_modes(self.fibers[arg[0]].neff, arg)

    def neff(self, fidx=None, wlidx=None):
        return self._apply(self._neff, fidx, wlidx)

    def _ng(self, arg):
        return self._apply_to_modes(self.fibers[arg[0]].ng, arg)

    def ng(self, fidx=None, wlidx=None):
        return self._apply(self._ng, fidx, wlidx)

    def _D(self, arg):
        return self._apply_to_modes(self.fibers[arg[0]].D, arg)

    def D(self, fidx=None, wlidx=None):
        return self._apply(self._D, fidx, wlidx)

    def _S(self, arg):
        return self._apply_to_modes(self.fibers[arg[0]].S, arg)

    def S(self, fidx=None, wlidx=None):
        return self._apply(self._S, fidx, wlidx)
