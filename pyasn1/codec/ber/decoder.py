# BER decoder
import types
from pyasn1.type import tag, base, univ, char, useful
from pyasn1.codec.ber import eoo
from pyasn1 import error

class AbstractDecoder:
    protoComponent = None
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        raise error.PyAsn1Error('Decoder not implemented for %s' % tagSet)

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        raise error.PyAsn1Error('Indefinite length mode decoder not implemented for %s' % tagSet)

class AbstractSimpleDecoder(AbstractDecoder):
    def _createComponent(self, asn1Spec, tagSet, value=None):
        if asn1Spec is None:
            return self.protoComponent.clone(value, tagSet)
        elif value is None:
            return asn1Spec
        else:
            return asn1Spec.clone(value)
        
class AbstractConstructedDecoder(AbstractDecoder):
    def _createComponent(self, asn1Spec, tagSet, value=None):
        if asn1Spec is None:
            return self.protoComponent.clone(tagSet)
        else:
            return asn1Spec.clone()
                                
class EndOfOctetsDecoder(AbstractSimpleDecoder):
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        return eoo.endOfOctets, substrate

class IntegerDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Integer(0)
    precomputedValues = {
        '\x00': 0,
        '\x01': 1,
        '\x02': 2,
        '\x03': 3,
        '\x04': 4,
        '\x05': 5,
        '\x06': 6,
        '\x07': 7,
        '\x08': 8,
        '\x09': 9,
        'xff': -1,
        'xfe': -2,
        'xfd': -3,
        'xfc': -4,
        'xfb': -5
        }
    
    def _valueFilter(self, value):
        try:
            return int(value)
        except OverflowError:
            return value
        
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        if substrate in self.precomputedValues:
            value = self.precomputedValues[substrate]
        else:
            firstOctet = ord(substrate[0])
            if firstOctet & 0x80:
                value = -1L
            else:
                value = 0L
            for octet in substrate:
                value = value << 8 | ord(octet)
            value = self._valueFilter(value)
        return self._createComponent(asn1Spec, tagSet, value), substrate

class BooleanDecoder(IntegerDecoder):
    protoComponent = univ.Boolean(0)
    def _valueFilter(self, value):
        if value:
            return 1
        else:
            return 0

class BitStringDecoder(AbstractSimpleDecoder):
    protoComponent = univ.BitString(())
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if tagSet[0][1] == tag.tagFormatSimple:    # XXX what tag to check?
            if not substrate:
                raise error.PyAsn1Error('Missing initial octet')
            trailingBits = ord(substrate[0])
            if trailingBits > 7:
                raise error.PyAsn1Error(
                    'Trailing bits overflow %s' % trailingBits
                    )
            substrate = substrate[1:]
            lsb = p = 0; l = len(substrate)-1; b = ()
            while p <= l:
                if p == l:
                    lsb = trailingBits
                j = 7                    
                o = ord(substrate[p])
                while j >= lsb:
                    b = b + ((o>>j)&0x01,)
                    j = j - 1
                p = p + 1
            return self._createComponent(asn1Spec, tagSet, b), ''
        r = self._createComponent(asn1Spec, tagSet, ())
        if not decodeFun:
            return r, substrate
        while substrate:
            component, substrate = decodeFun(substrate)
            r = r + component
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet, '')
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

class OctetStringDecoder(AbstractSimpleDecoder):
    protoComponent = univ.OctetString('')
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if tagSet[0][1] == tag.tagFormatSimple:    # XXX what tag to check?
            return self._createComponent(asn1Spec, tagSet, substrate), ''
        r = self._createComponent(asn1Spec, tagSet, '')
        if not decodeFun:
            return r, substrate
        while substrate:
            component, substrate = decodeFun(substrate)
            r = r + component
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet, '')
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

class NullDecoder(AbstractSimpleDecoder):
    protoComponent = univ.Null('')
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet)
        if substrate:
            raise error.PyAsn1Error('Unexpected substrate for Null')
        return r, substrate

class ObjectIdentifierDecoder(AbstractSimpleDecoder):
    protoComponent = univ.ObjectIdentifier(())
    def valueDecoder(self, substrate, asn1Spec, tagSet, length,
                     state, decodeFun):
        if not substrate:
            raise error.PyAsn1Error('Empty substrate')
        oid = (); index = 0        
        # Get the first subid
        subId = ord(substrate[index])
        oid = oid + divmod(subId, 40)

        index = index + 1
        substrateLen = len(substrate)
        
        while index < substrateLen:
            subId = ord(substrate[index])
            if subId < 128:
                oid = oid + (subId,)
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
                oid = oid + (subId,)
                index = index + 1
        return self._createComponent(asn1Spec, tagSet, oid), substrate[index:]

class SequenceDecoder(AbstractConstructedDecoder):
    protoComponent = univ.Sequence()
    def _getAsn1SpecByPosition(self, t, idx):
        if t.getComponentType() is not None:
            if isinstance(t, univ.Sequence):
                return t.getComponentTypeMapNearPosition(idx) # Sequence
            elif isinstance(t, base.AbstractConstructedAsn1Item):
                return t.getComponentType() # SequenceOf
        # or no asn1Specs

    def _getPositionByType(self, t, c, idx):
        if isinstance(t, univ.Sequence) and t.getComponentType() is not None:
            if isinstance(c, univ.Choice):
                effectiveTagSet = c.getEffectiveTagSet()
            else:
                effectiveTagSet = c.getTagSet()
            # Sequence
            return t.getComponentPositionNearType(effectiveTagSet, idx)
        else:
            return idx # SequenceOf or w/o asn1Specs

    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet)
        idx = 0
        if not decodeFun:
            return r, substrate
        while substrate:
            asn1Spec = self._getAsn1SpecByPosition(r, idx)
            component, substrate = decodeFun(
                substrate, asn1Spec
                )
            idx = self._getPositionByType(r, component, idx)
            r.setComponentByPosition(idx, component, asn1Spec is None)
            idx = idx + 1
        r.setDefaultComponents()
        r.verifySizeSpec()
        return r, substrate

    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet,
                             length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet)
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
            r.setComponentByPosition(idx, component, asn1Spec is None)
            idx = idx + 1                
        else:
            raise error.SubstrateUnderrunError(
                'No EOO seen before substrate ends'
                )
        r.setDefaultComponents()
        r.verifySizeSpec()
        return r, substrate

class SetDecoder(SequenceDecoder):
    protoComponent = univ.Set()
    def _getAsn1SpecByPosition(self, t, idx):
        if t.getComponentType() is not None:
            if isinstance(t, base.AbstractConstructedAsn1Item):            
                return t.getComponentTypeMap() # Set/SetOf
        # or no asn1Specs

    def _getPositionByType(self, t, c, idx):
        if t.getComponentType() is not None:
            if isinstance(t, univ.Set) and t.getComponentType():
                if isinstance(c, univ.Choice):
                    effectiveTagSet = c.getEffectiveTagSet()
                else:
                    effectiveTagSet = c.getTagSet()
                return t.getComponentPositionByType(effectiveTagSet) # Set
        return idx # SetOf or w/o asn1Specs
        
class ChoiceDecoder(AbstractConstructedDecoder):
    protoComponent = univ.Choice()
    def valueDecoder(self, substrate, asn1Spec, tagSet,
                     length, state, decodeFun):
        r = self._createComponent(asn1Spec, tagSet)
        if not decodeFun:
            return r, substrate
        if r.getTagSet() == tagSet: # explicitly tagged Choice
            component, substrate = decodeFun(
                substrate, r.getComponentTypeMap()
                )
        else:
            component, substrate = decodeFun(
                substrate, r.getComponentTypeMap(), tagSet, length, state
                )
        if isinstance(component, univ.Choice):
            effectiveTagSet = component.getEffectiveTagSet()
        else:
            effectiveTagSet = component.getTagSet()
        r.setComponentByType(effectiveTagSet, component, 0, asn1Spec is None)
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
  stGetValueDecoderByTag, stTryAsExplicitTag, stDecodeValue, stDumpRawValue,
  stErrorCondition, stStop ) = range(10)

class Decoder:
    defaultErrorState = stErrorCondition
    defaultRawDecoder = OctetStringDecoder()
    def __init__(self, codecMap):
        self.__codecMap = codecMap
        self.__emptyTagSet = tag.TagSet()
        self.__endOfOctetsTagSet = eoo.endOfOctets.getTagSet()
        # Tag & TagSet objects caches
        self.__tagCache = {}
        self.__tagSetCache = {}
    def __call__(self, substrate, asn1Spec=None, tagSet=None,
                 length=None, state=stDecodeTag, recursiveFlag=1):
        # Decode tag & length
        while state != stStop:
            if state == stDecodeTag:
                # Decode tag
                if not substrate:
                    raise error.SubstrateUnderrunError(
                        'Short octet stream on tag decoding'
                        )
                
                firstOctet = substrate[0]
                substrate = substrate[1:]
                if firstOctet in self.__tagCache:
                    lastTag = self.__tagCache[firstOctet]
                else:
                    t = ord(firstOctet)
                    tagClass = t&0xC0
                    tagFormat = t&0x20
                    tagId = t&0x1F
                    if tagId == 0x1F:
                        tagId = 0L
                        while 1:
                            if not substrate:
                                raise error.SubstrateUnderrunError(
                                    'Short octet stream on long tag decoding'
                                    )
                            t = ord(substrate[0])
                            tagId = tagId << 7 | (t&0x7F)
                            substrate = substrate[1:]
                            if not t&0x80:
                                break
                    lastTag = tag.Tag(
                        tagClass=tagClass, tagFormat=tagFormat, tagId=tagId
                        )
                    if tagId < 31:
                        # cache short tags
                        self.__tagCache[firstOctet] = lastTag
                if tagSet is None:
                    if firstOctet in self.__tagSetCache:
                        tagSet = self.__tagSetCache[firstOctet]
                    else:
                        # base tag not recovered
                        tagSet = tag.TagSet((), lastTag)
                        if firstOctet in self.__tagCache:
                            self.__tagSetCache[firstOctet] = tagSet
                else:
                    tagSet = lastTag + tagSet
                state = stDecodeLength
            if state == stDecodeLength:
                # Decode length
                if not substrate:
                     raise error.SubstrateUnderrunError(
                         'Short octet stream on length decoding'
                         )
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
            # 1) Either base types used in or no IMPLICIT tagging has been
            #    applied on subtyping.
            # 2) Subtype syntax drops base type information (by means of
            #    IMPLICIT tagging.
            # The first case allows for complete tag recovery from substrate
            # while the second one requires original ASN.1 type spec for
            # decoding.
            #
            # In either case a set of tags (tagSet) is coming from substrate
            # in an incremental, tag-by-tag fashion (this is the case of
            # EXPLICIT tag which is most basic). Outermost tag comes first
            # from the wire.
            #            
            if state == stGetValueDecoderByTag:
                if tagSet in self.__codecMap:
                    concreteDecoder = self.__codecMap[tagSet]
                else:
                    concreteDecoder = None
                if concreteDecoder:
                    state = stDecodeValue
                else:
                    _k = tagSet[:1]
                    if _k in self.__codecMap:
                        concreteDecoder = self.__codecMap[_k]
                    else:
                        concreteDecoder = None
                    if concreteDecoder:
                        state = stDecodeValue
                    else:
                        state = stTryAsExplicitTag
            if state == stGetValueDecoderByAsn1Spec:
                if type(asn1Spec) == types.DictType:
                    if tagSet in asn1Spec:
                        __chosenSpec = asn1Spec[tagSet]
                    else:
                        __chosenSpec = None
                elif asn1Spec is not None:
                    __chosenSpec = asn1Spec
                else:
                    __chosenSpec = None
                if __chosenSpec is not None and \
                       tagSet in __chosenSpec.getTypeMap():
                    # use base type for codec lookup to recover untagged types
                    baseTag = __chosenSpec.getTagSet().getBaseTag()
                    if baseTag: # XXX ugly
                        baseTagSet = tag.TagSet(baseTag, baseTag)
                    else:
                        baseTagSet = self.__emptyTagSet
                    if baseTagSet in self.__codecMap:
                        # tagged subtype
                        concreteDecoder = self.__codecMap[baseTagSet]
                    else:
                        concreteDecoder = None
                    if concreteDecoder:
                        asn1Spec = __chosenSpec
                        state = stDecodeValue
                    else:
                        state = stTryAsExplicitTag
                elif tagSet == self.__endOfOctetsTagSet:
                    concreteDecoder = self.__codecMap[tagSet]
                    state = stDecodeValue
                else:
                    state = stTryAsExplicitTag
            if state == stTryAsExplicitTag:
                if tagSet and \
                       tagSet[0][1] == tag.tagFormatConstructed and \
                       tagSet[0][0] != tag.tagClassUniversal:
                    # Assume explicit tagging
                    state = stDecodeTag
                else:
                    state = self.defaultErrorState
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
            if state == stDumpRawValue:
                concreteDecoder = self.defaultRawDecoder
                state = stDecodeValue
            if state == stErrorCondition:
                raise error.PyAsn1Error(
                    '%s not in asn1Spec: %s' % (tagSet, asn1Spec)
                    )

        return value, substrate
            
decode = Decoder(codecMap)

# XXX
# non-recursive decoding; return position rather than substrate
