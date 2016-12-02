import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from csets.cset import CSet


class TestCSet(unittest.TestCase):

    def test_cset_with_null(self):
        cset = CSet('a,an,the,')
        self.assertTrue(cset.include(''))
        self.assertTrue(cset.include('<null>'))

if __name__ == '__main__':
    unittest.main()
