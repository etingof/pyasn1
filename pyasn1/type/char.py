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

    Parameters
    ----------
    value: :class:`unicode`, :class:`str`, :class:`bytes` or :py:class:`~pyasn1.type.char.NumericString` object
        unicode object (Python 2) or string (Python 3), alternatively string
        (Python 2) or bytes (Python 3) representing octet-stream of serializied
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
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 19)
    )
    encoding = 'us-ascii'


class TeletexString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 20)
    )
    encoding = 'us-ascii'


class T61String(TeletexString):
    pass


class VideotexString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 21)
    )
    encoding = 'iso-8859-1'


class IA5String(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 22)
    )
    encoding = 'us-ascii'


class GraphicString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 25)
    )
    encoding = 'iso-8859-1'


class VisibleString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 26)
    )
    encoding = 'us-ascii'


class ISO646String(VisibleString):
    pass


class GeneralString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 27)
    )
    encoding = 'iso-8859-1'


class UniversalString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 28)
    )
    encoding = "utf-32-be"


class BMPString(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 30)
    )
    encoding = "utf-16-be"


class UTF8String(AbstractCharacterString):
    tagSet = AbstractCharacterString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 12)
    )
    encoding = "utf-8"
