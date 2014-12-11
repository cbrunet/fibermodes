
from fibermodes import Wavelength, ModeFamily
from fibermodes.material import Silica, SiO2GeO2
from fibermodes.material import Fixed
from fibermodes.simulator import PSimulator as Simulator
import numpy
from operator import mul
from math import sqrt, isnan
from matplotlib import pyplot

rho = 0.35
dn = 0.03

phiclad = numpy.array([110, 125, 140, 160, 180])
a = 1.4 * phiclad / phiclad[-1]
b = a / rho

# Refractive indices calculation
# wl = Wavelength(633e-9)
# n2 = Silica.n(wl)
# n1 = n2 + dn
# X = SiO2GeO2.xFromN(wl, n1)

# Values as 1550 nm
wl = Wavelength(1550e-9)
n2 = Silica.n(wl)
n1 = n2 + dn
X = SiO2GeO2.xFromN(wl, n1)
# n1 = SiO2GeO2.n(wl, X)
V0 = wl.k0 * b * 1e-6 * sqrt(n1*n1 - n2*n2)
# dn = n1 - n2
n02 = n1**2 / n2**2


sim = Simulator(delta=1e-4)
sim.setWavelength(wl)
sim.setMaterials(Silica, SiO2GeO2, Silica)
# sim.setMaterials(Fixed, Fixed, Fixed)
sim.setRadius(1, b * 1e-6)
sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
sim.setMaterialParam(1, 0, X)
# sim.setMaterialsParams((1.444,), (1.474,), (1.444,))

modes = sim.findVModes()


def latexSI(value, unit=None):
    if unit:
        return "\\SI{{{}}}{{\\{}}}".format(value, unit)
    else:
        return "\\si{{\\{}}}".format(value)


def latexMode(mode):
    return "\\mode{{{}}}{{{}}}{{{}}}".format(
        mode.family.name, mode.nu, mode.m)


def latexTable(content, columns, caption, label, pos="!t"):
    return ("\\begin{{table}}[{pos}]\n"
            "\\caption[]{{{caption}}}\n"
            "\\label{{tab:{label}}}\n"
            "\\centering\n"
            "{content}"
            "\\end{{table}}\n").format(
                pos=pos,
                caption=caption,
                label=label,
                content=latexTabular(columns, content))


def latexTabular(columns, content):
    return ("\\begin{{tabular}}{{{}}}\n"
            "{}"
            "\\hline\n\\end{{tabular}}\n").format(columns, content)


def latexRow(row, line=False):
    r = ' & '.join(row)
    r += ' \\\\'
    if line:
        r += '\n\\hline'
    r += '\n'
    return r


def latexNTable():
    content = "\\hline\n"
    content += latexRow(["Wavelength", "$\\lambda$",
                         latexSI(float(wl)*1e6, "um")])
    content += latexRow(["Cladding (Silica)", "$n_2$", "{:.4f}".format(n2)])
    content += latexRow(["Ring core (\\ce{SiO2GeO2})",
                         "$n_1$", "{:.4f}".format(n1)])
    content += latexRow(["Molar fraction of \\ce{GeO2} in \\ce{SiO2}",
                         "$X$", "{:.2f}".format(X)])
    content += latexRow(["Refractive index contrast",
                         "$\Delta n$", "{:.4f}".format(dn)])
    content += latexRow(["Refractive index contrast parameter",
                         "$n_0^2$", "{:.4f}".format(n02)])
    return latexTable(content,
                      "lcc",
                      "Fiber index parameters.",
                      "fiberindex")


def latexTable1():
    title = ["Fiber", "$a$", "$b$", "$\\Phi_{clad}$"]
    title.append("$V_0$ ({})".format(latexSI(1550, "nm")))
    content = latexRow(title, True)
    for ii, aa, bb, pc, v0 in zip(range(len(a)), a, b, phiclad, V0):
        row = [str(ii+1),
               latexSI("{:.2f}".format(aa), "um"),
               latexSI("{:.2f}".format(bb), "um"),
               latexSI("{:d}".format(pc), "um"),
               "{:.4f}".format(v0)]
        content += latexRow(row)
    return latexTable(content,
                      "ccccc",
                      "Geometry of the designed fibers.",
                      "fibergeom")


def latexTable2():
    title = ["Fiber"]
    neff = []
    for m in sorted(modes):
        title.append(str(m))
        neff.append(sim.getNeff(m))
    content = latexRow(title, True)

    for i, nn in enumerate(zip(*neff), 1):
        row = [str(i)]
        for n in nn:
            row.append("{:.4f}".format(n) if n else "---")
        content += latexRow(row)

    return latexTable(content,
                      "c" * len(title),
                      "Effective indices of the modes.",
                      "fiberneff")


def latexTableSep():
    title = ["Fiber",
             "--".join(str(m) for m in modes[1:4]),
             "--".join(str(m) for m in modes[4:6])]
    content = latexRow(title, True)

    neff = []
    for m in modes:
        neff.append(sim.getNeff(m))

    for i, nn in enumerate(zip(*neff), 1):
        row = [str(i)]

        n = min(nn[1] - nn[2], nn[2] - nn[3])
        row.append("\\num{{{:.2e}}}".format(n) if n else "---")
        n = nn[4] - nn[5]
        row.append("\\num{{{:.2e}}}".format(n) if n else "---")

        content += latexRow(row)

    return latexTable(content,
                      "ccc",
                      "Effective index separation within mode groups.",
                      "fiberdneff")


def latexTable3():
    title = ["Fiber"]
    ng = []
    for m in sorted(modes):
        title.append(str(m))
        ng.append(sim.getNg(m))
    content = latexRow(title, True)

    for i, nn in enumerate(zip(*ng), 1):
        row = [str(i)]
        for n in nn:
            row.append("{:.5f}".format(n) if not(isnan(n)) else "---")
        content += latexRow(row)

    return latexTable(content,
                      "c" * len(title),
                      "Group indices of the modes.",
                      "fiberng")


def latexTableD():
    title = ["Fiber"]
    D = []
    for m in sorted(modes):
        title.append(str(m))
        D.append(sim.getD(m))
    content = latexRow(title, True)

    for i, nn in enumerate(zip(*D), 1):
        row = [str(i)]
        for n in nn:
            row.append("{:.3f}".format(n) if not(isnan(n)) else "---")
        content += latexRow(row)

    return latexTable(
        content,
        "c" * len(title),
        "Dispersion parameter ({}) of the modes.".format(
            latexSI("ps \\per \\nm \\per \\km")),
        "fiberD")


def latexTableS():
    title = ["Fiber"]
    S = []
    for m in sorted(modes):
        title.append(str(m))
        S.append(sim.getS(m))
    content = latexRow(title, True)

    for i, nn in enumerate(zip(*S), 1):
        row = [str(i)]
        for n in nn:
            row.append("{:.4f}".format(n) if not(isnan(n)) else "---")
        content += latexRow(row)

    return latexTable(
        content,
        "c" * len(title),
        "Dispersion slope parameter ({}) of the modes.".format(
            latexSI("ps \\per \\square\\nm \\per \\km")),
        "fiberS")


def plotBvsV0():
    global n1, n2

    pyplot.figure()

    b = 4e-6
    V0a = numpy.linspace(2, 5, 200)
    NA = sqrt(n1*n1 - n2*n2)

    sim = Simulator(delta=1e-4)
    sim.setWavelength(Wavelength(k0=(v0 / b / NA)) for v0 in V0a)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setRadius(1, b)
    sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
    sim.setMaterialParam(1, 0, X)

    modes = sim.findVModes()
    n1a = numpy.fromiter((f['index', 0] for f in iter(sim)),
                         dtype=numpy.float)
    n2a = numpy.fromiter((f['index', 1] for f in iter(sim)),
                         dtype=numpy.float)

    for m in modes:
        b = (numpy.fromiter(sim.getNeff(m),
                            dtype=numpy.float) - n1a) / (n2a - n1a)
        pyplot.plot(V0a, b, label=str(m))

    for i, v0 in enumerate(V0, 1):
        pyplot.axvline(v0, ls='--')
        pyplot.annotate('fiber {}'.format(i),
                        xy=(v0, 0.7),
                        xytext=(0, 5),
                        textcoords='offset points',
                        horizontalalignment='center')

    pyplot.xlabel("Normalized frequency ($V_0$)")
    pyplot.ylabel("Normalized propagation constant ($\\widetilde{\\beta}$)")
    pyplot.legend(loc="upper left")


def plotDvsb():
    global n1, n2

    pyplot.figure()

    wl = Wavelength(1550e-9)
    V0a = numpy.linspace(2, 5, 100)
    NA = sqrt(n1*n1 - n2*n2)

    ba = V0a / wl.k0 / NA

    sim = Simulator(delta=1e-4)
    sim.setWavelength(wl)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setRadius(1, ba)
    sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
    sim.setMaterialParam(1, 0, X)

    modes = sim.findVModes()

    for m in modes:
        D = sim.getD(m)
        pyplot.plot(ba*1e6, D, label=str(m))

    for i, bb in enumerate(b, 1):
        pyplot.axvline(bb, ls='--')
        pyplot.annotate('fiber {}'.format(i),
                        xy=(bb, 50),
                        xytext=(0, 5),
                        textcoords='offset points',
                        horizontalalignment='center')

    pyplot.ylim((-100, 50))
    pyplot.axhspan(-100, -40, color='k', alpha=0.3)
    pyplot.axhspan(40, 100, color='k', alpha=0.3)
    pyplot.xlabel("Ring-core outer radius (µm)")
    pyplot.ylabel("Dispersion (ps / (nm km) )")
    pyplot.legend(loc="lower left")


def plotRhoVsV0():
    global n1, n2

    pyplot.figure()

    wl = Wavelength(1550e-9)
    V0a = numpy.linspace(2, 5, 75)
    NA = sqrt(n1*n1 - n2*n2)

    b = V0a / wl.k0 / NA
    rho = numpy.linspace(0, 1, 75)

    sim = Simulator(delta=1e-4)
    sim.setWavelength(wl)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setMaterialParam(1, 0, X)

    # coupures
    sim.setRadius(1, b[-1])
    sim.setRadius(0, rho * b[-1])
    modes = sim.findVModes()
    for m in modes:
        coupure = numpy.zeros(rho.size)
        for i, fiber in enumerate(iter(sim)):
            coupure[i] = fiber.cutoffV0(m)
            if coupure[i] > 5:
                break
        coupure = numpy.ma.masked_equal(coupure, 0)
        pyplot.plot(coupure, rho, label=str(m), color='k')

    # dneff
    sim.setRadius(1, b)
    neff = numpy.empty((len(modes), len(rho), len(b)))
    for j, r in enumerate(rho):
        sim.setRadiusFct(0, mul, ('value', r), ('radius', 1))

        for i, m in enumerate(modes):
            neff[i, j] = sim.getNeff(m).filled(0)
            if numpy.sum(neff[i, j]) == 0:
                break

        if i == 1:
            break

    dneff = numpy.ones((len(rho), len(b)))
    for i in range(len(rho)):
        for j in range(len(b)):
            for k in range(2, len(modes)):
                if neff[k, i, j]:
                    if abs(neff[k, i, j] - neff[k-1, i, j]) < dneff[i, j]:
                        dneff[i, j] = abs(neff[k, i, j] - neff[k-1, i, j])
    dneff = numpy.ma.masked_greater(dneff, 5e-4)
    pyplot.imshow(dneff, aspect='auto', extent=(V0a[0], V0a[-1], 1, 0))
    pyplot.colorbar()

    pyplot.axhline(0.35, ls='--', color='k')
    pyplot.plot(V0, [0.35] * V0.size, 'ok')

    pyplot.xlim((V0a[0], V0a[-1]))
    pyplot.ylim((0, 1))
    pyplot.xlabel("Normalized frequency ($V_0$)")
    pyplot.ylabel("Inner / outer radius ratio ($\\rho = a / b$)")
    # pyplot.legend(loc="upper left")


def plotBendCmap(R):
    r = numpy.linspace(-15, 15, 201)
    n = numpy.empty(r.size)
    for i, rr in enumerate(r):
        if 1.4 < abs(rr) < 4:
            n[i] = n1
        else:
            n[i] = n2

    neq = n * (1 + r*1e-6 / (1.4 * R))

    pyplot.plot(r, n, ':', label="Straight fiber")
    pyplot.plot(r, neq, label="Conformal mapping")
    pyplot.xlabel("Radius (µm)")
    pyplot.ylabel("Refractive index")
    pyplot.legend(loc="center right")


def plotRfield():
    R = numpy.linspace(0, 10, 200)
    for i, fiber in enumerate(iter(sim), 1):
        pyplot.figure()

        for m in modes:
        # m = modes[0]
            sm = sim.getMode(fiber, m)
            if sm is None:
                continue
            if sm.family in (ModeFamily.TE, ModeFamily.TM):
                continue

            try:
                f = sm.rfield(R*1e-6)
                fn = 'fiber {} {}.data'.format(i, str(m))
                numpy.savetxt(fn, f.T)

                Pe = numpy.sum(numpy.square(f[:3, :]), axis=0)
                Ph = numpy.sum(numpy.square(f[3:, :]), axis=0)

                pyplot.plot(R, Pe / numpy.nanmax(Pe), label=str(m))
                pyplot.plot(R, f[0, :] / sqrt(numpy.nanmax(Pe)),
                            label="ez")
                pyplot.plot(R, f[1, :] / sqrt(numpy.nanmax(Pe)),
                            label="er")
                pyplot.plot(R, f[2, :] / sqrt(numpy.nanmax(Pe)),
                            label="ep")
                pyplot.plot(R, f[3, :] / sqrt(numpy.nanmax(Ph)),
                            label="hz")
                pyplot.plot(R, f[4, :] / sqrt(numpy.nanmax(Ph)),
                            label="hr")
                pyplot.plot(R, f[5, :] / sqrt(numpy.nanmax(Ph)),
                            label="hp")
            except Exception as e:
                print(e)

        for r in fiber._r:
            pyplot.axvline(r*1e6, ls='--')

        pyplot.legend()
        pyplot.xlim((R[0], R[-1]))


def savefile(filename, output):
    with open(filename, 'w') as f:
        f.write(output)


if __name__ == '__main__':
    # savefile('tablen.tex', latexNTable())
    # savefile('tablegeom.tex', latexTable1())
    # savefile('tableneff.tex', latexTable2())
    # savefile('tabledneff.tex', latexTableSep())
    # savefile('tableng.tex', latexTable3())
    # savefile('tabled.tex', latexTableD())
    # savefile('tables.tex', latexTableS())

    print(latexTable3())

    # plotBendCmap(R=0.01)
    # plotBvsV0()
    # plotDvsb()
    # plotRhoVsV0()
    # plotRfield()
    # pyplot.show()

    # D
    # S
    # gamma
    # bending loss
    # Aeff
    # alpha (attenuation)
