# CER encoder
import string
from pyasn1.type import univ
from pyasn1.codec.ber import encoder

class BooleanEncoder(encoder.IntegerEncoder):
    def _encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        if client == 0:
            substrate = '\000'
        else:
            substrate = '\777'
        return substrate, 0

class BitStringEncoder(encoder.BitStringEncoder):
    def _encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        return encoder.BitStringEncoder._encodeValue(
            self, encodeFun, client, defMode, 1000
            )

class OctetStringEncoder(encoder.OctetStringEncoder):
    def _encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        return encoder.OctetStringEncoder._encodeValue(
            self, encodeFun, client, defMode, 1000
            )

# specialized RealEncoder here
# specialized GeneralStringEncoder here
# specialized GeneralizedTimeEncoder here
# specialized UTCTimeEncoder here

class SetOfEncoder(encoder.SequenceOfEncoder):
    def _cmpSetComponents(self, c1, c2):
        return cmp(
            getattr(c1, 'getMinimalTagSet', c1.getTagSet)(),
            getattr(c2, 'getMinimalTagSet', c2.getTagSet)()
            )
    
    def _encodeValue(self, encodeFun, client, defMode, maxChunkSize):
        if hasattr(client, 'setDefaultComponents'):
            client.setDefaultComponents()
        client.verifySizeSpec()
        substrate = ''; idx = len(client)
        # This is certainly a hack but how else do I distinguish SetOf
        # from Set if they have the same tags&constraints?
        if hasattr(client, 'getDefaultComponentByPosition'):
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

codecMap = encoder.codecMap.copy()
codecMap.update({
    univ.Boolean.tagSet: BooleanEncoder(),
    univ.BitString.tagSet: BitStringEncoder(),
    univ.OctetString.tagSet: OctetStringEncoder(),
    # Set & SetOf have same tags
    univ.SetOf().tagSet: SetOfEncoder()
    })
        
class Encoder(encoder.Encoder):
    def __call__(self, client, defMode=0, maxChunkSize=0):
        return encoder.Encoder.__call__(self, client, defMode, maxChunkSize)
        
encode = Encoder(codecMap)

# EncoderFactory queries class instance and builds a map of tags -> encoders
