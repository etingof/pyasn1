from pyasn1.type import tag, namedtype, univ
from pyasn1.codec.native import encoder, decoder
from pyasn1 import debug

x = str(univ.BitString('111'))

x = repr(univ.BitString('111'))

univ.BitString((1,1,1,1,1))[:3]

#debug.setLogger(debug.Debug('all'))
#
# class TBSCertificate(univ.Sequence):
#     componentType = namedtype.NamedTypes(
#         namedtype.DefaultedNamedType('version', univ.Integer(1).subtype(
#             explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0))),
#         namedtype.NamedType('serialNumber', univ.Integer()),
#         namedtype.NamedType('issuer', univ.OctetString())
#     )
#
#
# tbsCertificate = TBSCertificate()
#
# tbsCertificate.update(version=1, serialNumber=2, issuer='someone'),
#
# class Certificate(univ.Sequence):
#     componentType = namedtype.NamedTypes(
#         namedtype.NamedType('tbsCertificate', TBSCertificate()),
#         namedtype.NamedType('signatureAlgorithm', univ.ObjectIdentifier()),
#         namedtype.NamedType('signatureValue', univ.BitString())
#     )
#
# certificate = Certificate()
#
# certificate.update(
#     tbsCertificate=tbsCertificate,
#     signatureAlgorithm='1.3.2.1',
#     signatureValue=(1, 0, 1, 0, 1, 1, 1, 1)
# )
#
# #print(certificate.prettyPrint())
#
# substrate = encoder.encode(certificate)
#
# #print(substrate)
#
# certificate = decoder.decode(substrate, asn1Spec=Certificate())
#
# #print(certificate.prettyPrint())


from pyasn1_modules import rfc2459

from pyasn1.codec.der import decoder, encoder
from pyasn1.error import PyAsn1Error
from pyasn1.type import namedtype, univ
#
#
# class _DSSSigValue(univ.Sequence):
#     componentType = namedtype.NamedTypes(
#         namedtype.NamedType('r', univ.Integer()),
#         namedtype.NamedType('s', univ.Integer())
#     )
#
# def decode_dss_signature(signature):
#     try:
#         data, remaining = decoder.decode(signature, asn1Spec=_DSSSigValue())
#     except PyAsn1Error:
#         raise ValueError("Invalid signature data. Unable to decode ASN.1")
#
#     if remaining:
#         raise ValueError(
#             "The signature contains bytes after the end of the ASN.1 sequence."
#         )
#
#     r = int(data.getComponentByName('r'))
#     s = int(data.getComponentByName('s'))
#     return (r, s)
#
#
# sig=bytes.fromhex('3045022100a99e5b6a71f5622367286433638db4a7808becc63642d5f98a8c48b8f82fd82802201b872c32a1563df4918333960a3d0036ae4e2a8c4a7d77de182cbdba2dd5d061')

import cProfile

pr = cProfile.Profile()
pr.enable()

#for x in range(20000):
#    x = decode_dss_signature(sig)



substrate = b'0\x82\x02\xe70\x82\x02P\x02\x01\x010\r\x06\t*\x86H\x86\xf7\r\x01\x01\x05\x05\x000\x81\xbb1$0"\x06\x03U\x04\x07\x13\x1bValiCert Validation Network1\x170\x15\x06\x03U\x04\n\x13\x0eValiCert, Inc.1503\x06\x03U\x04\x0b\x13,ValiCert Class 3 Policy Validation Authority1!0\x1f\x06\x03U\x04\x03\x13\x18http://www.valicert.com/1 0\x1e\x06\t*\x86H\x86\xf7\r\x01\t\x01\x16\x11info@valicert.com0\x1e\x17\r990626002233Z\x17\r190626002233Z0\x81\xbb1$0"\x06\x03U\x04\x07\x13\x1bValiCert Validation Network1\x170\x15\x06\x03U\x04\n\x13\x0eValiCert, Inc.1503\x06\x03U\x04\x0b\x13,ValiCert Class 3 Policy Validation Authority1!0\x1f\x06\x03U\x04\x03\x13\x18http://www.valicert.com/1 0\x1e\x06\t*\x86H\x86\xf7\r\x01\t\x01\x16\x11info@valicert.com0\x81\x9f0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x81\x8d\x000\x81\x89\x02\x81\x81\x00\xe3\x98Q\x96\x1c\xe8\xd5\xb1\x06\x81jW\xc3ru\x93\xab\xcf\x9e\xa6\xfc\xf3\x16R\xd6-M\x9f5D\xa8.\x04M\x07I\x8a8)\xf5w7\xe7\xb7\xab]\xdf6q\x14\x99\x8f\xdc\xc2\x92\xf1\xe7`\x92\x97\xec\xd8H\xdc\xbf\xc1\x02 \xc6$\xa4(L0Zvm\xb1\\\xf3\xdd\xde\x9e\x10q\xa1\x88\xc7[\x9bAm\xca\xb0\xb8\x8e\x15\xee\xad3+\xcfG\x04\\uq\n\x98$\x98)\xa7IY\xa5\xdd\xf8\xb7Cba\xf3\xd3\xe2\xd0U?\x02\x03\x01\x00\x010\r\x06\t*\x86H\x86\xf7\r\x01\x01\x05\x05\x00\x03\x81\x81\x00V\xbb\x02X\x84g\x08,\xdf\x1f\xdb{I3\xf5\xd3g\x9d\xf4\xb4\n\x10\xb3\xc9\xc5,\xe2\x92jqx\'\xf2p\x83B\xd3>\xcf\xa9T\xf4\xf1\xd8\x92\x16\x8c\xd1\x04\xcbK\xab\xc9\x9fE\xae<\x8a\xa9\xb0q3]\xc8\xc5W\xdf\xaf\xa85\xb3\x7f\x89\x87\xe9\xe8%\x92\xb8\x7f\x85z\xae\xd6\xbc\x1e7X*g\xc9\x91\xcf*\x81>\xed\xc69\xdf\xc0>\x19\x9c\x19\xcc\x13M\x82A\xb5\x8c\xde\xe0=`\x08 \x0fE~k\xa2\x7f\xa3\x8c\x15\xee'

# 17 secs
# 13 secs (w/o SequenceAndSetBase.clone())

for x in range(1000):
    cert, rest = decoder.decode(substrate, asn1Spec=rfc2459.Certificate())

    if encoder.encode(cert) != substrate:
        raise Exception('!!!')

pr.disable()
pr.print_stats(sort='tottime')

#
# partialAsn1Spec = Certificate()
#
# partialAsn1Spec.update(tbsCertificate=dict(serialNumber=13))
#
# partialCertificate, _ = decoder.decode(substrate, asn1Spec=partialAsn1Spec)
#
# print(partialCertificate.prettyPrint())
