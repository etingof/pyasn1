#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pyasn1.sf.net/license.html
#

__all__ = ['OpenType']


class OpenType(object):
    """Create ASN.1 type map indexed by a value

    The *DefinedBy* object models the ASN.1 *DEFINED BY* clause which maps
    values to ASN.1 types in the context of the ASN.1 SEQUENCE/SET type.

    DefinedBy objects are immutable and duck-type Python :class:`dict` objects

    Parameters
    ----------
    name: :py:class:`str`
        Field name

    *choices:
        Sequence of (*value*, *type*) tuples representing the mapping 
    """

    def __init__(self, name, args, **kwargs):
        self.__name = name
        self.__choices = dict(args, **kwargs)

    @property
    def name(self):
        return self.__name

    # Python dict protocol

    def values(self):
        return self.__choices.values()

    def keys(self):
        return self.__choices

    def items(self):
        return self.__choices.items()

    def __contains__(self, key):
        return key in self.__choices

    def __getitem__(self, key):
        return self.__choices[key]

    def __iter__(self):
        return iter(self.__choices)
