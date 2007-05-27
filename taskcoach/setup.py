#!/usr/bin/env python

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
        'ics', 'html', 'csv')],
    'scripts': ['taskcoach.py', 'taskcoach.pyw'],
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
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Scheduling']}

if __name__ == '__main__':
    setup(**setupOptions)
