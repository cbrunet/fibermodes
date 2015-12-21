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


"""Scalar, list, range or code object.

This is a convenient object used to encapsulate a parameter that can
be either a scalar (float), a list of floats, a range, or a function (code).

"""

import math
import logging
import numpy


class SLRC(object):

    """Scalar, list, range or code object.

    Args:
        value(mixed): Initial value.

    Values are assumed to be always sorted.

    If the value is a `list` or a `numpy.ndarray`, it uses the value
    inside the list.

    If the value is a `dict`, it assumes keys `start`, `end`, and `num`
    to be set, and it creates a range of num values from start to
    end (included), just like `numpy.linspace`.

    If the value is a `str`, if assumes this is Python code to be evaluated.
    This code is evaluated in a restricted environment, where builtins are
    listed in `rglobals`. `math` module is also available. The code is assumed
    called inside a function definition, and must return a scalar value.

    Otherwise, the value is assumed to be a scalar (float or int).

    """

    logger = logging.getLogger(__name__)

    #: Allowed builtins for code. It includes the math module.
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

        Warning: When set, does not check the assigned value.

        Returns:
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
            return low + index*(high-low)/(n-1) if n > 1 else low
        else:
            return self.value

    @property
    def kind(self):
        """Find what is the kind of value.

        When read, the property returns a string identifying the kind
        of value contained.

        When set, the property converts the actual value to a new kind.
        Conversion is performed as described in the following table.
        Cases in **bold** are converted without loss of information.
        Case in *italic* is converted with possible loss of information.
        Other cases are converted with systematic loss of information.

        ========== ========== ======
        From       To         Result
        ========== ========== ======
        **scalar** **scalar** No change
        **scalar** **list**   List with one item
        **scalar** **range**  Range with one item
        **scalar** **code**   Return the value
        list       scalar     First item of the list
        **list**   **list**   No change
        *list*     *range*    Range from first item to last item with same number of elements (but intermediate values could be different)
        list       code       Return value of the first item
        range      scalar     First item of the range
        **range**  **list**   List with items of the range
        **range**  **range**  No change
        range      code       Return first item of the range
        code       scalar     0
        code       list       [0]
        code       range      {'start': 0, 'end': 1, 'num': 2}
        **code**   **code**   No change
        ========== ========== ======

        Returns:
            string. It can be 'scalar', 'list', 'range', or 'code'.

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
        k = self.kind
        if k == value:
            return

        self.logger.debug("Converted from '{}': {}".format(k, self._value))

        if value == 'code':
            if k == 'scalar':
                self._value = "return {}".format(self._value)
            elif k == 'list':
                self._value = "return {}".format(self._value[0])
            elif k == 'range':
                self._value = "return {}".format(self._value['start'])
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
        """If kind is code, call the function, using given arguments,
        otherwise return value.

        The difference with the `value` property is that when `kind=="code`,
        the property returns the reference to the function,
        while this calls the function and returns the result.

        Returns:
            Scalar value (for scalar or code)
            or list of values (for list or range).

        """
        if self.kind == 'code':
            return self.value(*args, **kwargs)
        else:
            return self.value
