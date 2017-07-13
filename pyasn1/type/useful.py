#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import datetime
from pyasn1.type import univ, char, tag
from pyasn1 import error

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

    yearsDigits = 4
    hasSubsecond = False

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

    UTC = FixedOffset(0, 'UTC')

    @property
    def asDateTime(self):
        string = str(self)
        if string.endswith('Z'):
            tzinfo = TimeMixIn.UTC
            string = string[:-1]

        elif string[-5] in ('-', '+'):
            try:
                minutes = int(string[-4:-2]) * 60 + int(string[-2:])
                if string[-5] == '-':
                    minutes *= -1

            except ValueError:
                raise error.PyAsn1Error('unknown time specification %s' % self)

            tzinfo = TimeMixIn.FixedOffset(minutes, '?')
            string = string[:-5]

        else:
            tzinfo = None

        if '.' in string or ',' in string:
            if '.' in string:
                string, _, ms = string.partition('.')
            else:
                string, _, ms = string.partition(',')

            try:
                ms = int(ms) * 10000

            except ValueError:
                raise error.PyAsn1Error('bad sub-second time specification %s' % self)

        else:
            ms = 0

        if len(string) - self.yearsDigits == 6:
            string += '0000'
        elif len(string) - self.yearsDigits == 8:
            string += '00'

        dt = datetime.datetime.strptime(string, self.yearsDigits == 4 and '%Y%m%d%H%M%S' or '%y%m%d%H%M%S')

        return dt.replace(microsecond=ms, tzinfo=tzinfo)

    @classmethod
    def fromDateTime(cls, dt):
        string = dt.strftime(cls.yearsDigits == 4 and '%Y%m%d%H%M%S' or '%y%m%d%H%M%S')
        if cls.hasSubsecond:
            string += '.%d' % (dt.microsecond // 10000)

        if dt.utcoffset():
            seconds = dt.utcoffset().seconds
            if seconds < 0:
                string += '-'
            else:
                string += '+'
            string += '%.2d%.2d' % (seconds // 3600, seconds % 3600)
        else:
            string += 'Z'

        return cls(string)


class GeneralizedTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 24)
    )

    yearsDigits = 4
    hasSubsecond = True


class UTCTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 23)
    )

    yearsDigits = 2
    hasSubsecond = False
