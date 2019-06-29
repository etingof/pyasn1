#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#


class PyAsn1Error(Exception):
    """Create pyasn1 exception object

    The `PyAsn1Error` exception represents generic, usually fatal, error.
    """


class ValueConstraintError(PyAsn1Error):
    """Create pyasn1 exception object

    The `ValueConstraintError` exception indicates an ASN.1 value
    constraint violation.
    """


class SubstrateUnderrunError(PyAsn1Error):
    """Create pyasn1 exception object

    The `SubstrateUnderrunError` exception indicates insufficient serialised
    data on input of a de-serialization routine.
    """


class PyAsn1UnicodeError(PyAsn1Error, UnicodeError):
    """Create pyasn1 exception object

    The `PyAsn1UnicodeError` exception is a base class for errors relating to
    unicode text de/serialization.
    """
    def __init__(self, message, unicode_error=None):
        if isinstance(unicode_error, UnicodeError):
            UnicodeError.__init__(self, *unicode_error.args)
        PyAsn1Error.__init__(self, message)


class PyAsn1UnicodeDecodeError(PyAsn1UnicodeError, UnicodeDecodeError):
    """Create pyasn1 exception object

    The `PyAsn1UnicodeDecodeError` exception represents a failure to
    deserialize unicode text.
    """


class PyAsn1UnicodeEncodeError(PyAsn1UnicodeError, UnicodeEncodeError):
    """Create pyasn1 exception object

    The `PyAsn1UnicodeEncodeError` exception represents a failure to
    serialize unicode text.
    """


