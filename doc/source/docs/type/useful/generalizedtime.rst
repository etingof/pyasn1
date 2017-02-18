
.. |ASN.1| replace:: GeneralizedTime

.. |encoding| replace:: iso-8859-1

|ASN.1| type
------------

.. autoclass:: pyasn1.type.useful.GeneralizedTime(value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   :members: hasValue, isSameTypeWith, isSuperTypeOf, tagSet

   .. note::


       The |ASN.1| type models a character string representing date and time in many different
       formats. For example, *20170126120000Z* stands for YYYYMMDDHHMMSSZ.

   .. automethod:: pyasn1.type.useful.GeneralizedTime.clone(self, value=NoValue(), tagSet=TagSet(), subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
   .. automethod:: pyasn1.type.useful.GeneralizedTime.subtype(self, value=NoValue(), implicitTag=TagSet(), explicitTag=TagSet(),subtypeSpec=ConstraintsIntersection(), encoding='us-ascii')
