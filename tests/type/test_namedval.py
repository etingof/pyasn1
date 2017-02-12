#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import sys
try:
    import unittest2 as unittest

except ImportError:
    import unittest

from pyasn1.type import namedval


class NamedValuesCaseBase(unittest.TestCase):
    def setUp(self):
        self.e = namedval.NamedValues(('off', 0), ('on', 1))

    def testIter(self):
        off, on = self.e
        assert off == ('off', 0) or on == ('on', 1), 'unpack fails'

    def testRepr(self):
        assert eval(repr(self.e), {'NamedValues': namedval.NamedValues}) == self.e, 'repr() fails'


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
