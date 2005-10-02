name = 'Task Coach'
description = 'Your friendly task manager'
version = '0.50'
previous_version = '0.49'
date = 'October 2, 2005'
author = 'Frank Niessink'
author_email = 'frank@niessink.com'
url = 'http://taskcoach.niessink.com/'
copyright = 'Copyright (C) 2004-2005 Frank Niessink'
license = 'GNU GENERAL PUBLIC LICENSE Version 2, June 1991'
platform = 'Any'
filename = 'TaskCoach'
filename_lower = filename.lower()
pythonversion = '2.4.1'
wxpythonversion = '2.5.5.1-unicode'
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
    formatting. See e.g. meta/help.py. '''
    metaDict = {}
    for key in locals:
        if not key.startswith('__'):
            metaDict[key] = locals[key]
    return metaDict

metaDict = __createDict(locals())

