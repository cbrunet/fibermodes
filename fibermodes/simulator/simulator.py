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

"""The simulator allows to link fibers with wavelengths, to simulate
an array of parameters.

"""

from fibermodes import FiberFactory, Wavelength, Mode, ModeFamily
from fibermodes.slrc import SLRC
from functools import reduce, partial
import operator


class _FSimulator(object):

    def __init__(self, fiber, wavelengths,
                 numax, mmax, vectorial, scalar, delta):
        self._fiber = fiber
        self._wavelengths = wavelengths
        self._modes = None

        self._numax = numax
        self._mmax = mmax
        self._vectorial = vectorial
        self._scalar = scalar
        self._delta = delta

    def modes(self):
        if self._modes is None:
            numax = self._numax
            mmax = self._mmax
            self._modes = [set() for _ in self._wavelengths]
            for i, wl in enumerate(self._wavelengths):
                if self._vectorial:
                    self._modes[i] |= self._fiber.findVmodes(wl, numax, mmax)
                if self._scalar:
                    self._modes[i] |= self._fiber.findLPmodes(wl, numax, mmax)

                numax = max(m.nu for m in self._modes[i])
                mmax = [max((m.m for m in self._modes[i] if m.nu == nu),
                            default=0)
                        for nu in range(numax+1)]
        return self._modes

    def cutoff(self):
        co = [{} for _ in self._wavelengths]
        for i, wl in enumerate(self._wavelengths):
            for m in self.modes()[i]:
                co[i][m] = self._fiber.cutoff(m)
        return co

    def cutoffWl(self):
        co = {}
        for m in reduce(operator.or_, self.modes(), set()):
            co[m] = self._fiber.toWl(self._fiber.cutoff(m))

        cod = [{} for _ in self._wavelengths]
        for i, wl in enumerate(self._wavelengths):
            for m in self._modes[i]:
                cod[i][m] = co[m]
        return cod

    def _beta(self, p):
        r = [{} for _ in self._wavelengths]
        for i, wl in enumerate(self._wavelengths):
            for m in self.modes()[i]:
                lowbound = self._lowbound(m, i)
                r[i][m] = self._fiber.beta(wl.omega, m, p=p,
                                           delta=self._delta,
                                           lowbound=lowbound)
        return r

    def beta0(self):
        return self._beta(0)

    def beta1(self):
        return self._beta(1)

    def beta2(self):
        return self._beta(2)

    def beta3(self):
        return self._beta(3)

    def _neff(self, mode, wlidx):
        lowbound = self._lowbound(mode, wlidx)
        wl = self._wavelengths[wlidx]
        return self._fiber.neff(mode, wl, delta=self._delta, lowbound=lowbound)

    def _lowbound(self, mode, i):
        wl = self._wavelengths[i]
        lowbound = max(layer.maxIndex(wl) for layer in self._fiber.layers)

        if i > 0:
            lowbound = min(lowbound, self._neff(mode, i-1))

        pm = None
        if mode.family is ModeFamily.EH:
            pm = Mode(ModeFamily.HE, mode.nu, mode.m)
        elif mode.m > 1:
            if mode.family is ModeFamily.HE:
                pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
            else:
                pm = Mode(mode.family, mode.nu, mode.m - 1)
        if pm is not None:
            lowbound = min(lowbound, self._neff(pm, i))

        if (mode.family is ModeFamily.LP and mode.nu > 0):  # or mode.nu > 1:
            pm = Mode(mode.family, mode.nu-1, mode.m)
            lowbound = min(lowbound, self._neff(pm, i))

        return lowbound

    def _apply_fct(self, fct):
        r = [{} for _ in self._wavelengths]
        for i, wl in enumerate(self._wavelengths):
            for m in self.modes()[i]:
                lowbound = self._lowbound(m, i)
                r[i][m] = fct(m, wl, delta=self._delta, lowbound=lowbound)
        return r

    def __getattr__(self, name):
        if name[0] != '_':
            fct = getattr(self._fiber, name)
            return partial(self._apply_fct, fct)
        return getattr(super(), name)


class Simulator(object):

    """The Simulator links :py:class:`~fibermodes.fiber.factory.FiberFactory`
    with a list of wavelengths, and provides a convenient way to compute
    a range of modal properties.

    Args:
        factory(:py:class:`~fibermodes.fiber.factory.FiberFactory`): A
            FiberFactory object.
        wavelengths(list): A list of wavelengths.
        numax(int): Maximum nu parameter used when finding modes, or None to
            find all modes.
        mmax(int): Maximum m parameter used when finding modes, or None to
            find all modes.
        vectorial(bool): Find vector modes.
        scalar(bool): Find scalar modes.
        delta(float): Delta parameter used for mode solver (smaller is mode
            precise, bigger is faster).
        clone(Simulator): Simulator object to clone.

    """

    def __init__(self, factory=None, wavelengths=None,
                 numax=None, mmax=None, vectorial=True, scalar=False,
                 delta=1e-6, clone=None):
        if clone is not None:
            self._fibers = clone._fibers
            self._wavelengths = clone._wavelengths
            self._numax = clone._numax
            self._mmax = clone._mmax
            self._vectorial = clone._vectorial
            self._scalar = clone._scalar
            self.delta = clone.delta
            self.factory = clone.factory
        else:
            self._fibers = None
            self._fsims = None
            self._wavelengths = None

            self._numax = numax
            self._mmax = mmax
            self._vectorial = vectorial
            self._scalar = scalar
            self.delta = delta

            self.set_factory(factory)
            if wavelengths is not None:
                self.set_wavelengths(wavelengths)
        self._build_fsims()

    def _build_fsims(self):
        if self.initialized:
            self._fsims = tuple(_FSimulator(fiber, self._wavelengths,
                                            self.numax, self.mmax,
                                            self.vectorial, self.scalar,
                                            self.delta)
                                for fiber in self._fibers)

    def set_wavelengths(self, value):
        """Set the list of wavelengths.

        It can be used if this was not done in the constructor, or to modify
        the current list of wavelengths.

        Args:
            value(list): List of wavelengths (in meters)

        """
        self._wavelengths = tuple(Wavelength(w) for w in iter(SLRC(value)))
        self._build_fsims()

    def set_factory(self, factory):
        """Set the FiberFactory.

        It can be used if this was not done in the constructor, or to modify
        the current FiberFactory.

        Args:
            factory(FiberFactory): FiberFactory object to use in simulator.

        """
        if isinstance(factory, str):
            factory = FiberFactory(factory)
        self.factory = factory
        if factory is not None:
            self._fibers = tuple(iter(factory))
            self._build_fsims()

    @property
    def fibers(self):
        """List of fibers, generated from the FiberFactory.

        Raises:
            ValueError: No FiberFactory was initialized.

        """
        if self._fibers is None:
            raise ValueError("Object not initialized. You must call "
                             "set_factory first.")
        return self._fibers

    @property
    def wavelengths(self):
        """List of wavelengths.

        This list always is sorted.

        Raises:
            ValueError: List of wavelengths was not initialized.

        """
        if self._wavelengths is None:
            raise ValueError("Object not initialized. You must call "
                             "set_wavelengths first.")
        return self._wavelengths

    @property
    def numax(self):
        """Maximum nu when finding modes."""
        return self._numax

    @numax.setter
    def numax(self, value):
        self._numax = value
        self._build_fsims()

    @property
    def mmax(self):
        """Maximum m when finding modes."""
        return self._mmax

    @mmax.setter
    def mmax(self, value):
        self._mmax = value
        self._build_fsims()

    @property
    def vectorial(self):
        """Whether to search for vector modes."""
        return self._vectorial

    @vectorial.setter
    def vectorial(self, value):
        self._vectorial = value
        self._build_fsims()

    @property
    def scalar(self):
        """Whether to search for scalar modes."""
        return self._scalar

    @scalar.setter
    def scalar(self, value):
        self._scalar = value
        self._build_fsims()

    @property
    def initialized(self):
        """Whether FiberFactory and wavelengths are set."""
        return not (self._fibers is None or self._wavelengths is None)

    def __getattr__(self, name):
        def wrapper():
            for fsim in self._fsims:
                fct = getattr(fsim, name)
                yield fct()
        return wrapper
