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
from pyasn1.error import PyAsn1Error


class NamedTypeCaseBase(unittest.TestCase):
    def setUp(self):
        self.e = namedtype.NamedType('age', univ.Integer(0))

    def testIter(self):
        n, t = self.e
        assert n == 'age' or t == univ.Integer(), 'unpack fails'

    def testRepr(self):
        assert eval(repr(self.e), {'NamedType': namedtype.NamedType, 'Integer': univ.Integer}) == self.e, 'repr() fails'


class NamedTypesCaseBase(unittest.TestCase):
    def setUp(self):
        self.e = namedtype.NamedTypes(
            namedtype.NamedType('first-name', univ.OctetString('')),
            namedtype.OptionalNamedType('age', univ.Integer(0)),
            namedtype.NamedType('family-name', univ.OctetString(''))
        )

    def testRepr(self):
        assert eval(repr(self.e), {'NamedTypes': namedtype.NamedTypes, 'NamedType': namedtype.NamedType,
                                   'OptionalNamedType': namedtype.OptionalNamedType, 'Integer': univ.Integer,
                                   'OctetString': univ.OctetString}) == self.e, 'repr() fails'

    def testContains(self):
        assert 'first-name' in self.e
        assert '<missing>' not in self.e

    # noinspection PyUnusedLocal
    def testGetItem(self):
        assert self.e[0] == namedtype.NamedType('first-name', univ.OctetString(''))

    def testIter(self):
        assert list(self.e) == ['first-name', 'age', 'family-name']

    def testGetTypeByPosition(self):
        assert self.e.getTypeByPosition(0) == univ.OctetString(''), \
            'getTypeByPosition() fails'

    def testGetNameByPosition(self):
        assert self.e.getNameByPosition(0) == 'first-name', \
            'getNameByPosition() fails'

    def testGetPositionByName(self):
        assert self.e.getPositionByName('first-name') == 0, \
            'getPositionByName() fails'

    def testGetTypesNearPosition(self):
        assert self.e.getTagMapNearPosition(0).getPosMap() == {
            univ.OctetString.tagSet: univ.OctetString('')
        }
        assert self.e.getTagMapNearPosition(1).getPosMap() == {
            univ.Integer.tagSet: univ.Integer(0),
            univ.OctetString.tagSet: univ.OctetString('')
        }
        assert self.e.getTagMapNearPosition(2).getPosMap() == {
            univ.OctetString.tagSet: univ.OctetString('')
        }

    def testGetTagMap(self):
        assert self.e.getTagMap().getPosMap() == {
            univ.OctetString.tagSet: univ.OctetString(''),
            univ.Integer.tagSet: univ.Integer(0)
        }

    def testStrTagMap(self):
        assert 'TagMap' in str(self.e.getTagMap())
        assert 'OctetString' in str(self.e.getTagMap())
        assert 'Integer' in str(self.e.getTagMap())

    def testReprTagMap(self):
        assert 'TagMap' in repr(self.e.getTagMap())
        assert 'OctetString' in repr(self.e.getTagMap())
        assert 'Integer' in repr(self.e.getTagMap())

    def testGetTagMapWithDups(self):
        try:
            self.e.getTagMap(1)
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Duped types not noticed'

    def testGetPositionNearType(self):
        assert self.e.getPositionNearType(univ.OctetString.tagSet, 0) == 0
        assert self.e.getPositionNearType(univ.Integer.tagSet, 1) == 1
        assert self.e.getPositionNearType(univ.OctetString.tagSet, 2) == 2


class OrderedNamedTypesCaseBase(unittest.TestCase):
    def setUp(self):
        self.e = namedtype.NamedTypes(
            namedtype.NamedType('first-name', univ.OctetString('')),
            namedtype.NamedType('age', univ.Integer(0))
        )

    def testGetTypeByPosition(self):
        assert self.e.getTypeByPosition(0) == univ.OctetString(''), \
            'getTypeByPosition() fails'


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
