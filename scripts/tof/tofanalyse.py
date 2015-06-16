import pickle
import numpy
from matplotlib import pyplot

from tofcommon import r1, r2, diam, RCF, X


def errng(ng, target):
    if len(ng) < len(target) + 1:
        return float("nan")

    ng.sort()

    e1 = (ng[2] - ng[1] - target[1] + target[0])**2
    e2 = (ng[3] - ng[2] - target[2] + target[1])**2
    if len(target) > 3:
        e3 = (ng[5] - ng[4] - target[4] + target[3])**2
    else:
        e3 = 0

    return e1+e2+e3

    dng = [ng[i] - ng[0] for i in range(1, len(ng))]
    return sum((n1 - n2)**2 for (n1, n2) in zip(dng, target))


if __name__ == '__main__':
    with open("tofoptim.data", "rb") as f:
        ngm = pickle.load(f)

    erf = numpy.empty((r1.size, X.size))

    for f in range(len(RCF)):
        pyplot.figure("Fiber {}".format(f+1))
        for i in range(r1.size):
            for j in range(X.size):
                erf[i, j] = errng(ngm[i][j], RCF[f])
        Xm, Ym = numpy.meshgrid(X, r1*1e6)
        erfma = numpy.ma.masked_invalid(erf)

        pc = pyplot.pcolormesh(Xm, Ym, erfma)
        pyplot.colorbar(pc)

        # x = diam[f] * 4 / 180
        x = 0.2
        y = diam[f] * 1.4 / 180
        pyplot.plot(x, y, '+w')
    pyplot.show()
