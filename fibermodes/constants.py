"""Physical constants."""

from math import sqrt
from scipy import constants

c = constants.c  #: Speed of light in vacuum (m/s).
h = constants.h  #: Plank constant (m²kg/s).
pi = constants.pi  #: Pi constant.
mu0 = constants.mu_0  #: Vacuum permeability (H/m).
epsilon0 = constants.epsilon_0  #: Vacuum permittivity (F/m).
eV = constants.eV  #: Electron charge (C).

tpi = 2 * pi  #: Two times pi
eta0 = sqrt(mu0 / epsilon0)  #: Impedance of free-space.
Y0 = sqrt(epsilon0 / mu0)  #: Admitance of free-space.
