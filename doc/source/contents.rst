
ASN.1 library for Python
========================

.. toctree::
   :maxdepth: 2

Abstract Syntax Notation One (`ASN.1
<http://en.wikipedia.org/wiki/Abstract_Syntax_Notation_1x>`_) is a
well established and heavily used technology for storing and
exchanging structured data between programs and systems.  Many
Internet, encryption and telephony protocols carry out their
operations basing on ASN.1-defined data structures.

The pyasn1 library makes it easier for programmers and network
engineers to develop, debug and experiment with ASN.1-based protocols
using Python programming language as a tool.

ASN.1 overview
--------------

ASN.1 is a set of standards concered with provisioning instrumentation
for developing data exchange protocols in a robust, clear and
interoperabable way for various IT systems and applications. Most of
the efforts are targeting the following areas:

* Data structures: the standard introduces a collection of basic data types
  (similar to integers, bits, strings, arrays and records in a programming
  language) that can be used for defining complex, possibly nested data
  structures representing domain-specific data units.

* Serialization protocols: domain-specific data units expressed in ASN.1
  types could be converted into a series of octets for storage or transmission
  over the wire and then recovered back into their structured form on the
  receiving end. This process is immune to various hardware and software
  related dependencies.

* Data description language: could be used to describe particular set of
  domain-specific data structures and their relationships. Such a description
  could be passed to an ASN.1 compiler for automated generation of program
  code that represents ASN.1 data structures in language-native environment
  and handles data serialization issues.

ASN.1 applications
------------------

Being an old and generally successful standard, ASN.1 is widely
adopted for many uses. To give you an example, some ASN.1-based
protocols:

* Signaling standards for the public switched telephone network (SS7 family)
* Network management standards (SNMP, CMIP)
* Directory standards (X.500 family, LDAP)
* Public Key Infrastructure standards (X.509, etc.)
* PBX control (CSTA)
* IP-based Videoconferencing (H.323 family)
* Biometrics (BIP, CBEFF, ACBio)
* Intelligent transportation (SAE J2735)
* Cellular telephony (GSM, GPRS/EDGE, UMTS, LTE)

Library capabilities
--------------------

As of this moment, pyasn1 library implements all ASN.1 data
types as Python objects in accordance with X.208 standard. Later,
post-1995, revision (X.680) introduced significant changes most of
which have not yet been supported by pyasn1. Aside from data types
a collection of data serialization codecs comes with pyasn1 package.

As for ASN.1 data definition language support, pyasn1 package does
not support that. However, there's a tool called
`asn1late <https://github.com/kimgr/asn1ate>`_ which is an ASN.1
grammar parser paired to code generator capable of generating pyasn1
code. So this is an alternative (or at least a good start) to manual
implementation of pyasn1 classes from ASN.1 specification.

Both pyasn1 and pyasn1-modules libraries can be used out-of-the-box
with Python versions 2.4 through 3.5. No external dependencies
required.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   /docs/tutorial
   /docs/api-reference

Examples
--------

   .. toctree::
      :maxdepth: 2

      /examples

Implemented protocols
---------------------

Typically, pyasn1 is used for building arbitrary protocol support into
various applications. This involves manual translation of ASN.1 data
structures into their pyasn1 implementations. To save time and effort,
data structures for some of the popular protocols are pre-programmed
and kept for further re-use in form of the `pyasn1-modules package
<http://sourceforge.net/projects/pyasn1/files/pyasn1-modules>`_ For
instance, many structures for PKI (X.509, PKCS#*, CRMF, OCSP), LDAP
and SNMP are present.  Applications authors are advised to import and
use relevant modules from that package whenever needed protocol
structures are already there. New protocol modules contributions are
welcome.

Download
--------

Best way to obtain and install pyasn1 is usually to:

.. code-block:: bash

   # pip install pyasn1
   
If that does not work for you for some reason, you might need to read the 
following page.

   .. toctree::
      :maxdepth: 2

      /download

Changes
-------

All changes and release history is maintained in changelog.  There you
could also download the latest unreleased pyasn1 tarball containing
the latest fixes and improvements.

   .. toctree::
      :maxdepth: 1

      /changelog

License
-------

   .. toctree::
      :maxdepth: 2

      /license

Getting help
------------

Although pyasn1 software is almost a decade old and used in many production
environments, it still may have bugs and non-implemented pieces. Anyone
who happens to run into such defect is welcome to search or complain to
`pyasn1-users <https://lists.sourceforge.net/lists/listinfo/pyasn1-users>`_
mailing list or ask for help from
`Stack Overflow <http://stackoverflow.com/questions/tagged/pyasn1>`_ 
community.

Books on ASN.1
--------------

The algorithms implemented in the pyasn1 library are
largely based on the information from the following sources:

* `ITU standards <http://www.itu.int/ITU-T/studygroups/com17/languages/X.680-X.693-0207w.zip>`_
* `ASN.1 - Communication between heterogeneous systems <http://www.oss.com/asn1/dubuisson.html>`_ by Olivier Dubuisson
* `ASN.1 Complete <http://www.oss.com/asn1/resources/books-whitepapers-pubs/larmouth-asn1-book.pdf>`_ by Prof John Larmouth
* `A Layman's Guide to a Subset of ASN.1, BER, and DER <ftp://ftp.rsasecurity.com/pub/pkcs/ascii/layman.asc>`_ by Burton S. Kaliski

Please refer to books above for getting proper understanding of ASN.1
design and internals.

