"""Scalar, list, range or code object.

This is a convenient object used to encapsulate a parameter that can
be either a scalar (float), a list of floats, a range, or a function (code).

"""

import math
import logging
import numpy


class SLRC(object):

    """Scalar, list, range or code object.

    Values are assumed to be always sorted.

    """

    logger = logging.getLogger(__name__)

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
        },
        'math': math
    }

    def __init__(self, value=0):
        self.codeParams = None
        SLRC.value.fset(self, value)

    @property
    def value(self):
        """Return evaluated value of object.

        The return value can be a float, a list, or a function.
        Use the type attribute if you need to know what kind it is.

        """
        k = self.kind
        if k == 'range':
            low = self._value['start']
            high = self._value['end']
            n = self._value['num']
            if n > 1:
                return [low + index*(high-low)/(n-1) for index in range(n)]
            elif n == 1:
                return [low]
            else:
                return []
        elif k == 'code':
            cp = ", ".join(self.codeParams) + ", " if self.codeParams else ""
            code = "def f({}*args, **kwargs):\n".format(cp)
            for line in self._value.splitlines():
                code += "    {}\n".format(line)
            loc = {}
            exec(code, self.rglobals, loc)
            return loc['f']
        else:
            return self._value

    @value.setter
    def value(self, value):
        """Set the value of the object.

        Warning: does not check the assigned value.

        """
        if isinstance(value, SLRC):
            self._value = value._value
        else:
            self._value = value
        if self.kind == 'list':
            self._value = sorted(value)
        self.logger.debug("Value set to {}".format(self._value))

    def __iter__(self):
        k = self.kind
        if k == 'list':
            yield from iter(self._value)
        elif k == 'range':
            yield from iter(self.value)
        else:
            yield self.value

    def __len__(self):
        k = self.kind
        if k == 'list':
            return len(self._value)
        elif k == 'range':
            return self._value['num']
        else:
            return 1

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        k = self.kind
        if k == 'list':
            return self._value[index]
        elif k == 'range':
            low = self._value['start']
            high = self._value['end']
            n = self._value['num']
            return low + index*(high-low)/(n-1)
        else:
            return self.value

    @property
    def kind(self):
        """Find what is the kind of value.

        The return value is a string. It can be 'scalar', 'list', 'range',
        or 'code'.

        """
        if isinstance(self._value, list):
            return 'list'
        elif isinstance(self._value, numpy.ndarray):
            return 'list'
        elif isinstance(self._value, str):
            return 'code'
        elif isinstance(self._value, dict):
            return 'range'
        else:
            return 'scalar'

    @kind.setter
    def kind(self, value):
        """Convert value to the given kind.

        """
        k = self.kind
        if k == value:
            return

        self.logger.debug("Converted from '{}': {}".format(k, self._value))

        if value == 'code':
            if k == 'range':
                low = self._value['start']
                high = self._value['end']
                n = self._value['num']
                self._value = ("return [{low} + index*({high}-{low})/({n}-1)"
                               " for index in range({n})]").format(
                    low=low, high=high, n=n)
            else:
                self._value = "return {}".format(repr(self._value))
        elif value == 'range':
            if k == 'scalar':
                self._value = {'start': self._value,
                               'end': self._value,
                               'num': 1}
            elif k == 'list':
                self._value = {'start': min(self._value),
                               'end': max(self._value),
                               'num': len(self._value)}
            else:
                self._value = {'start': 0,
                               'end': 1,
                               'num': 2}
        elif value == 'list':
            if k == 'scalar':
                self._value = [self._value]
            elif k == 'range':
                low = self._value['start']
                high = self._value['end']
                n = self._value['num']
                if n == 1:
                    self._value = [low]
                else:
                    self._value = [low + index*(high-low)/(n-1)
                                   for index in range(n)]
            else:
                self._value = [0]
        elif value == 'scalar':
            if k == 'list':
                self._value = self._value[0]
            elif k == 'range':
                self._value = self._value['start']
            else:
                self._value = 0
        else:
            raise ValueError

        self.logger.debug("Convert to '{}': {}".format(value, self._value))

    def __call__(self, *args, **kwargs):
        """If kind is code, call the function, otherwise return value.

        """
        if self.kind == 'code':
            return self.value(*args, **kwargs)
        else:
            return self.value
