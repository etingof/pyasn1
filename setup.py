#!/usr/bin/env python
import sys

def howto_install_setuptools():
    print """Error: You need setuptools Python package!

It's very easy to install it, just type (as root on Linux):
   wget http://peak.telecommunity.com/dist/ez_setup.py
   python ez_setup.py
"""

try:
    from setuptools import setup
except ImportError:
    for arg in sys.argv:
        if "egg" in arg:
            howto_install_setuptools()
            sys.exit(1)
    from distutils.core import setup

setup(name="pyasn1",
      version="0.0.5a",
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
