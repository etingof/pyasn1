
.. |ASN.1| replace:: NumericString

.. |encoding| replace:: us-ascii

|ASN.1| type
------------

.. autoclass:: pyasn1.type.char.NumericString(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   :members: hasValue, isSameTypeWith, isSuperTypeOf, tagSet

   .. note::

       The |ASN.1| models character string that can be entered from a telephone handset.

   .. automethod:: pyasn1.type.char.NumericString.clone(self, value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   .. automethod:: pyasn1.type.char.NumericString.subtype(self, value=NoValue(), implicitTag=TagSet(), explicitTag=TagSet(),subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')