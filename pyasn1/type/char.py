#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import sys
from pyasn1.type import univ, tag
from pyasn1 import error


class AbstractCharacterString(univ.OctetString):

    if sys.version_info[0] <= 2:
        def __str__(self):
            try:
                return self._value.encode(self._encoding)
            except UnicodeEncodeError:
                raise error.PyAsn1Error(
                    'Can\'t encode string \'%s\' with \'%s\' codec' % (self._value, self._encoding)
                )

        def __unicode__(self):
            return unicode(self._value)

        def prettyIn(self, value):
            if isinstance(value, unicode):
                return value
            elif isinstance(value, str):
                try:
                    return value.decode(self._encoding)
                except (LookupError, UnicodeDecodeError):
                    raise error.PyAsn1Error(
                        'Can\'t decode string \'%s\' with \'%s\' codec' % (value, self._encoding)
                    )
            elif isinstance(value, (tuple, list)):
                try:
                    return self.prettyIn(''.join([chr(x) for x in value]))
                except ValueError:
                    raise error.PyAsn1Error(
                        'Bad %s initializer \'%s\'' % (self.__class__.__name__, value)
                    )
            else:
                try:
                    return unicode(value)
                except UnicodeDecodeError:
                    raise error.PyAsn1Error(
                        'Can\'t turn object \'%s\' into unicode' % (value,)
                    )

        def asOctets(self, padding=True):
            return str(self)

        def asNumbers(self, padding=True):
            return tuple([ord(x) for x in str(self)])

    else:
        def __str__(self):
            return str(self._value)

        def __bytes__(self):
            try:
                return self._value.encode(self._encoding)
            except UnicodeEncodeError:
                raise error.PyAsn1Error(
                    'Can\'t encode string \'%s\' with \'%s\' codec' % (self._value, self._encoding)
                )

        def prettyIn(self, value):
            if isinstance(value, str):
                return value
            elif isinstance(value, bytes):
                try:
                    return value.decode(self._encoding)
                except UnicodeDecodeError:
                    raise error.PyAsn1Error(
                        'Can\'t decode string \'%s\' with \'%s\' codec' % (value, self._encoding)
                    )
            elif isinstance(value, (tuple, list)):
                return self.prettyIn(bytes(value))
            else:
                try:
                    return str(value)
                except (UnicodeDecodeError, ValueError):
                    raise error.PyAsn1Error(
                        'Can\'t turn object \'%s\' into unicode' % (value,)
                    )

        def asOctets(self, padding=True):
            return bytes(self)

        def asNumbers(self, padding=True):
            return tuple(bytes(self))

    def prettyOut(self, value):
        return value

    def __reversed__(self):
        return reversed(self._value)


class NumericString(AbstractCharacterString):
    """Creates ASN.1 NumericString type or object.

    The NumericString models character string that can
    be entered from a telephone handset. NumericString objects
    behave like Python 2 :class:`unicode` or Python 3 :class:`str`.

    From Unicode prospective, this type work with *us-ascii* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.NumericString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *NumericString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *NumericString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *NumericString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 18)
    )
    encoding = 'us-ascii'


class PrintableString(AbstractCharacterString):
    """Creates ASN.1 PrintableString type or object.

    The PrintableString models character string that can
    be entered from a very rudimentary terminals featuring letters,
    digits and punctuation marks. PrintableString objects
    behave like Python 2 :class:`unicode` or Python 3 :class:`str`.

    From Unicode prospective, this type work with *us-ascii* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.PrintableString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *PrintableString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *PrintableString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *PrintableString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 19)
    )
    encoding = 'us-ascii'


class TeletexString(AbstractCharacterString):
    """Creates ASN.1 TeletexString type or object.

    The TeletexString models character string that can
    be entered from a sophisticated text processing machines
    (by 20-th century standards) featuring letters from multiple
    alphabets (308 characters!), digits, punctuation marks and
    escape sequences.
    TeletexString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *iso-8859-1* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.TeletexString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *TeletexString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *TeletexString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *TeletexString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 20)
    )
    encoding = 'iso-8859-1'


class T61String(TeletexString):
    """Creates ASN.1 T61String type or object.

    Alias to the :py:class:`TeletexString` class
    """


class VideotexString(AbstractCharacterString):
    """Creates ASN.1 VideotexString type or object.

    The VideotexString models character string that can
    be consumed by sophisticated video terminals (by 20-th century
    standards) to render ascii-art style pictures and animations.
    VideotexString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *iso-8859-1* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.TeletexString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *VideotexString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *VideotexString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *VideotexString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 21)
    )
    encoding = 'iso-8859-1'


class IA5String(AbstractCharacterString):
    """Creates ASN.1 IA5String type or object.

    The IA5String models a basic character string first published
    in 1963 as an ISO/ITU standard, then it turned into ASCII.
    IA5String objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *us-ascii* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.IA5String` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *IA5String* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *IA5String* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *IA5String* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 22)
    )
    encoding = 'us-ascii'


class GraphicString(AbstractCharacterString):
    """Creates ASN.1 GraphicString type or object.

    The GraphicString models a character string that can hold
    any "graphical" characters mixed with control ones to
    select particular alphabet.
    GraphicString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *iso-8859-1* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.GraphicString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *GraphicString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *GraphicString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *GraphicString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 25)
    )
    encoding = 'iso-8859-1'


class VisibleString(AbstractCharacterString):
    """Creates ASN.1 VisibleString type or object.

    The VisibleString models a character string containing just
    printable symbols, no spaces and newlines.
    VisibleString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *us-ascii* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.VisibleString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *VisibleString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *VisibleString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *VisibleString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 26)
    )
    encoding = 'us-ascii'


class ISO646String(VisibleString):
    """Creates ASN.1 ISO646String type or object.

    Alias to the :py:class:`VisibleString` class
    """


class GeneralString(AbstractCharacterString):
    """Creates ASN.1 GeneralString type or object.

    The GeneralString models a character string similar to
    :py:class:`GraphicString` but additionally including control
    characters.
    GeneralString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    From Unicode prospective, this type work with *iso-8859-1* code
    points.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.GeneralString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *GeneralString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *GeneralString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *GeneralString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 27)
    )
    encoding = 'iso-8859-1'


class UniversalString(AbstractCharacterString):
    """Creates ASN.1 UniversalString type or object.

    The UniversalString models a Unicode (ISO10646-1) character string
    implicitly serialized into UTF-32 big endian.
    UniversalString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.UniversalString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *UniversalString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *UniversalString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *UniversalString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 28)
    )
    encoding = "utf-32-be"


class BMPString(AbstractCharacterString):
    """Creates ASN.1 BMPString type or object.

    The BMPString models a Unicode (ISO10646-1) character string
    implicitly serialized into UTF-16 big endian.
    BMPString objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.BMPString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *BMPString* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *BMPString* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *BMPString* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 30)
    )
    encoding = "utf-16-be"


class UTF8String(AbstractCharacterString):
    """Creates ASN.1 UniversalString type or object.

    The UTF8String models a Unicode (ISO10646-1) character string
    implicitly serialized into UTF-8.
    UTF8String objects behave like Python 2 :class:`unicode`
    or Python 3 :class:`str`.

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.UTF8String` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serialized
        unicode string (note `encoding` parameter) or *UTF8String* class instance.

    tagSet: :py:class:`~pyasn1.type.tag.TagSet`
        Object representing non-default ASN.1 tag(s)

    subtypeSpec: :py:class:`~pyasn1.type.constraint.ConstraintsIntersection`
        Object representing non-default ASN.1 subtype constraint(s)

    encoding: :py:class:`str`
        Unicode codec ID to encode/decode :class:`unicode` (Python 2) or
        :class:`str` (Python 3) the payload when *UTF8String* object is used
        in octet-stream context.

    Raises
    ------
    : :py:class:`pyasn1.error.PyAsn1Error`
        On constraint violation or bad initializer.
    """
    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for ASN.1
    #: *UTF8String* objects
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 12)
    )
    encoding = "utf-8"
