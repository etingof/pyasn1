Download PyASN1
===============

.. toctree::
   :maxdepth: 2

The PyASN1 software is provided under terms and conditions of BSD-style 
license, and can be freely downloaded from Source Forge
`download servers <http://sourceforge.net/projects/pyasn1/files/>`_ or 
`PyPI <http://pypi.python.org/pypi/pyasn1/>`_. 

Besides official releases, it's advisable to try the cutting-edge
development code that could be taken from PyASN1
`source code repository <http://pyasn1.cvs.sourceforge.net/viewvc/pyasn1/pyasn1/?view=tar>`_.
It may be less stable in regards to general operation and changes to
public interfaces, but it's first to contain fixes to recently discovered bugs.

The best way to obtain PyASN1 and dependencies is to run:

.. code-block:: bash

   $ pip install pyasn1

or

.. code-block:: bash

   $ easy_install pyasn1

In case you do not have the easy_install command on your system but still 
would like to use the on-line package installation method, please install 
`setuptools <http://pypi.python.org/pypi/setuptools>`_ package by 
downloading and running `ez_setup.pz <https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_ bootstrap:

.. code-block:: bash

   # wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py 
   # python ez_setup.py

In case you are installing PyASN1 on an off-line system, the
installation procedure for PyASN1 is as follows 
(on UNIX-based systems):

.. code-block:: bash

   $ tar zxf package-X.X.X.tar.gz 
   $ cd package-X.X.X 
   # python setup.py install 
   # cd .. 
   # rm -rf package-X.X.X

In case of any issues, please `let us know <http://pyasn1.sourceforge.net/contact.html>`_ so we could try to help out.


