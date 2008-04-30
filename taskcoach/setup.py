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

from distutils.core import setup
from taskcoachlib import meta

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
        ['taskcoachlib.' + subpackage for subpackage in ('meta', 'config', 
        'command', 'widgets', 'gui', 'gui.dialog', 'i18n', 'patterns', 
        'mailer', 'help', 'domain', 'persistence', 'thirdparty')] +
        ['taskcoachlib.domain.' + subpackage for subpackage in ('base',
        'date', 'category', 'effort', 'task', 'note', 'attachment')] +
        ['taskcoachlib.persistence.' + subpackage for subpackage in ('xml', 
        'ics', 'html', 'csv')] + ['buildlib'],
    'scripts': ['taskcoach.py', 'taskcoach.pyw'],
    # FIXME: this only makes sense on Linux systems:
    'data_files': [('share/applications', ['build.in/fedora/taskcoach.desktop']), ('share/pixmaps', ['icons.in/taskcoach.png'])],
    'classifiers': [\
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Dutch',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Spanish',
        'Natural Language :: Hungarian',
        'Natural Language :: Russian',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Scheduling']}

if __name__ == '__main__':
    setup(**setupOptions)
