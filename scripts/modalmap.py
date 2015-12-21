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

"""Plot modal map for RCF fiber.

TODO: parallel computing.
TODO: save results

"""

import numpy
from fibermodes import FiberFactory, Mode
from fibermodes.fiber.material.material import OutOfRangeWarning
import warnings
from matplotlib import pyplot


class Parameters(object):

    """Parameters to use in tests."""

    nr1 = 5
    nr2 = 9
    r2 = (2e-6, 10e-6)
    cn2 = 0.2
    modes = [
        Mode("HE", 2, 1),
        Mode("TE", 0, 1),
        Mode("TM", 0, 1),
        Mode("HE", 3, 1),
        Mode("EH", 1, 1),
        Mode("HE", 4, 1),
        Mode("EH", 2, 1)]


def test_build_factory():
    factory = build_factory(Parameters.nr1, Parameters.r2[0], Parameters.cn2)

    assert isinstance(factory, FiberFactory), "Returns a FiberFactory"
    assert len(factory) == Parameters.nr1, "Number of fibers is nr1"
    assert len(factory[0]) == 2, "SSIF when r1 == 0"
    for i in range(1, Parameters.nr1):
        assert len(factory[i]) == 3, "3 layers when r1 > 0"


def build_factory(nr1, r2, cn2):
    """Create a FiberFactory for RCF from given arguments.

    Args:
        nr1(int): Number of points for r1
        r2(float): Radius r2
        cn2(float): Concentration for ring-core

    Returns;
        FiberFactory

    """
    r1 = numpy.linspace(0, r2, nr1, endpoint=False)
    factory = FiberFactory()
    factory.addLayer(radius=r1, material='Silica')
    factory.addLayer(radius=r2, material='SiO2GeO2', x=cn2)
    factory.addLayer(material='Silica')
    return factory


def test_build_factories():
    factories = build_factories(Parameters.nr1, Parameters.nr2,
                                Parameters.r2, Parameters.cn2)

    assert len(factories) == Parameters.nr2, "Number of factories is nr2"
    for factory in factories:
        assert isinstance(factory, list), "list contains list"
        assert len(factory) == Parameters.nr1, "it contains nr1 fibers"


def build_factories(nr1, nr2, r2, cn2):
    """Create a list of FiberFactory for given parameters.

    Args:
        nr1(int): Number of points for r1
        nr2(int): Number of points for r2
        r2(tuple): Min and max values for r2
        cn2(float): Concentration for ring-core

    Returns:
        list of FiberFactory.

    """
    return [list(build_factory(nr1, r, cn2)) for r in numpy.linspace(*r2, nr2)]


def test_cutoff_map():
    factories = build_factories(Parameters.nr1, Parameters.nr2,
                                Parameters.r2, Parameters.cn2)
    cmap = cutoff_map(factories, Parameters.modes[0])

    assert isinstance(cmap, numpy.ndarray), "Returns ndarray"
    assert cmap.shape == (Parameters.nr1, Parameters.nr2), "nr1 x nr2 array"
    assert not numpy.any(cmap < 0), "Values are not negative"


def cutoff_map(factories, mode):
    """Return cutoffs (wavelength) as function of fiber geometry.

    Args:
        factories(FiberFactory): list of FiberFactory
        mode(Mode): Mode to solve for

    Returns:
        numpy 2D array of wavelengths

    """
    nr2 = len(factories)
    nr1 = len(factories[0])
    cmap = numpy.empty((nr1, nr2))

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=OutOfRangeWarning)
        for i, factory in enumerate(factories):
            for j, fiber in enumerate(factory):
                cmap[j, i] = fiber.cutoffWl(mode)

    return cmap


def modalmap(nr1, nr2, r2, cn2, modes):
    """

    Args:
        nr1(int): Number of points for r1
        nr2(int): Number of points for r2
        r2(tuple): Min and max values for r2
        cn2(float): Concentration for ring-core
        modes(iterable): List of modes to Plot

    """
    pyplot.figure()

    rho = numpy.linspace(0, 1, nr1, endpoint=False)
    r = numpy.linspace(*r2, nr2) * 1e6


    factories = build_factories(nr1, nr2, r2, cn2)
    for mode in modes:
        cmap = cutoff_map(factories, mode)
        pyplot.contour(X, Y, cmap, [1550e-9],
                       colors=(mode.color(asint=False),))


def run_tests():
    test_build_factory()
    test_build_factories()
    test_cutoff_map()
    print("All tests passed!")


if __name__ == '__main__':
    run_tests()
    # modalmap(50, 25, (2e-6, 10e-6), 0.2, Parameters.modes)
    # pyplot.show()
