#
# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
from io import BytesIO

from pyasn1.codec.ber.decoder import asSeekableStream
from pyasn1.codec.cer import decoder
from pyasn1.type import univ

__all__ = ['decode', 'decodeStream']


class BitStringDecoder(decoder.BitStringDecoder):
    supportConstructedForm = False


class OctetStringDecoder(decoder.OctetStringDecoder):
    supportConstructedForm = False

# TODO: prohibit non-canonical encoding
RealDecoder = decoder.RealDecoder

tagMap = decoder.tagMap.copy()
tagMap.update(
    {univ.BitString.tagSet: BitStringDecoder(),
     univ.OctetString.tagSet: OctetStringDecoder(),
     univ.Real.tagSet: RealDecoder()}
)

typeMap = decoder.typeMap.copy()

# Put in non-ambiguous types for faster codec lookup
for typeDecoder in tagMap.values():
    if typeDecoder.protoComponent is not None:
        typeId = typeDecoder.protoComponent.__class__.typeId
        if typeId is not None and typeId not in typeMap:
            typeMap[typeId] = typeDecoder


class Decoder(decoder.Decoder):
    supportIndefLength = False


_decode = Decoder(tagMap, decoder.typeMap)


def decodeStream(substrate, asn1Spec=None, **kwargs):
    """Iterator of objects in a substrate."""
    # TODO: This should become `decode` after API-breaking approved
    substrate = asSeekableStream(substrate)
    while True:
        result = _decode(substrate, asn1Spec, **kwargs)
        if result is None:
            break
        yield result
        # TODO: Check about eoo.endOfOctets?


#: Turns DER octet stream into an ASN.1 object.
#:
#: Takes DER octet-stream and decode it into an ASN.1 object
#: (e.g. :py:class:`~pyasn1.type.base.PyAsn1Item` derivative) which
#: may be a scalar or an arbitrary nested structure.
#:
#: Parameters
#: ----------
#: substrate: :py:class:`bytes` (Python 3) or :py:class:`str` (Python 2)
#:     DER octet-stream
#:
#: Keyword Args
#: ------------
#: asn1Spec: any pyasn1 type object e.g. :py:class:`~pyasn1.type.base.PyAsn1Item` derivative
#:     A pyasn1 type object to act as a template guiding the decoder. Depending on the ASN.1 structure
#:     being decoded, *asn1Spec* may or may not be required. Most common reason for
#:     it to require is that ASN.1 structure is encoded in *IMPLICIT* tagging mode.
#:
#: Returns
#: -------
#: : :py:class:`tuple`
#:     A tuple of pyasn1 object recovered from DER substrate (:py:class:`~pyasn1.type.base.PyAsn1Item` derivative)
#:     and the unprocessed trailing portion of the *substrate* (may be empty)
#:
#: Raises
#: ------
#: ~pyasn1.error.PyAsn1Error, ~pyasn1.error.SubstrateUnderrunError
#:     On decoding errors
#:
#: Examples
#: --------
#: Decode DER serialisation without ASN.1 schema
#:
#: .. code-block:: pycon
#:
#:    >>> s, _ = decode(b'0\t\x02\x01\x01\x02\x01\x02\x02\x01\x03')
#:    >>> str(s)
#:    SequenceOf:
#:     1 2 3
#:
#: Decode DER serialisation with ASN.1 schema
#:
#: .. code-block:: pycon
#:
#:    >>> seq = SequenceOf(componentType=Integer())
#:    >>> s, _ = decode(b'0\t\x02\x01\x01\x02\x01\x02\x02\x01\x03', asn1Spec=seq)
#:    >>> str(s)
#:    SequenceOf:
#:     1 2 3
#:
def decode(substrate, asn1Spec=None, **kwargs):
    # TODO: Temporary solution before merging with upstream
    #   It preserves the original API
    substrate = BytesIO(substrate)
    iterator = decodeStream(substrate, asn1Spec=asn1Spec, **kwargs)
    return next(iterator), substrate.read()
