#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import datetime
from pyasn1.type import univ, char, tag

__all__ = ['ObjectDescriptor', 'GeneralizedTime', 'UTCTime']

NoValue = univ.NoValue
noValue = univ.noValue


class ObjectDescriptor(char.GraphicString):
    __doc__ = char.GraphicString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.GraphicString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 7)
    )


class TimeMixIn(object):
    class FixedOffset(datetime.tzinfo):
        """Fixed offset in minutes east from UTC."""

        def __init__(self, offset, name):
            self.__offset = datetime.timedelta(minutes=offset)
            self.__name = name

        def utcoffset(self, dt):
            return self.__offset

        def tzname(self, dt):
            return self.__name

        def dst(self, dt):
            return datetime.timedelta(0)

    @property
    def asDateTime(self):
        string = str(self)
        if string.endswith('Z'):
            string = string[:-2]
        return datetime.datetime.strptime(string, '%Y%m%d%H%M%S.%f%z')

    @classmethod
    def fromDateTime(cls, dt):
        string = dt.strftime('%Y%m%d%H%M%S.%%d%z')
        string = '%s.%.2d' % (string, dt.microsecond // 10000)
        if '+' not in string:
            string += 'Z'
        return cls(string)


class GeneralizedTime(char.VisibleString, TimeMixIn):
    __doc__ = char.GraphicString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 24)
    )


class UTCTime(char.VisibleString, TimeMixIn):
    __doc__ = char.GraphicString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 23)
    )
