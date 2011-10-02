import test.type.suite
import test.codec.ber.suite
import test.codec.cer.suite
import test.codec.der.suite
from pyasn1.error import PyAsn1Error
try:
    import unittest
except ImportError:
    raise PyAsn1Error(
        'PyUnit package\'s missing. See http://pyunit.sourceforge.net/'
        )

suite = unittest.TestSuite()
for m in (
    test.type.suite,
    test.codec.ber.suite,
    test.codec.cer.suite,
    test.codec.der.suite
    ):
    suite.addTest(getattr(m, 'suite'))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
