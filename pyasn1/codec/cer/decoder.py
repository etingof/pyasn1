# CER decoder
from pyasn1.type import univ
from pyasn1.codec.ber import decoder
from pyasn1 import error

class BooleanDecoder(decoder.AbstractDecoder):
    protoComponent = univ.Boolean
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        byte = ord(substrate[0])
        if byte == 0xff:
            value = 1
        elif byte == 0x00:
            value = 0
        return self._createComponent(
            tagSet, asn1Spec
            ).clone(value), substrate[1:]

codecMap = decoder.codecMap.copy()
codecMap.update({
    univ.Boolean.tagSet: BooleanDecoder(),
    })

class Decoder(decoder.Decoder): pass

decode = Decoder(codecMap)
