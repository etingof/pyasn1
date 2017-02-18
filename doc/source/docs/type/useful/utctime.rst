
.. |ASN.1| replace:: UTCTime

.. |encoding| replace:: iso-8859-1

|ASN.1| type
------------

.. autoclass:: pyasn1.type.useful.UTCTime(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   :members: hasValue, isSameTypeWith, isSuperTypeOf, tagSet

   .. note::

       The |ASN.1| type models a character string representing date and time. An example
       format is *170126120000Z* which stands for YYMMDDHHMMSSZ.

   .. automethod:: pyasn1.type.useful.UTCTime.clone(self, value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   .. automethod:: pyasn1.type.useful.UTCTime.subtype(self, value=NoValue(), implicitTag=TagSet(), explicitTag=TagSet(),subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
