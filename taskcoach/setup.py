#!/usr/bin/env python

from distutils.core import setup
from taskcoachlib import meta

setupOptions = { 
    'name' : meta.filename,
    'author' : meta.author,
    'author_email' : meta.author_email,
    'description' : meta.description,
    'version' : meta.version,
    'url' : meta.url,
    'license' : meta.license,
    'packages' : ["taskcoachlib."+subpackage for subpackage in 
        ["meta", "config", "date", "command", "widgets", "gui", "task",
        "effort", "patterns"]] + ["taskcoachlib"], 
    'scripts' : ["taskcoach.py", "taskcoach.pyw"],
    'classifiers' : [\
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Scheduling']}

if __name__ == '__main__':
    setup(**setupOptions)
