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


"""Electromagnetic fields computation."""

import numpy
from itertools import product
from fibermodes import Wavelength, ModeFamily, HE11
from fibermodes import constants


class Field(object):

    """Electromagnetic field representation.

    Args:
        fiber(Fiber): Fiber object
        mode(Mode): Mode
        wl(Wavelength): Wavelength
        r(float): Radius of the field to compute.
        np(int): Number of points (field will be np x np)

    """

    FTYPES = ('Ex', 'Ey', 'Ez', 'Er', 'Ephi', 'Et', 'Epol', 'Emod',
              'Hx', 'Hy', 'Hz', 'Hr', 'Hphi', 'Ht', 'Hpol', 'Hmod')

    def __init__(self, fiber, mode, wl, r, np=101):
        self.fiber = fiber
        self.mode = mode
        self.wl = Wavelength(wl)
        self.np = np
        self.xlim = (-r, r)
        self.ylim = (-r, r)
        p = numpy.linspace(-r, r, np)
        self.X, self.Y = numpy.meshgrid(p, p)
        self.R = numpy.sqrt(numpy.square(self.X) + numpy.square(self.Y))
        self.Phi = numpy.arctan2(self.Y, self.X)

    def f(self, phi0):
        """Azimuthal dependency function.

        Args:
            phi0(float): Phase (rotation) of the field.

        Returns:
            2D array of values (ndarray). Values are between -1 and 1.

        """
        return numpy.cos(self.mode.nu * self.Phi + phi0)

    def g(self, phi0):
        """Azimuthal dependency function.

        Args:
            phi0(float): Phase (rotation) of the field.

        Returns:
            2D array of values (ndarray). Values are between -1 and 1.

        """
        return -numpy.sin(self.mode.nu * self.Phi + phi0)

    def Ex(self, phi=0, theta=0):
        """x component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            self._Ex = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Ex[j, i] = er[0] * f[j, i]
            return self._Ex
        else:
            return self.Et(phi, theta) * numpy.cos(self.Epol(phi, theta))

    def Ey(self, phi=0, theta=0):
        """y component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            self._Ey = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Ey[j, i] = er[1] * f[j, i]
            return self._Ey
        else:
            return self.Et(phi, theta) * numpy.sin(self.Epol(phi, theta))

    def Ez(self, phi=0, theta=0):
        """z component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        self._Ez = numpy.zeros(self.X.shape)
        f = self.f(phi)
        for i, j in product(range(self.np), repeat=2):
            er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
            self._Ez[j, i] = er[2] * f[j, i]
        return self._Ez

    def Er(self, phi=0, theta=0):
        """r component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return (self.Et(phi, theta) *
                    numpy.cos(self.Epol(phi, theta) - self.Phi))
        else:
            self._Er = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Er[j, i] = er[0] * f[j, i]
            return self._Er

    def Ephi(self, phi=0, theta=0):
        """phi component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return (self.Et(phi, theta) *
                    numpy.sin(self.Epol(phi, theta) - self.Phi))
        else:
            self._Ephi = numpy.zeros(self.X.shape)
            g = self.g(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Ephi[j, i] = er[1] * g[j, i]
            return self._Ephi

    def Et(self, phi=0, theta=0):
        """transverse component of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.sqrt(numpy.square(self.Ex(phi, theta)) +
                              numpy.square(self.Ey(phi, theta)))
        else:
            return numpy.sqrt(numpy.square(self.Er(phi, theta)) +
                              numpy.square(self.Ephi(phi, theta)))

    def Epol(self, phi=0, theta=0):
        """polarization of the transverse E field (in radians).

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.arctan2(self.Ey(phi, theta),
                                 self.Ex(phi, theta))
        else:
            return numpy.arctan2(self.Ephi(phi, theta),
                                 self.Er(phi, theta)) + self.Phi

    def Emod(self, phi=0, theta=0):
        """modulus of the E field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.sqrt(numpy.square(self.Ex(phi, theta)) +
                              numpy.square(self.Ey(phi, theta)) +
                              numpy.square(self.Ez(phi, theta)))
        else:
            return numpy.sqrt(numpy.square(self.Er(phi, theta)) +
                              numpy.square(self.Ephi(phi, theta)) +
                              numpy.square(self.Ez(phi, theta)))

    def Hx(self, phi=0, theta=0):
        """x component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            self._Hx = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Hx[j, i] = hr[0] * f[j, i]
            return self._Hx
        else:
            return self.Ht(phi, theta) * numpy.cos(self.Hpol(phi, theta))

    def Hy(self, phi=0, theta=0):
        """y component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            self._Hy = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Hy[j, i] = hr[1] * f[j, i]
            return self._Hy
        else:
            return self.Ht(phi, theta) * numpy.sin(self.Hpol(phi, theta))

    def Hz(self, phi=0, theta=0):
        """z component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        self._Hz = numpy.zeros(self.X.shape)
        f = self.f(phi)
        for i, j in product(range(self.np), repeat=2):
            er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
            self._Hz[j, i] = hr[2] * f[j, i]
        return self._Hz

    def Hr(self, phi=0, theta=0):
        """r component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return (self.Ht(phi, theta) *
                    numpy.cos(self.Hpol(phi, theta) - self.Phi))
        else:
            self._Hr = numpy.zeros(self.X.shape)
            f = self.f(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Hr[j, i] = hr[0] * f[j, i]
            return self._Hr

    def Hphi(self, phi=0, theta=0):
        """phi component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return (self.Ht(phi, theta) *
                    numpy.sin(self.Hpol(phi, theta) - self.Phi))
        else:
            self._Hphi = numpy.zeros(self.X.shape)
            g = self.g(phi)
            for i, j in product(range(self.np), repeat=2):
                er, hr = self.fiber._rfield(self.mode, self.wl, self.R[j, i])
                self._Hphi[j, i] = hr[1] * g[j, i]
            return self._Hphi

    def Ht(self, phi=0, theta=0):
        """transverse component of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.sqrt(numpy.square(self.Hx(phi, theta)) +
                              numpy.square(self.Hy(phi, theta)))
        else:
            return numpy.sqrt(numpy.square(self.Hr(phi, theta)) +
                              numpy.square(self.Hphi(phi, theta)))

    def Hpol(self, phi=0, theta=0):
        """polarization of the transverse H field (in radians).

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.arctan2(self.Hy(phi, theta),
                                 self.Hx(phi, theta))
        else:
            return numpy.arctan2(self.Hphi(phi, theta),
                                 self.Hr(phi, theta)) + self.Phi

    def Hmod(self, phi=0, theta=0):
        """modulus of the H field.

        Args:
            phi: phase (in radians)
            theta: orientation (in radians)

        Return:
            (np x np) numpy array

        """
        if self.mode.family is ModeFamily.LP:
            return numpy.sqrt(numpy.square(self.Hx(phi, theta)) +
                              numpy.square(self.Hy(phi, theta)) +
                              numpy.square(self.Hz(phi, theta)))
        else:
            return numpy.sqrt(numpy.square(self.Hr(phi, theta)) +
                              numpy.square(self.Hphi(phi, theta)) +
                              numpy.square(self.Hz(phi, theta)))

    def Aeff(self):
        """Estimation of mode effective area.

        Suppose than r is large enough, such as \|F(r, r)\| = 0.

        """
        modF = self.Emod()
        dx = (self.xlim[1] - self.xlim[0]) / (self.np - 1)
        dy = (self.ylim[1] - self.ylim[0]) / (self.np - 1)
        return (numpy.square(numpy.sum(numpy.square(modF))) /
                numpy.sum(numpy.power(modF, 4))) * dx * dy

    def I(self):
        neff = self.fiber.neff(HE11, self.wl)
        nm = self.fiber.neff(self.mode, self.wl)
        dx = (self.xlim[1] - self.xlim[0]) / (self.np - 1)
        dy = (self.ylim[1] - self.ylim[0]) / (self.np - 1)
        return nm / neff * numpy.sum(numpy.square(self.Et())) * dx * dy

    def N(self):
        """Normalization constant."""
        neff = self.fiber.neff(HE11, self.wl)
        return 0.5 * constants.epsilon0 * neff * constants.c * self.I()

    def S(self):
        """Pointing vector"""
        pass
