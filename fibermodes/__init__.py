""" This package provides tools for solving modes in different kind of
optical fibers.

"""

from .wavelength import Wavelength
from .mode import Mode, Family as ModeFamily
from .fiber.factory import Factory as FiberFactory, fixedFiber


__all__ = ['Wavelength', 'Mode', 'ModeFamily', 'FiberFactory', 'fixedFiber']
