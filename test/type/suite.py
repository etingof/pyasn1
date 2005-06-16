import tag, constraint, namedtype, univ
from pyasn1.error import PyAsn1Error
try:
    import unittest
except ImportError:
    raise PyAsn1Error(
        'PyUnit package\'s missing. See http://pyunit.sourceforge.net/'
        )

suite = unittest.TestSuite()
loader = unittest.TestLoader()
for m in (tag, constraint, namedtype, univ):
    suite.addTest(loader.loadTestsFromModule(m))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
