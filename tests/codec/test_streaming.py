#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
import io
import sys
import unittest

from pyasn1.codec import streaming
from tests.base import BaseTestCase


class CachingStreamWrapperTestCase(BaseTestCase):
    def setUp(self):
        self.shortText = b"abcdefghij"
        self.longText = self.shortText * (io.DEFAULT_BUFFER_SIZE * 5)
        self.shortStream = io.BytesIO(self.shortText)
        self.longStream = io.BytesIO(self.longText)

    def testReadJustFromCache(self):
        wrapper = streaming.CachingStreamWrapper(self.shortStream)
        wrapper.read(6)
        wrapper.seek(3)

        self.assertEqual(b'd', wrapper.read(1))
        self.assertEqual(b'e', wrapper.read(1))
        self.assertEqual(5, wrapper.tell())

    def testReadFromCacheAndStream(self):
        wrapper = streaming.CachingStreamWrapper(self.shortStream)
        wrapper.read(6)
        wrapper.seek(3)

        self.assertEqual(b'defg', wrapper.read(4))
        self.assertEqual(7, wrapper.tell())

    def testReadJustFromStream(self):
        wrapper = streaming.CachingStreamWrapper(self.shortStream)

        self.assertEqual(b'abcdef', wrapper.read(6))
        self.assertEqual(6, wrapper.tell())

    def testPeek(self):
        wrapper = streaming.CachingStreamWrapper(self.longStream)
        read_bytes = wrapper.peek(io.DEFAULT_BUFFER_SIZE + 73)

        self.assertEqual(io.DEFAULT_BUFFER_SIZE + 73, len(read_bytes))
        self.assertTrue(read_bytes.startswith(b'abcdefg'))
        self.assertEqual(0, wrapper.tell())
        self.assertEqual(b'abcd', wrapper.read(4))

    def testMarkedPositionResets(self):
        wrapper = streaming.CachingStreamWrapper(self.longStream)
        wrapper.read(10)
        wrapper.markedPosition = wrapper.tell()

        self.assertEqual(10, wrapper.markedPosition)

        # Reach the maximum capacity of cache
        wrapper.read(io.DEFAULT_BUFFER_SIZE)

        self.assertEqual(10 + io.DEFAULT_BUFFER_SIZE, wrapper.tell())

        # The following should clear the cache
        wrapper.markedPosition = wrapper.tell()

        self.assertEqual(0, wrapper.markedPosition)
        self.assertEqual(0, len(wrapper._cache.getvalue()))


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
