#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2015, Ilya Etingof <ilya@glas.net>
# License: http://pyasn1.sf.net/license.html
#
from pyasn1.codec.cer import decoder

tagMap = decoder.tagMap
typeMap = decoder.typeMap
class Decoder(decoder.Decoder):
    supportIndefLength = False

decode = Decoder(tagMap, typeMap)
