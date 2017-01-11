#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import test_debug

from sys import path, version_info
from os.path import sep

path.insert(1, path[0] + sep + 'type')
import type.suite

path.insert(1, path[0] + sep + 'codec')
import codec.suite

if version_info[0:2] < (2, 7) or \
                version_info[0:2] in ((3, 0), (3, 1)):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest

suite = unittest.TestSuite()

loader = unittest.TestLoader()
suite.addTest(loader.loadTestsFromModule(test_debug))

for m in type.suite, codec.suite:
    suite.addTest(getattr(m, 'suite'))

def runTests():
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    runTests()
