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

"""Compute modal properties for a range of fibers.

"""

import logging
import time
from datetime import timedelta
from functools import wraps
import os
import os.path
import numpy
from fibermodes import Mode, FiberFactory, HE11, Wavelength
from fibermodes.simulator import PSimulator as Simulator
from fibermodes.fiber.material import Silica, SiO2GeO2
from matplotlib import pyplot
import matplotlib


def measure_time(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        pts = time.process_time()
        mts = time.monotonic()

        r = f(*args, **kwargs)

        print("---")
        mt = time.monotonic() - mts
        print("Wall time: {}".format(str(timedelta(seconds=mt))))

        pt = time.process_time() - pts
        print("Processing time: {}".format(str(timedelta(seconds=pt))))

        return r
    return wrapper


def find_mode_list(simulator):
    print("Finding modes", end='')
    modes = set()
    for fmodes in simulator.modes():
        print('.', end='')
        modes |= fmodes[0]
    modes = list(sorted(modes))
    print("Found {}".format(len(modes)))
    return modes


def compute_fiber_r2(results, modes, simulator, i, Rho, r2, nc2, numax, mmax):
    # Updating numax and mmax
    if simulator.numax is None:
        simulator.numax = numax
    if simulator.mmax is None:
        simulator.mmax = mmax
    print(end='  ')
    mm = find_mode_list(simulator)
    numax, mmax = 1, 1
    for m in mm:
        numax = max(m.nu, numax)
        mmax = max(m.m, mmax)
    print("  numax={}, mmax={}".format(numax, mmax))

    # Find cutoffs
    cutoffs = simulator.cutoffWl()
    print("  Finding cutoffs  rho=", end='')
    for j, rho in enumerate(Rho):
        print("{:.3f}".format(rho), end='')
        for k in range(nc2):
            print(end='.')
            for mode, co in next(cutoffs)[0].items():
                try:
                    m = modes.index(mode)
                except ValueError:
                    modes.append(mode)
                    results['modes'] = modes
                    column = numpy.empty(results['cutoff'].shape[:-1]+(1,))
                    column.fill(numpy.nan)
                    for fct in ('cutoff', 'neff', 'beta1', 'beta2', 'beta3'):
                        results[fct] = numpy.concatenate(
                            (results[fct], column), axis=3)
                    m = len(modes)-1

                results['cutoff'][j, i, k, m] = co

                # This test is to ensure we get values in the right order:
                # fiber = sim[-1].fibers[j*nrho+k]
                # if rho > 0:
                #     assert fiber._r[0] / fiber._r[1] == rho
                #     assert fiber.layers[1]._mp[0] == c2, \
                #         "{} != {}".format(fiber.layers[1]._mp[0], c2)
    print()

    for fct in ('neff', 'beta1', 'beta2', 'beta3'):
        neffs = getattr(simulator, fct)()
        print("  Finding {}s  rho=".format(fct), end='')
        for j, rho in enumerate(Rho):
            print("{:.3f}".format(rho), end='')
            for k in range(nc2):
                print(end='.')
                for mode, neff in next(neffs)[0].items():
                    try:
                        m = modes.index(mode)
                    except ValueError:
                        print("{} not found when computing {}".format(
                            str(mode, fct)))
                    else:
                        results[fct][j, i, k, m] = neff
        print()

    return numax, mmax


@measure_time
def compute_fiber(filename, nrho, R2, C2, wl, numax=None, mmax=None):
    # Initialize simulators
    sim = []
    for i, r2 in enumerate(R2):
        r1 = numpy.linspace(0, r2, nrho, endpoint=False)
        factory = FiberFactory()
        factory.addLayer(radius=r1, material='Silica')
        factory.addLayer(radius=r2, material='SiO2GeO2', x=C2)
        factory.addLayer(material='Silica')
        sim.append(Simulator(factory, wl))

    nr2 = R2.size
    nc2 = C2.size
    ckfile, _ = os.path.splitext(filename)
    ckfile += '.ckp.npz'
    if os.path.isfile(ckfile):
        # Restore checkpoint
        data = numpy.load(ckfile)
        modes = [Mode(*a) for a in data['modes']]
        results = {
            'modes': modes
        }
        for fct in ('cutoff', 'neff', 'beta1', 'beta2', 'beta3'):
            results[fct] = data[fct]
    else:
        # Find modes
        sim[-1].numax = numax
        sim[-1].mmax = mmax
        modes = find_mode_list(sim[-1])

        # Initialize arrays
        shape = (nrho, nr2, C2.size, len(modes))
        results = {
            'modes': modes
        }
        for fct in ('cutoff', 'neff', 'beta1', 'beta2', 'beta3'):
            results[fct] = numpy.empty(shape)
            results[fct].fill(numpy.nan)

    Rho = numpy.linspace(0, 1, nrho, endpoint=False)
    for i, r2 in enumerate(R2[::-1], 1):
        print("Solving when r2={:.3f}µm".format(r2*1e6))
        if numpy.all(numpy.isnan(results['cutoff'][:, nr2-i, :, :])):
            numax, mmax = compute_fiber_r2(
                results, modes, sim[-i], nr2-i, Rho, r2, nc2, numax, mmax)
            numpy.savez_compressed(ckfile, **results)  # Save checkpoint

    os.rename(ckfile, filename)
    return results


def cleanup_file(filename):
    # Remove file if it exists
    if os.path.isfile(filename):
        os.remove(filename)
    assert not os.path.isfile(filename), "{} should not exist".format(filename)


def test_save_to_file(filename):
    # Test that file exist
    assert os.path.isfile(filename), "{} should exist".format(filename)


def test_lood_file(filename, result):
    # Test that file contains result
    data = numpy.load(filename)
    for key in result.keys():
        assert key in data
        if key != 'modes':
            assert data[key].ndim == 4, "Dimension of {} is {} not 4".format(
                key, data[key].ndim)
    return data


def test_list_of_modes(result):
    assert 'modes' in result
    assert Mode("HE", 1, 1) in result['modes']


def test_cutoff(result):
    assert 'cutoff' in result
    assert not numpy.any(result['cutoff'] < 0)


def test_neff(result):
    assert 'neff' in result
    for neff in result['neff'].ravel():
        if numpy.isnan(neff):
            continue
        assert neff > 1


def run_tests():
    filename = "TESTFILE.npz"
    cleanup_file(filename)
    nrho = 3
    nr2 = 3
    nc2 = 3
    wl = 1550e-9
    numax = 10
    mmax = 5

    R2 = numpy.linspace(2e-6, 4e-6, nr2)
    C2 = numpy.linspace(0.12, 0.15, nc2)
    result = compute_fiber(filename, nrho, R2, C2, wl, numax, mmax)

    test_save_to_file(filename)
    data = test_lood_file(filename, result)
    test_list_of_modes(data)
    test_cutoff(data)
    test_neff(data)
    cleanup_file(filename)


def compute_cutoffs(filename, nrho, R2, C2, wl):
    Rho = numpy.linspace(0, 1, nrho, endpoint=False)
    data = numpy.load(filename)
    modes = [Mode(*a) for a in data['modes']]

    k0 = Wavelength(wl).k0
    n1 = Silica.n(wl)
    R1 = Rho * R2[0]

    cutoffs = numpy.empty((C2.size, Rho.size, len(modes)))
    cutoffs.fill(numpy.nan)

    for i, c2 in enumerate(C2):
        print(c2)
        n2 = SiO2GeO2.n(wl, c2)
        factory = FiberFactory()
        factory.addLayer(radius=R1, index=n1)
        factory.addLayer(radius=R2[0], index=n2)
        factory.addLayer(index=n1)
        fibers = list(iter(factory))
        for m, mode in enumerate(modes):
            print(str(mode), end=' ')
            for j, rho in enumerate(Rho):
                print(".", end="")
                na = fibers[j].NA(wl)
                vco = fibers[j].cutoff(mode)
                try:
                    cutoffs[i, j, m] = vco / (k0 * na)
                except ZeroDivisionError:
                    cutoffs[i, j, m] = numpy.NaN
                if cutoffs[i, j, m] > R2[-1]:
                    break
            # pyplot.plot(R2*1e6, Rho, color=mode.color(asint=False), lw=2)
            print()

    filename = filename[:-4] + "_cutoffs.npz"
    numpy.savez_compressed(filename, cutoffs=cutoffs)


def plot_modal_map_cutoff(filename, modes, Rho, n2):
    """

    """
    filename = filename[:-4] + "_cutoffs.npz"
    data = numpy.load(filename)
    cutoffs = data['cutoffs']

    for m, mode in enumerate(modes):
        pyplot.plot(cutoffs[n2, :, m]*1e6, Rho,
                    color='k',
                    # color=mode.color(asint=False),
                    lw=2)


def plot_modal_map(filename, nrho, R2, C2, n2, wl):
    pyplot.figure()
    data = numpy.load(filename)
    modes = [Mode(*a) for a in data['modes']]
    Rho = numpy.linspace(0, 1, nrho, endpoint=False)
    X, Y = numpy.meshgrid(R2*1e6, Rho)

    # Plot dneff map
    dneff = numpy.empty((nrho, R2.size))
    dneff.fill(numpy.inf)
    for m1, mode1 in enumerate(modes[:-1]):
        for m2, mode2 in enumerate(modes[m1+1:], m1+1):
            dn = numpy.abs(data['neff'][:, :, n2, m1] -
                           data['neff'][:, :, n2, m2])
            dn = numpy.ma.masked_invalid(dn)
            dn = numpy.ma.filled(dn, numpy.inf)
            dneff = numpy.minimum(dneff, dn)
    pyplot.imshow(dneff, aspect='auto',
                  vmax=3e-4,
                  norm=matplotlib.colors.PowerNorm(.5),
                  extent=(R2[0]*1e6, R2[-1]*1e6, 1, 0))
    pyplot.colorbar()

    # Plot cutoff limits
    plot_modal_map_cutoff(filename, modes, Rho, n2)

    # Contour lines:
    # for m, mode in enumerate(modes):
    #     if mode == HE11:
    #         continue
    #     co = numpy.ma.masked_invalid(data['cutoff'][:, :, n2, m])
    #     co = numpy.ma.filled(co, 0)
    #     pyplot.contour(X, Y, co, [wl], colors=(mode.color(asint=False),))

    # Plot options
    pyplot.title("{:.2f}% GeO2".format(C2[n2]*100))
    pyplot.xlim((R2[0]*1e6, R2[-1]*1e6))
    pyplot.ylim((0, 1))
    pyplot.xlabel("Outer radius ($r_2$)")
    pyplot.ylabel("$\\rho = r_1 / r_2$")


def plot_neff(filename, nrho, R2, C2, rho, n2, wl):
    pyplot.figure()
    data = numpy.load(filename)
    modes = [Mode(*a) for a in data['modes']]

    # index1 = SiO2GeO2.n(wl, C2[n2])
    # index2 = Silica.n(wl)
    Rho = numpy.linspace(0, 1, nrho, endpoint=False)

    for m, mode in enumerate(modes):
        neff = data['neff'][rho, :, n2, m]
        # b = ((numpy.square(neff) - index2*index2) /
        #      (index1*index1 - index2*index2))
        # pyplot.plot(R2*1e6, b, label=str(mode), color=mode.color(asint=False))
        pyplot.plot(R2*1e6, neff, label=str(mode),
                    color=mode.color(asint=False))

    pyplot.xlim((3, 5))
    pyplot.xlabel("Outer radius ($r_2$)")
    pyplot.ylabel("$n_{eff}$")
    # pyplot.ylabel("$b = (n_{eff}^2 - n_2^2) / (n_1^2 - n_2^2) $")
    pyplot.title("$\\rho={:.2f}, x_2={}$".format(Rho[rho], C2[n2]))
    # pyplot.legend(loc='best')


if __name__ == '__main__':
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.CRITICAL)
    # print(time.ctime())

    # filename = "RCFS.npz"
    # nrho = 20
    # nr2 = 25
    # nc2 = 1
    # R2 = numpy.linspace(2e-6, 8e-6, nr2)
    # C2 = numpy.linspace(0.15, 0.25, nc2)

    filename = "RCFS_bigsim.npz"
    nrho = 50
    nr2 = 65
    nc2 = 5
    R2 = numpy.linspace(2e-6, 10e-6, nr2)
    C2 = numpy.linspace(0.15, 0.25, nc2)

    # run_tests()
    # compute_fiber(filename, nrho, R2, C2, numax=10, mmax=5)
    # compute_cutoffs(filename, nrho, R2, C2, 1550e-9)
    # for n2 in range(nc2):
    #     plot_modal_map(filename, nrho, R2, C2, n2, wl=1550e-9)
    plot_neff(filename, nrho, R2, C2, rho=15, n2=2, wl=1550e-9)
    pyplot.show()
