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

"""Test suite for slrc module"""

import unittest

from fibermodes.slrc import SLRC


class TestSLRC(unittest.TestCase):

    """Test suite for SLRC class"""

    def testScalar(self):
        x = SLRC(3.14)
        self.assertEqual(x.value, 3.14)
        self.assertEqual(x.kind, 'scalar')
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0], 3.14)
        visited = False
        for v in x:
            self.assertEqual(v, 3.14)
            visited = True
        self.assertTrue(visited)
        self.assertEqual(x(), 3.14)

    def testList(self):
        testList = [1, 2, 3]
        x = SLRC(testList)
        self.assertEqual(x.value, testList)
        self.assertEqual(x.kind, 'list')
        self.assertEqual(len(x), 3)
        for i, v in enumerate(testList):
            self.assertEqual(x[i], v)
        visited = False
        for v, t in zip(x, testList):
            self.assertEqual(v, t)
            visited = True
        self.assertTrue(visited)
        self.assertEqual(x(), testList)

    def testUnorderedList(self):
        testList = [1, 4, 2, 5, 3]
        x = SLRC(testList)
        self.assertEqual(x.value, sorted(testList))
        self.assertEqual(x.kind, 'list')
        self.assertEqual(len(x), 5)
        for i, v in enumerate(sorted(testList)):
            self.assertEqual(x[i], v)
        visited = False
        for v, t in zip(x, sorted(testList)):
            self.assertEqual(v, t)
            visited = True
        self.assertTrue(visited)
        self.assertEqual(x(), sorted(testList))

    def testRange(self):
        testRange = {'start': 0, 'end': 5, 'num': 6}
        testList = [0, 1, 2, 3, 4, 5]
        x = SLRC(testRange)
        self.assertEqual(x.value, testList)
        self.assertEqual(x.kind, 'range')
        self.assertEqual(len(x), testRange['num'])
        for i, v in enumerate(testList):
            self.assertEqual(x[i], v)
        visited = False
        for v, t in zip(x, testList):
            self.assertEqual(v, t)
            visited = True
        self.assertTrue(visited)
        self.assertEqual(x(), testList)

    def testCode(self):
        testCode = "x = args[0]; return 2 * x"
        x = SLRC(testCode)
        f = x.value
        self.assertEqual(f(2), 4)
        self.assertEqual(len(x), 1)
        f = x[0]
        self.assertEqual(f(1), 2)
        self.assertEqual(x(3), 6)  # test __call__

    def testMathCode(self):
        """Test if math module is available"""
        testCode = "return math.pi"
        x = SLRC(testCode)
        self.assertAlmostEqual(x(), 3.141592653589793)

    def testBadCode(self):
        """Test execution of not allowed code"""
        testCode = "import os"
        x = SLRC(testCode)
        with self.assertRaises(ImportError):
            x()

        testCode = "return globals()"
        x = SLRC(testCode)
        with self.assertRaises(NameError):
            x()

    def testConvertScalarToList(self):
        x = SLRC(5)
        x.kind = 'list'
        self.assertEqual(x.value, [5])

    def testConvertScalarToRange(self):
        x = SLRC(5)
        x.kind = 'range'
        self.assertEqual(x.value, [5])

    def testConvertScalarToCode(self):
        x = SLRC(5)
        x.kind = 'code'
        self.assertEqual(x(), 5)

    def testConvertListToScalar(self):
        x = SLRC([1, 2, 3])
        x.kind = 'scalar'
        self.assertEqual(x.value, 1)

    def testConvertListToRange(self):
        x = SLRC([1, 4, 5])
        x.kind = 'range'
        self.assertEqual(x.value, [1, 3, 5])

    def testConvertListToCode(self):
        x = SLRC([1, 2, 3])
        x.kind = 'code'
        self.assertEqual(x(), 1)

    def testConvertRangeToScalar(self):
        testRange = {'start': 0, 'end': 5, 'num': 6}
        x = SLRC(testRange)
        x.kind = 'scalar'
        self.assertEqual(x.value, 0)

    def testConvertRangeToList(self):
        testRange = {'start': 0, 'end': 5, 'num': 6}
        x = SLRC(testRange)
        x.kind = 'list'
        self.assertEqual(x.value, [0, 1, 2, 3, 4, 5])

    def testConvertRangeToCode(self):
        testRange = {'start': 0, 'end': 5, 'num': 6}
        x = SLRC(testRange)
        x.kind = 'code'
        self.assertEqual(x(), 0)

    def testConvertCodeToAnything(self):
        testCode = "return 0"
        x = SLRC(testCode)
        x.kind = "scalar"
        self.assertEqual(x.value, 0)

        x = SLRC(testCode)
        x.kind = "list"
        self.assertEqual(x.value, [0])

        x = SLRC(testCode)
        x.kind = "range"
        self.assertEqual(x.value, [0, 1])


if __name__ == "__main__":
    unittest.main()
