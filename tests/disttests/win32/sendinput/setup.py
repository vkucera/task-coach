
from distutils.core import setup, Extension

setup(name='sendinput',
      ext_modules=[Extension('sendinput', ['sendinput.c'],
                             define_macros=[('_WIN32_WINNT', '0x0502')])])
