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


import unittest

from fibermodes.mode import Mode, Family, HE11


class TestMode(unittest.TestCase):

    def testEquality(self):
        self.assertEqual(Mode('HE', 1, 1), Mode('HE', 1, 1))
        self.assertNotEqual(Mode('HE', 1, 1), Mode('HE', 2, 1))
        self.assertNotEqual(Mode('HE', 1, 1), Mode('LP', 0, 1))

    def testLpEq(self):
        mode = Mode(Family.HE, 1, 1)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 0, 1))
        mode = Mode(Family.HE, 2, 1)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 1, 1))
        mode = Mode(Family.HE, 1, 2)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 0, 2))
        mode = Mode(Family.EH, 1, 1)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 2, 1))
        mode = Mode(Family.TM, 0, 1)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 1, 1))
        mode = Mode(Family.TE, 0, 1)
        self.assertEqual(mode.lpEq(), Mode(Family.LP, 1, 1))

    def testSortModes(self):
        modes = [
            Mode(Family.LP, 0, 1),
            Mode(Family.HE, 1, 1),
            Mode(Family.LP, 1, 1),
            Mode(Family.TE, 0, 1),
            Mode(Family.HE, 2, 1),
            Mode(Family.TM, 0, 1),
            Mode(Family.LP, 2, 1),
            Mode(Family.EH, 1, 1),
            Mode(Family.HE, 3, 1),
            Mode(Family.EH, 2, 1),
            Mode(Family.HE, 4, 1),
            Mode(Family.LP, 0, 2),
            Mode(Family.HE, 1, 2),
            Mode(Family.TE, 0, 2),
            Mode(Family.HE, 2, 2),
            Mode(Family.TM, 0, 2),
            Mode(Family.EH, 1, 2),
            Mode(Family.HE, 3, 2),
            Mode(Family.EH, 2, 2),
            Mode(Family.HE, 4, 2)
            ]
        for i in range(len(modes)):
            for j in range(len(modes)):
                if i < j:
                    self.assertLess(modes[i], modes[j])
                    self.assertLessEqual(modes[i], modes[j])
                    self.assertGreater(modes[j], modes[i])
                    self.assertGreaterEqual(modes[j], modes[i])
                    self.assertNotEqual(modes[i], modes[j])
                elif i > j:
                    self.assertLess(modes[j], modes[i])
                    self.assertLessEqual(modes[j], modes[i])
                    self.assertGreater(modes[i], modes[j])
                    self.assertGreaterEqual(modes[i], modes[j])
                    self.assertNotEqual(modes[j], modes[i])
                else:
                    self.assertEqual(modes[i], modes[j])
                    self.assertLessEqual(modes[i], modes[j])
                    self.assertGreaterEqual(modes[i], modes[j])

    def testColor(self):
        # HE color is blue
        color = HE11.color()
        self.assertGreater(color[2], color[1])
        self.assertGreater(color[2], color[0])
        self.assertLess(color[0], 256)
        self.assertLess(color[1], 256)
        self.assertLess(color[2], 256)

        # asint=False
        color = HE11.color(asint=False)
        self.assertGreater(color[2], color[1])
        self.assertGreater(color[2], color[0])
        self.assertLessEqual(color[0], 1)
        self.assertLessEqual(color[1], 1)
        self.assertLessEqual(color[2], 1)

        # different modes == different colors
        co1 = HE11.color()
        co2 = Mode("HE", 1, 2).color()
        co3 = Mode("HE", 2, 1).color()
        co4 = Mode("EH", 1, 1).color()
        self.assertNotEqual(co1, co2)
        self.assertNotEqual(co1, co3)
        self.assertNotEqual(co2, co3)
        self.assertNotEqual(co1, co4)


if __name__ == "__main__":
    unittest.main()
