# CER encoder
import string
from pyasn1.type import univ
from pyasn1.codec.ber import encoder

class BooleanEncoder(encoder.IntegerEncoder):
    def encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        if client == 0:
            substrate = '\000'
        else:
            substrate = '\777'
        return substrate, 0

class BitStringEncoder(encoder.BitStringEncoder):
    def encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        return encoder.BitStringEncoder.encodeValue(
            self, encodeFun, client, defMode, 1000
            )

class OctetStringEncoder(encoder.OctetStringEncoder):
    def encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        return encoder.OctetStringEncoder.encodeValue(
            self, encodeFun, client, defMode, 1000
            )

# specialized RealEncoder here
# specialized GeneralStringEncoder here
# specialized GeneralizedTimeEncoder here
# specialized UTCTimeEncoder here

class SetOfEncoder(encoder.SequenceOfEncoder):
    def _cmpSetComponents(self, c1, c2):
        tagSet1 = isinstance(c1, univ.Choice) and \
                  c1.getMinTagSet() or c1.getTagSet()
        tagSet2 = isinstance(c2, univ.Choice) and \
                  c2.getMinTagSet() or c2.getTagSet()        
        return cmp(tagSet1, tagSet2)
    
    def encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        if isinstance(client, univ.SequenceAndSetBase):
            client.setDefaultComponents()
        client.verifySizeSpec()
        substrate = ''; idx = len(client)
        # This is certainly a hack but how else do I distinguish SetOf
        # from Set if they have the same tags&constraints?
        if isinstance(client, univ.SequenceAndSetBase):
            # Set
            comps = []
            while idx > 0:
                idx = idx - 1
                if client[idx] is None:  # Optional component
                    continue
                if client.getDefaultComponentByPosition(idx) == client[idx]:
                    continue
                comps.append(client[idx])
            comps.sort(self._cmpSetComponents)
            for c in comps:
                substrate = substrate + encodeFun(c, defMode, maxChunkSize)
        else:
            # SetOf
            compSubs = []
            while idx > 0:
                idx = idx - 1
                compSubs.append(
                    encodeFun(client[idx], defMode, maxChunkSize)
                    )
            compSubs.sort()  # perhaps padding's not needed
            substrate = string.join(compSubs, '')
        return substrate, 1

tagMap = encoder.tagMap.copy()
tagMap.update({
    univ.Boolean.tagSet: BooleanEncoder(),
    univ.BitString.tagSet: BitStringEncoder(),
    univ.OctetString.tagSet: OctetStringEncoder(),
    univ.SetOf().tagSet: SetOfEncoder()  # conflcts with Set
    })

typeMap = encoder.typeMap.copy()
typeMap.update({
    univ.Set.typeId: SetOfEncoder(),
    univ.SetOf.typeId: SetOfEncoder()
    })

class Encoder(encoder.Encoder):
    def __call__(self, client, defMode=0, maxChunkSize=0):
        return encoder.Encoder.__call__(self, client, defMode, maxChunkSize)

encode = Encoder(tagMap, typeMap)

# EncoderFactory queries class instance and builds a map of tags -> encoders
