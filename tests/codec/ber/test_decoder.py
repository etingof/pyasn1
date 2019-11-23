#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
import gzip
import io
import os
import sys
import tempfile
import unittest
import zipfile

from pyasn1 import error
from pyasn1.codec import streaming
from pyasn1.codec.ber import decoder
from pyasn1.codec.ber import eoo
from pyasn1.compat.octets import ints2octs
from pyasn1.compat.octets import null
from pyasn1.compat.octets import str2octs
from pyasn1.type import char
from pyasn1.type import namedtype
from pyasn1.type import opentype
from pyasn1.type import tag
from pyasn1.type import univ
from tests.base import BaseTestCase


class LargeTagDecoderTestCase(BaseTestCase):
    def testLargeTag(self):
        substrate = ints2octs((127, 141, 245, 182, 253, 47, 3, 2, 1, 1))
        expected = (1, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testLongTag(self):
        substrate = ints2octs((0x1f, 2, 1, 0))
        expected = univ.Integer.tagSet

        self.assertEqual(expected, decoder.decode(substrate)[0].tagSet)

    def testTagsEquivalence(self):
        integer = univ.Integer(2).subtype(
            implicitTag=tag.Tag(tag.tagClassContext, 0, 0))

        substrate1 = ints2octs((0x9f, 0x80, 0x00, 0x02, 0x01, 0x02))
        substrate2 = ints2octs((0x9f, 0x00, 0x02, 0x01, 0x02))

        self.assertEqual(decoder.decode(substrate1, asn1Spec=integer),
                         decoder.decode(substrate2, asn1Spec=integer))


class DecoderCacheTestCase(BaseTestCase):
    def testCache(self):
        substrate = ints2octs((0x1f, 2, 1, 0))

        self.assertEqual(decoder.decode(substrate), decoder.decode(substrate))


class IntegerDecoderTestCase(BaseTestCase):
    def testPosInt(self):
        substrate = ints2octs((2, 1, 12))
        expected = (12, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testNegInt(self):
        substrate = ints2octs((2, 1, 244))
        expected = (-12, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testZero(self):
        substrate = ints2octs((2, 0))
        expected = (0, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testZeroLong(self):
        substrate = ints2octs((2, 1, 0))
        expected = (0, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testMinusOne(self):
        substrate = ints2octs((2, 1, 255))
        expected = (-1, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testPosLong(self):
        substrate = ints2octs(
            (2, 9, 0, 255, 255, 255, 255, 255, 255, 255, 255))
        expected = (0xffffffffffffffff, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testNegLong(self):
        substrate = ints2octs((2, 9, 255, 0, 0, 0, 0, 0, 0, 0, 1))
        expected = (-0xffffffffffffffff, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testSpec(self):
        substrate = ints2octs((2, 1, 12))
        expected = (12, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=univ.Integer()))

        self.assertRaises(
            error.PyAsn1Error, decoder.decode, substrate, asn1Spec=univ.Null())

    def testTagFormat(self):
        substrate = ints2octs((34, 1, 12))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


class BooleanDecoderTestCase(BaseTestCase):
    def testTrue(self):
        substrate = ints2octs((1, 1, 1))
        expected = (1, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testTrueNeg(self):
        substrate = ints2octs((1, 1, 255))
        expected = (1, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testExtraTrue(self):
        substrate = ints2octs((1, 1, 1, 0, 120, 50, 50))
        expected = (1, ints2octs((0, 120, 50, 50)))

        self.assertEqual(expected, decoder.decode(substrate))

    def testFalse(self):
        substrate = ints2octs((1, 1, 0))
        expected = (0, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testTagFormat(self):
        substrate = ints2octs((33, 1, 1))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


class BitStringDecoderTestCase(BaseTestCase):
    def testDefMode(self):
        substrate = ints2octs((3, 3, 1, 169, 138))
        expected = ((1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefMode(self):
        substrate =  ints2octs((3, 3, 1, 169, 138))
        expected = ((1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testDefModeChunked(self):
        substrate = ints2octs((35, 8, 3, 2, 0, 169, 3, 2, 1, 138))
        expected = ((1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefModeChunked(self):
        assert decoder.decode(
            ints2octs((35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0))
        ) == ((1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1), null)

    def testDefModeChunkedSubst(self):
        substrate = ints2octs((35, 8, 3, 2, 0, 169, 3, 2, 1, 138))
        expected = (ints2octs((3, 2, 0, 169, 3, 2, 1, 138)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testIndefModeChunkedSubst(self):
        substrate = ints2octs((35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0))
        expected = (ints2octs((3, 2, 0, 169, 3, 2, 1, 138, 0, 0)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testTypeChecking(self):
        substrate = ints2octs((35, 4, 2, 2, 42, 42))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

class OctetStringDecoderTestCase(BaseTestCase):
    def testDefMode(self):
        substrate = ints2octs(
            (4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 32, 102, 111, 120))
        expected = (str2octs('Quick brown fox'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefMode(self):
        substrate = ints2octs(
            (36, 128, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110, 32, 102, 111, 120, 0, 0))
        expected = (str2octs('Quick brown fox'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testDefModeChunked(self):
        substrate =  ints2octs(
                (36, 23, 4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114, 4,
                 4, 111, 119, 110, 32, 4, 3, 102, 111, 120))
        expected = (str2octs('Quick brown fox'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (36, 128, 4, 4, 81, 117, 105, 99, 4, 4, 107,32, 98, 114, 4, 4,
             111, 119, 110, 32, 4, 3, 102, 111, 120, 0, 0))
        expected = (str2octs('Quick brown fox'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testDefModeChunkedSubst(self):
        substrate = ints2octs(
            (36, 23, 4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114, 4, 4,
             111, 119, 110, 32, 4, 3, 102, 111, 120))
        expected = (ints2octs(
            (4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114, 4, 4, 111, 119,
             110, 32, 4, 3, 102, 111, 120)), str2octs(''))

        self.assertEqual(expected, decoder.decode(
            substrate,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testIndefModeChunkedSubst(self):
        substrate = ints2octs(
            (36, 128, 4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114, 4, 4,
             111, 119, 110, 32, 4, 3, 102, 111, 120, 0, 0))
        expected = (ints2octs(
            (4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114, 4, 4, 111, 119,
             110, 32, 4, 3, 102, 111, 120, 0, 0)), str2octs(''))

        self.assertEqual(expected, decoder.decode(
            substrate,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))


class ExpTaggedOctetStringDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        tagSet = univ.OctetString.tagSet.tagExplicitly(
            tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 5))

        self.obj = univ.OctetString('Quick brown fox', tagSet=tagSet)


    def testDefMode(self):
        substrate = ints2octs(
            (101, 17, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110, 32, 102, 111, 120))

        obj, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.obj, obj)
        self.assertEqual(self.obj.tagSet, obj.tagSet)
        self.assertTrue(self.obj.isSameTypeWith(obj))

    def testIndefMode(self):
        substrate = ints2octs(
            (101, 128, 36, 128, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114,
             111, 119, 110, 32, 102, 111, 120, 0, 0, 0, 0))

        obj, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.obj, obj)
        self.assertEqual(self.obj.tagSet, obj.tagSet)
        self.assertTrue(self.obj.isSameTypeWith(obj))

    def testDefModeChunked(self):
        substrate = ints2octs(
            (101, 25, 36, 23, 4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114,
             4, 4, 111, 119, 110, 32, 4, 3, 102, 111, 120))

        obj, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.obj, obj)
        self.assertEqual(self.obj.tagSet, obj.tagSet)
        self.assertTrue(self.obj.isSameTypeWith(obj))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (101, 128, 36, 128, 4, 4, 81, 117, 105, 99, 4, 4, 107, 32, 98, 114,
             4, 4, 111, 119, 110, 32, 4, 3, 102, 111, 120, 0, 0, 0, 0))

        obj, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.obj, obj)
        self.assertEqual(self.obj.tagSet, obj.tagSet)
        self.assertTrue(self.obj.isSameTypeWith(obj))

    def testDefModeSubst(self):
        substrate = ints2octs(
            (101, 17, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110,
             32, 102, 111, 120))
        expected = (ints2octs(
            (4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 32, 102,
             111, 120)), str2octs(''))

        self.assertEqual(expected, decoder.decode(
            substrate,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testIndefModeSubst(self):
        substrate = ints2octs(
            (101, 128, 36, 128, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 32, 102, 111, 120, 0, 0, 0, 0))
        expected = (ints2octs(
            (36, 128, 4, 15, 81, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110,
             32, 102, 111, 120, 0, 0, 0, 0)), str2octs(''))

        self.assertEqual(expected, decoder.decode(
            substrate,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))


class NullDecoderTestCase(BaseTestCase):
    def testNull(self):
        substrate = ints2octs((5, 0))
        expected = (null, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testTagFormat(self):
        substrate = ints2octs((37, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


# Useful analysis of OID encoding issues could be found here:
# https://misc.daniel-marschall.de/asn.1/oid_facts.html
class ObjectIdentifierDecoderTestCase(BaseTestCase):
    def testOne(self):
        substrate = ints2octs((6, 6, 43, 6, 0, 191, 255, 126))
        expected = ((1, 3, 6, 0, 0xffffe), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge1(self):
        substrate = ints2octs((6, 1, 39))
        expected = ((0, 39), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge2(self):
        substrate = ints2octs((6, 1, 79))
        expected = ((1, 39), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge3(self):
        substrate = ints2octs((6, 1, 120))
        expected = ((2, 40), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge4(self):
        substrate = ints2octs((6, 5, 0x90, 0x80, 0x80, 0x80, 0x4F))
        expected = ((2, 0xffffffff), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge5(self):
        substrate = ints2octs((6, 1, 0x7F))
        expected = ((2, 47), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge6(self):
        substrate = ints2octs((6, 2, 0x81, 0x00))
        expected = ((2, 48), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge7(self):
        substrate = ints2octs((6, 3, 0x81, 0x34, 0x03))
        expected = ((2, 100, 3), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge8(self):
        substrate = ints2octs((6, 2, 133, 0))
        expected = ((2, 560), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEdge9(self):
        substrate = ints2octs((6, 4, 0x88, 0x84, 0x87, 0x02))
        expected = ((2, 16843570), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testNonLeading0x80(self):
        substrate = ints2octs((6, 5, 85, 4, 129, 128, 0))
        expected = ((2, 5, 4, 16384), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testLeading0x80Case1(self):
        substrate = ints2octs((6, 5, 85, 4, 128, 129, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testLeading0x80Case2(self):
        substrate = ints2octs(
            (6, 7, 1, 0x80, 0x80, 0x80, 0x80, 0x80, 0x7F))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testLeading0x80Case3(self):
        substrate = ints2octs((6, 2, 0x80, 1))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testLeading0x80Case4(self):
        substrate = ints2octs((6, 2, 0x80, 0x7F))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testTagFormat(self):
        substrate = ints2octs((38, 1, 239))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testZeroLength(self):
        substrate = ints2octs((6, 0, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testIndefiniteLength(self):
        substrate = ints2octs((6, 128, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testReservedLength(self):
        substrate = ints2octs((6, 255, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testLarge1(self):
        substrate = ints2octs(
            (0x06, 0x11, 0x83, 0xC6, 0xDF, 0xD4, 0xCC, 0xB3, 0xFF, 0xFF,
             0xFE, 0xF0, 0xB8, 0xD6, 0xB8, 0xCB, 0xE2, 0xB7, 0x17))
        expected = ((2, 18446744073709551535184467440737095), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testLarge2(self):
        substrate = ints2octs(
            (0x06, 0x13, 0x88, 0x37, 0x83, 0xC6, 0xDF, 0xD4, 0xCC, 0xB3,
             0xFF, 0xFF, 0xFE, 0xF0, 0xB8, 0xD6, 0xB8, 0xCB, 0xE2, 0xB6,
             0x47))
        expected = ((2, 999, 18446744073709551535184467440737095), null)

        self.assertEqual(expected, decoder.decode(substrate))


class RealDecoderTestCase(BaseTestCase):
    def testChar(self):
        substrate = ints2octs((9, 7, 3, 49, 50, 51, 69, 49, 49))
        expected = (univ.Real((123, 10, 11)), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testBin1(self):  # check base = 2
        #  (0.5, 2, 0) encoded with base = 2
        substrate = ints2octs((9, 3, 128, 255, 1))
        expected = (univ.Real((1, 2, -1)), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testBin2(self):  # check base = 2 and scale factor
        #  (3.25, 2, 0) encoded with base = 8
        substrate = ints2octs((9, 3, 148, 255, 13))
        expected = (univ.Real((26, 2, -3)), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testBin3(self):  # check base = 16
        #  (0.00390625, 2, 0) encoded with base = 16
        substrate = ints2octs((9, 3, 160, 254, 1))
        expected = (univ.Real((1, 2, -8)), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testBin4(self):  # check exponent = 0
        #  (1, 2, 0) encoded with base = 2
        substrate = ints2octs((9, 3, 128, 0, 1))
        expected = (univ.Real((1, 2, 0)), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testBin5(self):  # case of 2 octs for exponent and negative exponent
        #  (3, 2, -1020) encoded with base = 16
        substrate = ints2octs((9, 4, 161, 255, 1, 3))
        expected = (univ.Real((3, 2, -1020)), null)

        self.assertEqual(expected, decoder.decode(substrate))

# TODO: this requires Real type comparison fix

#    def testBin6(self):
#        assert decoder.decode(
#            ints2octs((9, 5, 162, 0, 255, 255, 1))
#        ) == (univ.Real((1, 2, 262140)), null)

#    def testBin7(self):
#        assert decoder.decode(
#            ints2octs((9, 7, 227, 4, 1, 35, 69, 103, 1))
#        ) == (univ.Real((-1, 2, 76354972)), null)

    def testPlusInf(self):
        substrate = ints2octs((9, 1, 64))
        expected = (univ.Real('inf'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testMinusInf(self):
        substrate = ints2octs((9, 1, 65))
        expected = (univ.Real('-inf'), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testEmpty(self):
        substrate = ints2octs((9, 0))
        expected = (univ.Real(0.0), null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testTagFormat(self):
        substrate = ints2octs((41, 0))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)

    def testShortEncoding(self):
        substrate = ints2octs((9, 1, 131))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


class UniversalStringDecoderTestCase(BaseTestCase):
    def testDecoder(self):
        substrate = ints2octs((28, 12, 0, 0, 0, 97, 0, 0, 0, 98, 0, 0, 0, 99))
        expected = (
            char.UniversalString(
                sys.version_info[0] >= 3 and 'abc' or unicode('abc')), null)

        self.assertEqual(expected, decoder.decode(substrate))


class BMPStringDecoderTestCase(BaseTestCase):
    def testDecoder(self):
        substrate = ints2octs((30, 6, 0, 97, 0, 98, 0, 99))
        expected = (
            char.BMPString(
                sys.version_info[0] >= 3 and 'abc' or unicode('abc')), null)

        self.assertEqual(expected, decoder.decode(substrate))


class UTF8StringDecoderTestCase(BaseTestCase):
    def testDecoder(self):
        substrate = ints2octs((12, 3, 97, 98, 99))
        expected = (
            char.UTF8String(
                sys.version_info[0] >= 3 and 'abc' or unicode('abc')), null)

        self.assertEqual(expected, decoder.decode(substrate))


class SequenceOfDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.SequenceOf(componentType=univ.OctetString())
        self.seq.setComponentByPosition(0, univ.OctetString('quick brown'))

    def testDefMode(self):
        substrate = ints2octs(
            (48, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefMode(self):
        substrate = ints2octs(
            (48, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testDefModeChunked(self):
        substrate = ints2octs(
            (48, 19, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (48, 128, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110, 0, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testSchemalessDecoder(self):
        substrate = ints2octs(
            (48, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=univ.SequenceOf()))


class ExpTaggedSequenceOfDecoderTestCase(BaseTestCase):

    def testWithSchema(self):
        substrate = ints2octs(
            (163, 15, 48, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114,
             111, 119, 110))

        seq1 = univ.SequenceOf().subtype(
            explicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 3))

        seq2, r = decoder.decode(substrate, asn1Spec=seq1)

        self.assertFalse(r)
        self.assertEqual([str2octs('quick brown')], seq2)
        self.assertEqual(seq2.tagSet, seq1.tagSet)

    def testWithoutSchema(self):
        substrate = ints2octs(
            (163, 15, 48, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))

        seq1 = univ.SequenceOf().subtype(
            explicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 3))

        seq2, r = decoder.decode(substrate)

        self.assertFalse(r)
        self.assertEqual([str2octs('quick brown')], seq2)
        self.assertEqual(seq2.tagSet, seq1.tagSet)


class SequenceOfDecoderWithSchemaTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.SequenceOf(
            componentType=univ.OctetString())
        self.seq.setComponentByPosition(
            0, univ.OctetString('quick brown'))

    def testDefMode(self):
        substrate = ints2octs(
            (48, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefMode(self):
        substrate = ints2octs(
            (48, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testDefModeChunked(self):
        substrate = ints2octs(
            (48, 19, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98, 114,
             4, 3, 111, 119, 110))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (48, 128, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98, 114,
             4, 3, 111, 119, 110, 0, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))


class SetOfDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.SetOf(
            componentType=univ.OctetString())
        self.seq.setComponentByPosition(
            0, univ.OctetString('quick brown'))

    def testDefMode(self):
        substrate = ints2octs(
            (49, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefMode(self):
        substrate = ints2octs(
            (49, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testDefModeChunked(self):
        substrate = ints2octs(
            (49, 19, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (49, 128, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110, 0, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testSchemalessDecoder(self):
        substrate = ints2octs(
            (49, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119,
             110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=univ.SetOf()))


class SetOfDecoderWithSchemaTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.SetOf(
            componentType=univ.OctetString())
        self.seq.setComponentByPosition(
            0, univ.OctetString('quick brown'))

    def testDefMode(self):
        substrate = ints2octs(
            (49, 13, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefMode(self):
        substrate = ints2octs(
            (49, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testDefModeChunked(self):
        substrate = ints2octs(
            (49, 19, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefModeChunked(self):
        substrate = ints2octs(
            (49, 128, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110, 0, 0, 0, 0))

        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate, asn1Spec=self.seq))


class SequenceDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.NamedType('first-name', univ.OctetString(null)),
                namedtype.NamedType('age', univ.Integer(33))
            )
        )

        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def testWithOptionalAndDefaultedDefMode(self):
        substrate = ints2octs(
            (48, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedIndefMode(self):
        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedDefModeChunked(self):
        substrate = ints2octs(
            (48, 24, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedIndefModeChunked(self):
        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedDefModeSubst(self):
        substrate = ints2octs(
            (48, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))
        expected = (
            ints2octs((5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
                       119, 110, 2, 1, 1)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testWithOptionalAndDefaultedIndefModeSubst(self):
        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (
            ints2octs((5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
                       114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testTagFormat(self):
        substrate = ints2octs(
            (16, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


class SequenceDecoderWithSchemaTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.OptionalNamedType('first-name', univ.OctetString()),
                namedtype.DefaultedNamedType('age', univ.Integer(33))))

    def _init(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))

    def _initWithOptional(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))

    def _initWithDefaulted(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def _initWithOptionalAndDefaulted(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def testDefMode(self):
        self._init()

        substrate = ints2octs((48, 2, 5, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefMode(self):
        self._init()

        substrate = ints2octs((48, 128, 5, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testDefModeChunked(self):
        self._init()

        substrate = ints2octs((48, 2, 5, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefModeChunked(self):
        self._init()

        substrate = ints2octs((48, 128, 5, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalDefMode(self):
        self._initWithOptional()

        substrate = ints2octs(
            (48, 15, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionaIndefMode(self):
        self._initWithOptional()

        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalDefModeChunked(self):
        self._initWithOptional()

        substrate = ints2octs(
            (48, 21, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalIndefModeChunked(self):
        self._initWithOptional()

        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedDefMode(self):
        self._initWithDefaulted()

        substrate = ints2octs((48, 5, 5, 0, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedIndefMode(self):
        self._initWithDefaulted()

        substrate = ints2octs((48, 128, 5, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

    def testWithDefaultedDefModeChunked(self):
        self._initWithDefaulted()

        substrate = ints2octs((48, 5, 5, 0, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedIndefModeChunked(self):
        self._initWithDefaulted()

        substrate = ints2octs((48, 128, 5, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedDefMode(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (48, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedIndefMode(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedDefModeChunked(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
                (48, 24, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
                 98, 114, 4, 3, 111, 119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedIndefModeChunked(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (48, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))


class SequenceDecoderWithUntaggedOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )

        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType('blob', univ.Any(), openType=openType)
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 6, 2, 1, 1, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1])

    def testDecodeOpenTypesChoiceTwo(self):
        substrate = ints2octs(
            (48, 16, 2, 1, 2, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(2, seq[0])
        self.assertEqual(univ.OctetString('quick brown'), seq[1])

    def testDecodeOpenTypesUnknownType(self):
        substrate = ints2octs((48, 6, 2, 1, 2, 6, 1, 39))

        self.assertRaises(
            error.PyAsn1Error, decoder.decode,
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

    def testDecodeOpenTypesUnknownId(self):
        substrate = ints2octs((48, 6, 2, 1, 3, 6, 1, 39))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='060127'), seq[1])

    def testDontDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 6, 2, 1, 1, 2, 1, 12))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(ints2octs((2, 1, 12)), seq[1])

    def testDontDecodeOpenTypesChoiceTwo(self):
        substrate = ints2octs(
            (48, 16, 2, 1, 2, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(2, seq[0])
        self.assertEqual(
            ints2octs((4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
                       119, 110)), seq[1])


class SequenceDecoderWithImplicitlyTaggedOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )
        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType(
                    'blob', univ.Any().subtype(
                        implicitTag=tag.Tag(
                            tag.tagClassContext, tag.tagFormatSimple, 3)),
                    openType=openType
                )
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 8, 2, 1, 1, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1])

    def testDecodeOpenTypesUnknownId(self):
        substrate = ints2octs((48, 8, 2, 1, 3, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='02010C'), seq[1])


class SequenceDecoderWithExplicitlyTaggedOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )
        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType(
                    'blob', univ.Any().subtype(
                        explicitTag=tag.Tag(
                            tag.tagClassContext, tag.tagFormatSimple, 3)),
                    openType=openType
                )
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 8, 2, 1, 1, 163, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1])

    def testDecodeOpenTypesUnknownId(self):
        substrate = ints2octs((48, 8, 2, 1, 3, 163, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='02010C'), seq[1])


class SequenceDecoderWithUnaggedSetOfOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )
        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType(
                    'blob', univ.SetOf(componentType=univ.Any()),
                    openType=openType)
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 8, 2, 1, 1, 49, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1][0])

    def testDecodeOpenTypesChoiceTwo(self):
        substrate = ints2octs(
            (48, 18, 2, 1, 2, 49, 13, 4, 11, 113, 117, 105, 99,
             107, 32, 98, 114, 111, 119, 110))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(2, seq[0])
        self.assertEqual(univ.OctetString('quick brown'), seq[1][0])

    def testDecodeOpenTypesUnknownType(self):
        substrate = ints2octs((48, 6, 2, 1, 2, 6, 1, 39))

        self.assertRaises(
            error.PyAsn1Error, decoder.decode, substrate,
            asn1Spec=self.seq, decodeOpenTypes=True)

    def testDecodeOpenTypesUnknownId(self):
        substrate = ints2octs((48, 8, 2, 1, 3, 49, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='02010c'), seq[1][0])

    def testDontDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 8, 2, 1, 1, 49, 3, 2, 1, 12))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(ints2octs((2, 1, 12)), seq[1][0])

    def testDontDecodeOpenTypesChoiceTwo(self):
        substrate = ints2octs(
            (48, 18, 2, 1, 2, 49, 13, 4, 11, 113, 117, 105, 99,
            107, 32, 98, 114, 111, 119, 110))
        expected = ints2octs(
            (4, 11, 113, 117, 105, 99, 107, 32, 98, 114,
             111, 119, 110))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(2, seq[0])
        self.assertEqual(expected, seq[1][0])


class SequenceDecoderWithImplicitlyTaggedSetOfOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )
        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType(
                    'blob', univ.SetOf(
                        componentType=univ.Any().subtype(
                            implicitTag=tag.Tag(
                                tag.tagClassContext, tag.tagFormatSimple, 3))),
                    openType=openType
                )
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs((48, 10, 2, 1, 1, 49, 5, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1][0])

    def testDecodeOpenTypesUnknownId(self):
        substrate = ints2octs((48, 10, 2, 1, 3, 49, 5, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='02010C'), seq[1][0])


class SequenceDecoderWithExplicitlyTaggedSetOfOpenTypesTestCase(BaseTestCase):
    def setUp(self):
        openType = opentype.OpenType(
            'id',
            {1: univ.Integer(),
             2: univ.OctetString()}
        )

        self.seq = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('id', univ.Integer()),
                namedtype.NamedType(
                    'blob', univ.SetOf(
                        componentType=univ.Any().subtype(
                            explicitTag=tag.Tag(
                                tag.tagClassContext, tag.tagFormatSimple, 3))),
                    openType=openType
                )
            )
        )

    def testDecodeOpenTypesChoiceOne(self):
        substrate = ints2octs(
            (48, 10, 2, 1, 1, 49, 5, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(1, seq[0])
        self.assertEqual(12, seq[1][0])

    def testDecodeOpenTypesUnknownId(self):
        substrate =  ints2octs((48, 10, 2, 1, 3, 49, 5, 131, 3, 2, 1, 12))

        seq, rest = decoder.decode(
            substrate, asn1Spec=self.seq, decodeOpenTypes=True)

        self.assertFalse(rest)
        self.assertEqual(3, seq[0])
        self.assertEqual(univ.OctetString(hexValue='02010C'), seq[1][0])


class SetDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.Set(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.NamedType('first-name', univ.OctetString(null)),
                namedtype.NamedType('age', univ.Integer(33))
            )
        )

        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def testWithOptionalAndDefaultedDefMode(self):
        substrate = ints2octs(
            (49, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedIndefMode(self):
        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedDefModeChunked(self):
        substrate = ints2octs(
                (49, 24, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
                 98, 114, 4, 3, 111, 119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedIndefModeChunked(self):
        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(expected, decoder.decode(substrate))

    def testWithOptionalAndDefaultedDefModeSubst(self):
        substrate = ints2octs(
            (49, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))
        expected = (
            ints2octs((5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
                       119, 110, 2, 1, 1)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testWithOptionalAndDefaultedIndefModeSubst(self):
        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (ints2octs(
            (5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 0, 0, 2, 1, 1, 0, 0)), str2octs(''))

        self.assertEqual(
            expected, decoder.decode(
                substrate,
                substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)))

    def testTagFormat(self):
        substrate = ints2octs(
            (16, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))

        self.assertRaises(error.PyAsn1Error, decoder.decode, substrate)


class SetDecoderWithSchemaTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.Set(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.OptionalNamedType('first-name', univ.OctetString()),
                namedtype.DefaultedNamedType('age', univ.Integer(33)),
            )
        )

    def _init(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))

    def _initWithOptional(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))

    def _initWithDefaulted(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def _initWithOptionalAndDefaulted(self):
        self.seq.clear()
        self.seq.setComponentByPosition(0, univ.Null(null))
        self.seq.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.seq.setComponentByPosition(2, univ.Integer(1))

    def testDefMode(self):
        self._init()

        substrate = ints2octs((49, 128, 5, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefMode(self):
        self._init()

        substrate = ints2octs((49, 128, 5, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testDefModeChunked(self):
        self._init()

        substrate = ints2octs((49, 2, 5, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testIndefModeChunked(self):
        self._init()

        substrate = ints2octs((49, 128, 5, 0, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalDefMode(self):
        self._initWithOptional()

        substrate = ints2octs(
            (49, 15, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalIndefMode(self):
        self._initWithOptional()

        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 0, 0))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalDefModeChunked(self):
        self._initWithOptional()

        substrate = ints2octs(
            (49, 21, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalIndefModeChunked(self):
        self._initWithOptional()

        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 0, 0))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedDefMode(self):
        self._initWithDefaulted()

        substrate = ints2octs((49, 5, 5, 0, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedIndefMode(self):
        self._initWithDefaulted()

        substrate = ints2octs((49, 128, 5, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedDefModeChunked(self):
        self._initWithDefaulted()

        substrate = ints2octs((49, 5, 5, 0, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithDefaultedIndefModeChunked(self):
        self._initWithDefaulted()

        substrate = ints2octs((49, 128, 5, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedDefMode(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 2, 1, 1))

        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedDefModeReordered(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 18, 2, 1, 1, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111,
             119, 110, 5, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedIndefMode(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107, 32, 98,
             114, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedIndefModeReordered(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 128, 2, 1, 1, 5, 0, 36, 128, 4, 11, 113, 117, 105, 99, 107,
             32, 98, 114, 111, 119, 110, 0, 0,  0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedDefModeChunked(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 24, 5, 0, 36, 17, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32, 98,
             114, 4, 3, 111, 119, 110, 2, 1, 1))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))

    def testWithOptionalAndDefaultedIndefModeChunked(self):
        self._initWithOptionalAndDefaulted()

        substrate = ints2octs(
            (49, 128, 5, 0, 36, 128, 4, 4, 113, 117, 105, 99, 4, 4, 107, 32,
             98, 114, 4, 3, 111, 119, 110, 0, 0, 2, 1, 1, 0, 0))
        expected = (self.seq, null)

        self.assertEqual(
            expected, decoder.decode(substrate, asn1Spec=self.seq))


class SequenceOfWithExpTaggedOctetStringDecoder(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.seq = univ.SequenceOf(
            componentType=univ.OctetString().subtype(
                explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3))
        )
        self.seq.setComponentByPosition(0, 'q')
        self.seq2 = univ.SequenceOf()

    def testDefModeSchema(self):
        substrate = ints2octs((48, 5, 163, 3, 4, 1, 113))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)

    def testIndefModeSchema(self):
        substrate = ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)

    def testDefModeNoComponent(self):
        substrate = ints2octs((48, 5, 163, 3, 4, 1, 113))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)

    def testIndefModeNoComponent(self):
        substrate = ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0))

        seq, rest = decoder.decode(substrate, asn1Spec=self.seq2)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)

    def testDefModeSchemaless(self):
        substrate = ints2octs((48, 5, 163, 3, 4, 1, 113))

        seq, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)

    def testIndefModeSchemaless(self):
        substrate = ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0))

        seq, rest = decoder.decode(substrate)

        self.assertFalse(rest)
        self.assertEqual(self.seq, seq)
        self.assertEqual(self.seq.tagSet, seq.tagSet)


class SequenceWithExpTaggedOctetStringDecoder(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.s = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType(
                    'x', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3))
                )
            )
        )
        self.s.setComponentByPosition(0, 'q')
        self.s2 = univ.Sequence()

    def testDefModeSchema(self):
        s, r = decoder.decode(ints2octs((48, 5, 163, 3, 4, 1, 113)), asn1Spec=self.s)
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet

    def testIndefModeSchema(self):
        s, r = decoder.decode(ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0)), asn1Spec=self.s)
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet

    def testDefModeNoComponent(self):
        s, r = decoder.decode(ints2octs((48, 5, 163, 3, 4, 1, 113)), asn1Spec=self.s2)
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet

    def testIndefModeNoComponent(self):
        s, r = decoder.decode(ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0)), asn1Spec=self.s2)
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet

    def testDefModeSchemaless(self):
        s, r = decoder.decode(ints2octs((48, 5, 163, 3, 4, 1, 113)))
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet

    def testIndefModeSchemaless(self):
        s, r = decoder.decode(ints2octs((48, 128, 163, 128, 4, 1, 113, 0, 0, 0, 0)))
        assert not r
        assert s == self.s
        assert s.tagSet == self.s.tagSet


class ChoiceDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.s = univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.NamedType('number', univ.Integer(0)),
                namedtype.NamedType('string', univ.OctetString())
            )
        )

    def testBySpec(self):
        self.s.setComponentByPosition(0, univ.Null(null))
        assert decoder.decode(
            ints2octs((5, 0)), asn1Spec=self.s
        ) == (self.s, null)

    def testWithoutSpec(self):
        self.s.setComponentByPosition(0, univ.Null(null))
        assert decoder.decode(ints2octs((5, 0))) == (self.s, null)
        assert decoder.decode(ints2octs((5, 0))) == (univ.Null(null), null)

    def testUndefLength(self):
        self.s.setComponentByPosition(2, univ.OctetString('abcdefgh'))
        assert decoder.decode(ints2octs((36, 128, 4, 3, 97, 98, 99, 4, 3, 100, 101, 102, 4, 2, 103, 104, 0, 0)),
                              asn1Spec=self.s) == (self.s, null)

    def testExplicitTag(self):
        s = self.s.subtype(explicitTag=tag.Tag(tag.tagClassContext,
                                               tag.tagFormatConstructed, 4))
        s.setComponentByPosition(0, univ.Null(null))
        assert decoder.decode(ints2octs((164, 2, 5, 0)), asn1Spec=s) == (s, null)

    def testExplicitTagUndefLength(self):
        s = self.s.subtype(explicitTag=tag.Tag(tag.tagClassContext,
                                               tag.tagFormatConstructed, 4))
        s.setComponentByPosition(0, univ.Null(null))
        assert decoder.decode(ints2octs((164, 128, 5, 0, 0, 0)), asn1Spec=s) == (s, null)


class AnyDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.s = univ.Any()

    def testByUntagged(self):
        assert decoder.decode(
            ints2octs((4, 3, 102, 111, 120)), asn1Spec=self.s
        ) == (univ.Any('\004\003fox'), null)

    def testTaggedEx(self):
        s = univ.Any('\004\003fox').subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))
        assert decoder.decode(ints2octs((164, 5, 4, 3, 102, 111, 120)), asn1Spec=s) == (s, null)

    def testTaggedIm(self):
        s = univ.Any('\004\003fox').subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))
        assert decoder.decode(ints2octs((132, 5, 4, 3, 102, 111, 120)), asn1Spec=s) == (s, null)

    def testByUntaggedIndefMode(self):
        assert decoder.decode(
            ints2octs((4, 3, 102, 111, 120)), asn1Spec=self.s
        ) == (univ.Any('\004\003fox'), null)

    def testTaggedExIndefMode(self):
        s = univ.Any('\004\003fox').subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))
        assert decoder.decode(ints2octs((164, 128, 4, 3, 102, 111, 120, 0, 0)), asn1Spec=s) == (s, null)

    def testTaggedImIndefMode(self):
        s = univ.Any('\004\003fox').subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))
        assert decoder.decode(ints2octs((164, 128, 4, 3, 102, 111, 120, 0, 0)), asn1Spec=s) == (s, null)

    def testByUntaggedSubst(self):
        assert decoder.decode(
            ints2octs((4, 3, 102, 111, 120)),
            asn1Spec=self.s,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)
        ) == (ints2octs((4, 3, 102, 111, 120)), str2octs(''))

    def testTaggedExSubst(self):
        assert decoder.decode(
            ints2octs((164, 5, 4, 3, 102, 111, 120)),
            asn1Spec=self.s,
            substrateFun=lambda a, b, c, d: streaming.readFromStream(b, c)
        ) == (ints2octs((164, 5, 4, 3, 102, 111, 120)), str2octs(''))


class EndOfOctetsTestCase(BaseTestCase):
    def testUnexpectedEoo(self):
        try:
            decoder.decode(ints2octs((0, 0)))
        except error.PyAsn1Error:
            pass
        else:
            assert 0, 'end-of-contents octets accepted at top level'

    def testExpectedEoo(self):
        result, remainder = decoder.decode(ints2octs((0, 0)), allowEoo=True)
        assert eoo.endOfOctets.isSameTypeWith(result) and result == eoo.endOfOctets and result is eoo.endOfOctets
        assert remainder == null

    def testDefiniteNoEoo(self):
        try:
            decoder.decode(ints2octs((0x23, 0x02, 0x00, 0x00)))
        except error.PyAsn1Error:
            pass
        else:
            assert 0, 'end-of-contents octets accepted inside definite-length encoding'

    def testIndefiniteEoo(self):
        result, remainder = decoder.decode(ints2octs((0x23, 0x80, 0x00, 0x00)))
        assert result == () and remainder == null, 'incorrect decoding of indefinite length end-of-octets'

    def testNoLongFormEoo(self):
        try:
            decoder.decode(ints2octs((0x23, 0x80, 0x00, 0x81, 0x00)))
        except error.PyAsn1Error:
            pass
        else:
            assert 0, 'end-of-contents octets accepted with invalid long-form length'

    def testNoConstructedEoo(self):
        try:
            decoder.decode(ints2octs((0x23, 0x80, 0x20, 0x00)))
        except error.PyAsn1Error:
            pass
        else:
            assert 0, 'end-of-contents octets accepted with invalid constructed encoding'

    def testNoEooData(self):
        try:
            decoder.decode(ints2octs((0x23, 0x80, 0x00, 0x01, 0x00)))
        except error.PyAsn1Error:
            pass
        else:
            assert 0, 'end-of-contents octets accepted with unexpected data'


class NonStringDecoderTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.s = univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('place-holder', univ.Null(null)),
                namedtype.NamedType('first-name', univ.OctetString(null)),
                namedtype.NamedType('age', univ.Integer(33))
            )
        )
        self.s.setComponentByPosition(0, univ.Null(null))
        self.s.setComponentByPosition(1, univ.OctetString('quick brown'))
        self.s.setComponentByPosition(2, univ.Integer(1))

        self.substrate = ints2octs([48, 18, 5, 0, 4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110, 2, 1, 1])

    def testOctetString(self):
        s = list(decoder.StreamingDecoder(
            univ.OctetString(self.substrate), asn1Spec=self.s))
        assert [self.s] == s

    def testAny(self):
        s = list(decoder.StreamingDecoder(
            univ.Any(self.substrate), asn1Spec=self.s))
        assert [self.s] == s


class ErrorOnDecodingTestCase(BaseTestCase):

    def testErrorCondition(self):
        decode = decoder.SingleItemDecoder(
            tagMap=decoder.TAG_MAP, typeMap=decoder.TYPE_MAP)
        substrate = ints2octs((00, 1, 2))
        stream = streaming.asSeekableStream(substrate)

        try:
            asn1Object = next(decode(stream))

        except error.PyAsn1Error:
            exc = sys.exc_info()[1]
            assert isinstance(exc, error.PyAsn1Error), (
                'Unexpected exception raised %r' % (exc,))

        else:
            assert False, 'Unexpected decoder result %r' % (asn1Object,)

    def testRawDump(self):
        substrate = ints2octs((31, 8, 2, 1, 1, 131, 3, 2, 1, 12))
        stream = streaming.asSeekableStream(substrate)

        class SingleItemEncoder(decoder.SingleItemDecoder):
            defaultErrorState = decoder.stDumpRawValue

        class StreamingDecoder(decoder.StreamingDecoder):
            SINGLE_ITEM_DECODER = SingleItemEncoder

        class OneShotDecoder(decoder.Decoder):
            STREAMING_DECODER = StreamingDecoder

        d = OneShotDecoder()

        asn1Object, rest = d(stream)

        assert isinstance(asn1Object, univ.Any), (
            'Unexpected raw dump type %r' % (asn1Object,))
        assert asn1Object.asNumbers() == (31, 8, 2, 1, 1), (
            'Unexpected raw dump value %r' % (asn1Object,))
        assert rest == ints2octs((131, 3, 2, 1, 12)), (
            'Unexpected rest of substrate after raw dump %r' % rest)


class BinaryFileTestCase(BaseTestCase):
    """Assure that decode works on open binary files."""
    def testOneObject(self):
        _, path = tempfile.mkstemp()
        try:
            with open(path, "wb") as out:
                out.write(ints2octs((2, 1, 12)))

            with open(path, "rb") as source:
                values = list(decoder.StreamingDecoder(source))

            assert values == [12]
        finally:
            os.remove(path)

    def testMoreObjects(self):
        _, path = tempfile.mkstemp()
        try:
            with open(path, "wb") as out:
                out.write(ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0)))

            with open(path, "rb") as source:
                values = list(decoder.StreamingDecoder(source))

            assert values == [12, (1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1)]

        finally:
            os.remove(path)

    def testInvalidFileContent(self):
        _, path = tempfile.mkstemp()
        try:
            with open(path, "wb") as out:
                out.write(ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0, 7)))

            with open(path, "rb") as source:
                list(decoder.StreamingDecoder(source))

        except error.EndOfStreamError:
            pass

        finally:
            os.remove(path)


class BytesIOTestCase(BaseTestCase):
    def testRead(self):
        source = ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0))
        stream = io.BytesIO(source)
        values = list(decoder.StreamingDecoder(stream))
        assert values == [12, (1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1)]


class UnicodeTestCase(BaseTestCase):
    def testFail(self):
        # This ensures that unicode objects in Python 2 & str objects in Python 3.7 cannot be parsed.
        source = ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0)).decode("latin-1")
        try:
            next(decoder.StreamingDecoder(source))

        except error.UnsupportedSubstrateError:
            pass

        else:
            assert False, 'Tolerated parsing broken unicode strings'


class RestartableDecoderTestCase(BaseTestCase):

    class NonBlockingStream(io.BytesIO):
        block = False

        def read(self, size=-1):
            self.block = not self.block
            if self.block:
                return  # this is what non-blocking streams sometimes do

            return io.BytesIO.read(self, size)

    def setUp(self):
        BaseTestCase.setUp(self)

        self.s = univ.SequenceOf(componentType=univ.OctetString())
        self.s.setComponentByPosition(0, univ.OctetString('quick brown'))
        source = ints2octs(
            (48, 26,
             4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110,
             4, 11, 113, 117, 105, 99, 107, 32, 98, 114, 111, 119, 110))
        self.stream = self.NonBlockingStream(source)

    def testPartialReadingFromNonBlockingStream(self):
        iterator = iter(decoder.StreamingDecoder(self.stream, asn1Spec=self.s))

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' not in res.context

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' not in res.context

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 0

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 0

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 0

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 1

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 1

        res = next(iterator)

        assert isinstance(res, error.SubstrateUnderrunError)
        assert 'asn1Object' in res.context
        assert isinstance(res.context['asn1Object'], univ.SequenceOf)
        assert res.context['asn1Object'].isValue
        assert len(res.context['asn1Object']) == 1

        res = next(iterator)

        assert isinstance(res, univ.SequenceOf)
        assert res.isValue
        assert len(res) == 2

        try:
            next(iterator)

        except StopIteration:
            pass

        else:
            assert False, 'End of stream not raised'


class CompressedFilesTestCase(BaseTestCase):
    def testGzip(self):
        _, path = tempfile.mkstemp(suffix=".gz")
        try:
            with gzip.open(path, "wb") as out:
                out.write(ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0)))

            with gzip.open(path, "rb") as source:
                values = list(decoder.StreamingDecoder(source))

            assert values == [12, (1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1)]

        finally:
            os.remove(path)

    def testZipfile(self):
        # File from ZIP archive is a good example of non-seekable stream in Python 2.7
        #   In Python 3.7, it is a seekable stream.
        _, path = tempfile.mkstemp(suffix=".zip")
        try:
            with zipfile.ZipFile(path, "w") as myzip:
                myzip.writestr("data", ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0)))

            with zipfile.ZipFile(path, "r") as myzip:
                with myzip.open("data", "r") as source:
                    values = list(decoder.StreamingDecoder(source))
                    assert values == [12, (1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1)]
        finally:
            os.remove(path)

    def testZipfileMany(self):
        _, path = tempfile.mkstemp(suffix=".zip")
        try:
            with zipfile.ZipFile(path, "w") as myzip:
                #for i in range(100):
                myzip.writestr("data", ints2octs((2, 1, 12, 35, 128, 3, 2, 0, 169, 3, 2, 1, 138, 0, 0)) * 1000)

            with zipfile.ZipFile(path, "r") as myzip:
                with myzip.open("data", "r") as source:
                    values = list(decoder.StreamingDecoder(source))
                    assert values == [12, (1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1)] * 1000
        finally:
            os.remove(path)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
