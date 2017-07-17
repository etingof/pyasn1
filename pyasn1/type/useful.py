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

    _yearsDigits = 4
    _hasSubsecond = False
    _optionalMinutes = False
    _shortTZ = False

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
        """Create :py:class:`datetime.datetime` object from a |ASN.1| object.

        Returns
        -------
        :
            new instance of :py:class:`datetime.datetime` object            
        """
        string = str(self)
        if string.endswith('Z'):
            tzinfo = TimeMixIn.UTC
            string = string[:-1]

        elif '-' in string or '+' in string:
            if '+' in string:
                string, plusminus, tz = string.partition('+')
            else:
                string, plusminus, tz = string.partition('-')

            if self._shortTZ and len(tz) == 2:
                tz += '00'

            if len(tz) != 4:
                raise error.PyAsn1Error('malformed time zone offset %s' % tz)

            try:
                minutes = int(tz[:2]) * 60 + int(tz[2:])
                if plusminus == '-':
                    minutes *= -1

            except ValueError:
                raise error.PyAsn1Error('unknown time specification %s' % self)

            tzinfo = TimeMixIn.FixedOffset(minutes, '?')

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

        if self._optionalMinutes and len(string) - self._yearsDigits == 6:
            string += '0000'
        elif len(string) - self._yearsDigits == 8:
            string += '00'

        try:
            dt = datetime.datetime.strptime(string, self._yearsDigits == 4 and '%Y%m%d%H%M%S' or '%y%m%d%H%M%S')

        except ValueError:
            raise error.PyAsn1Error('malformed datetime format %s' % self)

        return dt.replace(microsecond=ms, tzinfo=tzinfo)

    @classmethod
    def fromDateTime(cls, dt):
        """Create |ASN.1| object from a :py:class:`datetime.datetime` object.

        Parameters
        ----------
        dt : :py:class:`datetime.datetime` object
            The `datetime.datetime` object to initialize the |ASN.1| object from
            
        
        Returns
        -------
        :
            new instance of |ASN.1| value
        """
        string = dt.strftime(cls._yearsDigits == 4 and '%Y%m%d%H%M%S' or '%y%m%d%H%M%S')
        if cls._hasSubsecond:
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

    _yearsDigits = 4
    _hasSubsecond = True
    _optionalMinutes = True
    _shortTZ = True


class UTCTime(char.VisibleString, TimeMixIn):
    __doc__ = char.VisibleString.__doc__

    #: Default :py:class:`~pyasn1.type.tag.TagSet` object for |ASN.1| objects
    tagSet = char.VisibleString.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 23)
    )

    _yearsDigits = 2
    _hasSubsecond = False
    _optionalMinutes = False
    _shortTZ = False
