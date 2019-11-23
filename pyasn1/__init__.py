import sys

# https://www.python.org/dev/peps/pep-0396/
__version__ = '0.4.9'

if sys.version_info[:2] < (2, 7):
    raise RuntimeError('PyASN1 requires Python 2.7 or later')
