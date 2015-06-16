
from fibermodes.fiber import material


class Geometry(object):

    def __init__(self, *fp, m, mp):
        self._m = material.__dict__[m]()  # instantiate material object
        self._mp = mp
        self._fp = fp

    def __str__(self):
        return self.__class__.__name__ + ' ' + self._m.str(*self._mp)
