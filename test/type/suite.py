from  pyasn1 import error
import tag, constraint, namedtype, univ
try:
    import unittest
except ImportError:
    raise error.PyAsn1Error(
        'PyUnit package\'s missing. See http://pyunit.sourceforge.net/'
        )

suite = unittest.TestSuite()
loader = unittest.TestLoader()
for m in (tag, constraint, namedtype, univ):
    suite.addTest(loader.loadTestsFromModule(m))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
