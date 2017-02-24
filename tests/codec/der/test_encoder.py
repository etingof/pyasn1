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

from pyasn1.type import namedtype, univ
from pyasn1.codec.der import encoder
from pyasn1.compat.octets import ints2octs
from pyasn1.error import PyAsn1Error


class OctetStringEncoderTestCase(unittest.TestCase):
    def testShortMode(self):
        assert encoder.encode(
            univ.OctetString('Quick brown fox')
        ) == ints2octs((4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 32, 102, 111, 120))

    def testIndefMode(self):
        try:
            encoder.encode(univ.OctetString('Quick brown'), defMode=False)
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Indefinite length encoding tolerated'

    def testChunkedMode(self):
        try:
            x = encoder.encode(univ.OctetString('Quick brown'), maxChunkSize=2)
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Chunked encoding tolerated'


class BitStringEncoderTestCase(unittest.TestCase):
    def testShortMode(self):
        assert encoder.encode(
            univ.BitString((1,))
        ) == ints2octs((3, 2, 7, 128))


class SetWithChoiceEncoderTestCase(unittest.TestCase):
    def setUp(self):
        c = univ.Choice(componentType=namedtype.NamedTypes(
            namedtype.NamedType('name', univ.OctetString('')),
            namedtype.NamedType('amount', univ.Integer(0)))
        )
        self.s = univ.Set(componentType=namedtype.NamedTypes(
            namedtype.NamedType('place-holder', univ.Null('')),
            namedtype.NamedType('status', c))
        )

    def testDefMode(self):
        self.s.setComponentByPosition(0)
        self.s.setComponentByName('status')
        self.s.getComponentByName('status').setComponentByPosition(0, 'ann')
        assert encoder.encode(self.s) == ints2octs((49, 7, 4, 3, 97, 110, 110, 5, 0))


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
