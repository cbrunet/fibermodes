
import numpy
from matplotlib import pyplot
from datetime import datetime


def parseDate(dstr):
    return datetime.strptime(dstr, '%d %b %Y').date()


def parseTime(dstr):
    return datetime.strptime(dstr, '%H:%M:%S:%f').time()


TR = {
    'Type': str,
    'Points': int,
    'Count': int,
    'XInc': float,
    'XOrg': float,
    'YData range': float,
    'YData center': float,
    'Coupling': str,
    'XRange': float,
    'XOffset': float,
    'YRange': float,
    'YOffset': float,
    'Date': parseDate,
    'Time': parseTime,
    'Frame': str,
    'X Units': str,
    'Y Units': str,
}


def read(filename):
    header = True
    data = {}

    with open(filename) as f:
        for line in f:
            if header:
                if line == 'Data:\n':
                    data['Data'] = numpy.empty(data['Points'])
                    header = False
                    count = 0
                else:
                    key, value = line.split(':', 1)
                    data[key] = TR[key](value.strip())
            else:
                if line == '99.999E+33\n':
                    data['Data'][count] = 0
                else:
                    data['Data'][count] = float(line)
                count += 1

    return data


def getX(data):
    return numpy.linspace(0, data['XRange'], data['Points']) + data['XOrg']


def plot(data, xlim=None, ylim=None, label=None, yoff=True, scale='lin'):
    x = getX(data)
    yoff = data['YOffset'] if yoff else 0
    if scale == 'lin':
        pyplot.plot(x*1e9, data['Data'] + yoff, label=label)
    elif scale == 'log':
        pyplot.semilogy(x*1e9, data['Data'] + yoff, label=label)
    pyplot.xlabel("nano" + data['X Units'])
    pyplot.ylabel(data['Y Units'])
    # pyplot.grid(which='both')
    if xlim:
        pyplot.xlim(xlim)
    else:
        pyplot.xlim((x[0]*1e9, x[-1]*1e9))
    if ylim:
        pyplot.ylim(ylim)


if __name__ == '__main__':
    fn = '/home/cbrunet/Copy/PhD/Reports/RCF/TOF/rcf4/rcf4-4Feb2015/LCP.txt'
    data = read(fn)
    plot(data)
    print(data)
    pyplot.show()
