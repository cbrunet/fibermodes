
import oscilloscope
from fibermodes import Mode, ModeFamily
from fibermodes import constants
from fibers import fibers
from matplotlib import pyplot
import numpy
from scipy.optimize import minimize


PATH = '/home/cbrunet/Copy/PhD/Reports/RCF/TOF/'

FILES = {
    'RCF1': [
                'RCF1_6FEB2015/ALL.txt',
                 # 'RCF1_6FEB2015/ALL_A.txt',
                 # 'RCF1_6FEB2015/ALL_B.txt',
                 # 'RCF1_6FEB2015/ALL_C.txt',
            ],
    'RCF2': [
                'RCF2_6FEB2015/ALL.txt',
                # 'RCF2_6FEB2015/ALL_A.txt',
                'RCF2_6FEB2015/LCP.txt',
                'RCF2_6FEB2015/RCP.txt',
            ],
    'RCF2oam': [
                'rcf2_27jan2015/v-1.txt',
                'rcf2_27jan2015/v+1a.txt',
                # 'rcf2_27jan2015/v+1b.txt',
            ],
    'RCF3': [
                'RCF3_4FEB2015/ALL.txt',
                # 'RCF3_4FEB2015/ALL_A.txt',
                'RCF3_4FEB2015/LCP.txt',
                'RCF3_4FEB2015/RCP.txt',
            ],
    'RCF4': [
                # 'rcf4/rcf4-4Feb2015/LCP.txt',
                # 'rcf4/rcf4-4Feb2015/RCP.txt',
                # 'rcf4/RCF4_6FEB/ALL.txt',
                'rcf4/RCF4_6FEB/ALL_A.txt',
                # 'rcf4/RCF4_6FEB/ALL_B.txt',
                'rcf4/RCF4_6FEB/LCP.txt',
                'rcf4/RCF4_6FEB/RCP.txt',
            ],
    'RCF5': [
                'RCF5_4FEB2015/ALL.txt',
                'RCF5_4FEB2015/LCP.txt',
                'RCF5_4FEB2015/RCP.txt',
            ]
}
OPTS = {
    'RCF1': {'R': 1, 'N': 4},
    'RCF2': {'R': 1, 'N': 4},
    'RCF3': {'R': 1, 'N': 4},
    'RCF4': {'R': 1, 'N': 6},
    'RCF5': {'R': 1, 'N': 6},
    'RCF2oam': {'R': 2, 'N': 4},
}


def errorfunc(params, length, mdtg, sim, modes, scale=1e9, verbose=False):
    """

    params: rcore, dcore, cgeo2
    returns: sum(diff**2)

    """
    rcore, dcore, cgeo2 = params
    sim.setMaterialParam(1, 0, (cgeo2, ))
    sim.setRadii((rcore, ), (rcore + dcore, ))

    cng = numpy.array([sim.getNg(m) for m in modes])
    ctg = cng * length * scale / constants.c
    # ctg.sort()
    cdtg = ctg[1:] - ctg[0]

    sqerr = numpy.sum(numpy.square(cdtg - mdtg * scale))
    if numpy.isnan(sqerr):
        sqerr = float("inf")
    if verbose:
        print(rcore, dcore, cgeo2, length, ":", cdtg, sqerr)
    return sqerr


def errorfunc2(params, mdtg, sim, modes, scale=1e9, verbose=False):
    """

    params: rcore, cgeo2, length
    returns: sum(diff**2)

    """
    rcore, cgeo2, length = params
    sim.setMaterialParam(1, 0, (cgeo2, ))
    sim.setRadii((rcore, ), (rcore / 0.35, ))

    cng = numpy.array([sim.getNg(m) for m in modes])
    ctg = cng * length * scale / constants.c
    # ctg.sort()
    cdtg = ctg[1:] - ctg[0]

    sqerr = numpy.sum(numpy.square(cdtg - mdtg * scale))
    if numpy.isnan(sqerr):
        sqerr = float("inf")
    if verbose:
        print(rcore, cgeo2, length, ":", cdtg, sqerr)
    return sqerr


def errorfunc3(params, mdtg, sim, modes, scale=1e9, verbose=False):
    """

    params: rcore, dcore, length
    returns: sum(diff**2)

    """
    rcore, dcore, length = params
    sim.setRadii((rcore, ), (rcore + dcore, ))

    cng = numpy.array([sim.getNg(m) for m in modes])
    ctg = cng * length * scale / constants.c
    # ctg.sort()
    cdtg = ctg[1:] - ctg[0]

    sqerr = numpy.sum(numpy.square(cdtg - mdtg * scale))
    if numpy.isnan(sqerr):
        sqerr = float("inf")
    if verbose:
        print(rcore, dcore, length, ":", cdtg, sqerr)
    return sqerr


def lengtherrorfunc(length, mdtg, cng, scale=1e9, verbose=False):
    """

    returns: sum(diff**2)

    """
    ctg = cng * length * scale / constants.c
    cdtg = ctg[1:] - ctg[0]

    sqerr = numpy.sum(numpy.square(cdtg - mdtg * scale))
    if numpy.isnan(sqerr):
        sqerr = float("inf")
    if verbose:
        print(length, ":", cdtg, sqerr)
    return sqerr


# def findMax(data, modes, nn=1):
def findMax(data, npoints, nn=1):
    # npoints = len(modes)
    datamax = data[0]['Data']
    x = oscilloscope.getX(data[0])
    xoff = data[0]['XOffset']

    for i in range(1, len(data)):
        np = int((data[i]['XOffset'] - xoff) / data[0]['XInc'])
        dataalign = numpy.roll(data[i]['Data'], np)
        datamax = numpy.maximum(datamax, dataalign)
    datas = datamax.argsort()[::-1]
    print("{:.3f}".format((numpy.median(datamax) + data[0]['YOffset']) * 1e3))

    s = []
    pv = numpy.zeros((len(data), npoints))
    # im = iter(modes)
    for ds in datas:
        for j in range(1, nn+1):
            if datamax[ds-j] > datamax[ds] or datamax[ds+j] > datamax[ds]:
                break
        else:
            s.append((x[ds], datamax[ds]))
            for i, d in enumerate(data):
                np = int((data[i]['XOffset'] - xoff) / data[0]['XInc'])
                pv[i, len(s)-1] = d['Data'][ds-np] + d['YOffset']
        if len(s) == npoints:
            break

    for px, py in sorted(s):
        py += data[0]['YOffset']
        pyplot.plot(px*1e9, py, 'ok')
    #     pyplot.annotate(str(next(im)),
    #                     xy=(px*1e9, py), xycoords='data',
    #                     xytext=(10, 0), textcoords='offset pixels')

    for i in range(len(data)):
        for j in range(npoints):
            print("& {:.3f} ".format(pv[i, j] * 1e3), end='')
        print("& {:.3f} \\\\".format((numpy.median(data[i]['Data']) + data[i]['YOffset']) * 1e3))

    return sorted(s)


def printFiberParams(f):
    print("Params: a={:.2f} µm, b={:.2f} µm, "
          "b-a={:.2f} µm, X={:.2f} %, L={:.2f} m".format(
                f.a*1e6, f.b*1e6, (f.b - f.a)*1e6, f.X*100, f.length))


def plotDataAndMax(data, datafn, smodes, title):
    pyplot.figure(title)
    pyplot.title(title)
    for d, df in zip(data, datafn):
        oscilloscope.plot(d, label=df)
    mtg = findMax(data, smodes, nn=10)
    return mtg


def printTable(modes, sim, mea):
    for (mode, s, m) in zip(modes, sim, mea):
        print("{}\t{:.2f} ns\t{:.2f} ns\t{:.2f} ns\t{:.2f} %".format(
              str(mode), s*1e9, m*1e9, abs(s-m)*1e9, abs(s-m)*100/s))


def plotRCF2oam():
    datafiles = FILES["RCF2oam"]
    data = [oscilloscope.read(PATH + df) for df in datafiles]
    modes = [
        HE11,
        Mode(ModeFamily.TM, 0, 1),
        Mode(ModeFamily.HE, 2, 1),
        Mode(ModeFamily.TE, 0, 1),
        HE11,
        Mode(ModeFamily.TM, 0, 1),
        Mode(ModeFamily.HE, 2, 1),
        Mode(ModeFamily.TE, 0, 1),
    ]
    title = "RCF2 - OAM injected"
    plotDataAndMax(data, datafiles, modes, title)
    pyplot.legend(loc='best')
    fn = datafiles[0].split('/')[-2] + '.pdf'
    pyplot.savefig(fn, format='pdf')


def analyseFiber(f, optim=1):
    # extract data
    datafiles = FILES[f.name]
    data = [oscilloscope.read(PATH + df) for df in datafiles]

    print()
    print(f.name)
    printFiberParams(f)

    sim = f.getSimulator()
    modes = sim.findVModes()

    # find theoretical simulation data
    dtg = f.getDTg(sim, modes)
    idx = numpy.argsort(dtg)
    print("Expected ΔTg:",
          "\t".join("{:.2f} nm".format(d*1e9) for d in dtg[1:]))

    # find measured data
    smodes = [m for (i, m) in sorted(zip(idx, modes))]
    if f.name == "RCF3":
        smodes[1], smodes[2] = smodes[2], smodes[1]
    elif f.name == "RCF4":
        smodes[2], smodes[3] = smodes[3], smodes[2]

    title = "{} - Length: {}m".format(f.name, f.length)
    mtg = plotDataAndMax(data, datafiles, smodes, title)

    mdtg = mtg[1:] - mtg[0]
    print("Measured ΔTg:",
          "\t".join("{:.2f} nm".format(d*1e9) for d in mdtg))

    # plot theoretical simulation data
    for tg in dtg:
        p = pyplot.axvline((mtg[0] + tg)*1e9, ls=':')
    p.set_label("Expected $\\Delta T_g$")
    if mtg[0] + max(dtg) > data[0]['XRange'] + data[0]['XOrg']:
        pyplot.xlim((data[0]['XOrg']*1e9,
                     (mtg[0] + max(dtg) + max(dtg) / 10)*1e9))

    # save file
    pyplot.legend(loc='best')
    fn = datafiles[0].split('/')[-2] + '.pdf'
    pyplot.savefig(fn, format='pdf')

    # optimize fiber params
    if optim == 1:
        params = [f.a, f.b - f.a, f.X]
        cost = errorfunc(params, f.length, mdtg, sim, smodes)
        result = minimize(errorfunc, params,
                          (f.length, mdtg, sim, smodes, 1e9, False),
                          method='Nelder-Mead',
                          options={'disp': True, 'xtol': 0.1, 'ftol': 0.1})
        f.a = result.x[0]
        f.b = result.x[0] + result.x[1]
        f.X = result.x[2]
    elif optim == 2:
        params = [f.a, f.X, f.length]
        cost = errorfunc2(params, mdtg, sim, smodes)
        result = minimize(errorfunc2, params,
                          (mdtg, sim, smodes, 1e9, False),
                          method='Nelder-Mead',
                          options={'disp': True, 'xtol': 5, 'ftol': 5})
        f.a = result.x[0]
        f.b = result.x[0] / 0.35
        f.X = result.x[1]
        f.length = result.x[2]
    elif optim == 3:
        params = [f.a, f.b - f.a, f.length]
        cost = errorfunc3(params, mdtg, sim, smodes)
        result = minimize(errorfunc3, params,
                          (mdtg, sim, smodes, 1e9, False),
                          method='Nelder-Mead',
                          options={'disp': True, 'xtol': 1, 'ftol': 1})
        f.a = result.x[0]
        f.b = result.x[0] + result.x[1]
        f.length = result.x[2]

    print("Cost: {:.2f}".format(cost))
    printTable(smodes[1:], sorted(dtg[1:]), sorted(mdtg))

    sim.setMaterialParam(1, 0, (f.X, ))
    sim.setRadii((f.a, ), (f.b, ))
    dtg = f.getDTg(None, smodes)

    # print(errorfunc(params, mdtg, sim, modes))

    printFiberParams(f)
    print("Optimized ΔTg:",
          "\t".join("{:.2f} nm".format(d*1e9) for d in dtg[1:]))
    print("Cost:", result.fun)

    title = "Optimized {} - Length: {:.2f}m".format(f.name, f.length)
    mtg = plotDataAndMax(data, datafiles, smodes, title)

    for tg in dtg:
        p = pyplot.axvline((mtg[0] + tg)*1e9, ls=':')
    p.set_label("Optimized $\\Delta T_g$")
    if mtg[0] + max(dtg) > data[0]['XRange'] + data[0]['XOrg']:
        pyplot.xlim((data[0]['XOrg']*1e9,
                     (mtg[0] + max(dtg) + max(dtg) / 10)*1e9))

    pyplot.legend(loc='best')
    fn = datafiles[0].split('/')[-2] + '_Optim.pdf'
    pyplot.savefig(fn, format='pdf')

    printTable(smodes[1:], sorted(dtg[1:]), sorted(mdtg))

    print()


def plotAll():
    for rcf, files in FILES.items():
        print(rcf)
        for datafile in files:
            fn = 'results/' + datafile.replace('/', '_')[:-4] + '.pdf'
            # fig = pyplot.figure(fn)
            data = oscilloscope.read(PATH + datafile)
            med = numpy.median(data['Data'])
            # oscilloscope.plot(data)
            # pyplot.axhline(med + data['YOffset'], ls='--', color='r')
            # pyplot.savefig(fn, format='pdf')
            # pyplot.close(fig)

            # log scale
            fn = 'results/' + datafile.replace('/', '_')[:-4] + '_log.pdf'
            fig = pyplot.figure(fn)
            data['Data'] = numpy.abs(numpy.array(data['Data']) - med)
            # oscilloscope.plot(data, yoff=False, ylim=(1e-4, 1e-1), scale='log')
            # pyplot.savefig(fn, format='pdf')
            # pyplot.close(fig)

        # all together
        fn = 'results/' + rcf + '.pdf'
        # fig = pyplot.figure(fn)
        data = []
        for datafile in files:
            data.append(oscilloscope.read(PATH + datafile))
            # n = "OAM {}".format(datafile[16:18])
            n = datafile[-7:-4]
            if n == 'L_A':
                n = 'ALL'
            # oscilloscope.plot(data[-1], label=n)
        # pyplot.legend(loc='lower center', ncol=3)
        # pyplot.savefig(fn, format='pdf')

        # peak values
        N = OPTS[rcf]['N']
        R = OPTS[rcf]['R']
        peaks = findMax(data, R*N, 10)
        for i in range(len(peaks)):
            print("Peak {} & {:.3f} & {:.3f} & {:.3f} & {:.3f} \\\\".format(
                  i+1,
                  peaks[i][0] * 1e9,
                  (peaks[i][0] - peaks[(i // N)*N][0]) * 1e9,
                  constants.c * (peaks[i][0] - peaks[(i // N)*N][0]) / 1.580,
                  (peaks[i][1] + data[0]['YOffset']) * 1e3))

        # pyplot.close(fig)


if __name__ == '__main__':
    # plotRCF2oam()

    # for f in fibers[2:4]:
    #     analyseFiber(f, optim=2)

    plotAll()

    # pyplot.show()
