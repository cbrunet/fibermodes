"""A geometry describes a function applied to the refractive index,
as function of the radial position.

"""

from .stepindex import StepIndex
from .supergaussian import SuperGaussian


__all__ = ['StepIndex', 'SuperGaussian']
