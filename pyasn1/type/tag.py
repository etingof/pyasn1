# ASN.1 types tags
try:
    from sys import version_info
except ImportError:
    version_info = (0, 0)   # a really early version
from operator import getslice
from types import SliceType
from string import join
from pyasn1 import error

tagClassUniversal = 0x00
tagClassApplication = 0x40
tagClassContext = 0x80
tagClassPrivate = 0xC0

tagFormatSimple = 0x00
tagFormatConstructed = 0x20

tagCategoryImplicit = 0x01
tagCategoryExplicit = 0x02
tagCategoryUntagged = 0x04

class Tag:
    def __init__(self, tagClass, tagFormat, tagId):
        self.__tag = (tagClass, tagFormat, tagId)
        self.__uniqTag = (tagClass, tagId)
        self.__hashedUniqTag = hash(self.__uniqTag)
    def __repr__(self):
        return '%s(tagClass=%s, tagFormat=%s, tagId=%s)' % (
            (self.__class__.__name__,) + self.__tag
            )
    def __cmp__(self, other): return cmp(self.__uniqTag, other)
    def __eq__(self, other):
        return self is other or self.__hashedUniqTag == other
    def __hash__(self): return self.__hashedUniqTag
    def __getitem__(self, idx): return self.__tag[idx]
    def __and__(self, (tagClass, tagFormat, tagId)):
        return self.__class__(
            self.__tag&tagClass, self.__tag&tagFormat, self.__tag&tagId
            )
    def __or__(self, (tagClass, tagFormat, tagId)):
        return self.__class__(
            self.__tag[0]|tagClass, self.__tag[1]|tagFormat, self.__tag[2]|tagId
            )

class TagSet:
    def __init__(self, baseTag=(), *superTags):
        self.__baseTag = baseTag
        self.__superTags = superTags
        self.__hashedSuperTags = hash(superTags)
    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            join(map(lambda x: repr(x), self.__superTags), ', ')
            )

    def __add__(self, superTag):
        return apply(
            self.__class__, (self.__baseTag,) + self.__superTags + (superTag,)
            )
    def __radd__(self, superTag):
        return apply(
            self.__class__, (self.__baseTag, superTag) + self.__superTags
            )

    def tagExplicitly(self, superTag):
        tagClass, tagFormat, tagId = superTag
        if tagClass == tagClassUniversal:
            raise error.BadArgumentError(
                'Can\'t tag with UNIVERSAL-class tag'
                )
        if tagFormat != tagFormatConstructed:
            superTag = Tag(tagClass, tagFormatConstructed, tagId)
        return self + superTag

    def tagImplicitly(self, superTag):
        tagClass, tagFormat, tagId = superTag
        if self.__superTags:
            superTag = Tag(tagClass, self.__superTags[-1][1], tagId)
        return self[:-1] + superTag

    def getBaseTag(self): return self.__baseTag
    def __getitem__(self, idx):
        if type(idx) == SliceType:
            return apply(self.__class__,
                         (self.__baseTag,) + getslice(self.__superTags,
                                                      idx.start, idx.stop))
        return self.__superTags[idx]
    if version_info < (2, 0):
        def __getslice__(self, i, j):
            return self[max(0, i):max(0, j):]
    def __cmp__(self, other): return cmp(self.__superTags, other)
    def __eq__(self, other):
        return self is other or self.__hashedSuperTags == other
    def __hash__(self): return self.__hashedSuperTags
    def __len__(self): return len(self.__superTags)
    def isSuperTagSetOf(self, tagSet):
        # XXX optimization?
        l = len(self.__superTags)
        if len(tagSet) < l:
            return
        idx = 0
        while idx < l:
            if self.__superTags[idx] != tagSet[idx]:
                return
            idx = idx + 1
        return 1
    
def initTagSet(tag): return TagSet(tag, tag)
