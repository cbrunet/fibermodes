
from fibermodes.material import *


class StepIndex(object):

    def __init__(self, m, mp):
        self._m = globals()[m]()
        self._mp = mp

    def index(self, r, wl):
        return self._m.n(wl, *self._mp)

    def minIndex(self, wl):
        return self._m.n(wl, *self._mp)

    def maxIndex(self, wl):
        return self._m.n(wl, *self._mp)
