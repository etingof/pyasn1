#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
import sys
import datetime
from pyasn1.type import useful
from pyasn1.error import PyAsn1Error

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class FixedOffset(datetime.tzinfo):

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


class ObjectDescriptorTestCase(unittest.TestCase):
    pass

class GeneralizedTimeTestCase(unittest.TestCase):

    def testFromDateTime(self):
        assert useful.GeneralizedTime.fromDateTime(datetime.datetime(2017, 7, 11, 0, 1, 2, 30000, tzinfo=UTC)) == '20170711000102.3Z'

    def testToDateTime(self):
        assert datetime.datetime(2017, 7, 11, 0, 1, 2, 30000, tzinfo=UTC) == useful.GeneralizedTime('20170711000102.3Z').asDateTime


class UTCTimeTestCase(unittest.TestCase):


    def testFromDateTime(self):
        assert useful.UTCTime.fromDateTime(datetime.datetime(2017, 7, 11, 0, 1, 2, 30000, tzinfo=UTC)) == '20170711000102.3Z'

    def testToDateTime(self):
        assert datetime.datetime(2017, 7, 11, 0, 1, 2, 30000, tzinfo=UTC) == useful.UTCTime('20170711000102.3Z').asDateTime


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
