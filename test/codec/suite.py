from sys import path
from os.path import sep
path.insert(1, path[0]+sep+'codec'+sep+'ber')
import ber.suite
path.insert(1, path[0]+sep+'codec'+sep+'cer')
import cer.suite
path.insert(1, path[0]+sep+'codec'+sep+'der')
import der.suite
from pyasn1.error import PyAsn1Error
try:
    import unittest
except ImportError:
    raise PyAsn1Error(
        'PyUnit package\'s missing. See http://pyunit.sourceforge.net/'
        )

suite = unittest.TestSuite()
for m in (
    ber.suite,
    cer.suite,
    der.suite
    ):
    suite.addTest(getattr(m, 'suite'))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
