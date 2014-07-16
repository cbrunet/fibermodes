"""Simulator module."""

from ..wavelength import Wavelength
from ..fiber.factory import Factory
from ..mode import Family
from itertools import product
from functools import reduce
from operator import mul
import numpy
import shelve
from distutils.version import StrictVersion


class Simulator(object):

    __version__ = "1.0.0"

    """Simulator class."""

    def __init__(self):
        """Constructor."""
        self._wl = None  # list of wavelengths
        self._f = None  # fiber factory
        self._matparams = None  # list of material parameters
        self._r = None  # list of layer radii

        self._constraints = {}  # list of constraints

        self._lpModes = {}  # found lpModes (fiber: list(smode))
        self._vModes = {}  # found vModes (fiber: list(smode))
        self._cutoffs = {}  # found cutoffs (fiber: {mode: cutoff})

        self._vsolved = False
        self._lpsolved = False

    def setWavelength(self, wl):
        """Set the wavelengths used for the simulation.

        :param wl: wavelength as float (in meters),
                   or :class:`~fibermodes.wavelength.Wavelength` object,
                   or iterable returning either floats
                   or :class:`~fibermodes.wavelength.Wavelength` object.

        """
        self._wl = list(wl) if hasattr(wl, '__iter__') else [wl]
        for i, w in enumerate(self._wl):
            if not isinstance(w, Wavelength):
                self._wl[i] = Wavelength(w)
        self._vsolved = False
        self._lpsolved = False

    def setMaterials(self, *args):
        """Set the materials used for the simulation.

        Unlike other simulation parameters, fiber materials must be fixed
        for the simulation. However, materials parameters can be swept.

        """
        self._f = Factory(args)
        self._vsolved = False
        self._lpsolved = False

    def setMaterialsParams(self, *args):
        """Set the parameters used in the simulation, for each materials.

        """
        self._matparams = list()
        for params in args:  # for each layer
            self._matparams.append([list(p) if hasattr(p, '__iter__') else [p]
                                    for p in params])
        self._vsolved = False
        self._lpsolved = False

    def setRadius(self, layer, r):
        """Set the radius of layer to r"""
        if self._r is None:
            self._r = []
        self._r += [0] * max(0, layer - len(self._r) + 1)
        self._r[layer] = list(r) if hasattr(r, '__iter__') else [r]
        self._vsolved = False
        self._lpsolved = False

    def setRadiusFct(self, layer, fct, *args):
        self.setRadius(layer, ((fct,) + args,))
        self._vsolved = False
        self._lpsolved = False

    def setRadii(self, *args):
        """Set the radii of each layer used for the simulation.

        """
        self._r = list(list(r) if hasattr(r, '__iter__') else [r]
                       for r in args)
        self._vsolved = False
        self._lpsolved = False

    def addConstraint(self, name, cmp, *args):
        """Add constraint on parameters.

        :param name: Unique name for the constraint
        :param cmp: A comparison function. Take len(args) arguments.
                    Return ``True`` if arguments are accepted.
        :param args: Each arg is a tuple (pname, [arg1], [arg2]). See
                     :func:`getParam` for details.
        """
        self._constraints[name] = (cmp, args)
        self._vsolved = False
        self._lpsolved = False

    def delConstraint(self, name):
        """Delete constraint on parameters.

        :param name: Unique name of the constraint
        """
        del self._constraints[name]
        self._vsolved = False
        self._lpsolved = False

    def _testConstraints(self, fiber):
        """Return True if parameters are accepted.

        """
        for cmp, args in self._constraints.values():
            p = [fiber.get(pname, *pargs) for pname, *pargs in args]
            if not(cmp(*p)):
                break
        else:
            return True
        return False

    def save(self, filename):
        """Save the current state of the simulator.

        :param filename: file name (string)

        """
        with shelve.open(filename) as db:
            db['version'] = self.__version__
            db['wavelength'] = self._wl
            db['factory'] = self._f
            db['matparams'] = self._matparams
            db['radii'] = self._r
            db['constraints'] = self._constraints
            db['lpModes'] = self._lpModes
            db['vModes'] = self._vModes
            db['lpsolved'] = self._lpsolved
            db['vsolved'] = self._vsolved

    def read(self, filename):
        """Restore from a file the current state of the simulator.

        If db version is lowwer than current version,
        the database is automatically upgraded to current version.

        :param filename: file name (string)

        """
        with shelve.open(filename) as db:
            try:
                if StrictVersion(db['version']) < StrictVersion(self.__version__):
                    self._convert(db)
            except KeyError:
                raise FileNotFoundError()
            self._f = db['factory']
            self._wl = db['wavelength']
            self._matparams = db['matparams']
            self._r = db['radii']
            self._constraints = db['constraints']
            self._lpModes = db['lpModes']
            self._vModes = db['vModes']
            self._lpsolved = db['lpsolved']
            self._vsolved = db['vsolved']

    def _convert(self, db):
        """Convert db to current version."""
        pass

    def _iterator(self, wavelengths, matparam, radii):
        if None in (self._wl, self._r, self._matparams):
            return
        params = [[0]*(self._f[i].nparams+1) for i in range(self._f.nlayers)]
        for flatparam in product(*(x for y in matparam for x in y)):
            k = 0
            for i in range(self._f.nlayers):
                for j in range(self._f[i].nparams):
                    params[i][j+1] = flatparam[k]  # params[0] is radius
                    k += 1
            for wl in wavelengths:
                for r in product(*radii):
                    for i in range(self._f.nlayers-1):  # skip last layer
                        params[i][0] = r[i]
                    fiber = self._f(wl, *params)
                    if self._testConstraints(fiber):
                        yield fiber

    def __iter__(self):
        """Generator of each possible fiber, within simulation parameters."""
        yield from self._iterator(self._wl, self._matparams, self._r)

    def __len__(self):
        """Number of different fibers generated by simulation parameters."""
        if None in (self._wl, self._r, self._matparams):
            return 0
        if not self._constraints:
            return len(self._wl) * reduce(mul, (len(r) for r in self._r)) * \
                reduce(mul, (len(p) for x in self._matparams for p in x))
        else:
            return sum(1 for _ in self)

    def getParam(self, pname, *args):
        """Return the array of parameters, for a given parameter name.

        Possible names are: 'wavelength', 'radius', and 'material'.

        For 'wavelength', the optional second parameter is the wavelength
        conversion to apply ('wavelength', 'k0', 'omega', etc. *see*
        :class:`~fibermodes.wavelength.Wavelength`). It the second parameter
        is omitted, wavelength is assumed.

        For 'radius' and 'material', the second parameter is the layer index.

        For 'material', the third parameter is material parameter index.

        :raises: :class:`TypeError`

        """
        return numpy.fromiter((fiber.get(pname, *args) for fiber in self),
                              numpy.float)

    def filter(self, array, *args):
        """Filter values in ``array`` from parameters in ``args``.

        :param array: indexable object of len == len(self)

        """
        for i, fiber in enumerate(self):
            for filt in args:
                if fiber.get(filt[0], *filt[1:-1]) != filt[-1]:
                    break
            else:
                yield array[i]

    def getLPModes(self):
        """Return the list of modes that exist within simulation parameters.

        :rtype: :class:`set` of :class:`~fibermodes.mode.Mode` object.

        """
        modelist = set()
        wl = min(self._wl)
        r = max(self._r[self._f.nlayers-2])
        rr = self._r.copy()
        rr[self._f.nlayers-2] = [r]
        for fiber in self._iterator([wl], self._matparams, rr):
            if fiber not in self._lpModes:
                self._lpModes[fiber] = {smode.mode: smode
                                        for smode in fiber.lpModes()}
            for m in self._lpModes[fiber]:
                modelist.add(m)
        return modelist

    def getVModes(self):
        """Return the list of modes that exist within simulation parameters.

        :rtype: :class:`set` of :class:`~fibermodes.mode.Mode` object.

        """
        modelist = set()
        wl = min(self._wl)
        r = max(self._r[self._f.nlayers-2])
        rr = self._r.copy()
        rr[self._f.nlayers-2] = [r]
        for fiber in self._iterator([wl], self._matparams, rr):
            if fiber not in self._vModes:
                self._vModes[fiber] = {smode.mode: smode
                                       for smode in fiber.vModes()}
            for m in self._vModes[fiber]:
                modelist.add(m)
        return modelist

    def solveV(self):
        if self._vsolved:
            return
        for i, fiber in enumerate(self):
            lpm = self._lpModes[fiber] if fiber in self._lpModes else None
            if fiber not in self._vModes:
                self._vModes[fiber] = {smode.mode: smode
                                       for smode in fiber.vModes(lpm)}
        self._vsolved = True

    def solveLP(self):
        if self._lpsolved:
            return
        for i, fiber in enumerate(self):
            if fiber not in self._lpModes:
                self._lpModes[fiber] = {smode.mode: smode
                                        for smode in fiber.lpModes()}
        self._lpsolved = True

    def _getModeAttr(self, mode, attr):
        """Generic function to fetch list of ``attr`` from solved modes.

        """
        a = numpy.zeros(len(self))
        if mode.family == Family.LP:
            self.solveLP()
            modes = self._lpModes
        else:
            self.solveV()
            modes = self._vModes

        for i, fiber in enumerate(self):
            if mode in modes[fiber]:
                a[i] = getattr(modes[fiber][mode], attr)
        return numpy.ma.masked_equal(a, 0)

    def getNeff(self, mode):
        """Return list of effective indices for given mode.

        When the mode does not exist for a given set of parameters,
        the value is masked in the returned array.

        :param: :class:`~fibermodes.mode.Mode`
        :rtype: :class:`numpy.ma.core.MaskedArray`

        """
        return self._getModeAttr(mode, 'neff')

    def getBeta(self, mode):
        """Return list of propagation constants for given mode.

        When the mode does not exist for a given set of parameters,
        the value is masked in the returned array.

        :param: :class:`~fibermodes.mode.Mode`
        :rtype: :class:`numpy.ma.core.MaskedArray`

        """
        return self._getModeAttr(mode, 'beta')
