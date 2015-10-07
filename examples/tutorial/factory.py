"""This is the examples for the second tutorial: Using FiberFactory."""

from fibermodes import FiberFactory, Mode
import datetime
from matplotlib import pyplot
import numpy


def example1():
    """1. Defining fiber layers"""
    factory = FiberFactory()

    factory.name = "Name of your fiber"
    factory.author = "Your Name"
    factory.description = "Description of your fiber"

    print('crdate:', datetime.datetime.fromtimestamp(
          int(factory.crdate)).strftime('%Y-%m-%d %H:%M:%S'))
    print('tstamp:', datetime.datetime.fromtimestamp(
          int(factory.tstamp)).strftime('%Y-%m-%d %H:%M:%S'))

    # Default parameters
    factory.addLayer()
    # Comp material: molar fraction
    factory.addLayer(pos=0, name="core", geometry="StepIndex", radius=4e-6,
                     material="SiO2GeO2", x=0.1)
    # Comp material: index and wavelength
    factory.addLayer(pos=1, name="trench", radius=6e-6, material="SiO2F",
                     index=1.441, wl=1550e-9)

    # Getting information from layers
    print('Name of layer 0:', factory.layers[0].name)
    print('Radius of layer 1:', factory.layers[1].radius)
    factory.layers[2].name = "cladding"
    print('Name of layer 2:', factory.layers[2].name)


def example2():
    """2. Creating families of fibers: list of parameters"""

    # Varying core radius
    factory = FiberFactory()
    factory.addLayer(name="core", radius=[1e-6, 2e-6, 3e-6, 4e-6, 5e-6],
                     index=1.474)
    factory.addLayer()

    for i, fiber in enumerate(factory):
        print(factory.layers[0].radius[i],
              fiber.neff(Mode("HE", 1, 1), 1550e-9))

    # Varying core index
    n = numpy.linspace(1.454, 1.494)
    factory = FiberFactory()
    factory.addLayer(name="core", radius=4e-6, index=n)
    factory.addLayer(name="cladding")
    fibers = list(factory)
    print(fibers)

    neff = numpy.zeros(n.shape)
    for i, fiber in enumerate(factory):
        neff[i] = fiber.neff(Mode("HE", 1, 1), 1550e-9)

    pyplot.plot(n, neff)
    pyplot.title("neff as function of core index (HE 1,1 mode)")
    pyplot.xlabel("core index")
    pyplot.ylabel("effective index")
    pyplot.show()


def example3():
    """2. Creating families of fibers: range of parameters"""
    factory = FiberFactory()
    factory.addLayer(name="core",
                     radius={'start': 2e-6, 'end': 5e-6, 'num': 10},
                     index=[1.454, 1.464, 1.474])
    factory.addLayer(name="cladding")
    print('Number of generated fibers:', len(factory))


def example4():
    """2. Creating families of fibers: parameter as code"""
    factory = FiberFactory()
    factory.addLayer(radius="return 4e-6", index="return 1.474")
    factory.addLayer()
    fiber = factory[0]
    print('core radius:', fiber.outerRadius(0))
    print('core index:', fiber.maxIndex(0, 1550e-9))

    factory = FiberFactory()
    factory.addLayer(radius={'start': 1e-6, 'end': 10e-6, 'num': 10})
    factory.addLayer(radius="return r[0] + 2e-6", index=1.474)
    factory.addLayer()
    print('layer 0 radius', '/', 'layer 1 radius')
    for fiber in factory:
        print(fiber.outerRadius(0), '/', fiber.outerRadius(1))


def example5():
    """Another code example, and loading / saving factory."""
    code = """V = 10
    ncl = 1.444
    k0 = 2 * pi / 1550e-9
    n = sqrt((V / (k0 * r[0]))**2 - ncl**2)
    return n
    """
    factory = FiberFactory()
    factory.addLayer(radius={'start': 1e-6, 'end': 10e-6, 'num': 10},
                     index=code)
    factory.addLayer(index=1.444)
    print(len(factory))
    print('crdate:', datetime.datetime.fromtimestamp(
          int(factory.crdate)).strftime('%Y-%m-%d %H:%M:%S'))
    print('tstamp:', datetime.datetime.fromtimestamp(
          int(factory.tstamp)).strftime('%Y-%m-%d %H:%M:%S'))

    with open('myfiber.json', 'w') as f:
        factory.dump(f)

    with open('myfiber.json', 'r') as f:
        factory.load(f)
    print(len(factory))
    print('crdate:', datetime.datetime.fromtimestamp(
          int(factory.crdate)).strftime('%Y-%m-%d %H:%M:%S'))
    print('tstamp:', datetime.datetime.fromtimestamp(
          int(factory.tstamp)).strftime('%Y-%m-%d %H:%M:%S'))

    factory = FiberFactory('myfiber.json')
    print(len(factory))
    print('crdate:', datetime.datetime.fromtimestamp(
          int(factory.crdate)).strftime('%Y-%m-%d %H:%M:%S'))
    print('tstamp:', datetime.datetime.fromtimestamp(
          int(factory.tstamp)).strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    example1()
    example2()
    example3()
    example4()
    example5()
