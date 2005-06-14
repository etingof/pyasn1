import type.suite
import codec.ber.suite
import codec.cer.suite
import codec.der.suite
try:
    import unittest
except ImportError:
    raise error.PyAsn1Error(
        'PyUnit package\'s missing. See http://pyunit.sourceforge.net/'
        )

suite = unittest.TestSuite()
for m in (
    type.suite,
    codec.ber.suite,
    codec.cer.suite,
    codec.der.suite
    ):
    suite.addTest(getattr(m, 'suite'))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
