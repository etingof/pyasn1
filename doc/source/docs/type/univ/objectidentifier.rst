
.. |ASN.1| replace:: ObjectIdentifier

|ASN.1| type
------------

.. autoclass:: pyasn1.type.univ.ObjectIdentifier(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection())
   :members: hasValue, isSameTypeWith, isSuperTypeOf, tagSet, subtypeSpec, isPrefixOf

   .. note::

        The |ASN.1| type models ASN.1 OBJECT IDENTIFIER as a sequence of integer numbers.

   .. automethod:: pyasn1.type.univ.ObjectIdentifier.clone(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection())
   .. automethod:: pyasn1.type.univ.ObjectIdentifier.subtype(value=NoValue(), implicitTag=Tag(), explicitTag=Tag(), subtypeSpec=ConstraintsIntersection())
