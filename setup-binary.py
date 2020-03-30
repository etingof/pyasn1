# This file is part of pyasn1 software.
#
# Copyright (c) 2005-2018, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
# Created on 2018.06.12
#
# Author: Pedro Algarvio
#
# Copyright 2018 Giovanni Cannata
# Copyright 2018 Pedro Algarvio

# Import python libs
import os
import sys
import json
import glob
import shutil
import subprocess
import multiprocessing
import distutils.dist
# pylint: disable=no-name-in-module
from distutils.core import Command
from distutils.command.clean import clean
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext
from distutils.command.install import install
from setuptools import setup
from setuptools.command.develop import develop


# ----- Global Variables -------------------------------------------------------------------------------------------->
# Change to source's directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're most likely being frozen and __file__ triggered this NameError
    # Let's work around that
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])
if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)
NO_EXTENSIONS_PLACEHOLDER = object()

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Information Technology
Intended Audience :: System Administrators
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.4
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Communications
Topic :: Software Development :: Libraries :: Python Modules
"""

params = {
    'name': 'pyasn1-binary',
    'version': open(os.path.join(SETUP_DIRNAME, 'pyasn1', '__init__.py')).read().split('\'')[1],
    'description': 'ASN.1 types and codecs',
    'long_description': 'Pure-Python implementation of ASN.1 types and DER/BER/CER codecs (X.208)',
    'maintainer': 'Ilya Etingof <etingof@gmail.com>',
    'author': 'Ilya Etingof',
    'author_email': 'etingof@gmail.com',
    'url': 'https://github.com/etingof/pyasn1',
    'platforms': ['any'],
    'classifiers': [x for x in classifiers.split('\n') if x],
    'license': 'BSD',
    'packages': ['pyasn1',
                 'pyasn1.type',
                 'pyasn1.compat',
                 'pyasn1.codec',
                 'pyasn1.codec.ber',
                 'pyasn1.codec.cer',
                 'pyasn1.codec.der',
                 'pyasn1.codec.native']}
# Change to source's directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're most likely being frozen and __file__ triggered this NameError
    # Let's work around that
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])
if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)
# <---- Global Variables ---------------------------------------------------------------------------------------------


# ----- Custom Distutils/Setuptools Commands ------------------------------------------------------------------------>
class BuildPy(build_py):

    def find_package_modules(self, package, package_dir):
        modules = build_py.find_package_modules(self, package, package_dir)
        for package, module, filename in modules:
            if self.distribution.develop_mode is False:
                if package == 'pyasn1.codec.ber' and module in ('encoder',):
                    # We have issues when cython compiling asn1, include it as a python module
                    yield package, module, filename
                    continue
            if self.distribution.develop_mode is False and module not in ('__init__',):
                # We only want __init__ and _version python files
                # All others will be built as extensions
                continue
            yield package, module, filename


class BuildExt(build_ext):

    def run(self):
        self.extensions = self.distribution.get_ext_modules()
        build_ext.run(self)

    def build_extensions(self):
        if int(self.distribution.concurrency) > 1:
            self.check_extensions_list(self.extensions)
            import multiprocessing.pool
            multiprocessing.pool.ThreadPool(
                processes=int(self.distribution.concurrency)).map(
                    self.build_extension, self.extensions)
        else:
            build_ext.build_extensions(self)


class Clean(clean):

    def finalize_options(self):
        self.distribution._ext_modules = None
        clean.finalize_options(self)

    def run(self):
        clean.run(self)
        for subdir in ('pyasn1', 'tests'):
            root = os.path.join(os.path.dirname(__file__), subdir)
            for dirname, dirs, _ in os.walk(root):
                for to_remove_filename in glob.glob('{0}/*.py[ocx]'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.c'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.so'.format(dirname)):
                    os.remove(to_remove_filename)
                for dir_ in dirs:
                    if dir_ == '__pycache__':
                        shutil.rmtree(os.path.join(dirname, dir_))


class Develop(develop):

    def finalize_options(self):
        self.distribution.develop_mode = True
        develop.finalize_options(self)

    def run(self):
        # Clean up any previously generated cython files
        self.run_command('clean')
        develop.run(self)


class Install(install):

    def finalize_options(self):
        install.finalize_options(self)
        if self.distribution.has_ext_modules():
            self.install_lib = self.install_platlib

    def run(self):
        self.run_command('build_ext')
        install.run(self)


class BuildWheels(Command):

    description = 'Build manylinux1 wheel packages'
    user_options = []

    def initialize_options(self):
        '''
        Abstract method that is required to be overwritten
        '''

    def finalize_options(self):
        '''
        Abstract method that is required to be overwritten
        '''

    def run(self):
        try:
            docker_binary = subprocess.check_output('which docker', shell=True).decode(sys.stdin.encoding or 'asccii').strip()
        except subprocess.CalledProcessError:
            print('Docker binary not found')
            sys.exit(1)

        for manylinux_docker_image in ('quay.io/pypa/manylinux1_x86_64',
                                       'quay.io/pypa/manylinux1_i686'):
            if manylinux_docker_image.endswith('i686'):
                pre_cmd = 'linux32'
            else:
                pre_cmd = ''
            dest = manylinux_docker_image.replace('quay.io/pypa/manylinux1_', '')
            try:
                subprocess.check_call('{} pull {}'.format(docker_binary, manylinux_docker_image), shell=True)
            except subprocess.CalledProcessError as exc:
                print('Failed to download docker image {}: {}'.format(manylinux_docker_image, exc))
                sys.exit(1)
            try:
                subprocess.check_call(
                    '{docker_binary} run --rm -v `pwd`:/io {docker_image} {pre_cmd} '
                    '/io/build-binary-wheels.sh {dest} `id -u` `id -g`'.format(
                        docker_binary=docker_binary,
                        docker_image=manylinux_docker_image,
                        pre_cmd=pre_cmd,
                        dest=dest
                    ),
                    shell=True
                )
            except subprocess.CalledProcessError as exc:
                print('Failed to build package with docker image {}: {}'.format(manylinux_docker_image, exc))
                sys.exit(1)

        try:
            packages_listing = subprocess.check_output('ls wheelhouse/', shell=True).decode(sys.stdin.encoding or 'asccii')
            print('Built Packages')
            print(packages_listing)
        except subprocess.CalledProcessError as exc:
            print('Failed to list built packages: {}'.format(exc))
            sys.exit(1)
# <---- Custom Distutils/Setuptools Commands -------------------------------------------------------------------------


# ----- Custom Distribution Class ----------------------------------------------------------------------------------->
class Distribution(distutils.dist.Distribution):
    '''
    Distribution class
    '''

    DEFAULT_EXT_MODULES = object()
    global_options = distutils.dist.Distribution.global_options + [
        ('concurrency=', None, 'Parallelize extension module builds')
    ]

    def __init__(self, attrs=None):
        distutils.dist.Distribution.__init__(self, attrs)
        self._ext_modules = NO_EXTENSIONS_PLACEHOLDER
        self.concurrency = multiprocessing.cpu_count()
        self.develop_mode = False
        self.name = params['name']
        self.version = params['version']
        self.description = params['description']
        self.long_description = params['long_description']
        self.author = params['author']
        self.author_email = params['author_email']
        self.url = params['url']
        self.cmdclass.update(
            {
                'clean': Clean,
                'build_py': BuildPy,
                'build_ext': BuildExt,
                'install': Install,
                'build_wheels': BuildWheels,
                'develop': Develop,
            }
        )
        self.license = params['license']
        self.packages, self.package_dir, self.package_data = self.discover_packages()
        self.zip_safe = False
        self.update_metadata()

    def update_metadata(self):
        for attrname in dir(self):
            if attrname.startswith('__'):
                continue
            if attrname == 'ext_modules':
                # Don't trigger cythonize
                continue
            attrvalue = getattr(self, attrname, None)
            if attrvalue == 0:
                continue
            if hasattr(self.metadata, 'set_{0}'.format(attrname)):
                getattr(self.metadata, 'set_{0}'.format(attrname))(attrvalue)
            elif hasattr(self.metadata, attrname):
                try:
                    setattr(self.metadata, attrname, attrvalue)
                except AttributeError:
                    pass

    def find_ext(self):
        from Cython.Distutils.extension import Extension
        ret = []
        for package in ('pyasn1',):
            for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
                commonprefix = os.path.commonprefix([SETUP_DIRNAME, root])
                for filename in files:
                    full = os.path.join(root, filename)
                    if not filename.endswith(('.py', '.c')):
                        continue
                    if filename in ('__init__.py',):
                        continue
                    relpath = os.path.join(root, filename).split(commonprefix)[-1][1:]
                    if relpath in ('pyasn1/codec/ber/encoder.py',):
                        # We have issues when cython compiling asn1, skipt it
                        continue
                    module = os.path.splitext(relpath)[0].replace(os.sep, '.')
                    ret.append(Extension(module, [full]))
        return ret

    def discover_packages(self):
        modules = []
        pkg_data = {}
        pkg_dir = {}
        for package in ('pyasn1',):
            for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
                if '__init__.py' not in files:
                    continue
                pdir = os.path.relpath(root, SETUP_DIRNAME)
                modname = pdir.replace(os.sep, '.')
                modules.append(modname)
                pkg_data.setdefault(modname, []).append('*.so')
                pkg_dir[modname] = pdir
        return modules, pkg_dir, pkg_data

    def get_ext_modules(self):
        if self.develop_mode is False and self._ext_modules is NO_EXTENSIONS_PLACEHOLDER:
            from Cython.Build import cythonize
            self.ext_modules = self._ext_modules = cythonize(self.find_ext(),
                                                             nthreads=int(self.concurrency))
        return self._ext_modules

    # ----- Static Data -------------------------------------------------------------------------------------------->
    @property
    def _property_classifiers(self):
        return params['classifiers']

    #@property
    #def _property_dependency_links(self):
    #    return []

    #@property
    #def _property_tests_require(self):
    #    return ['pytest']
    # <---- Static Data ----------------------------------------------------------------------------------------------

    # ----- Dynamic Data -------------------------------------------------------------------------------------------->
    @property
    def _property_package_data(self):
        return self.package_data

    @property
    def _property_data_files(self):
        return []

    @property
    def _property_install_requires(self):
        return [i.strip() for i in open('requirements.txt').readlines()]

    @property
    def _property_extras_require(self):
        return {}

    @property
    def _property_scripts(self):
        return []

    @property
    def _property_setup_requires(self):
        return []

    #@property
    #def _property_entry_points(self):
    #    return {'console_scripts': ['...']}
    # <---- Dynamic Data ---------------------------------------------------------------------------------------------

    # ----- Overridden Methods -------------------------------------------------------------------------------------->
    def parse_command_line(self):
        args = distutils.dist.Distribution.parse_command_line(self)
        # Setup our property functions after class initialization and
        # after parsing the command line since most are set to None
        # ATTENTION: This should be the last step before returning the args or
        # some of the requirements won't be correctly set
        for funcname in dir(self):
            if not funcname.startswith('_property_'):
                continue
            property_name = funcname.split('_property_', 1)[-1]
            setattr(self, property_name, getattr(self, funcname))

        return args

    def has_ext_modules(self):
        # Make sure we tell distutils that this is not a pure python package
        return self.develop_mode is False

    def has_pure_modules(self):
        # Make sure we tell distutils that this is a pure python package
        return True
    # <---- Overridden Methods ---------------------------------------------------------------------------------------

# <---- Custom Distribution Class ------------------------------------------------------------------------------------
if __name__ == '__main__':
    setup(distclass=Distribution)
