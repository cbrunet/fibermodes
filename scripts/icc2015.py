
from fibermodes import Wavelength, ModeFamily, Mode
from fibermodes.material import Silica, SiO2GeO2
# from fibermodes.material.sio2geo2cm import SiO2GeO2
# from fibermodes.material import Fixed
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
# modes = [Mode('LP', 0, 1), Mode('LP', 1, 1), Mode('LP', 2, 1)]


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
             "--".join(str(m) for m in modes[1:3]),
             "--".join(str(m) for m in modes[2:4]),
             "--".join(str(m) for m in modes[4:6])]
    content = latexRow(title, True)

    neff = []
    for m in modes:
        neff.append(sim.getNeff(m))

    for i, nn in enumerate(zip(*neff), 1):
        row = [str(i)]

        n = nn[1] - nn[2]
        row.append("\\num{{{:.4e}}}".format(n) if n else "---")
        n = nn[2] - nn[3]
        row.append("\\num{{{:.4e}}}".format(n) if n else "---")
        n = nn[4] - nn[5]
        row.append("\\num{{{:.4e}}}".format(n) if n else "---")

        content += latexRow(row)

    return latexTable(content,
                      "cccc",
                      "Effective index separation within mode groups.",
                      "fiberdneff")


def latexTable3():
    """Group index."""
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

    n1a = numpy.fromiter((f['index', 0] for f in iter(sim)),
                         dtype=numpy.float)
    n2a = numpy.fromiter((f['index', 1] for f in iter(sim)),
                         dtype=numpy.float)

    # modes = sim.findLPModes()
    # for m in modes:
    #     b = (numpy.fromiter(sim.getNeff(m),
    #                         dtype=numpy.float) - n1a) / (n2a - n1a)
    #     pyplot.plot(V0a, b, label=str(m))

    modes = sim.findVModes()
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


def plotDneffvsb():
    global n1, n2

    pyplot.figure()

    B = numpy.linspace(2, 4.5, 200)

    sim = Simulator(delta=1e-4)
    sim.setWavelength(1550e-9)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setRadius(1, B * 1e-6)
    sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
    sim.setMaterialParam(1, 0, X)

    # modes = sim.findLPModes()
    # for m in modes:
    #     b = (numpy.fromiter(sim.getNeff(m),
    #                         dtype=numpy.float) - n1a) / (n2a - n1a)
    #     pyplot.plot(V0a, b, label=str(m))

    modes = sim.findVModes()
    neff = {}
    for m in modes:
        neff[m] = sim.getNeff(m)

    for (m1, m2) in [(modes[1], modes[2]),
                     (modes[2], modes[3]),
                     (modes[4], modes[5])]:
        dneff = numpy.abs(neff[m1] - neff[m2]) * 1e4
        pyplot.plot(B, dneff, label="{} - {}".format(str(m1), str(m2)))

    for i, bb in enumerate(b, 1):
        pyplot.axvline(bb, ls='--')
        pyplot.annotate('fiber {}'.format(i),
                        xy=(bb, 2),
                        xytext=(0, 5),
                        textcoords='offset points',
                        horizontalalignment='center')

    pyplot.axhline(1, ls=":")

    pyplot.xlabel("Outer core radius (um)")
    pyplot.ylabel("Mode separation ($\\Delta n_{eff} \\cdot 10^{-4}$)")
    pyplot.legend(loc="bottom right")


def plotNgvsb():
    global n1, n2

    pyplot.figure()

    B = numpy.linspace(2, 4.5, 200)

    sim = Simulator(delta=1e-4)
    sim.setWavelength(1550e-9)
    sim.setMaterials(Silica, SiO2GeO2, Silica)
    sim.setRadius(1, B * 1e-6)
    sim.setRadiusFct(0, mul, ('value', rho), ('radius', 1))
    sim.setMaterialParam(1, 0, X)

    # modes = sim.findLPModes()
    # for m in modes:
    #     b = (numpy.fromiter(sim.getNeff(m),
    #                         dtype=numpy.float) - n1a) / (n2a - n1a)
    #     pyplot.plot(V0a, b, label=str(m))

    modes = [Mode('HE', 1, 1),
             Mode('TE', 0, 1), Mode('HE', 2, 1), Mode('TM', 0, 1),
             Mode('EH', 1, 1), Mode('HE', 3, 1)]

    for m in modes:
        ng = sim.getNg(m)
        pyplot.plot(B, ng, label=str(m))

    for i, bb in enumerate(b, 1):
        pyplot.axvline(bb, ls='--')
        pyplot.annotate('fiber {}'.format(i),
                        xy=(bb, 1.505),
                        xytext=(0, 5),
                        textcoords='offset points',
                        horizontalalignment='center')

    pyplot.xlabel("Outer core radius (um)")
    pyplot.ylabel("Group index ($n_g$)")
    pyplot.legend(loc="bottom right")
    pyplot.ylim((1.48, 1.505))


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
    V0a = numpy.linspace(2, 5, 15)  # 75
    NA = sqrt(n1*n1 - n2*n2)

    b = V0a / wl.k0 / NA
    rho = numpy.linspace(0, 1, 15)  # 75

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


def neffVsWl():
    wl = numpy.linspace(1500e-9, 1600e-9, 101)
    sim.setWavelength(wl)

    neff = {}
    for mode in modes:
        neff[mode] = sim.getNeff(mode)

    for fnum in range(5):
        output = "Wavelength"
        for mode in modes:
            output += "\t" + str(mode)
        output += "\n"

        for i in range(wl.size):
            output += "{:.3e}".format(wl[i])
            for mode in modes:
                try:
                    output += "\t{:.6f}".format(neff[mode][i, fnum])
                except TypeError:
                    output += "\t"
            output += "\n"

        savefile("fiber{}.tab".format(fnum+1), output)


def printNeff(fnum, wl, mode, measured=None):
    sim.setWavelength(wl)
    sim.setRadius(1, b[fnum-1] * 1e-6)
    neff = sim.getNeff(mode)
    if measured:
        print("{} ({:.2f}) = {:.4f} ({:.4e})".format(
              str(mode), wl * 1e9, float(neff), neff-measured))
    else:
        print("{} ({:.2f}) = {}".format(
              str(mode), wl * 1e9, float(neff)))

def printDNeff(fnum, wl, measured):
    sim.setWavelength(wl)
    sim.setRadius(1, b[fnum-1] * 1e-6)

    neff = []
    for m in [Mode("TE", 0, 1), Mode("HE", 2, 1), Mode("TM", 0, 1)]:
        neff.append(sim.getNeff(m))

    print("{:.2e} & {:.2e}".format(measured[0] - measured[1],
                                   measured[1] - measured[2]))
    print("{:.2e} & {:.2e}".format(neff[0] - neff[1],
                                   neff[1] - neff[2]))


def printDNeff2(fnum, wl, measured):
    sim.setWavelength(wl)
    sim.setRadius(1, b[fnum-1] * 1e-6)

    neff = []
    for m in [Mode("EH", 1, 1), Mode("HE", 3, 1)]:
        neff.append(sim.getNeff(m))

    print("{:.2e}".format(measured[0] - measured[1]))
    print("{:.2e}".format(neff[0] - neff[1]))

def fibre1():
    printNeff(1, 1559.8113e-9, Mode("HE", 1, 1))
    printNeff(1, 1557.735e-9, Mode("HE", 1, 1))
    printNeff(1, 1557.5625e-9, Mode("HE", 1, 1))
    printNeff(1, 1558.3696e-9, Mode("HE", 1, 1))
    print()
    printNeff(1, 1550.1165e-9, Mode("TE", 0, 1))
    printNeff(1, 1548.058e-9, Mode("TE", 0, 1))
    printNeff(1, 1547.8758e-9, Mode("TE", 0, 1))
    printNeff(1, 1548.683433e-9, Mode("TE", 0, 1))
    print()
    printNeff(1, 1550.0013e-9, Mode("TE", 0, 1))
    printNeff(1, 1547.926e-9, Mode("TE", 0, 1))
    printNeff(1, 1547.7535e-9, Mode("TE", 0, 1))
    printNeff(1, 1548.560267e-9, Mode("TE", 0, 1))
    print()
    printNeff(1, 1550.0013e-9, Mode("HE", 2, 1))
    printNeff(1, 1547.926e-9, Mode("HE", 2, 1))
    printNeff(1, 1547.7535e-9, Mode("HE", 2, 1))
    printNeff(1, 1548.560267e-9, Mode("HE", 2, 1))
    print()
    printNeff(1, 1549.852e-9, Mode("HE", 2, 1))
    printNeff(1, 1547.787e-9, Mode("HE", 2, 1))
    printNeff(1, 1547.6081e-9, Mode("HE", 2, 1))
    printNeff(1, 1548.4157e-9, Mode("HE", 2, 1))
    print()
    printNeff(1, 1549.852e-9, Mode("TM", 0, 1))
    printNeff(1, 1547.787e-9, Mode("TM", 0, 1))
    printNeff(1, 1547.6081e-9, Mode("TM", 0, 1))
    printNeff(1, 1548.4157e-9, Mode("TM", 0, 1))
    print()
    printNeff(1, 1549.7535e-9, Mode("TM", 0, 1))
    printNeff(1, 1547.6835e-9, Mode("TM", 0, 1))
    printNeff(1, 1547.5063e-9, Mode("TM", 0, 1))
    printNeff(1, 1548.314433e-9, Mode("TM", 0, 1))


def fibre2():
    printNeff(2, 1559.8114e-9, Mode("HE", 1, 1))
    printNeff(2, 1559.895e-9, Mode("HE", 1, 1))
    printNeff(2, 1559.885e-9, Mode("HE", 1, 1))
    printNeff(2, 1559.8638e-9, Mode("HE", 1, 1))
    print()
    printNeff(2, 1551.578e-9, Mode("TE", 0, 1))
    printNeff(2, 1551.664e-9, Mode("TE", 0 , 1))
    printNeff(2, 1551.665e-9, Mode("TE", 0 , 1))
    printNeff(2, 1551.635667e-9, Mode("TE", 0, 1))
    print()
    printNeff(2, 1551.3974e-9, Mode("HE", 2, 1))
    printNeff(2, 1551.4852e-9, Mode("HE", 2 , 1))
    printNeff(2, 1551.486e-9, Mode("HE", 2, 1))
    printNeff(2, 1551.4562e-9, Mode("HE", 2, 1))
    print()
    printNeff(2, 1551.2468e-9, Mode("TM", 0, 1))
    printNeff(2, 1551.335e-9, Mode("TM", 0, 1))
    printNeff(2, 1551.3345e-9, Mode("TM", 0 , 1))
    printNeff(2, 1551.305433e-9, Mode("TM", 0, 1))


def fibre3():
    printNeff(3, 1561.74e-9, Mode("HE", 1, 1))
    printNeff(3, 1561.695e-9, Mode("HE", 1, 1))
    printNeff(3, 1561.672e-9, Mode("HE", 1, 1))
    printNeff(3, 1561.702333e-9, Mode("HE", 1, 1))
    print()
    printNeff(3, 1555.031e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.946e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.947e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.974667e-9, Mode("TE", 0, 1))
    print()
    printNeff(3, 1554.859e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.768e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.779e-9, Mode("TE", 0, 1))
    printNeff(3, 1554.802e-9, Mode("TE", 0, 1))
    print()
    printNeff(3, 1554.859e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.768e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.779e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.802e-9, Mode("HE", 2, 1))
    print()
    printNeff(3, 1554.82e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.728e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.745e-9, Mode("HE", 2, 1))
    printNeff(3, 1554.764333e-9, Mode("HE", 2, 1))
    print()
    printNeff(3, 1554.82e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.728e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.745e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.764333e-9, Mode("TM", 0, 1))
    print()
    printNeff(3, 1554.64e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.545e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.548e-9, Mode("TM", 0, 1))
    printNeff(3, 1554.577667e-9, Mode("TM", 0, 1))


def fibre4():
    printNeff(4, 1564.560167e-9, Mode("HE", 1, 1))
    printNeff(4, 1564.542308e-9, Mode("HE", 1, 1))
    printNeff(4, 1564.552513e-9, Mode("HE", 1, 1))
    printNeff(4, 1564.551663e-9, Mode("HE", 1, 1))
    print()
    printNeff(4, 1559.451302e-9, Mode("TE", 0, 1))
    printNeff(4, 1559.441164e-9, Mode("TE", 0 , 1))
    printNeff(4, 1559.456372e-9, Mode("TE", 0 , 1))
    printNeff(4, 1559.449613e-9, Mode("TE", 0, 1))
    print()
    printNeff(4, 1559.278963e-9, Mode("HE", 2, 1))
    printNeff(4, 1559.256156e-9, Mode("HE", 2 , 1))
    printNeff(4, 1559.281497e-9, Mode("HE", 2, 1))
    printNeff(4, 1559.272205e-9, Mode("HE", 2, 1))
    print()
    printNeff(4, 1559.086393e-9, Mode("TM", 0, 1))
    printNeff(4, 1559.050925e-9, Mode("TM", 0, 1))
    printNeff(4, 1559.086393e-9, Mode("TM", 0 , 1))
    printNeff(4, 1559.07457e-9, Mode("TM", 0, 1))
    print()
    printNeff(4, 1549.615784e-9, Mode("EH", 1, 1))
    printNeff(4, 1549.585751e-9, Mode("EH", 1, 1))
    printNeff(4, 1549.608276e-9, Mode("EH", 1 , 1))
    printNeff(4, 1549.60327e-9, Mode("EH", 1, 1))
    print()
    printNeff(4, 1549.510673e-9, Mode("HE", 3, 1))
    printNeff(4, 1549.485649e-9, Mode("HE", 3, 1))
    printNeff(4, 1549.508171e-9, Mode("HE", 3 , 1))
    printNeff(4, 1549.501498e-9, Mode("HE", 3, 1))


def fibre5():
    printNeff(5, 1565.755096e-9, Mode("HE", 1, 1))
    printNeff(5, 1565.553e-9, Mode("HE", 1, 1))
    printNeff(5, 1565.537933e-9, Mode("HE", 1, 1))
    printNeff(5, 1565.61543e-9, Mode("HE", 1, 1))
    print()
    printNeff(5, 1561.504562e-9, Mode("TE", 0, 1))
    printNeff(5, 1561.314e-9, Mode("TE", 0 , 1))
    printNeff(5, 1561.288576e-9, Mode("TE", 0 , 1))
    printNeff(5, 1561.36904e-9, Mode("TE", 0, 1))
    print()
    printNeff(5, 1561.33685e-9, Mode("HE", 2, 1))
    printNeff(5, 1561.156e-9, Mode("HE", 2 , 1))
    printNeff(5, 1561.120911e-9, Mode("HE", 2, 1))
    printNeff(5, 1561.204745e-9, Mode("HE", 2, 1))
    print()
    printNeff(5, 1561.138692e-9, Mode("TM", 0, 1))
    printNeff(5, 1560.943e-9, Mode("TM", 0, 1))
    printNeff(5, 1560.917728e-9, Mode("TM", 0 , 1))
    printNeff(5, 1560.999848e-9, Mode("TM", 0, 1))
    print()
    printNeff(5, 1552.652631e-9, Mode("EH", 1, 1))
    printNeff(5, 1552.474e-9, Mode("EH", 1, 1))
    printNeff(5, 1552.439086e-9, Mode("EH", 1 , 1))
    printNeff(5, 1552.52199e-9, Mode("EH", 1, 1))
    print()
    printNeff(5, 1552.584793e-9, Mode("HE", 3, 1))
    printNeff(5, 1552.396e-9, Mode("HE", 3, 1))
    printNeff(5, 1552.356197e-9, Mode("HE", 3 , 1))
    printNeff(5, 1552.445791e-9, Mode("HE", 3, 1))


if __name__ == '__main__':
    # fibre5()
    # printNeff(1, 1558.37e-9, Mode("HE", 1, 1), 1.456420187)
    # printNeff(1, 1548.56e-9, Mode("TE", 0, 1), 1.447252586)
    # printNeff(1, 1548.41e-9, Mode("HE", 2, 1), 1.447117477)
    # printNeff(1, 1548.31e-9, Mode("TM", 0, 1), 1.447022835)
    # print()
    # printNeff(2, 1559.86e-9, Mode("HE", 1, 1), 1.457816636)
    # printNeff(2, 1551.64e-9, Mode("TE", 0, 1), 1.450126791)
    # printNeff(2, 1551.46e-9, Mode("HE", 2, 1), 1.449959065)
    # printNeff(2, 1551.31e-9, Mode("TM", 0, 1), 1.449818162)
    # print()
    # printNeff(3, 1561.70e-9, Mode("HE", 1, 1), 1.459534891)
    # printNeff(3, 1554.97e-9, Mode("TE", 0, 1), 1.453247352)
    # printNeff(3, 1554.76e-9, Mode("HE", 2, 1), 1.453085981)
    # printNeff(3, 1554.58e-9, Mode("TM", 0, 1), 1.452876324)
    # print()
    # printNeff(4, 1564.551663e-9, Mode("HE", 1, 1), 1.462197816)
    # printNeff(4, 1559.449613e-9, Mode("TE", 0, 1), 1.457429545)
    # printNeff(4, 1559.272205e-9, Mode("HE", 2, 1), 1.457263743)
    # printNeff(4, 1559.07457e-9,  Mode("TM", 0, 1), 1.457079038)
    # printNeff(4, 1549.60327e-9,  Mode("EH", 1, 1), 1.448227355)
    # printNeff(4, 1549.501498e-9, Mode("HE", 3, 1), 1.448132241)
    # print()
    # printNeff(5, 1565.61543e-9,  Mode("HE", 1, 1), 1.46319199)
    # printNeff(5, 1561.36904e-9,  Mode("TE", 0, 1), 1.459223402)
    # printNeff(5, 1561.204745e-9, Mode("HE", 2, 1), 1.459069855)
    # printNeff(5, 1560.999848e-9, Mode("TM", 0, 1), 1.458878362)
    # printNeff(5, 1552.52199e-9,  Mode("EH", 1, 1), 1.450955131)
    # printNeff(5, 1552.445791e-9, Mode("HE", 3, 1), 1.450883917)


    # printDNeff(1, 1548e-9, [1.447252586, 1.447117477, 1.447022835])
    # printDNeff(2, 1551e-9, [1.450126791, 1.449959065, 1.449818162])
    # printDNeff(3, 1555e-9, [1.453247352, 1.453050779, 1.452876324])
    # printDNeff(4, 1559.27e-9, [1.457429545, 1.457263743, 1.457079038])
    # printDNeff2(4, 1549.55e-9, [1.448227355, 1.448132241])
    # printDNeff(5, 1561.20e-9, [1.459223402, 1.459069855, 1.458878362])
    # printDNeff2(5, 1552.48e-9, [1.450955131, 1.450883917])

    # neffVsWl()  # Effective index tables for Lixian

    # print(latexTable3())
    # savefile('tablen.tex', latexNTable())
    # savefile('tablegeom.tex', latexTable1())
    # savefile('tableneff.tex', latexTable2())
    # savefile('tabledneff.tex', latexTableSep())
    # savefile('tableng.tex', latexTable3())
    # savefile('tabled.tex', latexTableD())
    # savefile('tables.tex', latexTableS())

    # print(latexTable3())

    # plotBendCmap(R=0.01)
    plotNgvsb()
    # plotDvsb()
    # plotRhoVsV0()
    # plotRfield()
    pyplot.show()

    # D
    # S
    # gamma
    # bending loss
    # Aeff
    # alpha (attenuation)
