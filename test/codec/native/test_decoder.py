#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyasn1.type import tag, namedtype, univ, char
from pyasn1.codec.native import decoder
from pyasn1.error import PyAsn1Error


class BadAsn1SpecTestCase(unittest.TestCase):
    def testBadSpec(self):
        try:
            decoder.decode('', asn1Spec='not an Asn1Item')
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Invalid asn1Spec accepted'


class IntegerDecoderTestCase(unittest.TestCase):
    def testPosInt(self):
        assert decoder.decode(12, asn1Spec=univ.Integer()) == univ.Integer(12)

    def testNegInt(self):
        assert decoder.decode(-12, asn1Spec=univ.Integer()) == univ.Integer(-12)


class BooleanDecoderTestCase(unittest.TestCase):
    def testTrue(self):
        assert decoder.decode(True, asn1Spec=univ.Boolean()) == univ.Boolean(True)

    def testTrueNeg(self):
        assert decoder.decode(False, asn1Spec=univ.Boolean()) == univ.Boolean(False)


class BitStringDecoderTestCase(unittest.TestCase):
    def testSimple(self):
        assert decoder.decode('11111111', asn1Spec=univ.BitString()) == univ.BitString(hexValue='ff')


class OctetStringDecoderTestCase(unittest.TestCase):
    def testSimple(self):
        assert decoder.decode('Quick brown fox', asn1Spec=univ.OctetString()) == univ.OctetString('Quick brown fox')


class NullDecoderTestCase(unittest.TestCase):
    def testNull(self):
        assert decoder.decode(None, asn1Spec=univ.Null()) == univ.Null()


class ObjectIdentifierDecoderTestCase(unittest.TestCase):
    def testOne(self):
        assert decoder.decode('1.3.6.11', asn1Spec=univ.ObjectIdentifier()) == univ.ObjectIdentifier('1.3.6.11')


class RealDecoderTestCase(unittest.TestCase):
    def testSimple(self):
        assert decoder.decode(1.33, asn1Spec=univ.Real()) == univ.Real(1.33)


class SequenceDecoderTestCase(unittest.TestCase):
    def setUp(self):
        self.s = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null()),
                namedtype.NamedType('first-name', univ.OctetString()),
                namedtype.NamedType('age', univ.Integer(33))
            )
        )

    def testSimple(self):
        s = self.s.clone()
        s[0] = univ.Null()
        s[1] = univ.OctetString('xx')
        s[2] = univ.Integer(33)
        assert decoder.decode({'place-holder': None, 'first-name': 'xx', 'age': 33}, asn1Spec=self.s) == s


class ChoiceDecoderTestCase(unittest.TestCase):
    def setUp(self):
        self.s = univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null()),
                namedtype.NamedType('first-name', univ.OctetString()),
                namedtype.NamedType('age', univ.Integer(33))
            )
        )

    def testSimple(self):
        s = self.s.clone()
        s[1] = univ.OctetString('xx')
        assert decoder.decode({'first-name': 'xx'}, asn1Spec=self.s) == s


class AnyDecoderTestCase(unittest.TestCase):
    def setUp(self):
        self.s = univ.Any()

    def testSimple(self):
        assert decoder.decode('fox', asn1Spec=univ.Any()) == univ.Any('fox')


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
