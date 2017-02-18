
.. |ASN.1| replace:: PrintableString

.. |encoding| replace:: us-ascii

|ASN.1| type
------------

.. autoclass:: pyasn1.type.char.PrintableString(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   :members: hasValue, isSameTypeWith, isSuperTypeOf, tagSet

   .. note::

       The |ASN.1| models character string that can be entered from a very rudimentary terminals featuring letters,
       digits and punctuation marks.

   .. automethod:: pyasn1.type.char.PrintableString.clone(self, value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   .. automethod:: pyasn1.type.char.PrintableString.subtype(self, value=NoValue(), implicitTag=TagSet(), explicitTag=TagSet(),subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')