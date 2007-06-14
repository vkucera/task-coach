name = 'Task Coach'
description = 'Your friendly task manager'
version = '0.64.2'
release_month = 'June'
release_month_nr = '%02d'%(['January', 'February', 'March', 'April', 'May', 
                    'June', 'July', 'August', 'September', 'October', 
                    'November', 'December'].index(release_month) + 1)
release_day = '0'
release_day_nr = '%02d'%int(release_day)
release_year = '2007'
release_status = 'Alpha'
date = release_month + ' ' + release_day + ', ' + release_year
long_description = 'Task Coach is a simple open source todo manager to manage' \
' personal tasks and todo lists. It grew out of a frustration that ' \
'well-known task managers, such as those provided with Outlook or Lotus ' \
'Notes, do not provide facilities for composite tasks. Often, tasks and ' \
'other things todo consist of several activities. Task Coach is designed ' \
'to deal with composite tasks. '
keywords = 'task manager, todo list, pim, time registration, track effort'
author_first = 'Frank'
author_last = 'Niessink'
author = author_first + ' ' + author_last
author_email = 'frank@niessink.com'
filename = 'TaskCoach'
filename_lower = filename.lower()
url = 'http://www.taskcoach.org/'
screenshot = url + 'screenshot-0.62-treeview.png'
icon = url + 'taskcoach.png'
pad = url + 'pad.xml'
download = url + 'download.html'
dist_download_prefix = 'http://downloads.sourceforge.net/%s'%filename_lower
copyright = 'Copyright (C) 2004-%s %s'%(release_year, author)
license = 'GNU GENERAL PUBLIC LICENSE Version 2, June 1991'
platform = 'Any'
pythonversion = '2.4'
wxpythonversion = '2.8.4-unicode'
languages = {
    'English': None, 
    'French': 'fr', 
    'German': 'de',
    'Dutch': 'nl',
    'Russian': 'ru',
    'ChineseSimplified': 'zh',
    'Japanese': 'ja',
    'Spanish': 'es',
    'Slovak': 'sk',
    'Hungarian': 'hu',
    'Breton': 'br'}
languages_list = ','.join(languages.keys())

def __createDict(locals):
    ''' Provide the local variables as a dictionary for use in string
        formatting. '''
    metaDict = {}
    for key in locals:
        if not key.startswith('__'):
            metaDict[key] = locals[key]
    return metaDict

metaDict = __createDict(locals())

