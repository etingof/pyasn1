#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
import sys
import unittest

from pyasn1 import debug
from pyasn1 import error
from tests.base import BaseTestCase


class DebugCaseBase(BaseTestCase):
    def testKnownFlags(self):
        debug.setLogger(0)
        debug.setLogger(debug.Debug('all', 'encoder', 'decoder'))
        debug.setLogger(0)

    def testUnknownFlags(self):
        self.assertRaises(
            error.PyAsn1Error, debug.Debug, 'all', 'unknown', loggerName='xxx')


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
