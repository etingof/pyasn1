#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
import unittest

suite = unittest.TestLoader().loadTestsFromNames(
    ['tests.compat.test_integer.suite',
     'tests.compat.test_octets.suite']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
