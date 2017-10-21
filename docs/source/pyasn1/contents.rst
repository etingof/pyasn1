
.. _pyasn1:

ASN.1 types
-----------

The ASN.1 data description
`language <https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-X.208-198811-W!!PDF-E&type=items>`_
defines a handful of built-in data types. ASN.1 types exhibit different semantics
(e.g. number vs string) and can be distinguished from each other by
:ref:`tags <type.tag>`.

Subtypes can be created on top of base ASN.1 types by adding/overriding the
tags and/or imposing additional *constraints* on accepted values.

ASN.1 types in pyasn1 are Python objects. One or more ASN.1 types
comprise a *schema* describing data structures of unbounded complexity.

.. code-block:: python

   class RSAPublicKey(Sequence):
       """
       ASN.1 specification:

       RSAPublicKey ::= SEQUENCE {
           modulus           INTEGER,  -- n
           publicExponent    INTEGER   -- e
       }
       """
       componentType = NamedTypes(
           NamedType('modulus', Integer()),
           NamedType('publicExponent', Integer())
       )

ASN.1 schema can be "instantiated" by essentially putting some concrete value
into the type container. Such instantiated schema object can still be
used as a schema, but additionally it can play a role of a value in the
context of any applicable operator (e.g. arithmetic etc.).

.. code-block:: python

   rsaPublicKey = RSAPublicKey()

   # ASN.1 SEQUENCE type quacks like Python dict
   rsaPublicKey['modulus'] = 280789907761334970323210643584308373
   rsaPublicKey['publicExponent'] = 65537

Main use of ASN.1 schemas is to guide data transformation. Instantiated
ASN.1 schemas carry concrete data to/from data transformation services.

.. _isValue:

To tell instantiated schema object from just a schema, the *.isValue*
property can come in handy:

.. code-block:: python

   schema = RSAPublicKey()

   # non-instantiated schema
   assert schema.isValue == False

   rsaPublicKey['modulus'] = 280789907761334970323210643584308373

   # partially instantiated schema
   assert schema['modulus'].isValue == True
   assert schema.isValue == False

   rsaPublicKey['publicExponent'] = 65537

   # fully instantiated schema
   assert schema.isValue == True

Copies of existing ASN.1 types can be created with *.clone()* method.
All the existing properties of the prototype ASN.1 object get copied
over the new type unless the replacements are given. Main use-case
for *.clone()* is to instantiate a schema.

.. _clone:

.. code-block:: python

   instantiated_schema_A = Integer(1)

   # ASN.1 INTEGER type quacks like Python int
   assert instantiated_schema_A == 1

   instantiated_schema_B = instantiated_schema_A.clone(2)

   assert instantiated_schema_B == 2

.. _subtype:

New ASN.1 types can be created on top of existing ASN.1 types with
the *subtype()* method. Desired properties of the new type get
merged with the corresponding properties of the old type. Main use-case
for *.subtype()* is to assemble new ASN.1 types by :ref:`tagging <type.tag>`
or applying additional constraints to accepted type's values.

.. code-block:: python

   parent_type_schema = Integer()

   child_type_schema = parent_type_schema.subtype(
       explicitTag=Tag(tag.tagClassApplication, tag.tagFormatSimple, 0x06)
   )

   # test ASN.1 type relationships
   assert child_type_schema.isSubtypeOf(parent_type_schema) == True
   assert child_type_schema.isSameTypeWith(parent_type_schema) == False


.. toctree::
   :maxdepth: 2

   /pyasn1/type/univ/contents
   /pyasn1/type/char/contents
   /pyasn1/type/useful/contents
   /pyasn1/type/tag/contents
   /pyasn1/type/namedtype/contents
   /pyasn1/type/opentype/contents
   /pyasn1/type/namedval/contents

Serialisation codecs
--------------------

Common use-case for pyasn1 is to instantiate ASN.1 schema with
user-supplied values and pass instantiated schema to the encoder.
The encoder will then turn the data structure into serialized form
(stream of bytes) suitable for storing into a file or sending over
the network.

.. code-block:: python

    value = 1
    instantiated_schema = Integer(value)

    serialized = encode(instantiated_schema)

Alternatively, value and schema can be passed separately:

.. code-block:: python

    value = 1
    schema = Integer()

    serialized = encode(value, asn1Spec=schema)

At the receiving end, a decoder would be invoked and given the
serialized data as received from the network along with the ASN.1
schema describing the layout of the data structures. The outcome
would be an instance of ASN.1 schema filled with values as supplied
by the sender.

.. code-block:: python

    serialized = b'\x01\x01\x01'
    schema = Integer()

    value, _ = decode(serialized, asn1Spec=schema)

    assert value == 1

Many distinct serialization protocols exist for ASN.1, some are
implemented in pyasn1.

.. toctree::
   :maxdepth: 2

   /pyasn1/codec/ber/contents
   /pyasn1/codec/cer/contents
   /pyasn1/codec/der/contents
   /pyasn1/codec/native/contents
