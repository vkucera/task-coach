#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import platform
from distutils.core import setup
from taskcoachlib import meta

# Import this  here so that py2exe  and py2app can  find the _pysyncml
# module.

import taskcoachlib.syncml.core

setupOptions = { 
    'name': meta.filename,
    'author': meta.author,
    'author_email': meta.author_email,
    'description': meta.description,
    'long_description': meta.long_description,
    'version': meta.version,
    'url': meta.url,
    'license': meta.license,
    'packages': ['taskcoachlib'] + 
        ['taskcoachlib.' + subpackage for subpackage in ('application', 'meta', 
        'config', 'command', 'widgets', 'gui', 'gui.dialog', 'i18n', 'patterns', 
        'mailer', 'help', 'domain', 'persistence', 'thirdparty', 'syncml')] +
        ['taskcoachlib.domain.' + subpackage for subpackage in ('base',
        'date', 'category', 'effort', 'task', 'note', 'attachment')] +
        ['taskcoachlib.persistence.' + subpackage for subpackage in ('xml', 
        'ics', 'html', 'csv')] + ['buildlib'],
    'scripts': ['taskcoach.py', 'taskcoach.pyw'],
    'classifiers': [\
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Scheduling']}

# Add available translations:
languages = sorted(meta.data.languages.keys())
for language in languages:
    setupOptions['classifiers'].append('Natural Language :: %s'%language)

# Add data files for Debian-based systems:
if 'debian' in platform.dist():
    setupOptions['data_files'] = [\
        ('share/applications', ['build.in/fedora/taskcoach.desktop']), 
        ('share/pixmaps', ['icons.in/taskcoach.png'])]


if platform.system() == 'Linux':
    setupOptions['package_data'] = {'taskcoachlib': ['bin.in/linux/_pysyncml.so']}


if __name__ == '__main__':
    setup(**setupOptions)
