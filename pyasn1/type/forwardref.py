#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#
from pyasn1 import error


__all__ = ['ForwardRef']


class ForwardRef(object):
    # TODO: this is not thread-safe
    waitingList = {}

    def __init__(self, symbol, *args, **kwargs):
        self.__symbol = symbol
        self.args = args
        self.kwargs = kwargs

    def callLater(self, cbFun):
        if self.__symbol not in self.waitingList:
            self.__class__.waitingList[self.__symbol] = []
        self.waitingList[self.__symbol].append((self, cbFun))

    # TODO: make two callbacks - one for updating types and the other for
    # initialization once all updates are done
    @classmethod
    def newTypeNotification(cls, name, obj):
        # TODO: name collision at different modules possible
        if name in cls.waitingList:
            for waitingObject, cbFun in cls.waitingList.pop(name):

                cbFun(obj.clone(*waitingObject.args, **waitingObject.kwargs))

    def subtype(self, *args, **kwargs):
        # TODO: make a copy; combine kw/args to mimic subtype/clone ops
        self.args = args
        self.kwargs = kwargs
        return self

    def __getattr__(self, item):
        raise error.PyAsn1Error('Unresolved forward reference %s (.%s attempted)' % (self.__symbol, item))

