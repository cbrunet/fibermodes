'''
Created on 2014-05-06

@author: cbrunet
'''

import numpy
from scipy.optimize import brentq

from ..mode import SMode, Family


class Fiber(object):

    '''
    classdocs
    '''

    def __init__(self, wl, *args):
        '''
        Constructor

        args are: (material, radius, mat_params)
        '''
        n = len(args)

        self._wl = wl
        self._mat = []
        self._r = numpy.empty(n)
        self._n = numpy.empty(n)
        self._params = []

        for i in range(n):
            self._mat.append(args[i][0])
            self._r[i] = args[i][1]
            self._n[i] = args[i][0].n(self._wl, *args[i][2:])
            self._params.append(args[i][2:])

    def solve(self, mode, bound=None, epsilon=1e-12):
        fct = self._ceq(mode)

        if bound is None:
            bound = (self._n.min() + epsilon, self._n.max() - epsilon)

        s = 1 if fct(bound[1], mode) > 0 else -1
        n = 1
        d = bound[1] - bound[0]
        sc = 1 if fct(bound[0], mode) > 0 else -1
        while sc == s:
            n *= 2
            if n > 1024:
                # TODO: find better exception, and limit.
                raise OverflowError("Did not found root in given interval.")
            d /= 2
            for i in range(n-1, 0, -2):  # only odd indices, since we
                                         # already tried the others
                b = bound[0] + i * d
                sc = 1 if fct(b, mode) > 0 else -1
                if sc != s:
                    bound[0] = b
                    bound[1] = b + d
                    break

        neff = brentq(
            fct, bound[0], bound[1], args=(mode,))

        if bound[0] < neff < bound[1]:
            return SMode(self, mode, neff)

    def csolve(self, mode):
        pass

    def cutoff(self, mode):
        pass

    def lpModes(self, nmax=None):
        pass

    def vModes(self, lpmodes=None, nmax=None):
        pass

    def _ceq(self, mode):
        M = {Family.LP: self._lpceq,
             Family.TE: self._teceq,
             Family.TM: self._tmceq,
             Family.HE: self._heceq,
             Family.EH: self._ehceq}
        return M[mode.family]
