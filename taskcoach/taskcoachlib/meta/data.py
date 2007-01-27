name = 'Task Coach'
description = 'Your friendly task manager'
long_description = '''Task Coach is a simple open source todo manager to
manage personal tasks and todo lists. It grew out of a frustration that
well-known task managers, such as those provided with Outlook or Lotus
Notes, do not provide facilities for composite tasks. Often, tasks and
other things todo consist of several activities. Task Coach is designed
to deal with composite tasks. '''
version = '0.61.6'
date = 'January 27, 2006'
author = 'Frank Niessink'
author_email = 'frank@niessink.com'
url = 'http://www.taskcoach.org/'
copyright = 'Copyright (C) 2004-2007 Frank Niessink'
license = 'GNU GENERAL PUBLIC LICENSE Version 2, June 1991'
platform = 'Any'
filename = 'TaskCoach'
filename_lower = filename.lower()
pythonversion = '2.4.1'
wxpythonversion = '2.6.3.2-unicode'
languages = {
    'English': None, 
    'French': 'fr_FR', 
    'German': 'de_DE',
    'Dutch': 'nl_NL',
    'Russian': 'ru_RU',
    'Simplified Chinese': 'zh_CN',
    'Japanese': 'ja_JP',
    'Spanish': 'es_ES',
    'Hungarian': 'hu_HU'}

def __createDict(locals):
    ''' Provide the local variables as a dictionary for use in string
        formatting. '''
    metaDict = {}
    for key in locals:
        if not key.startswith('__'):
            metaDict[key] = locals[key]
    return metaDict

metaDict = __createDict(locals())

