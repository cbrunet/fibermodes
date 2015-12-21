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

from fibermodes.fiber import material


class Geometry(object):

    def __init__(self, ri, ro, *fp, m, mp, **kwargs):
        self._m = material.__dict__[m]()  # instantiate material object
        self._mp = mp
        cm = kwargs.get("cm", None)
        if cm:
            self._cm = material.__dict__[cm]()
            self._cmp = kwargs.get("cmp")
        self._fp = fp
        self.ri = ri
        self.ro = ro

    def __str__(self):
        return self.__class__.__name__ + ' ' + self._m.str(*self._mp)
