# BER decoder
import types
from pyasn1.type import tag, univ, char, useful
from pyasn1.codec.ber import eoo
from pyasn1 import error

class AbstractDecoder:
    protoComponent = None
    def _createComponent(self, tagSet, asn1Spec):
        if asn1Spec is None:
            return self.protoComponent.clone(tagSet=tagSet)
        else:
            return asn1Spec.clone()
        
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        raise error.PyAsn1Error('Decoder not implemented for %s' % tagSet)

class EndOfOctetsDecoder(AbstractDecoder):
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        return eoo.endOfOctets, substrate

class IntegerDecoder(AbstractDecoder):
    protoComponent = univ.Integer(0)
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        octets = map(ord, substrate)
        if octets[0] & 0x80:
            value = -1L
        else:
            value = 0L
        for octet in octets:
            value = value << 8 | octet
        try:
            value = int(value)
        except OverflowError:
            pass
        return self._createComponent(tagSet, asn1Spec).clone(value), substrate

class BooleanDecoder(IntegerDecoder):
    protoComponent = univ.Boolean(0)

class BitStringDecoder(AbstractDecoder):
    protoComponent = univ.BitString(())
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if tagSet[0][1] == tag.tagFormatSimple:    # XXX what tag to check?
            if not substrate:
                raise error.PyAsn1Error('Missing initial octet')
            trailingBits = ord(substrate[0])
            if trailingBits > 7:
                raise error.PyAsn1Error(
                    'Trailing bits overflow %s' % trailingBits
                    )
            substrate = substrate[1:]
            lsb = p = 0; l = len(substrate)-1; b = []
            while p <= l:
                if p == l:
                    lsb = trailingBits
                j = 7                    
                o = ord(substrate[p])
                while j >= lsb:
                    b.append((o>>j)&0x01)
                    j = j - 1
                p = p + 1
            return r.clone(tuple(b)), ''
        if r: r = r.clone(value=())
        if not decodeFun:
            return r, substrate
        while substrate:
            component, substrate = decodeFun(substrate)
            r = r + component
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if r: r = r.clone(value='')
        if not decodeFun:
            return r, substrate
        while substrate:
            component, substrate = decodeFun(substrate)
            if component == eoo.endOfOctets:
                break
            r = r + component
        else:
            raise error.SubstrateUnderrunError(
                'No EOO seen before substrate ends'
                )
        return r, substrate

class OctetStringDecoder(AbstractDecoder):
    protoComponent = univ.OctetString('')
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if tagSet[0][1] == tag.tagFormatSimple:    # XXX what tag to check?
            return r.clone(str(substrate)), ''
        if r: r = r.clone(value='')
        if not decodeFun:
            return r, substrate
        while substrate:
            component, substrate = decodeFun(substrate)
            r = r + component
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if r: r = r.clone(value='')
        if not decodeFun:
            return r, substrate        
        while substrate:
            component, substrate = decodeFun(substrate)
            if component == eoo.endOfOctets:
                break
            r = r + component
        else:
            raise error.SubstrateUnderrunError(
                'No EOO seen before substrate ends'
                )
        return r, substrate

class NullDecoder(AbstractDecoder):
    protoComponent = univ.Null('')
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if substrate:
            raise error.PyAsn1Error('Unexpected substrate for Null')
        return r, substrate

class ObjectIdentifierDecoder(AbstractDecoder):
    protoComponent = univ.ObjectIdentifier(())
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec) # XXX use default tagset
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        oid = []; index = 0        
        # Get the first subid
        subId = ord(substrate[index])
        oid.append(int(subId / 40))
        oid.append(int(subId % 40))

        index = index + 1
        substrateLen = len(substrate)
        
        while index < substrateLen:
            subId = ord(substrate[index])
            if subId < 128:
                oid.append(subId)
                index = index + 1
            else:
                # Construct subid from a number of octets
                nextSubId = subId
                subId = 0
                while nextSubId >= 128 and index < substrateLen:
                    subId = (subId << 7) + (nextSubId & 0x7F)
                    index = index + 1
                    nextSubId = ord(substrate[index])
                if index == substrateLen:
                    raise error.SubstrateUnderrunError(
                        'Short substrate for OID %s' % oid
                        )
                subId = (subId << 7) + nextSubId
                oid.append(subId)
                index = index + 1
        return r.clone(tuple(oid)), substrate[index:]

class SequenceDecoder(AbstractDecoder):
    protoComponent = univ.Sequence()
    def _getAsn1SpecByPosition(self, t, idx):
        if t.getComponentType() is not None:
            if hasattr(t, 'getComponentTypeMapNearPosition'):
                return t.getComponentTypeMapNearPosition(idx) # Sequence
            elif hasattr(t, 'getComponentTypeMap'):  # XXX
                return t.getComponentTypeMap() # SequenceOf
        # or no asn1Specs
    def _getPositionByType(self, t, c, idx):
        if t.getComponentType() is not None:
            if hasattr(t, 'getComponentPositionNearType'):
                effectiveTagSet = getattr(
                    c, 'getEffectiveTagSet', c.getTagSet
                    )()
                return t.getComponentPositionNearType(effectiveTagSet, idx) # Sequence
        return idx # SequenceOf or w/o asn1Specs

    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec)
        idx = 0
        if not decodeFun:
            return r, substrate
        while substrate:
            asn1Spec = self._getAsn1SpecByPosition(r, idx)
            component, substrate = decodeFun(
                substrate, asn1Spec
                )
            idx = self._getPositionByType(r, component, idx)
            r.setComponentByPosition(idx, component)
            idx = idx + 1
        if hasattr(r, 'setDefaultComponents'):
            r.setDefaultComponents()
        r.verifySizeSpec()
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec)
        idx = 0
        while substrate:
            try:
                asn1Spec = self._getAsn1SpecByPosition(r, idx)
            except error.PyAsn1Error:
                asn1Spec = None # XXX
            if not decodeFun:
                return r, substrate
            component, substrate = decodeFun(substrate, asn1Spec)
            if component == eoo.endOfOctets:
                break
            idx = self._getPositionByType(r, component, idx)
            r.setComponentByPosition(idx, component)
            idx = idx + 1                
        else:
            raise error.SubstrateUnderrunError(
                'No EOO seen before substrate ends'
                )
        if hasattr(r, 'setDefaultComponents'):
            r.setDefaultComponents()
        r.verifySizeSpec()
        return r, substrate

class SetDecoder(SequenceDecoder):
    protoComponent = univ.Set()
    def _getAsn1SpecByPosition(self, t, idx):
        if t.getComponentType() is not None:
            if hasattr(t, 'getComponentTypeMap'):
                return t.getComponentTypeMap() # Set/SetOf
        # or no asn1Specs
    def _getPositionByType(self, t, c, idx):
        if t.getComponentType() is not None:
            if t.getComponentType() and hasattr(t, 'getComponentPositionByType'):
                effectiveTagSet = getattr(
                    c, 'getEffectiveTagSet', c.getTagSet
                    )()
                return t.getComponentPositionByType(effectiveTagSet) # Set
        return idx # SetOf or w/o asn1Specs
        
class ChoiceDecoder(AbstractDecoder):
    protoComponent = univ.Choice()
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(tagSet, asn1Spec)
        if not decodeFun:
            return r, substrate
        component, substrate = decodeFun(
            substrate, r.getComponentTypeMap(), tagSet, length, state
            )
        effectiveTagSet = getattr(
            component, 'getEffectiveTagSet', component.getTagSet
            )()
        r.setComponentByType(effectiveTagSet, component)
        return r, substrate

    indefLenValueDecoder = valueDecoder

# character string types
class UTF8StringDecoder(OctetStringDecoder):
    protoComponent = char.UTF8String()
class NumericStringDecoder(OctetStringDecoder):
    protoComponent = char.NumericString()
class PrintableStringDecoder(OctetStringDecoder):
    protoComponent = char.PrintableString()
class TeletexStringDecoder(OctetStringDecoder):
    protoComponent = char.TeletexString()
class VideotexStringDecoder(OctetStringDecoder):
    protoComponent = char.VideotexString()
class IA5StringDecoder(OctetStringDecoder):
    protoComponent = char.IA5String()
class GraphicStringDecoder(OctetStringDecoder):
    protoComponent = char.GraphicString()
class VisibleStringDecoder(OctetStringDecoder):
    protoComponent = char.VisibleString()
class GeneralStringDecoder(OctetStringDecoder):
    protoComponent = char.GeneralString()
class UniversalStringDecoder(OctetStringDecoder):
    protoComponent = char.UniversalString()
class BMPStringDecoder(OctetStringDecoder):
    protoComponent = char.BMPString()

# "useful" types
class GeneralizedTimeDecoder(OctetStringDecoder):
    protoComponent = useful.GeneralizedTime()
class UTCTimeDecoder(OctetStringDecoder):
    protoComponent = useful.UTCTime()

codecMap = {
    eoo.endOfOctets.tagSet: EndOfOctetsDecoder(),
    univ.Integer.tagSet: IntegerDecoder(),
    univ.Boolean.tagSet: BooleanDecoder(),
    univ.BitString.tagSet: BitStringDecoder(),
    univ.OctetString.tagSet: OctetStringDecoder(),
    univ.Null.tagSet: NullDecoder(),
    univ.ObjectIdentifier.tagSet: ObjectIdentifierDecoder(),
    univ.Enumerated.tagSet: IntegerDecoder(),
    univ.Sequence.tagSet: SequenceDecoder(),
    univ.Set.tagSet: SetDecoder(),
    univ.Choice.tagSet: ChoiceDecoder(),
    # character string types
    char.UTF8String.tagSet: UTF8StringDecoder(),
    char.NumericString.tagSet: NumericStringDecoder(),
    char.PrintableString.tagSet: PrintableStringDecoder(),
    char.TeletexString.tagSet: TeletexStringDecoder(),
    char.VideotexString.tagSet: VideotexStringDecoder(),
    char.IA5String.tagSet: IA5StringDecoder(),
    char.GraphicString.tagSet: GraphicStringDecoder(),
    char.VisibleString.tagSet: VisibleStringDecoder(),
    char.GeneralString.tagSet: GeneralStringDecoder(),
    char.UniversalString.tagSet: UniversalStringDecoder(),
    char.BMPString.tagSet: BMPStringDecoder(),
    # useful types
    useful.GeneralizedTime.tagSet: GeneralizedTimeDecoder(),
    useful.UTCTime.tagSet: UTCTimeDecoder()
    }

( stDecodeTag, stDecodeLength, stGetValueDecoder, stGetValueDecoderByAsn1Spec,
  stGetValueDecoderByTag, stTryAsExplicitTag, stDecodeValue, stStop ) = range(8)

class Decoder:
    def __init__(self, codecMap):
        self.__codecMap = codecMap
    def __call__(self, substrate, asn1Spec=None, tagSet=None,
                 length=None, state=stDecodeTag, recursiveFlag=1):
        # Decode tag & length
        while state != stStop:
            if state == stDecodeTag:
                # Decode tag
                lenOfStream = len(substrate)
                if lenOfStream < 2:
                    raise error.SubstrateUnderrunError(
                        'Short octet stream (%d octets)' % lenOfStream
                        )
                t = ord(substrate[0])
                lastTag = tag.Tag(
                    tagClass=(t&0xC0),
                    tagFormat=(t&0x20),
                    tagId=t&0x1F
                    )
                if tagSet is None:
                    tagSet = tag.TagSet((), lastTag)  # base tag is not recovered
                else:
                    tagSet = lastTag + tagSet
                substrate = substrate[1:]
                state = stDecodeLength
            if state == stDecodeLength:
                # Decode length (we know there's at least 2 bytes from above)
                firstOctet  = ord(substrate[0])
                if firstOctet == 128:
                    size = 1
                    length = -1
                elif firstOctet < 128:
                    length, size = firstOctet, 1
                else:
                    size = firstOctet & 0x7F
                    # encoded in size bytes
                    length = 0
                    lengthString = substrate[1:size+1]
                    # missing check on maximum size, which shouldn't be a
                    # problem, we can handle more than is possible
                    if len(lengthString) != size:
                        raise error.SubstrateUnderrunError(
                            '%s<%s at %s' %
                            (size, len(lengthString), tagSet)
                            )
                    for char in lengthString:
                        length = (length << 8) | ord(char)
                    size = size + 1
                state = stGetValueDecoder
                substrate = substrate[size:]
                if length != -1 and len(substrate) < length:
                    raise error.SubstrateUnderrunError(
                        '%d-octet short' % (length - len(substrate))
                        )
            if state == stGetValueDecoder:
                if asn1Spec is None:
                    state = stGetValueDecoderByTag
                else:
                    state = stGetValueDecoderByAsn1Spec
            #
            # There're two ways of creating subtypes in ASN.1 what influences
            # decoder operation. These methods are:
            # 1) Either base types used in or no IMPLICIT tagging has been applied
            #    on subtyping.
            # 2) Subtype syntax drops base type information (by means of IMPLICIT
            #    tagging.
            # The first case allows for complete tag recovery from substrate while
            # the second one requires original ASN.1 type spec for decoding.
            #
            # In either case a set of tags (tagSet) is coming from substrate in
            # an incremental, tag-by-tag fashion (this is the case of EXPLICIT tag
            # which is most basic). Outermost tag comes first from wire.
            #            
            if state == stGetValueDecoderByTag:
                concreteDecoder = self.__codecMap.get(tagSet)
                if concreteDecoder:
                    state = stDecodeValue
                else:
                    concreteDecoder = self.__codecMap.get(tagSet[:1])
                    if concreteDecoder:
                        state = stDecodeValue
                    else:
                        state = stTryAsExplicitTag
            if state == stGetValueDecoderByAsn1Spec:
                if tagSet == eoo.endOfOctets.getTagSet():
                    concreteDecoder = self.__codecMap[tagSet]
                    state = stDecodeValue
                    continue
                if type(asn1Spec) == types.DictType:
                    __chosenSpec = asn1Spec.get(tagSet)
                elif asn1Spec is not None:
                    __chosenSpec = asn1Spec
                else:
                    __chosenSpec = None
                if __chosenSpec is None or not\
                       __chosenSpec.getTypeMap().has_key(tagSet):
                    state = stTryAsExplicitTag
                else:
                    # use base type for codec lookup to recover untagged types
                    baseTag = __chosenSpec.getTagSet().getBaseTag()
                    if baseTag: # XXX ugly
                        baseTagSet = tag.TagSet(baseTag, baseTag)
                    else:
                        baseTagSet = tag.TagSet()
                    concreteDecoder = self.__codecMap.get( # tagged subtype
                        baseTagSet
                        )
                    if concreteDecoder:
                        asn1Spec = __chosenSpec
                        state = stDecodeValue
                    else:
                        state = stTryAsExplicitTag
            if state == stTryAsExplicitTag:
                if lastTag[1] == tag.tagFormatConstructed and \
                       lastTag[0] != tag.tagClassUniversal:
                    # Assume explicit tagging
                    state = stDecodeTag
                else:
                    raise error.PyAsn1Error(
                        '%s not in asn1Spec: %s' % (tagSet, asn1Spec)
                        )
            if state == stDecodeValue:
                if recursiveFlag:
                    decodeFun = self
                else:
                    decodeFun = None
                if length == -1:  # indef length
                    value, substrate = concreteDecoder.indefLenValueDecoder(
                        substrate, asn1Spec, tagSet, length,
                        stGetValueDecoder, decodeFun
                        )
                else:
                    value, _substrate = concreteDecoder.valueDecoder(
                        substrate[:length], asn1Spec, tagSet,
                        length, stGetValueDecoder, decodeFun
                        )
                    if recursiveFlag:
                        substrate = substrate[length:]
                    else:
                        substrate = _substrate
                state = stStop
        return value, substrate
            
decode = Decoder(codecMap)

# XXX
# non-recursive decoding; return position rather than substrate
