name = 'Task Coach'
description = 'Your friendly task manager'
version = '0.58'
previous_version = '0.57'
date = '? ?, 2006'
author = 'Frank Niessink'
author_email = 'frank@niessink.com'
url = 'http://taskcoach.niessink.com/'
copyright = 'Copyright (C) 2004-2006 Frank Niessink'
license = 'GNU GENERAL PUBLIC LICENSE Version 2, June 1991'
platform = 'Any'
filename = 'TaskCoach'
filename_lower = filename.lower()
pythonversion = '2.4.1'
wxpythonversion = '2.6.1.0-unicode'
languages = {
    'English': None, 
    'French': 'fr_FR', 
    'German': 'de_DE',
    'Dutch': 'nl_NL',
    'Russian': 'ru_RU',
    'Simplified Chinese': 'zh_CN',
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

