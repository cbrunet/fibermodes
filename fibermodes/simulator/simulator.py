"""The simulator allows to link fibers with wavelengths, to simulate
an array of parameters.

"""

from itertools import starmap, repeat
from fibermodes import FiberFactory
from fibermodes.slrc import SLRC


class Simulator(object):

    """Simulator class."""

    def __init__(self, factory=None, wavelengths=None,
                 numax=None, mmax=None, vectorial=True):
        self._fibers = None
        self._wavelengths = None
        self._vModes = None
        self._lpModes = None

        self.numax = numax
        self.mmax = mmax
        self.vectorial = vectorial

        if factory:
            self.set_factory(factory)
        if wavelengths:
            self.set_wavelengths(wavelengths)

    def set_wavelengths(self, value):
        self._wavelengths = tuple(iter(SLRC(value)))
        if self._fibers is not None:
            self._init_modes()

    def set_factory(self, factory):
        if isinstance(factory, str):
            factory = FiberFactory(factory)
        self._fibers = tuple(iter(factory))
        if self._wavelengths is not None:
            self._init_modes()

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

    def _apply(self, fct, fidx, wlidx):
        if wlidx is None:
            wlidx = range(len(self.wavelengths))
        if isinstance(fidx, int):
            if isinstance(wlidx, int):
                return fct(fidx, wlidx)
            else:
                return starmap(fct, zip(repeat(fidx), wlidx))
        else:
            if fidx is None:
                fidx = range(len(self.fibers))
            if isinstance(wlidx, int):
                return starmap(fct, zip(fidx, repeat(wlidx)))
            else:
                return (starmap(fct, zip(repeat(i), wlidx))
                        for i in fidx)

    def _init_modes(self):
        self._vModes = [[None] * len(self.wavelengths)
                        for _ in self.fibers]
        self._lpModes = [[None] * len(self.wavelengths)
                         for _ in self.fibers]

    def _v_modes(self, fidx, wlidx):
        if self._vModes[fidx][wlidx] is None:
            self._vModes[fidx][wlidx] = self.fibers[fidx].findVmodes(
                self.wavelengths[wlidx], self.numax, self.mmax)
        return self._vModes[fidx][wlidx]

    def _lp_modes(self, fidx, wlidx):
        if self._lpModes[fidx][wlidx] is None:
            self._lpModes[fidx][wlidx] = self.fibers[fidx].findLPmodes(
                self.wavelengths[wlidx], self.numax, self.mmax)
        return self._lpModes[fidx][wlidx]

    def modes(self, fidx=None, wlidx=None):
        fct = self._v_modes if self.vectorial else self._lp_modes
        return self._apply(fct, fidx, wlidx)

    def _cutoff(self, fidx, wlidx):
        modes = (self._vModes[fidx][wlidx] if self.vectorial
                 else self._lpModes[fidx][wlidx])
        return {mode: self.fibers[fidx].cutoff(mode) for mode in modes}

    def cutoff(self, fidx=None, wlidx=None):
        self.modes(fidx, wlidx)  # Ensure we already found modes
        return self._apply(self._cutoff, fidx, wlidx)
