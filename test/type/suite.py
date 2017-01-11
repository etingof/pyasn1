#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import test_tag
import test_constraint
import test_namedtype
import test_univ
from sys import version_info

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
for m in (test_tag, test_constraint, test_namedtype, test_univ):
    suite.addTest(loader.loadTestsFromModule(m))


def runTests():
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    runTests()
