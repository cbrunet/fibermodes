'''
Created on 2014-05-01

@author: cbrunet
'''
import unittest

from fibermodes import Mode


class TestMode(unittest.TestCase):

    def testEquality(self):
        self.assertEqual(Mode('HE', 1, 1), Mode('HE', 1, 1))
        self.assertNotEqual(Mode('HE', 1, 1), Mode('HE', 2, 1))
        self.assertEqual(Mode('HE', 1, 1), Mode('LP', 0, 1))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
