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


"""This file contains the code to generate plots used in the JLT paper
about cutoff of three-layer step-index fibers.

"""

from fibermodes import FiberFactory, Simulator, Mode, ModeFamily
from itertools import zip_longest
import numpy
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import seaborn as sns
from math import sqrt


FIBERS = [
    ("Fiber (a)", [4e-6, 6e-6], [1.47, 1.43, 1.44]),
    ("Fiber (b)", [4e-6, 6e-6], [1.47, 1.45, 1.44]),
    ("Fiber (c)", [4e-6, 6e-6], [1.43, 1.47, 1.44]),
    ("Fiber (d)", [4e-6, 6e-6], [1.45, 1.47, 1.44]),
    ("Fiber (e)", [4e-6, 6e-6], [1.44, 1.47, 1.44]),
]

VLIM = (2.5, 7.0)

MODE_COLORS = {
    "HE(1,1)": sns.xkcd_rgb['mid blue'],
    "LP(0,1)": sns.xkcd_rgb['mid blue'],

    "TE(0,1)": sns.xkcd_rgb['orange'],
    "HE(2,1)": sns.xkcd_rgb['bright sky blue'],
    "LP(1,1)": sns.xkcd_rgb['bright sky blue'],
    "TM(0,1)": sns.xkcd_rgb['red'],

    "EH(1,1)": sns.xkcd_rgb['darkish green'],
    "HE(3,1)": sns.xkcd_rgb['purplish blue'],
    "LP(2,1)": sns.xkcd_rgb['purplish blue'],

    "EH(2,1)": sns.xkcd_rgb['bluish green'],
    "HE(4,1)": sns.xkcd_rgb['fuchsia'],
    "LP(3,1)": sns.xkcd_rgb['fuchsia'],

    "EH(3,1)": sns.xkcd_rgb['leafy green'],
    "HE(5,1)": sns.xkcd_rgb['neon pink'],
    "LP(4,1)": sns.xkcd_rgb['neon pink'],

    "EH(4,1)": sns.xkcd_rgb['bright olive'],
    "HE(6,1)": sns.xkcd_rgb['rosy pink'],
    "LP(5,1)": sns.xkcd_rgb['rosy pink'],

    "EH(5,1)": sns.xkcd_rgb['darkish green'],
    "HE(7,1)": sns.xkcd_rgb['purplish blue'],
    "LP(6,1)": sns.xkcd_rgb['purplish blue'],

    "EH(6,1)": sns.xkcd_rgb['bluish green'],
    "HE(8,1)": sns.xkcd_rgb['fuchsia'],
    "LP(7,1)": sns.xkcd_rgb['fuchsia'],

    "EH(7,1)": sns.xkcd_rgb['leafy green'],
    "HE(9,1)": sns.xkcd_rgb['neon pink'],
    "LP(8,1)": sns.xkcd_rgb['neon pink'],

    "EH(8,1)": sns.xkcd_rgb['bright olive'],
    "HE(10,1)": sns.xkcd_rgb['rosy pink'],
    "LP(9,1)": sns.xkcd_rgb['rosy pink'],

    "HE(1,2)": sns.xkcd_rgb['deep sky blue'],
    "LP(0,2)": sns.xkcd_rgb['deep sky blue'],

    "TE(0,2)": sns.xkcd_rgb['browny orange'],
    "HE(2,2)": sns.xkcd_rgb['true blue'],
    "LP(1,2)": sns.xkcd_rgb['true blue'],
    "TM(0,2)": sns.xkcd_rgb['blood red'],

    "EH(1,2)": sns.xkcd_rgb['evergreen'],
    "HE(3,2)": sns.xkcd_rgb['bright violet'],
    "LP(2,2)": sns.xkcd_rgb['bright violet'],

    "LP(0,3)": sns.xkcd_rgb['turquoise blue'],
}

FIRSTMODES = (
              Mode(ModeFamily.TE, 0, 1),
              Mode(ModeFamily.HE, 2, 1),
              Mode(ModeFamily.TM, 0, 1),
              Mode(ModeFamily.EH, 1, 1),
              Mode(ModeFamily.HE, 3, 1),
              Mode(ModeFamily.HE, 1, 2),
              )


def plot_b_vs_V(vectorial=True, scalar=False):
    nf = len(FIBERS)
    fig, axes = pyplot.subplots(nf, 1, sharex=False, sharey=False,
                                subplot_kw={'xlim': VLIM, 'ylim': (0, 0.3)},
                                figsize=(6, 9))
    sns.despine(fig)
    lines = {}
    for i, (name, r, n) in enumerate(FIBERS):
        axes[i].set_title(name)
        f = FiberFactory()
        for (r_, n_) in zip_longest(r, n):
            f.addLayer(radius=r_, index=n_)
        fiber = f[0]
        V = numpy.linspace(*VLIM)
        wl = [fiber.toWl(v) for v in V[::-1]]
        sim = Simulator(f, wl, vectorial=vectorial, scalar=scalar, delta=1e-5)
        co = next(sim.cutoff())
        b = next(sim.b())
        assert len(b) == len(wl)
        for mode, cutoff in co[0].items():
            if cutoff == 0:
                continue  # skip HE(1,1) / LP(0,1)
            color = MODE_COLORS[str(mode)]
            axes[i].axvline(cutoff, ls=':', color=color)

            b_ = numpy.empty(len(wl))
            for j, b__ in enumerate(b):
                b_[j] = b__.get(mode, float("nan"))
            lines[mode], = axes[i].plot(V[::-1], b_, color=color)
        if i == 1 and vectorial is True:  # fiber b
            r = Rectangle((4.6, 0), 0.8, 0.04, alpha=.3, facecolor='grey')
            axes[i].add_patch(r)

    handles = [lines[k] for k in sorted(lines)]
    labels = [str(k) for k in sorted(lines)]
    leg = fig.legend(handles, labels, loc='upper left',
                     bbox_to_anchor=(0.18, 1), frameon=True)
    frame = leg.get_frame()
    frame.set_linewidth(0)
    fig.text(0.04, 0.5, "Normalized propagation constant ($b$)",
             rotation='vertical', ha='center', va='center')
    axes[-1].set_xlabel("Normalized frequency ($V_0$)")

    fig.tight_layout(rect=(0.04, 0, 1, 1))


def plot_zoom(fiber, vlim=(4.6, 5.4), blim=(0, 0.04)):
    fig = pyplot.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, xlim=vlim, ylim=blim)
    sns.despine(fig)
    name, r, n = fiber
    ax.set_title(name)
    f = FiberFactory()
    for (r_, n_) in zip_longest(r, n):
        f.addLayer(radius=r_, index=n_)
    fiber = f[0]
    V = numpy.linspace(*vlim)
    wl = [fiber.toWl(v) for v in V[::-1]]
    sim = Simulator(f, wl, delta=1e-7)
    co = next(sim.cutoff())
    b = next(sim.b())
    for mode, cutoff in co[0].items():
        if cutoff == 0:
            continue  # skip HE(1,1) / LP(0,1)
        color = MODE_COLORS[str(mode)]
        ax.axvline(cutoff, ls=':', color=color)

        b_ = numpy.empty(len(wl))
        for j, b__ in enumerate(b):
            b_[j] = b__.get(mode, float("nan"))
        ax.plot(V[::-1], b_, color=color,
                label=str(mode) if mode.nu in (1, 3) else None)

    ax.set_ylabel("Normalized propagation constant ($b$)")
    ax.set_xlabel("Normalized frequency ($V_0$)")
    ax.legend(loc='best')
    fig.tight_layout()


def plot_var(n1, n2, n3, vlim, modes=None, mmax=None, numax=None, colors=None):
    f = FiberFactory()
    f.addLayer(radius=4e-6, index=n1)
    f.addLayer(radius=6e-6, index=n2)
    f.addLayer(index=n3)

    wl = 800e-9
    if modes is not None:
        numax = max(m.nu for m in modes)
        mmax = max(m.m for m in modes)
    sim = Simulator(f, wl, delta=1e-5, numax=numax, mmax=mmax)
    co = list(sim.cutoff())

    if modes is None:
        modes = set()
        for m_ in sim.modes():
            modes |= m_[0]

    fig = pyplot.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, xlim=vlim, ylim=(1.2, 1.8))
    sns.despine(fig)

    if hasattr(n1, '__iter__'):
        yl = 'Index of center layer ($n_1$)'
        n = n1
        on = n2
        var = 1
    else:
        yl = 'Index of middle layer ($n_2$)'
        n = n2
        on = n1
        var = 2

    na = sqrt(on**2 - n3*n3)

    lines = {}
    for mode in modes:
        co_ = numpy.empty(len(n))
        for i, co__ in enumerate(co):
            co_[i] = co__[0].get(mode, float("nan"))
            nm = max(n[i], on)
            if n[i] == n3 and var == 2:
                co_[i] *= 6 / 4
            else:
                co_[i] *= na / sqrt(nm*nm - n3*n3)
        if colors:
            color = colors[mode.m][mode.nu]
        else:
            color = MODE_COLORS[str(mode)]
        lines[mode], = ax.plot(co_, n, color=color, label=str(mode))

    ax.axhline(1.4, ls='--', color='k')
    ax.axhline(1.6, ls='--', color='k')
    ax.axhspan(1.2, 1.4, color='grey', alpha=0.6)
    ax.axhspan(1.4, 1.6, color='grey', alpha=0.4)
    ax.axhspan(1.6, 1.8, color='grey', alpha=0.2)

    ax.set_ylabel(yl)
    ax.set_xlabel("Normalized frequency ($V_0$)")
    if colors:
        m = [Mode("TE", 0, 1), Mode("HE", 1, 2), Mode("HE", 1, 3)]
        handles = [lines[m_] for m_ in m]
        labels = ["$m=1$", "$m=2$", "$m=3$"]
        ax.legend(handles, labels, loc='best')
    else:
        ax.legend(loc='best')
    fig.tight_layout()


if __name__ == '__main__':
    sns.set_style("ticks")

    # plot_b_vs_V()  # veccutoff.pdf
    # plot_b_vs_V(vectorial=False, scalar=True)  # lpcutoff.pdf
    # plot_zoom(FIBERS[1])  # fiberbzoom.pdf

    COLORS = [[],
              sns.color_palette("Blues_r"),
              sns.color_palette("Reds_r"),
              sns.color_palette("Greens_r")]
    # plot_var(numpy.linspace(1.2, 1.8, 31), 1.6, 1.4,
    #          (1, 8), FIRSTMODES)  # centervar
    plot_var(numpy.linspace(1.2, 1.8), 1.6, 1.4,
             (0, 25), mmax=3, numax=5, colors=COLORS)
    # plot_var(1.6, numpy.linspace(1.2, 1.8, 31), 1.4,
    #          (1, 8), FIRSTMODES)  # ringvar

    pyplot.show()
