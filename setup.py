#!/usr/bin/env python
from distutils.core import setup

setup(name="pyasn1",
      version="0.0.4a",
      description="ASN.1 library for Python",
      author="Ilya Etingof",
      author_email="ilya@glas.net ",
      url="http://sourceforge.net/projects/pyasn1/",
      packages = [ 'pyasn1',
                   'pyasn1.v1',
                   'pyasn1.v1.type',
                   'pyasn1.v1.codec',
                   'pyasn1.v1.codec.ber',
                   'pyasn1.v1.codec.cer',
                   'pyasn1.v1.codec.der' ],
      license="BSD"
      )
