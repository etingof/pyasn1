# CER decoder
from pyasn1.type import univ
from pyasn1.codec.ber import decoder
from pyasn1.compat.octets import oct2int
from pyasn1 import error

class BooleanDecoder(decoder.AbstractSimpleDecoder):
    protoComponent = univ.Boolean(0)
    def valueDecoder(self, fullSubstrate, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        substrate = substrate[:length]
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        byte = oct2int(substrate[0])
        if byte == 0xff:
            value = 1
        elif byte == 0x00:
            value = 0
        else:
            raise error.PyAsn1Error('Boolean CER violation: %s' % byte)
        return self._createComponent(asn1Spec, tagSet, value), substrate[1:]

class ObjectIdentifierDecoder(decoder.AbstractSimpleDecoder):
    protoComponent = univ.ObjectIdentifier(())
    def valueDecoder(self, fullSubstrate, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        substrate = substrate[:length]        
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')

        # Get the first subid
        subId = oct2int(substrate[0])
        oid = divmod(subId, 40)

        index = 1
        substrateLen = len(substrate)
        while index < substrateLen:
            subId = oct2int(substrate[index])
            index = index + 1
            if subId == 128:
                # ASN.1 spec forbids leading zeros (0x80) in sub-ID OID
                # encoding,#tolerating it opens a vulnerability.
                # See http://www.cosic.esat.kuleuven.be/publications/article-1432.pdf page 7
                raise error.PyAsn1Error('Invalid leading 0x80 in sub-OID')
            elif subId > 128:
                # Construct subid from a number of octets
                nextSubId = subId
                subId = 0
                while nextSubId >= 128:
                    subId = (subId << 7) + (nextSubId & 0x7F)
                    if index >= substrateLen:
                        raise error.SubstrateUnderrunError(
                            'Short substrate for sub-OID past %s' % (oid,)
                            )
                    nextSubId = oct2int(substrate[index])
                    index = index + 1
                subId = (subId << 7) + nextSubId
            oid = oid + (subId,)
        return self._createComponent(asn1Spec, tagSet, oid), substrate[index:]

tagMap = decoder.tagMap.copy()
tagMap.update({
    univ.Boolean.tagSet: BooleanDecoder(),
    univ.ObjectIdentifier.tagSet: ObjectIdentifierDecoder(),
    })

typeMap = decoder.typeMap

class Decoder(decoder.Decoder): pass

decode = Decoder(tagMap, decoder.typeMap)
