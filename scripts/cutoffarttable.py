
from collections import OrderedDict
from fibermodes import fixedFiber, Mode, ModeFamily, HE11


FIBERS = OrderedDict([
    ('(a)', fixedFiber(1550e-9, [4e-6, 6e-6], [1.47, 1.43, 1.44])),
    ('(b)', fixedFiber(1550e-9, [4e-6, 6e-6], [1.47, 1.45, 1.44])),
    ('(c)', fixedFiber(1550e-9, [4e-6, 6e-6], [1.43, 1.47, 1.44])),
    ('(d)', fixedFiber(1550e-9, [4e-6, 6e-6], [1.45, 1.47, 1.44])),
    ('(e)', fixedFiber(1550e-9, [4e-6, 6e-6], [1.44, 1.47, 1.44])),
    ])

LPMODES = (
           Mode(ModeFamily.LP, 0, 1),
           Mode(ModeFamily.LP, 1, 1),
           Mode(ModeFamily.LP, 2, 1),
           Mode(ModeFamily.LP, 3, 1),
           Mode(ModeFamily.LP, 4, 1),
           Mode(ModeFamily.LP, 5, 1),
           Mode(ModeFamily.LP, 6, 1),
           Mode(ModeFamily.LP, 7, 1),
           Mode(ModeFamily.LP, 0, 2),
           Mode(ModeFamily.LP, 1, 2),
           Mode(ModeFamily.LP, 2, 2),
           Mode(ModeFamily.LP, 3, 2),
           Mode(ModeFamily.LP, 0, 3),
           Mode(ModeFamily.LP, 1, 3),
           )

VMODES = (
          HE11,
          Mode(ModeFamily.TE, 0, 1),
          Mode(ModeFamily.HE, 2, 1),
          Mode(ModeFamily.TM, 0, 1),
          Mode(ModeFamily.EH, 1, 1),
          Mode(ModeFamily.HE, 3, 1),
          Mode(ModeFamily.EH, 2, 1),
          Mode(ModeFamily.HE, 4, 1),
          Mode(ModeFamily.EH, 3, 1),
          Mode(ModeFamily.HE, 5, 1),
          Mode(ModeFamily.EH, 4, 1),
          Mode(ModeFamily.HE, 6, 1),
          Mode(ModeFamily.EH, 5, 1),
          Mode(ModeFamily.HE, 7, 1),
          Mode(ModeFamily.EH, 6, 1),
          Mode(ModeFamily.HE, 8, 1),
          Mode(ModeFamily.HE, 1, 2),
          Mode(ModeFamily.TE, 0, 2),
          Mode(ModeFamily.HE, 2, 2),
          Mode(ModeFamily.TM, 0, 2),
          Mode(ModeFamily.EH, 1, 2),
          Mode(ModeFamily.HE, 3, 2),
          Mode(ModeFamily.EH, 2, 2),
          Mode(ModeFamily.HE, 4, 2),
          Mode(ModeFamily.TE, 0, 3),
          Mode(ModeFamily.HE, 2, 3),
          Mode(ModeFamily.TM, 0, 3),
          )


def saveTable(modes, fname):
    output = "\\begin{{tabular}}{{c{0:s}{0:s}{0:s}{0:s}{0:s}}}\n".format(
        "S[table-format=2.3]")
    output += "{:<16s}".format("Mode")
    for ftype in FIBERS.keys():
        output += "&{:^8}".format("{" + ftype + "}")
    output += "\\\\ \\hline\n"

    co = {}
    for m in modes:
        output += "\\mode{{{}}}{{{}}}{{{}}} ".format(m.family.name, m.nu, m.m)
        for ftype, fiber in FIBERS.items():
            if ftype not in co:
                co[ftype] = {}
            vmin = co[ftype][Mode(m.family, m.nu, m.m-1)] if m.m > 1 else 0
            co[ftype][m] = fiber.cutoffV0(m, vmin)
            output += "& {:>6.3f} ".format(co[ftype][m])
        output += "\\\\\n"

    output += "\\hline\n\\end{tabular}\n"

    with open(fname, 'w') as f:
        f.write(output)

if __name__ == '__main__':
    saveTable(LPMODES, 'lptab.tex')
    saveTable(VMODES, 'vtab.tex')
