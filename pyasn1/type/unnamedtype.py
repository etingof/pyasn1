#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#


class UnnamedType(object):
    """Create a container holding a single ASN.1 type.

    The UnnamedType object represents a single, unnamed ASN.1 type
    for the field definition of constructed ASN.1 types.

    Parameters
    ----------
    *asn1Object: :class:`~pyasn1.type.base.Asn1Item`
    """
    def __init__(self, asn1Object=None):
        self.__asn1Object = asn1Object

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__asn1Object)

    # descriptor protocol

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # This is a bit of hack: look up instance attribute first,
        # then try class attribute if instance attribute with that
        # name is not available.
        # The rationale is to have `.componentType` readable-writeable
        # as a class attribute and read-only as instance attribute.
        try:
            return instance._componentType

        except AttributeError:
            return self

    def __set__(self, instance, value):
        raise AttributeError('attribute is read-only')

    @property
    def asn1Object(self):
        return self.__asn1Object
