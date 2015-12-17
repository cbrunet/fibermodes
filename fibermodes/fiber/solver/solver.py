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

from itertools import count
from scipy.optimize import brentq
import logging


class FiberSolver(object):

    """Generic abstract class for callable objects used as fiber solvers."""

    logger = logging.getLogger(__name__)
    _MCD = 0.1

    def __init__(self, fiber):
        self.fiber = fiber
        self.log = []
        self._logging = False

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def start_log(self):
        self.log = []
        self._logging = True

    def stop_log(self):
        self._logging = False

    def __record(self, fct):
        def wrapper(z, *args):
            r = fct(z, *args)
            if self._logging:
                self.log.append((z, r))
            return r
        return wrapper

    def _findFirstRoot(self, fct, args=(), lowbound=0, highbound=None,
                       ipoints=[], delta=0.25, maxiter=None):
        fct = self.__record(fct)  # For debug purpose.
        while True:
            if ipoints:
                maxiter = len(ipoints)
            elif highbound:
                maxiter = int((highbound - lowbound) / delta)
            assert maxiter is not None

            a = lowbound
            fa = fct(a, *args)
            if fa == 0:
                return a

            for i in range(1, maxiter+1):
                b = ipoints.pop(0) if ipoints else a + delta
                if highbound:
                    if ((b > highbound > lowbound) or
                            (b < highbound < lowbound)):
                        self.logger.info("_findFirstRoot: no root found within"
                                         " allowed range")
                        return float("nan")
                fb = fct(b, *args)
                if fb == 0:
                    return b

                if (fa > 0 and fb < 0) or (fa < 0 and fb > 0):
                    z = brentq(fct, a, b, args=args, xtol=1e-20)
                    fz = fct(z, *args)
                    if abs(fa) > abs(fz) < abs(fb):  # Skip discontinuities
                        self.logger.debug("skipped ({}, {}, {})".format(
                            fa, fz, fb))
                        return z

                a, fa = b, fb
            if highbound and maxiter < 100:
                delta /= 10
            else:
                break
        self.logger.info("maxiter reached ({}, {}, {})".format(
                            maxiter, lowbound, highbound))
        return float("nan")

    def _findBetween(self, fct, lowbound, highbound, args=(), maxj=15):
        fct = self.__record(fct)  # For debug purpose.
        v = [lowbound, highbound]
        s = [fct(lowbound, *args), fct(highbound, *args)]

        for j in count():  # probably not needed...
            if j == maxj:
                self.logger.warning("_findBetween: max iter reached")
                return float("nan")
            for i in range(len(s)-1):
                a, b = v[i], v[i+1]
                fa, fb = s[i], s[i+1]

                if (fa > 0 and fb < 0) or (fa < 0 and fb > 0):
                    z = brentq(fct, a, b, args=args)
                    fz = fct(z, *args)
                    if abs(fa) > abs(fz) < abs(fb):  # Skip discontinuities
                        return z

            ls = len(s)
            for i in range(ls-1):
                a, b = v[2*i], v[2*i+1]
                c = (a + b) / 2
                v.insert(2*i+1, c)
                s.insert(2*i+1, fct(c, *args))
