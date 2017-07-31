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

from pyasn1.type import namedtype, univ, useful
from pyasn1.codec.cer import encoder
from pyasn1.compat.octets import ints2octs
from pyasn1.error import PyAsn1Error


class BooleanEncoderTestCase(unittest.TestCase):
    def testTrue(self):
        assert encoder.encode(univ.Boolean(1)) == ints2octs((1, 1, 255))

    def testFalse(self):
        assert encoder.encode(univ.Boolean(0)) == ints2octs((1, 1, 0))


class BitStringEncoderTestCase(unittest.TestCase):
    def testShortMode(self):
        assert encoder.encode(
            univ.BitString((1, 0) * 5)
        ) == ints2octs((3, 3, 6, 170, 128))

    def testLongMode(self):
        assert encoder.encode(univ.BitString((1, 0) * 501)) == ints2octs((3, 127, 6) + (170,) * 125 + (128,))


class OctetStringEncoderTestCase(unittest.TestCase):
    def testShortMode(self):
        assert encoder.encode(
            univ.OctetString('Quick brown fox')
        ) == ints2octs((4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 32, 102, 111, 120))

    def testLongMode(self):
        assert encoder.encode(
            univ.OctetString('Q' * 1001)
        ) == ints2octs((36, 128, 4, 130, 3, 232) + (81,) * 1000 + (4, 1, 81, 0, 0))


class SetEncoderTestCase(unittest.TestCase):
    def setUp(self):
        self.s = univ.Set(componentType=namedtype.NamedTypes(
            namedtype.NamedType('place-holder', univ.Null('')),
            namedtype.OptionalNamedType('first-name', univ.OctetString()),
            namedtype.DefaultedNamedType('age', univ.Integer(33))
        ))

    def __init(self):
        self.s.clear()
        self.s.setComponentByPosition(0)

    def __initWithOptional(self):
        self.s.clear()
        self.s.setComponentByPosition(0)
        self.s.setComponentByPosition(1, 'quick brown')

    def __initWithDefaulted(self):
        self.s.clear()
        self.s.setComponentByPosition(0)
        self.s.setComponentByPosition(2, 1)

    def __initWithOptionalAndDefaulted(self):
        self.s.clear()
        self.s.setComponentByPosition(0, univ.Null(''))
        self.s.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.s.setComponentByPosition(2, univ.Integer(1))

    def testIndefMode(self):
        self.__init()
        assert encoder.encode(self.s) == ints2octs((49, 128, 5, 0, 0, 0))

    def testWithOptionalIndefMode(self):
        self.__initWithOptional()
        assert encoder.encode(
            self.s
        ) == ints2octs((49, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 5, 0, 0, 0))

    def testWithDefaultedIndefMode(self):
        self.__initWithDefaulted()
        assert encoder.encode(
            self.s
        ) == ints2octs((49, 128, 2, 1, 1, 5, 0, 0, 0))

    def testWithOptionalAndDefaultedIndefMode(self):
        self.__initWithOptionalAndDefaulted()
        assert encoder.encode(
            self.s
        ) == ints2octs((49, 128, 2, 1, 1, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 5, 0, 0, 0))


class SetWithChoiceEncoderTestCase(unittest.TestCase):
    def setUp(self):
        c = univ.Choice(componentType=namedtype.NamedTypes(
            namedtype.NamedType('actual', univ.Boolean(0))
        ))
        self.s = univ.Set(componentType=namedtype.NamedTypes(
            namedtype.NamedType('place-holder', univ.Null('')),
            namedtype.NamedType('status', c)
        ))

    def testIndefMode(self):
        self.s.setComponentByPosition(0)
        self.s.setComponentByName('status')
        self.s.getComponentByName('status').setComponentByPosition(0, 1)
        assert encoder.encode(self.s) == ints2octs((49, 128, 1, 1, 255, 5, 0, 0, 0))


class GeneralizedTimeEncoderTestCase(unittest.TestCase):
    #    def testExtraZeroInSeconds(self):
    #        try:
    #            assert encoder.encode(
    #                useful.GeneralizedTime('20150501120112.10Z')
    #            )
    #        except PyAsn1Error:
    #            pass
    #        else:
    #            assert 0, 'Meaningless trailing zero in fraction part tolerated'

    def testLocalTimezone(self):
        try:
            assert encoder.encode(
                useful.GeneralizedTime('20150501120112.1+0200')
            )
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Local timezone tolerated'

    def testMissingTimezone(self):
        try:
            assert encoder.encode(
                useful.GeneralizedTime('20150501120112.1')
            )
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Missing timezone tolerated'


    def testDecimalCommaPoint(self):
        try:
            assert encoder.encode(
                    useful.GeneralizedTime('20150501120112,1Z')
             )
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Decimal comma tolerated'

    def testWithSubseconds(self):
        assert encoder.encode(
                    useful.GeneralizedTime('20170801120112.59Z')
             ) == ints2octs((24, 18, 50, 48, 49, 55, 48, 56, 48, 49, 49, 50, 48, 49, 49, 50, 46, 53, 57, 90))

    def testWithSeconds(self):
        assert encoder.encode(
                    useful.GeneralizedTime('20170801120112Z')
             ) == ints2octs((24, 15, 50, 48, 49, 55, 48, 56, 48, 49, 49, 50, 48, 49, 49, 50, 90))

    def testWithMinutes(self):
        assert encoder.encode(
                    useful.GeneralizedTime('201708011201Z')
             ) == ints2octs((24, 13, 50, 48, 49, 55, 48, 56, 48, 49, 49, 50, 48, 49, 90))


class UTCTimeEncoderTestCase(unittest.TestCase):
    def testFractionOfSecond(self):
        try:
            assert encoder.encode(
                useful.UTCTime('150501120112.10Z')
            )
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Decimal point tolerated'

    def testMissingTimezone(self):
        try:
            assert encoder.encode(
                useful.UTCTime('150501120112')
            ) == ints2octs((23, 13, 49, 53, 48, 53, 48, 49, 49, 50, 48, 49, 49, 50, 90))
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Missing timezone tolerated'

    def testLocalTimezone(self):
        try:
            assert encoder.encode(
                useful.UTCTime('150501120112+0200')
            )
        except PyAsn1Error:
            pass
        else:
            assert 0, 'Local timezone tolerated'

    def testWithSeconds(self):
        assert encoder.encode(
                    useful.UTCTime('990801120112Z')
             ) == ints2octs((23, 13, 57, 57, 48, 56, 48, 49, 49, 50, 48, 49, 49, 50, 90))

    def testWithMinutes(self):
        assert encoder.encode(
                    useful.UTCTime('9908011201Z')
             ) == ints2octs((23, 11, 57, 57, 48, 56, 48, 49, 49, 50, 48, 49, 90))


class NestedOptionalSequenceEncoderTestCase(unittest.TestCase):
    def setUp(self):
        inner = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.OptionalNamedType('first-name', univ.OctetString()),
                namedtype.DefaultedNamedType('age', univ.Integer(33)),
            )
        )

        outerWithOptional = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.OptionalNamedType('inner', inner),
            )
        )

        outerWithDefault = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.DefaultedNamedType('inner', inner),
            )
        )

        self.s1 = outerWithOptional
        self.s2 = outerWithDefault

    def __initOptionalWithDefaultAndOptional(self):
        self.s1.clear()
        self.s1[0][0] = 'test'
        self.s1[0][1] = 123
        return self.s1

    def __initOptionalWithDefault(self):
        self.s1.clear()
        self.s1[0][1] = 123
        return self.s1

    def __initOptionalWithOptional(self):
        self.s1.clear()
        self.s1[0][0] = 'test'
        return self.s1

    def __initOptional(self):
        self.s1.clear()
        return self.s1

    def __initDefaultWithDefaultAndOptional(self):
        self.s2.clear()
        self.s2[0][0] = 'test'
        self.s2[0][1] = 123
        return self.s2

    def __initDefaultWithDefault(self):
        self.s2.clear()
        self.s2[0][0] = 'test'
        return self.s2

    def __initDefaultWithOptional(self):
        self.s2.clear()
        self.s2[0][1] = 123
        return self.s2

    def testOptionalWithDefaultAndOptional(self):
        s = self.__initOptionalWithDefaultAndOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 2, 1, 123, 0, 0, 0, 0))

    def testOptionalWithDefault(self):
        s = self.__initOptionalWithDefault()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 2, 1, 123, 0, 0, 0, 0))

    def testOptionalWithOptional(self):
        s = self.__initOptionalWithOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 0, 0, 0, 0))

    def testOptional(self):
        s = self.__initOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 0, 0))

    def testDefaultWithDefaultAndOptional(self):
        s = self.__initDefaultWithDefaultAndOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 2, 1, 123, 0, 0, 0, 0))

    def testDefaultWithDefault(self):
        s = self.__initDefaultWithDefault()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 0, 0, 0, 0))

    def testDefaultWithOptional(self):
        s = self.__initDefaultWithOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 2, 1, 123, 0, 0, 0, 0))


class NestedOptionalChoiceEncoderTestCase(unittest.TestCase):
    def setUp(self):
        layer3 = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.OptionalNamedType('first-name', univ.OctetString()),
                namedtype.DefaultedNamedType('age', univ.Integer(33)),
            )
        )

        layer2 = univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('inner', layer3),
                namedtype.NamedType('first-name', univ.OctetString())
            )
        )

        layer1 = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.OptionalNamedType('inner', layer2),
            )
        )

        self.s = layer1

    def __initOptionalWithDefaultAndOptional(self):
        self.s.clear()
        self.s[0][0][0] = 'test'
        self.s[0][0][1] = 123
        return self.s

    def __initOptionalWithDefault(self):
        self.s.clear()
        self.s[0][0][1] = 123
        return self.s

    def __initOptionalWithOptional(self):
        self.s.clear()
        self.s[0][0][0] = 'test'
        return self.s

    def __initOptional(self):
        self.s.clear()
        return self.s

    def testOptionalWithDefaultAndOptional(self):
        s = self.__initOptionalWithDefaultAndOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 2, 1, 123, 0, 0, 0, 0))

    def testOptionalWithDefault(self):
        s = self.__initOptionalWithDefault()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 2, 1, 123, 0, 0, 0, 0))

    def testOptionalWithOptional(self):
        s = self.__initOptionalWithOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 0, 0, 0, 0))

    def testOptional(self):
        s = self.__initOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 0, 0))


class NestedOptionalSequenceOfEncoderTestCase(unittest.TestCase):
    def setUp(self):
        layer2 = univ.SequenceOf(
            componentType=univ.OctetString()
        )

        layer1 = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.OptionalNamedType('inner', layer2),
            )
        )

        self.s = layer1

    def __initOptionalWithValue(self):
        self.s.clear()
        self.s[0][0] = 'test'
        return self.s

    def __initOptional(self):
        self.s.clear()
        return self.s

    def testOptionalWithValue(self):
        s = self.__initOptionalWithValue()
        assert encoder.encode(s) == ints2octs((48, 128, 48, 128, 4, 4, 116, 101, 115, 116, 0, 0, 0, 0))

    def testOptional(self):
        s = self.__initOptional()
        assert encoder.encode(s) == ints2octs((48, 128, 0, 0))


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
