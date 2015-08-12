
Single-mode fiber
=================

Suppose we have a fiber with the following characteristics:

+------------------------+--------+
| **Radius of the core** | 4.5 µm |
+------------------------+--------+
| **Index of the core**  | 1.4489 |
+------------------------+--------+
| **Index of cladding**  | 1.4444 |
+------------------------+--------+

We want to know the effective index of the HE(1,1) mode.

First we import needed modules::

    from fibermodes import FiberFactory, Mode, ModeFamily, Wavelength

We create a :py:class:`~fibermodes.fiber.factory.FiberFactory` object.
FiberFactory are used to create families of
:py:class:`~fibermodes.fiber.fiber.Fiber` object. However, even in the
case we only need a single fiber, we need to create it using a FiberFactory::

    factory = FiberFactory()
    factory.addLayer(name="core", radius=4.5e-6, material="Fixed", geometry="StepIndex", index=1.4489)
    factory.addLayer(name="cladding", material="Fixed", index=1.4444)

We create an empty factory, and we add the two layers. When **pos** argument
is not specified, layers are added to the end of the fiber. We do not need
to specify **radius** for the cladding, as it is considered to be infinite.
Cladding should always be :py:class:`~fibermodes.fiber.geometry.StepIndex`.

The FiberFactory is an iterator. Therefore, we could loop through generated
Fibers within a for loop. We can also access generated fibers using index::

    fiber = factory[0]

In this case, there is only one fiber generated. Therefore, specifying
an index other than zero would raise an exception.

We can now solve for effective indices of this fiber. First, we create
a :py:class:`~fibermodes.mode.Mode` object::

    he11 = Mode(ModeFamily.HE, 1, 1)

The constructor of Mode also accept a string to specify the family.

The effective index also depends on the :py:class:`~fibermodes.wavelength.Wavelength`.
We can explicitly build a Wavelength object::

    wl = Wavelength(1550e-9)

Now we can compute the effective index::

    neff = fiber.neff(he11, wl)

The wavelength parameter could also simply be given as a float number (in meters).

Suppose we want to be sure the designed fiber is really single mode. We could
request the fiber to find all the modes at a given wavelength::

    modes = fiber.findVmodes(wl)

You can now explore the documentation of the :py:class:`~fibermodes.fiber.fiber.Fiber`
class to learn about other available functions. 
