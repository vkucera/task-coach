'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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

import sys, wx
from taskcoachlib import meta


defaults = { \
'view': { \
    'statusbar': 'True',
    'toolbar': '(22, 22)',
    'mainviewer': '0',               # Index of active viewer in main window
    'effortviewerintaskeditor': '0', # Index of active effort viewer in task editor
    'tasklistviewercount': '0',      # Number of task list viewers in main window
    'tasktreeviewercount': '0',      # (This viewer is currently not used)
    'tasktreelistviewercount': '1',  # Number of task tree list viewers in main window
    'categoryviewercount': '1',      # etc.
    'noteviewercount': '0',
    'effortlistviewercount': '0',
    'effortperdayviewercount': '0',
    'effortperweekviewercount': '0',
    'effortpermonthviewercount': '0',
    'perspective': '',
    'language': 'en_US',
    'taskcategoryfiltermatchall': 'True',
    'descriptionpopups': 'True',
    # The next three options are used in the effort dialog to populate the
    # drop down menu with start and stop times.
    'efforthourstart': '8',          # Earliest time, i.e. start of working day
    'efforthourend': '18',           # Last time, i.e. end of working day
    'effortminuteinterval': '15',    # Generate times with this interval
    'perspective': 'layout2|name=tasktreelistviewer;caption=Task tree;state=18428;dir=5;layer=0;row=0;pos=0;prop=100000;bestw=200;besth=200;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1|name=categoryviewer;caption=Categories;state=2099196;dir=2;layer=0;row=1;pos=0;prop=100000;bestw=100;besth=80;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=19;floaty=124;floatw=108;floath=104|name=toolbar;caption=Toolbar;state=2112240;dir=1;layer=10;row=0;pos=0;prop=100000;bestw=661;besth=36;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1|dock_size(5,0,0)=202|dock_size(1,10,0)=38|dock_size(2,0,1)=147|'},
'tasklistviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28}",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False',
    'hidecompositetasks': 'False' },
'tasktreeviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'tasktreelistviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28}",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'categoryviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'noteviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{}" },
'effortlistviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortlistviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewer': { 
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewerintaskeditor': { 
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'window': { \
    'size': '(700, 500)',
    'position': '(-1, -1)',
    'iconized': 'False',
    'starticonized': 'WhenClosedIconized', # 'Never', 'Always', 'WhenClosedIconized'
    'splash': 'True',
    'hidewheniconized': 'False',
    'hidewhenclosed': 'False',
    'tips': 'True',
    'tipsindex': '0',
    'blinktaskbariconwhentrackingeffort': 'True' },
'file': { \
    'recentfiles': '[]',
    'maxrecentfiles': '4',
    'lastfile': '',
    'autosave': 'False',
    'backup': 'False',
    'saveinifileinprogramdir': 'False',
    'attachmentbase': '' },
'color': { \
    'activetasks': '(0, 0, 0)',
    'completedtasks': '(0, 255, 0)',
    'overduetasks': '(255, 0, 0)',
    'inactivetasks': '(192, 192, 192)',
    'duetodaytasks': '(255, 128, 0)' },
'editor': { \
    'maccheckspelling': 'True' },
'version': { \
    'python': '', # Filled in by the Settings class when saving the settings
    'wxpython': '', # Idem
    'pythonfrozen': '', # Idem
    'current': meta.data.version,
    'notified': meta.data.version,
    'notify': 'True' },
'behavior': { \
    'markparentcompletedwhenallchildrencompleted': 'True' },
'feature': { \
    'notes': 'True' },
'syncml': { \
    'url': '',
    'client': 'TaskCoach',
    'username': '',
    'preferredsyncmode': 'TWO_WAY',
    'verbose': 'True',
    'taskdbname': 'task',
    'notedbname': 'note',
    'effortdbname': 'cal',
    'synctasks': 'True',
    'syncnotes': 'True',
    'syncefforts': 'False'
    },
}

minimum = { \
'view': { \
    'tasktreelistviewercount': 1 }
}
