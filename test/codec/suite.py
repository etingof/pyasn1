#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
from sys import path, version_info
from os.path import sep

path.insert(1, path[0] + sep + 'codec' + sep + 'ber')
import ber.suite

path.insert(1, path[0] + sep + 'codec' + sep + 'cer')
import cer.suite

path.insert(1, path[0] + sep + 'codec' + sep + 'der')
import der.suite

path.insert(1, path[0] + sep + 'codec' + sep + 'native')
import native.suite

if version_info[0:2] < (2, 7) or \
        version_info[0:2] in ((3, 0), (3, 1)):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest

suite = unittest.TestSuite()
for m in (ber.suite, cer.suite, der.suite, native.suite):
    suite.addTest(getattr(m, 'suite'))


def runTests():
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    runTests()
