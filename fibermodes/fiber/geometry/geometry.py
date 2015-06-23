
from fibermodes.fiber import material


class Geometry(object):

    def __init__(self, ri, ro, *fp, m, mp, cm, cmp):
        self._m = material.__dict__[m]()  # instantiate material object
        self._mp = mp
        self._cm = material.__dict__[cm]()
        self._cmp = cmp
        self._fp = fp
        self.ri = ri
        self.ro = ro

    def __str__(self):
        return self.__class__.__name__ + ' ' + self._m.str(*self._mp)
