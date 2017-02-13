#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import sys
from pyasn1.type import char, univ, constraint
from pyasn1.compat.octets import ints2octs
from pyasn1.error import PyAsn1Error

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class UTF8StringTestCase(unittest.TestCase):

    def setUp(self):
        self.asn1String = char.UTF8String(ints2octs([209, 132, 208, 176]))
        self.pythonString = ints2octs([209, 132, 208, 176]).decode('utf-8')

    def testUnicode(self):
        assert self.asn1String == self.pythonString, 'unicode init fails'

    def testLength(self):
        assert len(self.asn1String) == len(self.pythonString), 'unicode len() fails'

    def testSizeConstraint(self):
        asn1Spec = char.UTF8String(subtypeSpec=constraint.ValueSizeConstraint(1, 1))

        try:
            asn1Spec.clone(ints2octs([0xd1, 0x84, 0xd1, 0x84]))
        except PyAsn1Error:
            pass
        else:
            assert False, 'Size constraint tolerated'

        try:
            asn1Spec.clone(ints2octs([0xd1, 0x84]))
        except PyAsn1Error:
            assert False, 'Size constraint failed'

    if sys.version_info[0] <= 2:
        def testStr(self):
            assert str(self.asn1String) == self.pythonString.encode('utf-8'), '__str__() fails'

        def testInit(self):
            assert char.UTF8String(unicode('abc')) == 'abc'
            assert char.UTF8String('abc') == 'abc'
            assert char.UTF8String([97, 98, 99]) == 'abc'
#            assert char.UTF8String(map(lambda x: x, [97, 98, 99])) == 'abc'
    else:
        def testStr(self):
            assert str(self.asn1String) == self.pythonString, '__str__() fails'

        def testInit(self):
            assert char.UTF8String(bytes('abc', 'utf-8')) == 'abc'
            assert char.UTF8String('abc') == 'abc'
            assert char.UTF8String([97, 98, 99]) == 'abc'
#            assert char.UTF8String(map(lambda x: x, [97, 98, 99])) == 'abc'

    def testInitFromAsn1(self):
            assert char.UTF8String(char.UTF8String('abc')) == 'abc'
            assert char.UTF8String(univ.OctetString('abc')) == 'abc'

    def testAsOctets(self):
        assert self.asn1String.asOctets() == self.pythonString.encode('utf-8'), 'testAsOctets() fails'

    def testAsNumbers(self):
        assert self.asn1String.asNumbers() == (209, 132, 208, 176), 'testAsNumbers() fails'

    def testSeq(self):
        assert self.asn1String[0] == self.pythonString[0], '__getitem__() fails'

    # def testEmpty(self):
    #     try:
    #         str(char.UTF8String())
    #     except PyAsn1Error:
    #         pass
    #     else:
    #         assert 0, 'Value operation on ASN1 type tolerated'

    def testAdd(self):
        assert self.asn1String + 'q' == self.pythonString + 'q', '__add__() fails'

    def testRadd(self):
        assert 'q' + self.asn1String == 'q' + self.pythonString, '__radd__() fails'

    def testMul(self):
        assert self.asn1String * 2 == self.pythonString * 2, '__mul__() fails'

    def testRmul(self):
        assert 2 * self.asn1String == 2 * self.pythonString, '__rmul__() fails'

    def testContains(self):
        assert self.pythonString in self.asn1String
        assert 'q' + self.pythonString not in self.asn1String

#    if sys.version_info[:2] > (2, 4):
#        def testReverse(self):
#            assert reversed(self.asn1String) == self.pythonString[1] + self.pythonString[0]


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
