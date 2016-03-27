#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2016, Ilya Etingof <ilya@glas.net>
# License: http://pyasn1.sf.net/license.html
#


class PyAsn1Error(Exception):
    pass


class ValueConstraintError(PyAsn1Error):
    pass


class SubstrateUnderrunError(PyAsn1Error):
    pass
