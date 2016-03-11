
ASN.1 library for Python
------------------------
[![Can I Use Python 3?](https://caniusepython3.com/project/pyasn1.svg)](https://caniusepython3.com/project/pyasn1)
[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/etingof/pyasn1/master/LICENSE.txt)
[![Downloads](https://img.shields.io/pypi/dm/pyasn1.svg)](https://pypi.python.org/pypi/pyasn1)
[![Build status](https://travis-ci.org/etingof/pyasn1.svg?branch=master)](https://secure.travis-ci.org/etingof/pyasn1)
[![Coverage Status](https://img.shields.io/codecov/c/github/etingof/pyasn1.svg)](https://codecov.io/github/etingof/pyasn1/coverage.svg?branch=master)

This is a free and open source implementation of ASN.1 types and codecs
as a Python package. It has been first written to support particular
protocol (SNMP) but then generalized to be suitable for a wide range
of protocols based on
[ASN.1 specification](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-X.208-198811-W!!PDF-E&type=items).

Features
--------

* Generic implementation of ASN.1 types (X.208)
* Fully standard compliant BER/CER/DER codecs
* 100% Python, works with Python 2.4 up to Python 3.5
* MT-safe

Misfeatures
-----------

* No ASN.1 compiler shipped with pyasn1, so by-hand ASN.1 spec compilation 
  into Python code would be needed. But there is a project, called
  [Asn1ate](https://github.com/kimgr/asn1ate) that compiles ASN.1 documents
  into pyasn1 code. 
* Codecs are not restartable

Installation
------------

Download pyasn1 from [PyPI](https://pypi.python.org/pypi/pyasn1) or just run:

    $ pip install pyasn1

Documentation
-------------

Information on pyasn1 APIs can be found in the
[documentation](http://pyasn1.sourceforge.net),
working examples are in the pyasn1-modules
[repo](https://github.com/etingof/pyasn1-modules).

Download
--------

The pyasn1 package is distributed under terms and conditions of 2-clause
BSD [license](http://pyasn1.sourceforge.net/license.html). Source code is freely
available as a Github [repo](https://github.com/etingof/pyasn1).

Feedback
--------

If something does not work as expected, try browsing pyasn1
[mailing list archives](https://sourceforge.net/p/pyasn1/mailman/pyasn1-users/)
or post your question
[to Stack Overflow](http://stackoverflow.com/questions/ask).  
Copyright (c) 2005-2016, [Ilya Etingof](http://ilya@glas.net).
All rights reserved.
