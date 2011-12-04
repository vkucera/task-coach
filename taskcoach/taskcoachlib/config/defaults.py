'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
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

import wx
from taskcoachlib import meta


defaults = { \
'view': { \
    'statusbar': 'True',
    'toolbar': '(22, 22)',
    'effortviewerintaskeditor': '0', # Index of active effort viewer in task editor
    'taskviewercount': '1',          # Number of task viewers in main window
    'categoryviewercount': '1',      # Number of category viewers in main window
    'noteviewercount': '0',          # Number of note viewers in main window
    'effortviewercount': '0',        # Number of effort viewers in main window
    'squaretaskviewercount': '0',
    'timelineviewercount': '0',
    'calendarviewercount': '0',
    'taskstatsviewercount': '0',
    'language': '',                  # Language and locale, maybe set externally (e.g. by PortableApps)
    'language_set_by_user': '',      # Language and locale as set by user via preferences, overrides language
    'categoryfiltermatchall': 'False',
    'descriptionpopups': 'True',
    # The next three options are used in the effort dialog to populate the
    # drop down menu with start and stop times.
    'efforthourstart': '8',          # Earliest time, i.e. start of working day
    'efforthourend': '18',           # Last time, i.e. end of working day
    'effortminuteinterval': '15',    # Generate times with this interval
    'snoozetimes': "[5, 10, 15, 30, 60, 120, 1440]",
    'defaultsnoozetime': '5',        # Default snooze time
    'perspective': '',               # The layout of the viewers in the main window
    'datestied': '',                 # What to do when changing the start date or due date
    # Default date and times to offer in the task dialog, see preferences for
    # possible values.
    'defaultstartdatetime': 'preset_today_currenttime',
    'defaultduedatetime': 'propose_tomorrow_endofworkingday',
    'defaultcompletiondatetime': 'propose_today_currenttime',
    'defaultreminderdatetime': 'propose_tomorrow_startofworkingday',
},
'taskviewer': { \
    'title': '',                     # User supplied viewer title 
    'treemode': 'True',              # True = tree mode, False = list mode
    'sortby': 'dueDateTime',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "['startDateTime', 'dueDateTime']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28, 'notes': 28, 'ordering': 38}",
    'columnautoresizing': 'True',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False',
},              
'taskstatsviewer': { \
    'title': '',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False',
    'piechartangle': '30',
},
'prerequisiteviewerintaskeditor': { \
    'title': '',                     # User supplied viewer title 
    'treemode': 'True',              # True = tree mode, False = list mode
    'sortby': 'subject',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "['prerequisites', 'dependencies', 'startDateTime', 'dueDateTime']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28, 'notes': 28}",
    'columnautoresizing': 'True',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.   
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False' },
'squaretaskviewer': { \
    'title': '',
    'sortby': 'budget',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.   
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False' },
'timelineviewer': { \
    'title': '',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.   
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False' },
'calendarviewer': { \
    'title': '',
    'viewtype': '1',
    'periodcount': '1',
    'periodwidth': '150',
    'vieworientation': '1',
    'viewdate': '',
    'gradient': 'False',
    'shownostart': 'False',
    'shownodue': 'False',
    'showunplanned': 'False',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'tasksdue': 'Never',             # Show tasks when they're due today, tomorrow, etc.
    'taskscompleted': 'Never',       # Show tasks completed today, yesterday, etc.   
    'tasksinactive': 'Never',        # Show tasks when they'll be active today, tomorrow, etc.   
    'hideactivetasks': 'False',
    'hidecompositetasks': 'False',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'False',
    'sortbystatusfirst': 'True',
    'highlightcolor': '',
    'shownow': 'True' },
'categoryviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28, 'notes': 28}",
    'columnautoresizing': 'True' },
'categoryviewerintaskeditor': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28, 'notes': 28}",
    'columnautoresizing': 'True' },
'categoryviewerinnoteeditor': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28, 'notes': 28}",
    'columnautoresizing': 'True' },
'noteviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28}",
    'columnautoresizing': 'True' },
'noteviewerintaskeditor': {
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'columns': "['subject']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{}",
    'columnautoresizing': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False' },
'noteviewerincategoryeditor': {
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'columns': "['subject']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{}",
    'columnautoresizing': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False' },
'noteviewerinattachmenteditor': {
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'columns': "['subject']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{}",
    'columnautoresizing': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False' },
'effortviewer': { \
    'title': '',
    'aggregation': 'details', # 'details' (default), 'day', 'week', or 'month'
    'sortby': 'period',
    'sortascending': 'False',
    'sortcasesensitive': 'True',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{'period': 160, 'monday': 70, 'tuesday': 70, 'wednesday': 70, 'thursday': 70, 'friday': 70, 'saturday': 70, 'sunday': 70}",
    'columnautoresizing': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'round': '0' # round effort to this number of seconds, 0 = no rounding
},
'effortviewerintaskeditor': { \
    'aggregation': 'details', # 'details' (default), 'day', 'week', or 'month'
    'sortby': 'period',
    'sortascending': 'False',
    'sortcasesensitive': 'True',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'columnautoresizing': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'round': '0' # round effort to this number of seconds, 0 = no rounding
},
'attachmentviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['type', 'subject']",
    'columnwidths': "{'notes': 28, 'type': 28}",
    'columnautoresizing': 'True' },
'attachmentviewerintaskeditor': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['type', 'subject']",
    'columnwidths': "{'notes': 28, 'type': 28}",
    'columnautoresizing': 'True' },
'attachmentviewerinnoteeditor': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['type', 'subject']",
    'columnwidths': "{'notes': 28, 'type': 28}",
    'columnautoresizing': 'True' },
'attachmentviewerincategoryeditor': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'searchdescription': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['type', 'subject']",
    'columnwidths': "{'notes': 28, 'type': 28}",
    'columnautoresizing': 'True' },
'window': { \
    'size': '(700, 500)', # Default size of the main window
    'position': '(-1, -1)', # Position of the main window, undefined by default
    'iconized': 'False', # Don't start up iconized by default
    'maximized': 'False', # Don't start up maximized by default
    'starticonized': 'WhenClosedIconized', # 'Never', 'Always', 'WhenClosedIconized'
    'splash': 'True', # Show a splash screen while starting up
    'hidewheniconized': 'False', # Don't hide the window from the task bar
    'hidewhenclosed': 'False', # Close window quits the application
    'tips': 'True', # Show tips after starting up
    'tipsindex': '0', # Start at the first tip
    'blinktaskbariconwhentrackingeffort': 'True' },
'taskdialog': { \
    'size': '(-1, -1)',     # Size of the dialogs, calculated by default
    'position': '(-1, -1)', # Position of the dialog, undefined by default
    'maximized': 'False',   # Don't open the dialog maximized by default
    'perspectives': '{}'    # The layout of the tabs in the dialog
    },
'categorydialog': { \
    'size': '(-1, -1)',     # Size of the dialogs, calculated by default
    'position': '(-1, -1)', # Position of the dialog, undefined by default
    'maximized': 'False',   # Don't open the dialog maximized by default
    'perspectives': '{}'    # The layout of the tabs in the dialog
    },
'effortdialog': { \
    'size': '(-1, -1)',     # Size of the dialogs, calculated by default
    'position': '(-1, -1)', # Position of the dialog, undefined by default
    'maximized': 'False'    # Don't open the dialog maximized by default
    },
'notedialog': { \
    'size': '(-1, -1)',     # Size of the dialogs, calculated by default
    'position': '(-1, -1)', # Position of the dialog, undefined by default
    'maximized': 'False',   # Don't open the dialog maximized by default
    'perspectives': '{}'    # The layout of the tabs in the dialog
    },
'attachmentdialog': { \
    'size': '(-1, -1)',     # Size of the dialogs, calculated by default
    'position': '(-1, -1)', # Position of the dialog, undefined by default
    'maximized': 'False',   # Don't open the dialog maximized by default
    'perspectives': '{}'    # The layout of the tabs in the dialog
    },
'file': { \
    'recentfiles': '[]',
    'maxrecentfiles': '9',
    'lastfile': '',
    'autosave': 'False',
    'autoload': 'False',
    'autoimport': '[]',     # Formats to automatically import from, only "Todo.txt" supported at this time
    'autoexport': '[]',     # Formats to automatically export to, only "Todo.txt" supported at this time
    'nopoll': 'False',
    'backup': 'False',
    'saveinifileinprogramdir': 'False',
    'attachmentbase': '',
    'lastattachmentpath': '',
    'inifileloaded': 'True',
    'inifileloaderror': '' },
'fgcolor': { \
    'activetasks': '(0, 0, 0, 255)',
    'completedtasks': '(0, 255, 0, 255)',
    'overduetasks': '(255, 0, 0, 255)',
    'inactivetasks': '(192, 192, 192, 255)',
    'duesoontasks': '(255, 128, 0, 255)' },
'bgcolor': { \
    'activetasks': '(255, 255, 255, 255)',
    'completedtasks': '(255, 255, 255, 255)',
    'overduetasks': '(255, 255, 255, 255)',
    'inactivetasks': '(255, 255, 255, 255)',
    'duesoontasks': '(255, 255, 255, 255)' },
'font': { \
    'activetasks': '',
    'completedtasks': '',
    'overduetasks': '',
    'inactivetasks': '',
    'duesoontasks': '' },
'icon': { \
    'activetasks': 'led_blue_icon',
    'completedtasks': 'led_green_icon',
    'overduetasks': 'led_red_icon',
    'inactivetasks': 'led_grey_icon',
    'duesoontasks': 'led_orange_icon' },
'editor': { \
    'taskpages': '[]',        # Order of tabs in the task editor
    'categorypages': '[]',    # Order of tabs in the category editor
    'notepages': '[]',        # Order of tabs in the note editor
    'attachmentpages': '[]',  # Order of tabs in the attachment editor
    'preferencespages': '[]', # Order of tabs in the preferences dialog
    'maccheckspelling': 'True' },
'version': { \
    'python': '', # Filled in by the Settings class when saving the settings
    'wxpython': '', # Idem
    'pythonfrozen': '', # Idem
    'current': meta.data.version,
    'notified': meta.data.version,
    'notify': 'True' },
'behavior': { \
    'markparentcompletedwhenallchildrencompleted': 'True',
    'duesoonhours': '24' }, # When a task is considered to be "due soon"
'feature': { \
    'notes': 'True',
    'effort': 'True',
    'syncml': 'False',
    'iphone': 'False',
    'notifier': 'Task Coach',
    'minidletime': '0' },
'syncml': { \
    'url': '',
    'username': '',
    'preferredsyncmode': 'TWO_WAY',
    'verbose': 'True',
    'taskdbname': 'task',
    'notedbname': 'note',
    'synctasks': 'True',
    'syncnotes': 'True',
    'showwarning': 'True' },
'iphone': { \
    'password': '',
    'service': '',
    'synccompleted': 'True',
    'showlog': 'False' },
'printer': { \
    'margin_left': '0',
    'margin_top': '0',
    'margin_bottom': '0',
    'margin_right': '0',
    'paper_id': '0',
    'orientation': str(wx.PORTRAIT) },
'export': { \
    'html_selectiononly': 'False',
    'html_separatecss': 'False',
    'csv_selectiononly': 'False',
    'csv_separatedateandtimecolumns': 'False',
    'ical_selectiononly': 'False',
    'todotxt_selectiononly': 'False' }
}

minimum = { \
'view': { \
    'taskviewercount': '1' }
}
