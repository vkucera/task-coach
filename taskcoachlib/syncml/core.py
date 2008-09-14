
import sys, os

_BINBASE = os.path.join(os.path.split(__file__)[0], '..', 'bin.in')

if sys.platform == 'linux2':
    sys.path.insert(0, os.path.join(_BINBASE, 'linux'))
elif sys.platform == 'darwin':
    sys.path.insert(0, os.path.join(_BINBASE, 'macos'))
else:
    sys.path.insert(0, os.path.join(_BINBASE, 'windows'))

from _pysyncml import *
