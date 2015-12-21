"""This is the examples for the first tutorial: Single-mode fiber."""


from fibermodes import FiberFactory, HE11, Wavelength


factory = FiberFactory()
factory.addLayer(name="core", radius=4.5e-6, material="Fixed",
                 geometry="StepIndex", index=1.4489)
factory.addLayer(name="cladding", material="Fixed", index=1.4444)
print(factory)

fiber = factory[0]
print(fiber)

he11 = HE11
print(he11)

wl = Wavelength(1550e-9)
print(wl)

neff = fiber.neff(he11, wl)
print(neff)

modes = fiber.findVmodes(wl)
print(modes)
