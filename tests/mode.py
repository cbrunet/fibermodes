'''
Created on 2014-05-01

@author: cbrunet
'''
import unittest

from fibermodes.mode import Mode, SMode, sortModes, Family


class TestMode(unittest.TestCase):

    def testEquality(self):
        self.assertEqual(Mode('HE', 1, 1), Mode('HE', 1, 1))
        self.assertNotEqual(Mode('HE', 1, 1), Mode('HE', 2, 1))
        self.assertEqual(Mode('HE', 1, 1), Mode('LP', 0, 1))

    def testSortModes(self):
        he11 = SMode(None, Mode(Family.HE, 1, 1), 1.448)
        he12 = SMode(None, Mode(Family.HE, 1, 2), 1.446)
        te01 = SMode(None, Mode(Family.TE, 0, 1), 1.447)

        # Sort empty list
        modes = []
        sortModes(modes)
        self.assertEqual(modes, [])

        # Sort list with only one mode
        modes = [he11]
        cmodes = modes.copy()
        sortModes(modes)
        self.assertEqual(modes, cmodes)

        # Sort list with 3 modes
        modes.insert(0, he12)
        modes.append(te01)
        sortModes(modes)
        self.assertEqual(modes, [he11, te01, he12])

        # Rename modes according to order
        for i in range(len(modes)):
            modes[i].m = 5
        sortModes(modes)
        self.assertEqual(modes, [he11, te01, he12])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
