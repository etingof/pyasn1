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
    params = {
        'zip_safe': True
        }    
except ImportError:
    for arg in sys.argv:
        if arg.find('egg') != -1:
            howto_install_setuptools()
            sys.exit(1)
    from distutils.core import setup
    params = {}

params.update( {
    'name': 'pyasn1',
    'version': '0.0.14',
    'description': 'ASN.1 types and codecs',
    'author': 'Ilya Etingof',
    'author_email': 'ilya@glas.net',
    'url': 'http://sourceforge.net/projects/pyasn1/',
    'license': 'BSD',
    'packages': [ 'pyasn1',
                  'pyasn1.type',
                  'pyasn1.codec',
                  'pyasn1.codec.ber',
                  'pyasn1.codec.cer',
                  'pyasn1.codec.der' ]
      } )

apply(setup, (), params)
