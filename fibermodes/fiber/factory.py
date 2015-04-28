"""Fiber factory module."""

import json
import time
from distutils.version import StrictVersion as Version
from operator import mul
from functools import reduce
from itertools import product, islice
from .fiber import Fiber


__version__ = "0.0.1"


class FiberFactoryValidationError(Exception):
    pass


class Factory(object):

    def __init__(self, filename=None):
        self._fibers = {
            "version": __version__,
            "name": "",
            "description": "",
            "author": "",
            "crdate": time.time(),
            "tstamp": time.time(),
            "layers": []
        }
        if filename:
            with open(filename, 'r') as f:
                self.load(f)
        else:
            self.addLayer(name="core", radius=4e-6)
            self.addLayer(pos=1, name="cladding")

    @property
    def name(self):
        return self._fibers["name"]

    @property
    def author(self):
        return self._fibers["author"]

    @property
    def description(self):
        return self._fibers["description"]

    @property
    def crdate(self):
        return self._fibers["crdate"]

    @property
    def tstamp(self):
        return self._fibers["tstamp"]

    @property
    def layers(self):
        return self._fibers["layers"]

    def addLayer(self, pos=None, name="", radius=0):
        if pos is None:
            pos = len(self._fibers["layers"])
        layer = {
            "name": name,
            "type": "StepIndex",
            "tparams": [radius],
            "material": "Fixed",
            "mparams": [1.444],
        }
        self._fibers["layers"].insert(pos, layer)

    def dump(self, fp, **kwargs):
        fp.write(self.dumps(**kwargs))

    def dumps(self, **kwargs):
        self._fibers["tstamp"] = time.time()
        return json.dumps(self._fibers, **kwargs)

    def load(self, fp, **kwargs):
        self.loads(fp.read(), **kwargs)

    def loads(self, s, **kwargs):
        fibers = json.loads(s, **kwargs)
        self.validate(fibers)
        self._fibers = fibers

    def validate(self, obj):
        for key in ("version", "name", "description",
                    "author", "crdate", "tstamp", "layers"):
            if key not in obj.keys():
                raise FiberFactoryValidationError(
                    "Missing '{}' parameter".format(key))

        if Version(obj["version"]) > Version(__version__):
            raise FiberFactoryValidationError("Version of loaded object "
                                              "is higher that version "
                                              "of current library")
        elif Version(obj["version"]) < Version(__version__):
            self._upgrade(obj)

        for layernum, layer in enumerate(obj["layers"], 1):
            self._validateLayer(layer, layernum)

    def _validateLayer(self, layer, layernum):
        for key in ("name", "type", "tparams", "material", "mparams"):
            if key not in layer.keys():
                raise FiberFactoryValidationError(
                    "Missing '{}' parameter for layer {}".format(key,
                                                                 layernum))

    def _upgrade(self, obj):
        obj["version"] = __version__

    def __iter__(self):
        self._buildFiberList()
        g = product(*(range(i) for i in self._nitems))
        return (self._buildFiber(i) for i in g)

    def __len__(self):
        self._buildFiberList()
        return reduce(mul, self._nitems)

    def __getitem__(self, key):
        self._buildFiberList()
        return self._buildFiber(self._getIndexes(key))

    def _buildFiberList(self):
        self._nitems = []
        for layer in self._fibers["layers"]:
            for key in ("tparams", "mparams"):
                for tp in layer[key]:
                    if isinstance(tp, list):
                        self._nitems.append(len(tp))
                    elif isinstance(tp, dict):
                        self._nitems.append(tp["num"])
                    else:
                        self._nitems.append(1)

    def _getIndexes(self, index):
        """Get list of indexes from a single index."""
        g = product(*(range(i) for i in self._nitems))
        return next(islice(g, index, None))

    rglobals = {
        '__builtins__': {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'complex': complex,
            'dict': dict,
            'divmod': divmod,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'frozenset': frozenset,
            'int': int,
            'iter': iter,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'next': next,
            'pow': pow,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'slice': slice,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip
        }
    }

    def _buildFiber(self, indexes):
        """Build Fiber object from list of indexes"""

        def __get(param, index):
            if isinstance(param, list):
                return param[index]
            elif isinstance(param, dict):
                low = param['start']
                high = param['end']
                n = param['num']
                return low + index*(high-low)/(n-1)
            else:
                assert index == 0
                try:
                    return float(param)
                except ValueError:
                    code = "def f(r, fp, mp):\n"
                    for line in param.splitlines():
                        code += "    {}\n".format(line)
                    loc = {}
                    exec(code, self.rglobals, loc)
                    return loc['f']

        r = []
        f = []
        fp = []
        m = []
        mp = []
        names = []

        # Get parameters for selected fiber
        ii = 0
        for i, layer in enumerate(self._fibers["layers"], 1):
            name = layer["name"] if layer["name"] else "layer {}".format(i+1)
            names.append(name)

            if i < len(self._fibers["layers"]):
                r.append(__get(layer["tparams"][0], indexes[ii]))
            ii += 1  # we count radius of cladding, even if we don't use it

            f.append(layer["type"])
            fp_ = []
            for p in layer["tparams"][1:]:
                fp_.append(__get(p, indexes[ii]))
                ii += 1
            fp.append(fp_)

            m.append(layer["material"])
            mp_ = []
            for p in layer["mparams"]:
                mp_.append(__get(p, indexes[ii]))
                ii += 1
            mp.append(mp_)

        # Execute code parts
        for i, p in enumerate(r):
            if callable(p):
                r[i] = float(p(r, fp, mp))
        for i, pp in enumerate(fp):
            for j, p in enumerate(pp):
                if callable(p):
                    fp[i][j] = float(p(r, fp, mp))
            fp[i] = tuple(fp[i])
        for i, pp in enumerate(mp):
            for j, p in enumerate(pp):
                if callable(p):
                    mp[i][j] = float(p(r, fp, mp))
            mp[i] = tuple(mp[i])

        # Remove unneeded layers
        i = len(m)-2
        while i >= 0 and len(m) > 1:
            if (r[i] == 0 or
                    (i > 0 and r[i] <= r[i-1]) or
                    (f[i] == f[i+1] == 'StepIndex' and
                     m[i] == m[i+1] and
                     mp[i] == mp[i+1])):
                del r[i]
                del f[i]
                del fp[i]
                del m[i]
                del mp[i]
                del names[i]
            i -= 1

        return Fiber(r, f, fp, m, mp, names)
