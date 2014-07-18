"""Simulator module."""

from ..wavelength import Wavelength
from ..fiber.factory import Factory
from ..mode import Family, Mode, sortModes
from itertools import product
from functools import reduce
from operator import mul
import numpy
import shelve
from distutils.version import StrictVersion
from copy import deepcopy


class Simulator(object):

    __version__ = "1.0.0"

    """Simulator class."""

    def __init__(self, scalar=True, vectorial=False,
                 delta=1e-6, cladding=False):
        """Constructor."""
        self._wl = None  # list of wavelengths
        self._f = None  # fiber factory
        self._matparams = None  # list of material parameters
        self._r = None  # list of layer radii

        self._constraints = {}  # list of constraints

        self._lpModes = {}  # found lpModes (fiber: list(smode))
        self._vModes = {}  # found vModes (fiber: list(smode))
        self._cutoffs = {}  # found cutoffs (fiber: {mode: cutoff})

        self._delta = delta
        self._nmax = None
        self._cladding = cladding
        self._scalar = scalar
        self._vectorial = vectorial

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

    def setMaterials(self, *args):
        """Set the materials used for the simulation.

        Unlike other simulation parameters, fiber materials must be fixed
        for the simulation. However, materials parameters can be swept.

        """
        self._f = Factory(args)

    def setMaterialsParams(self, *args):
        """Set the parameters used in the simulation, for each materials.

        """
        self._matparams = list()
        for params in args:  # for each layer
            self._matparams.append([list(p) if hasattr(p, '__iter__') else [p]
                                    for p in params])

    def setMaterialParam(self, layer, pnum, pval):
        if self._matparams is None:
            self._matparams = []
        self._matparams += [[]] * max(0, layer - len(self._r) + 1)
        self._matparams[layer] += [0] * max(0,
                                            pnum - self._f[layer].nparams + 1)
        self._matparams[layer][pnum] = (list(pval)
                                        if hasattr(pval, '__iter__')
                                        else [pval])

    def setRadius(self, layer, r):
        """Set the radius of layer to r"""
        if self._r is None:
            self._r = []
        self._r += [0] * max(0, layer - len(self._r) + 1)
        self._r[layer] = list(r) if hasattr(r, '__iter__') else [r]

    def setRadiusFct(self, layer, fct, *args):
        self.setRadius(layer, ((fct,) + args,))

    def setRadii(self, *args):
        """Set the radii of each layer used for the simulation.

        """
        self._r = list(list(r) if hasattr(r, '__iter__') else [r]
                       for r in args)

    def addConstraint(self, name, cmp, *args):
        """Add constraint on parameters.

        :param name: Unique name for the constraint
        :param cmp: A comparison function. Take len(args) arguments.
                    Return ``True`` if arguments are accepted.
        :param args: Each arg is a tuple (pname, [arg1], [arg2]). See
                     :func:`getParam` for details.
        """
        self._constraints[name] = (cmp, args)

    def delConstraint(self, name):
        """Delete constraint on parameters.

        :param name: Unique name of the constraint
        """
        del self._constraints[name]

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

    def setDelta(self, delta):
        self._delta = delta

    def setNMax(self, nmax):
        self._nmax = nmax

    def setCladdingModes(self, cladding):
        self._cladding = cladding

    def setScalar(self, scalar):
        self._scalar = scalar

    def setVectorial(self, vectorial):
        self._vectorial = vectorial

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

    def read(self, filename):
        """Restore from a file the current state of the simulator.

        If db version is lowwer than current version,
        the database is automatically upgraded to current version.

        :param filename: file name (string)

        """
        with shelve.open(filename) as db:
            try:
                if (StrictVersion(db['version']) <
                        StrictVersion(self.__version__)):
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

    def _convert(self, db):
        """Convert db to current version."""
        pass

    def _iterator(self, wavelengths, matparam, radii, skipAsNone=False):
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
                    elif skipAsNone:
                        yield None

    def __iter__(self):
        """Generator of each possible fiber, within simulation parameters."""
        yield from self._iterator(self._wl, self._matparams, self._r)

    def __len__(self):
        """Number of different fibers generated by simulation parameters."""
        if None in (self._wl, self._r, self._matparams):
            return 0
        if not self._constraints:
            return self.__length_hint__()
        else:
            return sum(1 for _ in self)

    def __length_hint__(self):
        return len(self._wl) * reduce(mul, (len(r) for r in self._r)) * \
            reduce(mul, (len(p) for x in self._matparams for p in x))

    def getDimensions(self):
        dims = []
        if len(self._wl) > 1:
            dims.append(('wavelength',))
        for i, r in enumerate(self._r):
            if len(r) > 1:
                dims.append(('radius', i))
        for i, mp in enumerate(self._matparams):
            for j, p in enumerate(mp):
                if len(p) > 1:
                    dims.append(('material', i, j))
        return dims

    def shape(self):
        return tuple(len(self._getParameter(p)) for p in self.getDimensions())

    def _getParameter(self, dim):
        if dim[0] == 'wavelength':
            return self._wl
        elif dim[0] == 'radius':
            return self._r[dim[1]]
        elif dim[0] == 'material':
            return self._matparams[dim[1]][dim[2]]
        else:
            raise TypeError("Wrong parameter type {}".format(dim))

    def getParameters(self, dims=None):
        if dims is None:
            dims = self.getDimensions()
        return [self._getParameter(dim) for dim in dims]

    def _getMinMaxParams(self):
        if len(self._wl) > 1:
            wl = [min(self._wl), max(self._wl)]
        else:
            wl = [self._wl[0]]
        rr = deepcopy(self._r)
        for i, r in enumerate(rr):
            if len(r) > 1:
                rr[i] = [min(r), max(r)]
        matpar = deepcopy(self._matparams)
        for i, mp in enumerate(matpar):
            for j, p in enumerate(mp):
                if len(p) > 1:
                    matpar[i][j] = [min(p), max(p)]
        return wl, matpar, rr

    def _solveFiber(self, fiber, lpHint=None, vHint=None):
        lpModes, vModes = [], []
        if self._scalar and fiber not in self._lpModes:
            if lpHint:
                for m in lpHint:
                    try:
                        lpModes.append(fiber.solve(m, (m.neff,
                                                       m.neff - self._delta,
                                                       None),
                                                   delta=self._delta))
                    except OverflowError:
                        if m == Mode("LP", 0, 1):
                            lpModes = []
                            break
            if not lpModes:
                lpModes = [smode for smode in fiber.lpModes(delta=self._delta)]

        if self._vectorial and fiber not in self._vModes:
            if lpModes:
                vModes = [smode for smode in fiber.vModes(lpModes,
                                                          delta=self._delta)]
            elif vHint:
                for m in vHint:
                    try:
                        vModes.append(fiber.solve(m, (m.neff,
                                                      m.neff - self._delta,
                                                      None),
                                                  delta=self._delta))
                    except OverflowError:
                        if m == Mode("HE", 1, 1):
                            vModes = []
                            break
            if not vModes:
                vModes = [smode for smode in fiber.vModes(delta=self._delta)]

        return lpModes, vModes

    def _solveBetween(self, fiber, param):
        if len(self._wl) > 1 and param[0] != 'wavelength':
            wl = [fiber._wl]
        else:
            wl = self._wl

        ra = []
        for i, r in enumerate(self._r):
            if len(r) > 1 and param != ('radius', i):
                ra.append([fiber._r[i]])
            else:
                ra.append(self._r[i])

        mp = []
        for i, lp in enumerate(self._matparams):
            mp.append([])
            for j, p in enumerate(lp):
                if len(p) > 1 and param != ('material', i, j):
                    mp[i].append([fiber._params[i][j]])
                else:
                    mp[i].append(self._matparams[i][j])

        fibers = list(self._iterator(wl, mp, ra))
        neff1 = (self._lpModes[fibers[0]][Mode("LP", 0, 1)].neff
                 if self._scalar
                 else self._vModes[fibers[0]][Mode("HE", 1, 1)].neff)
        neff2 = (self._lpModes[fibers[-1]][Mode("LP", 0, 1)].neff
                 if self._scalar
                 else self._vModes[fibers[-1]][Mode("HE", 1, 1)].neff)
        if neff1 > neff2:
            s = slice(1, -1, 1)
            fp = fibers[0]
        else:
            s = slice(-2, 0, -1)
            fp = fibers[-1]
        lpModes = list(self._lpModes[fp].values()) if self._scalar else None
        vModes = list(self._vModes[fp].values()) if self._vectorial else None

        self._iterSolve(fibers[s], lpModes, vModes)

    def _solve(self, mmwl, mmmatparams, mmradii, dims):
        if dims:
            p = dims.pop()
            if p[0] == 'wavelength':
                mmwl.pop()
            elif p[0] == 'radius':
                mmradii[p[1]].pop()
            elif p[0] == 'material':
                mmmatparams[p[1]][p[2]].pop()

            for fiber in self._iterator(mmwl, mmmatparams, mmradii):
                self._solveBetween(fiber, p)

            if p[0] == 'wavelength':
                mmwl = self._wl
            elif p[0] == 'radius':
                mmradii[p[1]] = self._r[p[1]]
            elif p[0] == 'material':
                mmmatparams[p[1]][p[2]] = self._matparams[p[1]][p[2]]
            self._solve(mmwl, mmmatparams, mmradii, dims)

    def _iterSolve(self, fiter, lpModes=None, vModes=None):
        for f in fiter:
            lpModes, vModes = self._solveFiber(f, lpModes, vModes)
            if lpModes:
                self._lpModes[f] = {smode.mode: smode for smode in lpModes}
            if vModes:
                self._vModes[f] = {smode.mode: smode for smode in vModes}

    def solve(self):
        wl, matparams, radii = self._getMinMaxParams()
        self._iterSolve(self._iterator(wl, matparams, radii))
        self._solve(wl, matparams, radii, self.getDimensions())
        # TODO: find missing modes
        # TODO: find wrong modes

    def _getModeAttr(self, mode, attr):
        """Generic function to fetch list of ``attr`` from solved modes.

        """
        if mode.family == Family.LP:
            if not self._scalar:
                raise TypeError()
            modes = self._lpModes
        else:
            if not self._vectorial:
                raise TypeError()
            modes = self._vModes
        self.solve()

        a = numpy.fromiter((getattr(modes[fiber][mode], attr)
                            if fiber and fiber in modes
                            and mode in modes[fiber] else 0
                            for fiber in self._iterator(self._wl,
                                                        self._matparams,
                                                        self._r, True)),
                           numpy.float,
                           self.__length_hint__())
        a = a.reshape(self.shape(), order='F')
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
