# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2009 Jerome Laheurte <fraca7@free.fr>

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

from changetypes import *

releases = [

Release('0.72.10', 'June ??, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''When opening a task edit dialog, the priority field would not
show the priority until the up or down button was clicked (Mac OS X only).'''),
        Bug('''When opening a locked file, Task Coach would hang
(Mac OS X only).'''),
        Bug('''Require wxPython 2.8.9.1 instead of 2.8.9.2 in the Debian 
package file (.deb) because Ubuntu 9.04 is still shipping 2.8.9.1 (Ubuntu 
only).''', '2798457'),
        Bug('''When logging off or shutting down the computer save unsaved 
changes (Linux only).'''),
        Bug('''When using SyncML the task file could get corrupted.''')
        ]
    ),
    
Release('0.72.9', 'May 28, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Don't throw an exception when exporting an active effort record
to iCal format.'''),
        Bug('''Refuse to open task files that have a different format because
they are created by a newer version of Task Coach than the one the user is 
using.'''),
        Bug('''Updating menu items would trigger exceptions after closing a
(task) viewer.'''),
        Bug('''After merging, Task Coach would display the wrong filename in the
window title.'''),
        Bug('''Smaller task edit dialog to cater for lower resolution 
screens.''', '2214687'),
        Bug('''Dragging email from a Thunderbird client that uses Gmail as IMAP
server didn't work.'''),
        Bug('''When the SyncML feature is turned on, Task Coach would show 
deleted tasks in the drop down menu of the start effort tracking button on the 
toolbar and it would show effort for deleted tasks in the effort viewer.''', 
'2679544', '2214043')
        ],
    featuresAdded=[
        Feature('''All export options can now also export selected items only.'''),
        Feature('''Put line breaks in the XML so that task files are 
easier to examine in a text editor.''', '1277365')
        ]
    ),
    
Release('0.72.8', 'May 17, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Drag and drop from Thunderbird would not work on Debian-derived 
distributions.''', '2790274'),
        Bug('''Work around a bug in wxPython 2.8.9.2 on Mac OS X that prevented
dialogs to be opened for items that have a color set.''', '2789977'),
        Bug('''Draw check boxes instead of black squares in the category viewer
on Windows XP and Vista with the classic theme.'''),
        Bug('''The background of check boxes were corrupted under Linux.'''),
        Bug('''Double clicking an item in a specific column wouldn't select the 
appropriate tab in the dialog.''', '2791100'),
        Bug('''Reduce flickering when tracking effort for a task.'''),
        Bug('''Opening a task file with e-mail attachments not specifying their
encoding on a different system than the one the task file was created could fail.'''),
        Bug('''Couldn't add effort to a freshly created task.''')
        ],
    featuresAdded=[
        Feature('''Use the settings for effort dialog start and stop times for
the reminder drop down as well.''', '2792160')
        ],
    dependenciesChanged=[
        Dependency('''Task Coach now at least needs wxPython 2.8.9.2-unicode.
Since the Windows installer and the Mac OS X dmg package have wxPython included, 
this only affects users of the RPM, Debian, and source distributions.''')
        ]
),

Release('0.72.7', 'May 10, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Support locking of task files on USB sticks/drives that
have a different file system than the host system has.''', '2776249'),
        Bug('''Task Coach would sometimes crash when dragging a task onto 
another task on Windows. Fixed by using a different widget for tree-list 
controls.''', '2573263', '1995248', '2247808', '1963262')
    ],
    featuresAdded=[
        Feature('''The category viewer can show additional columns (description,
attachment, ...) besides just the subject of categories. This is a side effect 
of the fix for the drag and drop issues.''')
    ],
    websiteChanges=[
        Website('''Follow Task Coach on twitter: http://twitter.com/taskcoach. 
The latest tweets are also listed on http://www.taskcoach.org.''', 'index.html'),
        Website('''Added Google Ads to generate additional revenue to cover the
cost of hardware and commercial operating systems.''', 'index.html')
    ]
),

Release('0.72.6', 'April 18, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Task Coach couldn't be installed using EasyInstall.'''),
        Bug('''Task Coach couldn't be installed on Linux systems that have 
2.6 as their default Python version. Task Coach currently needs Python 2.5.
Fixed by forcing an install for Python 2.5 on all Linux systems when 
installing from a RPM or Debian package.''', '2724839'),
        Bug('''The lockfile package used for file locking had a bug when
used with Python 2.6. Fixed by upgrading the lockfile package to version 
0.8.''', '2761466'),
        Bug('''Task Coach would sometimes crash when dragging a task onto 
another task on Windows.''', '2573263', '1995248')
    ]
),

Release('0.72.5', 'April 5, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Include the lockfile package in the distributions.''')
    ]
),

Release('0.72.4', 'April 5, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''When exporting effort to iCalendar format, use 'floating times'
rather than UTC.''', '2722224'),
        Bug('''Lock a task file while the user is working on it. Note that
locks are only honored by Task Coach itself; locked files can still be 
removed using a file explorer.''', '2318647', '2236420'),
        Bug('''Fail silently if checking for the availability of a new 
Task Coach version doesn't work for some reason.''', '2669995'),
        Bug('''Don't open the category edit dialog when the user double clicks
a category check box.''', '2685754'),
        Bug('''In the budget page of the task edit dialog, make sure that 
selected values can be overwritten.''', '2654254'),
        Bug('''Make the Debian package work with python versions >= 2.5 
(but smaller than python 3.0).''', '2724839')
    ]
),

Release('0.72.3', 'March 13, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Don't turn on the color selection in the task edit dialog when 
the task color is based on the category it belongs to.'''),
        Bug('''Make it easier to edit budget values in the task edit 
dialog.''', '2654254'),
        Bug('''Fix regression caused by the saving of print margins added in 
release 0.72.2.''', '2632431')
    ]
),
            
Release('0.72.2', 'March 11, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Support drag and drop from Thunderbird Portable under
Windows''', '2665317'),
        Bug('''Correctly read task files with version <= 13 (Task Coach release
0.57 and earlier) that contain categories.'''),
        Bug('''When a subtask belongs to a category with color, use that 
color to color the subtask, rather than the color of the parent task.'''),
        Bug('''Save print margins in the TaskCoach.ini file.''', '2632431')
        ]
    ),
            
Release('0.72.1', 'February 14, 2009',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Drag and drop from Thunderbird wouldn't work with
GMail IMAP accounts.''', '2549194'),
        Bug('''Exception when synchronizing with the new version of
ScheduleWorld.''',
            '2553046'),
        Bug('''On MacOS, the window height would increase by 29 pixels
each time Task Coach is launched.'''),
        Bug('''Exporting a selection of effort records resulted in an empty 
HTML file.'''),
        Bug('''Opening a task from a reminder dialog didn't work.''', 
            '2580772'),
        Bug('''Include effort for subtasks in the effort viewer for one task.'''),
        Bug('''Correctly display error message when the user enters an invalid
regular expression in a search control.'''),
        Bug('''Update the task square map viewer when the task status changes
(e.g. when a task is completed).'''),
        Bug('''When SyncML is enabled and the last subtask of a task is
deleted, correctly update the icon in the task viewer.''')
        ],
    featuresAdded=[
        Feature('''When the single task, whose effort records are shown in
a single task effort viewer, is removed, the effort viewer resets to
show all effort records of all tasks.'''),
        Feature('''Tool tips for task square map viewer.''')
        ]
    ),

Release('0.72.0', 'January 30, 2009', 
    summary='''This release adds a square map task viewer and a 
single-task effort viewer. This release also fixes a few bugs and adds a few
smaller feature enhancements.''',
    featuresAdded=[
        Feature('''One can now export only the current selection as HTML.'''),
        Feature('''When using yearly recurrence of tasks, allow for keeping
the recurring date on the same weekday (e.g. to recur on the first
Monday of the year).''', '2164568'),
        Feature('''Added a square map viewer for tasks that displays tasks in 
the form of a set of nested squares. The relative size of the squares is 
determined by either budget, budget left, time spent, fixed fee or revenue.'''),
        Feature('''One can now open an effort viewer for a specific task.'''),
        Feature('''Added (incomplete) Hindi and German (Low) translations.''')
        ],
    bugsFixed=[
        Bug('''Don't crash when adding a task.''', '2467347'),
        Bug('''Update the total fixed fee column in the task viewer when
adding a subtask with a fixed fee.'''),
        Bug('''Mark task file dirty when the user edits a task color.'''),
        Bug('''Update the hourly fee column in the task viewer when the 
the user edits the hourly fee of a task.'''),
        Bug('''Make it possible to add an effort record to a new task.'''),
        Bug('''When opening all attachments of an item, give an error message
for each attachment that cannot be opened.''')
        ]
    ),

Release('0.71.5', 'December 24, 2008',
    summary='''This release adds one usability enhancement and a few bug 
fixes.''',
    featuresAdded=[
        Feature('''When double clicking an item in a viewer, open the editor
on the right page, depending on the column clicked. For example, when clicking
on the due date column in a task viewer, Task Coach will open the task editor
with the dates page raised. Patch provided by Carl Zmola.''')
        ],
    bugsFixed=[
        Bug('''Don't wake up every second just to keep track of reminders and 
midnight.'''),
        Bug('''Hide main window after showing reminder dialog when it was 
hidden before.''', '2372909'),
        Bug('''When marking a recurring task completed, recur its reminder too, 
if any.''', '2376415'),
        Bug('''Refresh task status at midnight.''', '2095205'),
        Bug('''Fix tab traversal in the effort editor on Linux.''', '1965751')
        ]
    ),
             
Release('0.71.4', 'December 6, 2008',
    summary='''This is a bugfix release.''',
    featuresAdded=[
        Feature('''Add a "Purge deleted items" entry in the File menu for
people who have been using Task Coach with SyncML disabled.'''),
    ],
    bugsFixed=[
        Bug('''Opening an old .tsk file with missing e-mail attachments
would crash Task Coach.'''),
        Bug('''Don't throw exception when showing an (error) message while
synchronizing.''', '2356799'),
        Bug('''When merging from the same file multiple times, update the
existing items instead of duplicating them.''', '2062616'),
        Bug('''Don't set negative priorities to zero in the task editor
(Linux only).''', '2324869'),
        Bug('''Save the column width of the first column when automatic 
resizing of columns is off.''', '2255690'),
        Bug('''Actually delete tasks and notes when SyncML is disabled.''',
            '2319921'),
        Bug('''Do not create subitems in two steps, this is counter intuitive.'''),
        Bug('''Properly iterate over the open viewers with Ctrl-PgDn and 
Ctrl-PgUp.''', '1973357'),
        Bug('''Update the task viewer when a note is deleted from a task.''',
            '2277217'),
        Bug('''Update the tray icon tool tip when deleting an overdue task.''',
            '2321351'),
        Bug('''Wrap long lines in description tool tip windows.''', '2318094')
        ]
    ),
            
Release('0.71.3', 'November 10, 2008',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Spell checking in editor didn't work under Mac OS X.''', '2214676'),
        Bug('''Dropping a mail with several recipients from Outlook would result
in a "No subject" subject.''', '2220224'),
        Bug('''A ghost window would appear on the secondary display under 
Mac OS X if it's placed on the right.''', '2206656'),
        Bug('''The note total would include deleted notes.''', '2209640'),
        Bug('''Don't hang when exiting the application.''', '2185910', '2209679'),
        Bug('''Don't show all effort in the effort tab of a task editor, but
only effort for the task being edited.''', '2207166'),
        Bug('''Fix for a backwards incompatible change in python 2.6.''', 
            '2212857'),
        Bug('''Update task details at midnight, even when Task Coach is not 
active at precisely midnight.''', '2095205', '2061826'),
        Bug('''Allow for empty task subjects.''', '2214812'),
        Bug('''Make the drop down button for picking dates look disabled when
it is disabled.''', '2214706')
        ]
    ),

Release('0.71.2', 'October 24, 2008',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''The reminder dialog didn't work.''', '2168756'),
        Bug('''One couldn't add an URI attachment "by hand".''', '2167705'),
        Bug('''The combobox with tasks in the effort editor
wouldn't always be properly filled, making it impossible to edit the effort
record.''', '2167798', '2173127'),
        Bug('''Warn the user when the task file cannot be saved.''', '2121470'),
        Bug('''Warn the user when the TaskCoach.ini file cannot be loaded.''',
            '2101765'),
        Bug('''When saving selected tasks, also include any categories the 
selected tasks are in.'''),
        Bug('''The right-click menu item 'Start tracking effort' wouldn't 
work for recurring tasks.''', '2165652')
        ],
    featuresAdded = [
        Feature('''The SyncML password dialog now has a more specific
title.''', '2176781'),
        Feature('''The system tray popup menu now has a 'New note' menu 
item.''', '2182735')
        ]
    ),

Release('0.71.1', 'October 13, 2008',
    summary='''This is a bugfix release.''',
    bugsFixed=[
        Bug('''Older task files containing e-mail attachments could
not be opened.'''),
        Bug('''Newly created templates would not appear in the Task
menu, only in the toolbar template button.'''),
        Bug('''Installing from source wouldn't work on platforms
where pysyncml is not supported.''', '2164313'),
        Bug('''The installers for Mac OS X and Windows for release 0.71.0
were missing some files, causing Task Coach not to be able to save.''', 
        '2162181')
        ]
    ),

Release('0.71.0', 'October 12, 2008',
    summary='''This release adds task and note synchronization, task templates, 
more task recurrence options, more translations and a whole bunch of smaller 
enhancements.''',
    featuresAdded=[
        Feature('''E-mail attachments are now stored directly in the
task file.'''),
        Feature('''Tasks and notes can now be synchronized with a
Funambol server (http://www.funambol.com/).''', '2006123', '1892874'),
        Feature('''Tasks can now be saved and reused as templates.''', 
                '1851847', '1549002', '1484368', '1601869'),
        Feature('''Attachments are now regular domain objects; they may
have notes.'''),
        Feature('''The task and note editors now use an actual category
viewer. It is possible to create and edit categories from these editors.'''),
        Feature('''The description tooltip now works for efforts and
categories. It also contains a summary of notes and attachments belonging
to the hovered object.''', '1642608', '1917999'),
        Feature('''More task recurrence options. Tasks can now also recur 
yearly, in addition to daily, weekly, and monthly. Tasks can also recur 
with a multiple period frequency, e.g. every other week or every three months.
Monthly recurring tasks can be set to recur on the same week day (e.g. first
Monday of the month).''', '1963803', '1917090', '1913656', '2076511'),
        Feature('''The times used in the drop down menus of the start and stop
entries of the effort dialog can now be changed via the preferences dialog. 
Patch supplied by Rob McMullen.'''),
        Feature('''The effort tracking feature can be turned off via the
preferences dialog.'''),
        Feature('''The system tray icon shows the task being tracked in 
its tool tip. Patch provided by João Alexandre de Toledo.'''),
        Feature('''Categories and notes can have attachments.'''),
        Feature('''Tasks and categories can contain notes. ''', '1954879', 
                '2140239', '1525434'),
        Feature('''The four different effort viewers are integrated in one
viewer that can switch between different effort aggregation modes, i.e. details,
per day, per week and per month, via the toolbar.'''),
        Feature('''The two different task viewers are integrated in one
viewer that can switch between list and tree mode, via the toolbar.'''),
        Feature('''Category filtering is done either by showing tasks and notes
that match any category or that match all categories. This filtering mode 
can be switched via the toolbar of the category viewer.''', '2024510'),
        Feature('''The effort background is now colored with the same color as
the task it belongs to.'''),
        Feature('''The effort viewer can show the (overall) categories of the 
task of each effort in an (overall) categories column. Patch provided by
Thomas Sonne Olesen.''', '1911052', '1791670'),
        Feature('''When the effort viewer is in weekly mode, it can show effort
per weekday. Patch provided by Thomas Sonne Olesen.'''),
        Feature('''The automatic resizing of columns can be turned off on a
viewer by viewer basis, using the 'Automatic column resizing' checkable
menu item in the View->Columns menu and/or in the column header right-click
menu.''', '2047851', '1466164'),
        Feature('''The expansion state of tasks, categories and notes is 
saved in the task file.''', '2045453', '1790057'),
        Feature('''Added Catalan translation thanks to Ferran Roig, Jordi
Mallach, Josep-Miquel Ivars, and devaleitzer.'''),
        Feature('''Added an (incomplete) Arabic translation thanks to 
Moayyed. Please help finish it. See http://www.taskcoach.org/i18n.html.'''),
        Feature('''Added largely incomplete Esperanto, Estonian, Indonesian, 
Marathi, Lithuanian, Norwegion Nynorsk, Slovenian, Telugu, and Vietnamese 
translations. Please help finish them. 
See http://www.taskcoach.org/i18n.html.''')],
    bugsFixed=[
        Bug('''Undo would not work well when creating notes in a category or 
task.'''),
        Bug('''An IndexError would be raised when undoing then editing.'''),
        Bug('''Ctrl-PgDn and Ctrl-PgUp would sometimes need to be pressed
multiple times before the next or previous viewer would be activated. ''')],
    implementationChanged=[
        Implementation('''The task file format (version 20) was changed.  
Task nodes may have a recurrence node that contains the recurrence state of
the task. Categories and notes can contain attachments. Tasks and categories
can now contain notes.''')]),

Release('0.70.4', 'September 28, 2008',
    summary='''Bug fix release.''',
    bugsFixed=[
        Bug('''Allow Task Coach to be installed on Ubuntu 7.10.''', '2117477'),
        Bug('''Task Coach wasn't notifying users of new versions.'''),
        Bug('''When merging, merge notes too.'''),
        Bug('''When the notes feature is turned off, hide
the 'Create new note' menu item in the category pop up menu.'''),
        Bug('''Fixed a translation bug.''', '2087395'),
        Bug('''Hide/show the main window with one click on the task bar icon 
instead of a double click (Linux only).'''),
        Bug('''The Task Coach main window would get a very small size if it
was started minimized and had not been restored in the previous session.''',
'2052910')]),
        
Release('0.70.3', 'August 17, 2008',
    summary='''Bug fix release.''',
    bugsFixed=[
        Bug('''wxPython 2.8.8.1 generates images in a new, backwards 
incompatible way, even when told not to do that. This bug affects users 
that have an older version of wxPython installed and use one of the 
Linux packages. Fixed by adding the relevant pieces from wxPython 2.8.8.1 to 
the Task Coach sources.''', '2046084'),
        Bug('''Opening a new task viewer didn't work.''', '2053008'),
        Bug('''Closing effort viewers causes exceptions.''', '2053008')]),

Release('0.70.2', 'August 6, 2008',
    summary='''This release fixes some bugs and brings back
the Fedora RPM.''',
    bugsFixed=[
        Bug('''Using the "Save selection" feature together with
mail attachments could result in data loss.'''),
        Bug('''Under KDE, the maximized state of the main window
would not be restored.'''),
        Bug('''One couldn't e-mail tasks with non-ASCII characters
in their description.''', '2025676'),
        Bug('''Dragging an email message from Thunderbird and dropping it
on Task Coach could give a "UnicodeDecodeError" on Fedora.''', '1953166'),
        Bug('''When an invalid regular expression was entered in
a search control, no items were displayed. Additionally, if it was
saved in TaskCoach.ini, TaskCoach would crash on launch later.'''),
        Bug('''Mention of non-existing files in taskcoach.spec
prevented the Fedora RPM from being built.'''),
        Bug('''The category viewer would sometimes skip keyboard navigation or
need an extra mouse-click to get focus.''', '2020816', '2020812'),
        Bug('''On Mac OS X, the keyboard shortcut for 'help' was interfering 
with the shortcut for 'hide window'.''', '2006455')],
    featuresAdded=[
        Feature('''Notes can be e-mailed.'''),
        Feature('''Display a tool tip to warn user when a search
string is an invalid regular expression. In this case, default to
substring search.'''),
        Feature('''Optionally put Task Coach in the user's startup menu so
that Task Coach is started automatically when the user logs on 
(Windows only).''', '2017400', '1913650'),
        Feature('''Made (right-click) context menu's more consistent.''')],
    featuresRemoved=[
        Feature('''Don't supply the dummy recipient 'Please enter recipient' to 
the email program when mailing a task. This only forces the user to perform 
an extra action to remove that dummy text, while most if not all email 
programs will warn the user when she forgets to enter a recipient. ''', 
'2026833')]),

Release('0.70.1', 'June 28, 2008',
    summary='''This release optionally brings back the tabbed user 
interface that was removed in the previous release and fixes a few 
bugs.''',
    bugsFixed=[
        Bug('''The search control in the toolbar did not maintain 
state correctly for different viewers. Task Coach viewers now each 
have their own toolbar with search control.''', '1977196'),
        Bug('''Marking tasks completed or changing their priority would change
the selection.''', '1888598', '1926362'),
        Bug('''On Max OS X, put preferences menu item in the TaskCoach 
menu instead of the Edit menu to conform with Mac OS X standards.''', 
            '1965861'),
        Bug('''Focus issues: On Mac OS X, text couldn't be edited while the 
timer was running. On Windows, notifications from other programs overlapping 
with the main window would take away focus from dialogs.''', '1995469', 
'2000152'),
        Bug('''Prevent crash under Windows XP when dropping e-mail 
from Thunderbird if the APPDATA environment variable is not 
defined.''', '1960827'),
        Bug('''ImportError: No module named thirdparty.ElementTree. 
This exception would happen when using a source distribution of Task 
Coach or a package (rpm, deb) for Linux *and* when the default version 
of Python on the system is Python 2.4. Task Coach tried to import a 
module from the wrong package.''', '1964069'),
        Bug('''On Linux, when using a dark theme, use appropriate 
background colors for the category viewer and the text color buttons 
in the preferences dialog.''', '1988160'),
        Bug('''Remember whether the main window was maximized and if 
so, maximize the main window when starting the next time.''', 
            '1969266'),
        Bug('''Correctly sort tasks on startup when sort column is 
'Overall categories'.''', '1962003'),
        Bug('''Correctly redraw toolbar when it is 'damaged' by other 
windows''', '1977208'),
        Bug('''Correctly sort effort for subtasks in effort per day, 
per week, and per month effort viewers.''', '1989553'),
        Bug('''Better navigation with tab key in dialogs.'''),
        Bug('''Keep newlines in descriptions when printing or 
exporting to HTML.''')],
    featuresAdded=[
        Feature('''Task Coach can now use either the old tabbed user interface
(whose layout still cannot be saved, by the way) or the 'managed frame' 
interface introduced in release 0.70.0. This can be changed in the Preferences
dialog.''', '1964213')]),

Release('0.70.0', 'May 12, 2008',
    summary='''Small feature enhancements, more translations and several bug 
fixes. Task Coach is now distributed under the GPLv3+.''',
    featuresAdded=[
        Feature('Paths to file attachments may be relative.'),
        Feature('Monthly recurrence of tasks.', '1933222', '1957687'),
        Feature('Added and reorganized keyboard short cuts.', '1857101'),
        Feature('''Start tracking effort for any active task using the 
system tray icon right-click menu.''', '1934738', '1739666'),
        Feature('''Added a largely complete Ukranian translation thanks to
Vitovt and incomplete Finnish, Greek, Persian and Thai translations.''')],
    featuresChanged=[
        Feature('''Slightly higher preference window so all icons fit and
no scrolling is needed.''', '1918678')],
    bugsFixed=[
        Bug('''Allow for editing seconds in effort editor.''', '1925748'),
        Bug('''The combobox in the effort detail editor always picked the 
first task when multiple tasks had the same subject, effectively prohibiting
the user to move an effort record to another task with the same subject.''', 
            '1918033'),
        Bug('''Reset invalid input in the priority field of the task editor
to 0 instead of to the minimum priority (a large negative value).''', '1949222'),
        Bug('''"View->Filter->Reset all filters" now also unchecks all 
categories.'''),
        Bug('''Task Coach now is packaged as a proper Debian package, thanks to
Stani Michiels. The Debian package installs a menu item for Task Coach in the 
Applications/Office menu.''', '1792706', '1792711', '1896796')],
    dependenciesChanged=[
        Dependency('''Task Coach now uses Subversion for version control. See
http://sourceforge.net/svn/?group_id=130831. This only affects you if
you want to develop or use Task Coach source code.'''),
        Dependency('''Task Coach is now distributed under the GNU General 
Public License version 3 or (at your option) any later version. This only 
affects you if you want to distribute changed versions of Task Coach or 
want to include source code from Task Coach in other software.''')]),
    
Release('0.69.2', 'March 28, 2008',
    summary='Bug fix release.',
    featuresAdded=[
        Feature('''Task Coach now suggests a reminder date, based
on the due date or start date of a task.'''),
        Feature('''Added a complete Norwegion Bokmal translation thanks to Amund Amundsen
and incomplete Galician, Korean and Romanian translations.''')],
    bugsFixed=[
        Bug('''Tasks created via the context menu of the category view now 
automatically belong to the selected category.''', '1592103'),
        Bug('''Update task status and colors at midnight.''', '1183043'),
        Bug('''Exception when starting Task Coach ("AttributeError: 
'CategoryList' object has no attribute 'EventTypePrefix'").''', '1901385'),
        Bug('''Exception when reopening a closed viewer (with the message
"ConfigParser.NoSectionError: No section: 'effortperdayviewer1'" in the log 
file).''', '1894488'),
        Bug('''Exception when resetting all filters in the task tree viewer
(with the message "No option 'hidecompositetasks' in section: 
'tasktreelistview'" in the log file).''', '1903679'),
        Bug('''Don't take the priority of completed subtasks into account when
calculating the overall priority of a task.''', '1905774'),
        Bug('''It was not clear that backup files can be opened in Task Coach.
Backup files now have the extension '.tsk.bak'. The file open dialog has 
'*.tsk.bak' as selectable file type to make it easier to open backup files.''', 
'1911538'),
        Bug('''Exception when opening the task menu while the toolbar 
is hidden.''')]),
    
Release('0.69.1', 'February 14, 2008',
    summary='Bug fix release.',
    bugsFixed=[
        Bug('''Exception when closing a task editor dialog. This 
causes updates of task states not to be displayed properly. The bug itself
does not cause data loss, but it might trick users into saving an empty
task file over their existing data.''', '1893634'),
        Bug('''On Mac OS X, users couldn't enter 'P' and 'M' in text boxes,
because these were mapped to menu items. Reorganized keyboard shortcuts to fix 
this.''', '1890566'),
        Bug('''The arrow ('→') and infinity symbol ('∞') are not 
visible on all computers, so Task Coach is back to using '->' and 'Infinite'
again.''')]),
    
Release('0.69.0', 'February 9, 2008',
    summary='''This release makes it possible to repeat tasks on either a daily 
or a weekly basis and to add notes to categories. It also contains a number of 
other changes and bug fixes.''',
    featuresAdded=[
        Feature('''Tasks can recur on a daily or weekly basis. This feature is
not complete yet. Most obviously, recurring on a monthly basis is missing. 
Also, recurring tasks with recurring subtasks do not behave entirely 
correctly yet.''', '1623364', '1464793', '1264210'),
        Feature('''Notes can be assigned to categories.'''),
        Feature('''Added Bulgarian translation, thanks to Rumen Belev.'''),
        Feature('''Added Danish translation, thanks to different translators.'''),
        Feature('''Added a number of rather incomplete translations (Italian,
Portuguese, Swedish, and Turkish).
See http://www.taskcoach.org/i18n.html for how you can help improve these 
translations.'''),
        Feature('''When filtering by one or more categories, new tasks and 
notes are automatically added to those categories. Of course, you can still
change the categories in the category tab of the edit dialog before pressing
the OK button.'''),
        Feature('''Whether descriptions of tasks, effort records, categories and
notes are shown in a popup tooltip window is now a setting.''', '1857098'),
        Feature('''Added menu items for increasing, decreasing, maximizing, and 
minimizing task priority.''', '1768210', '1570616'),
        Feature('''Clicking a column header in a task viewer now iterates
through the following sort orders: 'ascending, after sorting by task status first', 
'descending, after sorting by task status first', 'ascending, without sorting
by task status first', 'descending, without sorting by task status first'.''')],
    featuresChanged=[
        Feature('''Previously, unset dates were displayed as 'None' in   
date columns. To be consistent with how other attributes are displayed in 
columns, Task Coach now simply displays nothing for unset dates in date
columns.'''),
        Feature('''Task Coach now uses the infinity symbol ('∞') to display
the number of days left for tasks without a due date, instead of the word 
'Infinite'.'''),
        Feature('''Task Coach now uses a real arrow symbol ('→') instead of 
'->' for separating parent and child subjects in the different viewers.''')],
    featuresRemoved=[
        Feature('''Task Coach no longer keeps track of the 'last modification 
time' of tasks.''')],
    bugsFixed=[
        Bug('''The reminder dialog didn't close when opening the task from
the reminder dialog. If the user had entered a snooze option in the reminder
dialog, that snooze option would be overwritten when closing the task 
editor.''', '1862286'),
        Bug('''Don't allow filtering by both a parent and a child category at
the same time.'''),
        Bug('''Sorting by total categories in the task viewers didn't sort
correctly.'''),
        Bug('''Save didn't work for task files without a file name and
without tasks, but with categories or notes.'''),
        Bug('''Adding a task to a category or removing it from a category
was not undoable.''')]),
    
Release('0.68.0', 'December 26, 2007',
    summary='''This release makes it possible to open a task from its reminder dialog, adds
a command line option to facilitate the PortableApps.com Task Coach distribution, makes 
starting and stopping effort tracking quicker and fixes a number of bugs.''',
    featuresAdded=[
        Feature('''It is possible to open a task from its reminder 
dialog.'''),
        Feature('''Task Coach has a --ini command line option that can
be used to specify where the ini file is located.''')],
    bugsFixed=[
        Bug('''Start and stop tracking effort is faster for tasks that 
have a large number of associated effort records.'''),
        Bug('''Task Coach now gives an error message if the file that it tries
to open doesn't exist.''', '1857093'),
        Bug('''When selecting all text in a text control with '<cmd>a',
indeed select all text and not all tasks (Max OSX only).''', '1857091'),
        Bug('''Attempt to prevent crashes on Fedora 8 that sometimes happen
when adding top level tasks.''', '1840111')]),
        
Release('0.67.0', 'December 16, 2007',
    summary='''This release make it possible to color tasks via their
categories, adds a translation in Hebrew, and makes it easier to mark 
tasks as not completed.''',
    featuresAdded=[
        Feature('''Added Hebrew translation thanks to Ziv Barcesat.'''),
        Feature('''You can assign a color to a category. Tasks are colored 
according to the color of the categories they belong to.''', '1466159', '1784932'),
        Feature('''The 'mark task completed' button and menu items can now 
also be used to mark tasks as not completed.''', '1449714')],
    bugsFixed=[
        Bug('''Don't move selection to the first line of the task tree viewer
when deleting a subtask.''', '1849171')],
    dependenciesChanged=[
        Dependency('''Task Coach now needs at least wxPython 
2.8.6.0-unicode. Since the Windows installer and the Mac OSX dmg package have
wxPython included, this only affects users of the RPM, Debian, and source
distributions.''')]),
            
Release('0.66.3', 'December 11, 2007',
    summary='Bug fix release to address crashes.',
    bugsFixed=[
        Bug('''Work around a bug in the TreeListCtrl widget that caused
crashes. The TreeListCtrl widget is used by Task Coach for the task tree 
view.''', '1846906', '1840111', '1832490', '1829622', '1821858', '1820497')]),

Release('0.66.2', 'November 9, 2007',
    summary='Bug fix release to address crashes.',
    bugsFixed=[
        Bug('''Don't crash when refreshing a tree view.''', '1828846')]),
        
Release('0.66.1', 'November 7, 2007',
    summary='This release fixes a number of minor bugs.',
    bugsFixed=[
        Bug('''When changing the sort order in a tree viewer, keep 
collapsed items collapsed and expanded items expanded.''', '1791638'),
        Bug('Sort categories alphabetically in task editor.', '1824180'),
        Bug('''Double clicking a task in the tree view did not open
the task edit dialog.'''),
        Bug('''When filtering on a specific category, a newly added task
belonging to that category was not shown in the task viewers.''')]),
        
Release('0.66.0', 'October 31, 2007',
    summary='''Small feature enhancements and a translation in 
Traditional Chinese.''',
    featuresAdded=[
        Feature('Added Traditional Chinese translation thanks to Joey Weng.'),
        Feature('''Added an 'overall categories' column that recursively shows 
the categories a task belongs to, i.e. its own categories and the categories
of its parent task(s).''', '1790054'),
        Feature('Column widths are saved between sessions.', '1799998'),
        Feature('''Ctrl-PageUp and Ctrl-PageDown can be used to cycle through 
open viewers.''', '1818428')],
    bugsFixed=[
        Bug('Make categories and category viewer more robust.', '1821776')]),
        
Release('0.65.3', 'October 20, 2007',
    summary='''This bugfix release fixes one critical bug that affects 
users on the Windows platform and several minor bugs that affect users on all 
platforms.''',
    bugsFixed=[
        Bug('''Don't leak GDI objects on Windows.''', '1813632', '1811058',
            '1810297', '1806004', '1803085'),
        Bug('''Don't notify of new version when the user has just installed 
that version.'''),
        Bug('''Mail disappears from Outlook when dropped in TaskCoach. Try to
use Outlook to open mail attachment when it's the "default" mailer.''', '1812399'),
        Bug('''Mail task doesn't work.''', '1810356'),
        Bug('''Categories not sorted correctly.''', '1810469')]),

Release('0.65.2', 'October 8, 2007',
    summary='This release is aimed at better performance.',
    bugsFixed=[
        Bug('''Slow performance.''', '1806001', '1794007'),
        Bug('''Don't require administrator privileges for installation
on Windows XP/Vista.''')]),
        
Release('0.65.1', 'September 23, 2007',
    summary='''This release fixes one critical bug and two minor bugs.''',
    bugsFixed=[
        Bug('''Tooltip windows steals keyboard focus on some platforms.''',
        '1791627'),
        Bug('''Taskbar icon is not transparent on Linux.''', '1648082'),
        Bug('''Saving a task file after adding attachments via the
'add attachment' menu or context menu fails.''', '1796829')]),

Release('0.65.0', 'September 9, 2007', 
    summary='''This release adds the ability to record notes, improves the 
flexibility of the different views, and fixes several bugs.''',
    featuresAdded=[
        Feature('''Notes. Notes have a subject and an optional description.
Notes can be hierarchical, i.e. notes may contain subnotes. Notes can be sorted
and searched (filtered), printed, and exported. This feature can be turned
on or off via the preferences dialog.'''),
        Feature('''Categories can be searched (filtered) using the search
control on the toolbar. '''),
        Feature('''Category sorting can be changed: ascending or descending,
case sensitive or case insensitive.'''),
        Feature('''Categories can have a description.'''),
        Feature('''Each viewer/tab has its own settings for sort order
and visible columns. Viewers can be renamed. This makes it possible to
e.g. create a 'Todo today'.'''),
        Feature('''The search control on the toolbar can (optionally) include
subitems in the search result. This makes it easy to show
one task and its subtasks in a task viewer or show effort for one task and 
its subtasks in an effort viewer.'''),
        Feature('''Added a setting to start Task Coach iconized either 
always, never, or only when Task Coach was iconized when last 
quitted.''', '1749886'),
        Feature('''Added a setting to turn off spell checking 
(Mac OSX only)''', '1768330'),
        Feature('''Added (incomplete) translations in Brazilian Portuguese, 
Czech, Latvian and Polish. See http://www.taskcoach.org/i18n.html for more
information about translations and on how you can help.''')],
    bugsFixed=[
        Bug('''Made subject column resizable.''', '1702270', '1766664'),
        Bug('''Enable export of data containing non-ASCII 
characters to CSV.''', '1753422'),
        Bug('''Don't activate another viewer when another application is
minimized (Windows only).''', '1765103'),
        Bug('''Outlook 2003 email messages added as attachment couldn't be
opened from Task Coach.''', '1748738'),
        Bug('''German translation had wrong menu accelerators.''', '1772019'),
        Bug('''Apply undo/redo/cut/copy/paste actions to text if a text control
is visible and has focus (Mac OSX only)''', '1768315'),
        Bug('''Added a copy of the ElementTree package to the Task Coach 
source code, so the source code distribution of Task Coach
works with Python 2.4, without needing to install ElementTree.''', 
'1783575')]),
             
Release('0.64.2', 'June 30, 2007',
    summary='''This release fixes sorting of tasks by priority
and makes sure that Task Coach does not block OS shutdown.''',
    bugsFixed=[
        Bug('''Don't take child task priority into account when sorting by 
priority in the task tree view.''', '1732968'),
        Bug('''Don't block OS shutdown on Windows.''', '1735532', '1484652',
            '1489870')]),
            
Release('0.64.1', 'June 10, 2007',
    bugsFixed=[
        Bug('''Task Coach would complain about an error when closing the 
application. This was due to a missing package in the Windows executable
distribution.''', '1727237'),
        Bug('''On Linux, Task Coach was not very helpful when the 
taskcoachlib package is installed for a different python version than the one
the user is starting Task Coach with. ''', '1728485')]),
            
Release('0.64.0', 'May 28, 2007',
    bugsFixed=[
        Bug('''Ubuntu users had to manually install the wxaddons package. 
This package is now included in the Task Coach distribution.'''),
        Bug('''Don't hide the main window when it's iconized by default 
because on Linux with some window managers the main window receives minimize 
events in other situations as well, most notably when changing virtual 
desktops. So, to reduce the chances of confusing new users this option is off 
by default.''', '1721166')],
    featuresAdded=[
        Feature('''Added Breton translation thanks to Ronan Le Déroff'''),
        Feature('''Show a tooltip with a task's description when the mouse
is hovering over a task. Patch provided by Jerome Laheurte.''', '1642608',
'1619521', '1578623'),
        Feature('''Allow for dragging emails from Thunderbird and Outlook to 
the attachment pane of tasks to create email attachments. Opening an attached 
email will open it in the user's default mail program. Patch provided by 
Jerome Laheurte.''')]),

Release('0.63.2', 'April 20, 2007',
    bugsFixed=[
        Bug('''Task tree view does not refresh tasks after task editing.''', 
            '1701368')]),

Release('0.63.1', 'April 16, 2007',
    bugsFixed=(
        Bug('''Dropping a file on a task in the tree viewer didn't work.'''),
        Bug('''Showing the description column in the composite effort viewers 
(effort per day, per week, per month) caused exceptions.'''),
        Bug('''The task tree viewer was trying to update tasks that weren't
shown, resulting in exceptions.''', '1697568', '1697574'))),

Release('0.63.0', 'April 9, 2007',
    featuresAdded=(
        Feature('''Export to HTML and printing of tasks colors tasks 
appropriately.'''),
        Feature('''Added description columns to the task and effort viewers. 
Like other columns, the description column is printed and exported if 
visible.'''),
        Feature('''Added reminder column to the task viewers.''')),
    bugsFixed=(
        Bug("""Cancelling printing would give a 'Task Coach Error'"""),
        Bug('''Make sure the main window is on a visible display when starting. 
This is for laptop users that sometimes extend their desktop to a second 
display.''', '1667120'),
        Bug('''Sort categories alphabetically in the categories viewer.''', 
            '1694532'),
        Bug('''Filtering a category no longer automatically checks all 
subcategories. However, tasks belonging to a subcategory are still filtered 
(since they belong to the filtered category via the subcategory).'''))),
        
Release('0.62.0', 'April 1, 2007',
    dependenciesChanged=[
        Dependency('''Task Coach now requires 
wxPython 2.8.3-unicode or newer (this is only relevant if you use the 
source distribution).''')],
    bugsFixed=[
        Bug('''When saving timestamps in a task file, e.g. for effort start
and stop times, microseconds are no longer saved as part of the timestamp. 
The microseconds caused problems when importing Task Coach data in
Excel.''', '1660670'),
        Bug('''When exporting tasks to HTML or CSV format from the task
tree viewer, child tasks hidden by a filter would still be exported.''', 
'1659307')],
    featuresAdded=[
        Feature('Added Slovak translation thanks to Viliam Búr'),
        Feature('''Printing a selection is enabled (except on Mac OSX).'''),
        Feature('''The notebook that contains the different views allows for
dragging and dropping of tabs, enabling you to create almost any layout you
like. Unfortunately, this widget does not yet provide functionality to store
the layout in the TaskCoach.ini file.'''),
        Feature('''Whether the clock icon in the task bar blinks
or not is now a setting (see Edit -> Preferences -> Window 
behavior.'''),
        Feature('''The toolbar buttons for 'new item', 'new sub item',
'edit item' and 'delete item' now work for tasks, effort records
and categories, depending on what view is active.'''),
        Feature('''Added a category column for task viewers.''', '1629283'),
        Feature('''Added an attachment column that shows whether a task
has one or more attachments.'''),
        Feature('''Added an 'Open all attachments' menu item for tasks'''),
        Feature('''Added snooze option to reminders.''')],
    featuresChanged=[
        Feature('''Removed filter sidebar. Filter options previously available 
on the sidebar are now available via the search filter on the toolbar, the
category tab and the view menu. ''')]),
        
Release('0.61.6', 'January 27, 2007',
    bugsFixed=[
        Bug('''Crash on trying to use down-arrow to move to sub-task.''', 
'1640806'),
        Bug('''When deleting a task that has subtasks that belong to categories,
the task file gets 'corrupted', giving errors when loading it.''', 
'1638419', '1589993')]),

Release('0.61.5', 'January 10, 2007',
    bugsFixed=[
        Bug('''Opening a Task Coach file with many effort records is slow.
Opening an edit dialog for a task with many effort records is slow too.''', 
'1630102')]),

Release('0.61.4', 'December 30, 2006',
    featuresAdded=[
        Feature('Added RPM and Debian distributions.')], 
    bugsFixed=[
        Bug('Make Task Coach work with Python 2.5.'),
        Bug('Cancel reminders when marking a task completed.', '1606990'),
        Bug('Unchecking a reminder would cause an exception.', '1606990'),
        Bug('Column resizing is now less jumpy.', '1606319'),
        Bug('MSVCP71.DLL was missing from the Windows distribution.', 
            '1602364'),
        Bug('''Marking a task completed while completed tasks are hidden 
wouldn't immediately hide the completed task.''', '1572920'),
        Bug('''The category filter was not applied correctly on launch; 
showing categories as filtered but not hiding the associated tasks.''', 
'1603846'),
        Bug('''Turning on filtering for a category didn't mark the
task file as changed.''', '1603846')]),
        
Release('0.61.3', 'November 19, 2006',
    bugsFixed=[
        Bug('''If saving the TaskCoach.ini file would fail, displaying
the error message would fail (too) because the i18n translator had not
been imported at that point.''', '1598568'),
        Bug('''Mac OSX distribution did not start. Upgraded py2app.''', 
            '1594190'),
        Bug('''Dragging and dropping a task in the task tree view would 
sometimes drag the wrong task.'''),
        Bug('''Give category dialog focus and select default category title
to make it easier to quickly enter categories using the keyboard.'''),
        Bug('''The gdiplus.dll was missing from the Windows 
distribution.''', '1596843')]),

Release('0.61.2', 'November 11, 2006',
    bugsFixed=[
        Bug('''Some Linux distributions do not have the BROWSER environment
variable set, causing errors. Be prepared.''', '1567244'),
        Bug('''Saving failed with a UnicodeError if a category
description would contain non-ASCII characters.''', '1589991'),
        Bug('''Deleting a task would not delete the task from the
categories it belonged to, resulting in errors upon next loading
of the task file.''', '1589993')]),

Release('0.61.1', 'November 3, 2006',
    bugsFixed=[
        Bug('''Source distribution was missing some files.''')]),

Release('0.61.0', 'November 2, 2006',
    bugsFixed=[
        Bug('''Displaying a previously hidden toolbar would result in
an incorrectly drawn window.''', '1551885'),
        Bug('''Exported HTML didn't contain an explicit charset.''', '1561490'),
        Bug('''Negative effort preventation was not working correctly.''',
            '1575458')],
    featuresAdded=[
        Feature('''Hierarchical categories.'''),
        Feature('''Export in Comma Separated Values (CSV) format. As
with export to HTML, the current view is exported.''', '1534862'),
        Feature('''Task Coach can be run from a removable medium, such as a 
USB stick. On Windows, use the installer to install Task Coach to the medium.
Then, start Task Coach and turn the setting 'Save settings to same 
directory as program' on. This setting can be found in Edit -> Preferences -> 
File). This makes sure the TaskCoach.ini file is saved on the 
removable medium, in the same directory as the main program.''', '1464435')]),

Release('0.60', 'August 30, 2006',
    bugsFixed=[
        Bug('''Closing a task file did not reset the 'lastfile'
setting.''', '1548126'),
        Bug('''Selecting Japanese translation would cause error upon next 
restart.''', '1545593'),
        Bug('''Task Coach wouldn't quit when the setting 'Minimize window
when closing' was set.''', '1545936'),
        Bug('''Deleting an effort record would throw an exception.''',
            '1548117')],
    websiteChanges=[
        Website('Added MD5 digests to download page.', 'download.html')]),
    
Release('0.59', 'August 23, 2006',
    bugsFixed=[
        Bug('''Improved efficiency while tracking effort for tasks.''',
        '1429545'),
        Bug('''The column width of the list with filenames in the attachment 
page of the task editor is now adaptable, so that long filenames can be made 
visible entirely.''', '1503006'),
        Bug('''Translation errors in tips.''', '1525410', '1525423'),
        Bug('''When having multiple tasks with the same subject, new effort
records would always be created for the first of these tasks instead of the
selected task.''', '1513403', '1524037'),
        Bug('''Opening a file with a non-ascii filename specified on the 
command line did not work.''', '1532528')],
    featuresAdded=[
        Feature('''Japanese translation thanks to Yutaka Usui.'''),
        Feature('''Filter sidebar.'''),
        Feature('''Printing. Selecting 'File' -> 'Print' will print the 
currently active view. This means only the visible columns will be
printed and only the filtered tasks will be printed, in the current sort
order.''', '1481881', '1472662', '1307275', '1205819'),
        Feature('''Export to HTML. Selecting 'File' -> 'Export' ->
'Export to HTML' will export the currently active view to HTML. This
means only the visible columns will be exported and only the filtered
tasks will be printed, in the current sort order.''', '1375773',
'1205819'),
        Feature('''Columns with numbers or dates are right-aligned.''')]),

Release('0.58', 'May 14, 2006', 
    bugsFixed=[
        Bug('''On Mac OSX, Task Coach would seg fault upon exiting.'''),
        Bug('''Right-clicking a task in the task tree view would,
correctly, pop up the context menu, but would not select the underlying
task.''', '1440416'),
        Bug('''The memory leak in the TreeListCtrl was fixed in wxPython
2.6.3.2. The installer for Windows and the disk image for Mac OSX use
wxPython 2.6.3.2, thus fixing the memory leak in Task Coach. If you use
the source distribution of Task Coach you will have to install wxPython
2.6.3.2 yourself to get the fix.''', '1309858'),
        Bug('''Filtering on task categories was improved.'''),
        Bug('''Hitting Delete when editing the text in the find dialog would 
delete any selected tasks. Unfortunately, to fix this bug some accelerators had
to be changed: the accelerator for "Delete task" is now Ctrl-Delete, for 
"New task" it is now Ctrl-Insert, and for "New subtask" it is now 
Shift-Ctrl-Insert.''', '1463316'),
        Bug('''Don't close the current file when user cancels opening another
file.''', '1475473')],
    featuresAdded=[
        Feature('''Added toolbar button for 'new subtask'.'''),
        Feature('''Task Coach searches incrementally as you type a query 
in the find bar.'''),
        Feature('''When dragging a task in the tree view, hover over
a tree button (a boxed plus-sign or a triangle, depending on your
platform) to expand the sub tree.'''),
        Feature('''To promote a sub task to a top-level task in the tree
view, drag it and drop it anywhere as long as it is not on another task.'''),
        Feature('''When filtering tasks by multiple categories, you may 
either choose to view tasks that belong to at least one of the selected
categories, or view tasks that belong to all selected categories.''')]),
 
Release('0.57', 'March 16, 2006',
    featuresAdded=[
        Feature('''Task Coach is now also available as disk image (.dmg)
for Mac OSX (tested on OSX 10.4).''')],
    bugsFixed=[
        Bug('''When adding a new effort to a task, take into account that the
user may have changed the task that the effort belongs to in the effort editor
dialog (using the dropdown combobox). Because Task Coach didn't do that, the
effort would be added twice if the user changed the task of the new effort
record.''', '1443906'),
        Bug('''A file that was saved with an active effort couldn't be loaded 
again. Task Coach would complain that the file was invalid.''', '1433611'),
        Bug('''Added different sizes of the Task Coach icon. This 
prevents scaling up the 16x16 version to 32x32 on Windows or to even 128x128
on the Mac.''', '1406651', '1434044')]),
             
Release('0.56', 'February 14, 2006',
    featuresAdded=[
        Feature('''Tasks can have attachments. Attachments can be added, removed
and opened. Opening of attachments is done by starting the default application
for the attachment file type. Attachments can also be dragged from a file 
browser and dropped onto a task in one of the task viewers or on the task 
attachment pane in the task editor dialog.''', '1250241', '1339113'),
        Feature('''Whether a task is marked completed when all its
child tasks are completed is now a setting that can be changed application-wide
via the preferences dialog. The application-wide setting can be overruled
on a task-by-task basis via the task editor dialog.''', '1393803'),
        Feature('''Task Coach shows a 'tips' dialog at startup. Hopefully it
is helpful for new users. Experienced users can turn it off.''')],
    featuresChanged=[
        Feature('''More visual feedback when dragging tasks in the tree 
view.'''),
        Feature('''Task editor layout changed. Priority is now part of the
task description. Budget and revenue have been merged into one pane.''', 
'1312284')],
    implementationChanged=[
        Implementation('''Default values for task and effort attributes are 
no longer saved in the Task Coach file, resulting in an estimated 33%% 
reduction of file size.''')]),
                   
Release('0.55', 'January 13, 2006',
    dependenciesChanged=[
        Dependency('''Task Coach now requires wxPython 2.6.1.0-unicode or newer
(this is only relevant if you use the source distribution).''')],
    bugsFixed=[
        Bug('''Sorting by total budget was broken.''', '1399116')],
    featuresAdded=[
        Feature('''Simple reminders.''', '1372932')]),

Release('0.54', 'January 6, 2006',
    bugsFixed=[
        Bug('''The accelerators INSERT and Ctrl+INSERT were mapped to 'c'
and 'Command-Copy' on the Mac, which caused Task Coach to create a new task
whenever the user typed a 'c'. Fixed by changing the accelerators for
new task and new subtask to Ctrl+N and Shift+Ctrl+N (on the Mac only).''', 
        '1311413'),
        Bug('''It was possible to enter control characters -- by 
copy-and-pasting -- resulting in invalid XML in the Task Coach 
file.''', '1288689'),
        Bug('''One python file was missing in the source distribution
of release 0.53. Added a test to check that all python files in the source
are actually added to the source distributions, so hopefully this will never
happen again.''', '1389224')],
    featuresAdded=[
        Feature('''Effort can be exported as iCalendar (ICS) file and imported
into e.g. Mozilla Sunbird. Each effort record is exported as a "VEVENT".
This is an experimental feature. Patch provided by Gissehel.''')]),

Release('0.53', 'December 19, 2005',
    bugsFixed=[
        Bug('''On some platforms, Python and wxPython seem to disagree on what
the maximum integer is. The maximum integer is used to set the maximum and 
minimum allowed priority values. Fixed by allowing priority values between 
the rather arbitrary minimum and maximum values of -1000000000 and
1000000000.'''),
        Bug('''Fixed exception: "wx._core.PyAssertionError: C++ assertion
"ucf.GotUpdate()" failed in ..\..\src\msw\textctrl.cpp(813): EM_STREAMIN didn't 
send EN_UPDATE?". This seems to be a bug in wxPython 2.6.0 and 2.6.1.
Patch provided by Franz Steinhaeusler.''', '1344023')],
    featuresAdded=[
        Feature('''Columns in the effort view are hideable too, just like
columns in the task views. See 'View' -> 'Effort columns', or right-click
a column header in the effort view.'''),
        Feature('''Added possibility to mail tasks via your default mailer, see 
'Task' -> 'Mail task' or right-click a task in one of the task views.'''),
        Feature('''Added option to minimize the window when you attempt
to close the application via the close button on the window title bar or 
the system menu. See 'Edit' -> 'Preferences' -> 'Window behavior'.''')]),

Release('0.52', 'November 29, 2005',
    featuresRemoved=[
        Feature('''Files in the old comma-separated format can no longer
be read by Task Coach.''')],
    featuresAdded=[
        Feature('''Tasks can be dragged and dropped.''', '1262863'),
        Feature('''Tasks can have an hourly fee and/or a fixed fee. Revenue
is calculated based on effort spent.''', '1361790'),
        Feature('''First tiny steps towards a user manual, see 'Help' -> 
'Help contents'.'''),
        Feature('''Whether the main window hides itself when iconized is now
adjustable behavior. See 'Edit' -> 'Preferences'.''')],
    featuresChanged=[
        Feature('''Backups are created just before saving, instead of when 
loading a .tsk file. Patch provided by Maciej Malycha.''')],
    bugsFixed=[
        Bug('''For completed tasks, the number of days left for a task is 
now the number of days between the completion date and the due 
date. This prevents that the number of days left of completed tasks keeps 
decreasing, i.e. becoming more negative. For uncompleted tasks, the number
of days left is still the number of days between today and the due date, 
of course. Patch provided by Maciej Malycha.'''),
        Bug('''Put taskocachlib package first on the Python search path to
prevent name conflict with the config module on Gentoo Linux.''', '1353636'),
        Bug('''Mention blue icon in the help on task colors.''', '1355985'),
        Bug('''Don't allow empty categories.''', '1333896')]),
                    
Release('0.51', 'October 30, 2005',
    featuresAdded=[
        Feature('''Escape closes pop-up windows. Patch provided by
Markus Meyer.''', '1241547'),
        Feature('''The task of an effort record can be changed.'''),
        Feature('''Effort records can be cut, copied, and pasted.''')],
    bugsFixed=[
        Bug('''Hitting enter in the find dialog didn't work on Linux.'''),
        Bug('''Old TaskCoach.ini files with a language setting of 'en' instead
of 'en_US' or 'en_GB' would cause an exception. Patch provided by 
Nirendra Maharaj.''')]),

Release('0.50', 'October 2, 2005',
    bugsFixed=[
        Bug('''Exception was thrown when opening a task with logged effort.''')]),
             
Release('0.49', 'October 2, 2005',
    bugsFixed=[
        Bug('''Previous release did not work on Linux/Mac OSX because of a
platform inconsistency between Windows and Linux (GetCountPerPage method 
is missing on Linux, added manually).''', '1305457')],
    featuresAdded=[
        Feature('''Task colors can be adjusted via 
'Edit' -> 'Preferences'.''', '1205579')]),
                    
Release('0.48', 'September 24, 2005',
    bugsFixed=[
        Bug('''Filtering tasks by status ('View' -> 'Tasks that are' -> '...')
would cause an exception.'''),
        Bug('''Sorting by days left would cause an exception.''', '1295122')]),
                    
Release('0.47', 'September 18, 2005',
    featuresAdded=[
        Feature('''Added Hungarian translation thanks to Majsa Norbert.'''),
        Feature('''The task tree view now also shows columns with task details,
similar to the task list view.''', '1194642'),
        Feature('''Sorting on task subject can now also be case 
insensitive. See the menu item 'View' -> 'Sort' -> 'Sort case sensitive'.''', '1228873'),
        Feature('''Recent files are remembered and can be opened from the 
File menu. The maximum number of recent files shown can be set in the
Preferences dialog. Set the maximum to zero to disable this feature. ''', '1191707'),
        Feature('''The last modification time of tasks can be viewed.''')],
    bugsFixed=[
        Bug(''''View'->'All tasks' now also resets any search criterium entered
by the user in the search bar.'''),
        Bug('''When opening a task with a (long) description, the cursor will
be positioned on the first line of the text, instead of on the last line.''', '1265845'),
        Bug('''When viewing tasks due before a certain date in the tree view,
tasks with subtasks due before that date will be visible.''', '1275708')]),

Release('0.46', 'August 12, 2005',
    bugsFixed=[
        Bug('''In the effort views, the status bar would show information about
tasks, not about effort.'''),
        Bug('''Entering a negative effort duration while using a non-english 
language would crash Task Coach.''', '1250177'),
        Bug('''Having a two letter language string (e.g. 'en') in the 
TaskCoach.ini file would cause an error in the preferences dialog.''', 
'1247506')],
    featuresChanged=[
        Feature('''Keyboard shortcut for deleting a task is now 'Delete'
instead of 'Ctrl-D' and 'Ctrl-Enter' marks the selected task(s) completed.''', 
        '1241549')], 
    featuresAdded=[
        Feature('''Double-clicking the system tray icon when Task Coach
is not minimized will raise the Task Coach window.''', '1242520'),
        Feature('''Added Spanish translation thanks to Juan José.''')],
    implementationChanged=[
        Implementation('''Task ids are now persistent, i.e. they are saved to
and loaded from the Task Coach (XML) file. This will make it easier, in the future,
to keep tasks synchronized with external sources, e.g. Outlook.'''),
        Implementation('''Task Coach now keeps track of the last modification 
time of tasks. These times are saved to and loaded from the Task Coach (XML) file.
This change is also in preparation of synchronization functionality.''')]),

Release('0.45', 'July 26, 2005',
    bugsFixed=[
        Bug('''When tracking effort the task file would be marked as 
changed after every clock tick.'''),
        Bug('''Task priority can now be set to both positive and
negative integers.'''),
        Bug('''Opening a help dialog before the splash screen disappeared
would make Task Coach stop responding to input. Fixed by making the
helpdialogs modeless (as they should be).''', '1241058')],
    featuresChanged=[
        Bug('''Setting the start date of a subtask earlier than the
start date of the parent task, or setting the due date of a subtask
later than the due date of the parent task will adapt the parent start
or due date as necessary.''', '1237634')]),
                
Release('0.44', 'July 21, 2005',
    featuresAdded=[
        Feature('Added Russian translation thanks to Valdimir Ilyash.')]),

Release('0.43', 'July 19, 2005',
    bugsFixed=[
        Bug('''Tree and list view were not updated correctly when changing sort key 
or sort order.''')]),
             
Release('0.42', 'July 17, 2005',
    bugsFixed=[
        Bug('''Double clicking a task with children in the tree view would 
open the edit dialog and expand or collapse the task as well. Fixed to not 
collapse or expand the task when double clicking it.'''),
        Bug('''Adding a subtask to a collapsed parent task now automatically
expands the parent task.'''),
        Bug('''Changing the description of a task or effort record wouldn't 
mark the task file as changed.'''),
        Bug('Time spent is now updated every second.', '1173048'),
        Bug('''Don't try to make a backup when loading the file fails. 
Reported by Scott Schroeder.'''),
        Bug('''(Windows installer only) Association between .tsk files and
Task Coach was broken.''')],
    featuresChanged=[
        Feature('''The start date of a task can now be left unset, creating
a task that is permanently inactive. This can be useful for activities that
you would normally not want to plan, but have to keep a time record for, e.g.
sickness.''')]),
    
Release('0.41', 'June 20, 2005',
    bugsFixed=[],
    featuresAdded=[
        Feature('''URL's (including mailto) in task and effort descriptions are
clickable.''', '1190310'),
        Feature('''Tasks can have a priority. Priorities are integer numbers:
the higher the number, the higher the priority. Default priority is 0.
Negative numbers are allowed''', 
        '1194527', '1194567', '1210154')],
    featuresChanged=[
        Feature('''Default start date of new subtasks is today
(used to be the start date of the parent task)'''),
        Feature('''When 'sort by status first' is on, active tasks always come
before inactive tasks which in turn come before completed tasks, regardless of
whether the sort order is ascending or descending.''')]),

Release('0.40', 'June 16, 2005', 
    bugsFixed=[
        Bug('Budget left was rendered incorrectly when over budget.', 
            '1216951')],
    featuresAdded=[
        Feature('''Tasks can belong to zero or more categories.
Tasks can be viewed/hidden by category.''', '1182172')]),

Release('0.39', 'June 6, 2005',
    bugsFixed=[
        Bug('''When sorting by due date, composite tasks in the tree view are
now sorted according to the most urgent subtask instead of the least urgent
subtask.''')],
    featuresAdded=[
        Feature('''Tasks can be sorted on all attributes (subject, start date,
due date, budget, etc.) This includes options to sort ascending or descending
and to first sort by status (active/inactive/completed).'''),
        Feature('Sorting order can be changed by clicking on column headers.'),
        Feature('Added German translation, thanks to J. Martin.'),
        Feature('Minor view menu changes.', '1189978')]),

Release('0.38', 'May 22, 2005',
    featuresAdded=[
        Feature('Simplified Chinese user interface added, thanks to limodou.'),
        Feature('Autosave setting to automatically save after every change.', 
            '1188194'),
        Feature('''Backup setting to create a backup when opening a Task
Coach file.'''),
        Feature('''Added preference dialog to edit preferences not related
to the view settings.'''),
        Feature('Now using gettext for i18n.')]),

Release('0.37', 'May 14, 2005',
    bugsFixed=[
        Bug('Icons in tree view on Windows 2000.', '1194654')],
    featuresAdded=[
        Feature('''Columns in the task list view can be turned on/off by
right-clicking on the column headers.'''),
        Feature('Tasks can be sorted either by due date or alphabetically.', 
            '1177984'),
        Feature('More options when editing an effort record.'),
        Feature('Used a new DatePickerCtrl.', '1191909')]),

Release('0.36', 'May 5, 2005',
    bugsFixed=[
        Bug('Descriptions loose newlines after reload.', '1194259')],
    featuresAdded=[
        Feature('French user interface added, thanks to Jerome Laheurte.')]),

Release('0.35', 'May 2, 2005',
    bugsFixed=[
        Bug('''Toolbar icons had a black background instead of a transparent
background on some Windows platforms.''', '1190230'),
        Bug('Package i18n was missing.', '1190967')],
    featuresAdded=[
        Feature('''Internationalization support. Task Coach is available with
Dutch and English user interface.''', '1164461'),
        Feature('''Added 'expand selected task' and 'collapse selected task'
menu items to the view menu and the task context menu.''', '1189978')],
    featuresRemoved=[
        Feature(''''Select' -> 'Completed tasks'. This can be done through
the View menu too.''')]),

Release('0.34', 'April 25, 2005',
    bugsFixed=[
        Bug('msvcr71.dll was not shipped with the Windows installer.', 
            '1189311'),
        Bug('''Budgets larger than 24 hours were not written correctly to
the XML file.'''),
        Bug('Mark completed stops effort tracking of parent task.',
        '1186667')]),

Release('0.33', 'April 24, 2005',
    bugsFixed=[
        Bug('''The .tsk fileformat is now XML, making Task Coach fully
unicode-enabled.''')]),

Release('0.32', 'April 18, 2005',
    bugsFixed=[
        Bug('''Task Coach failure on startup due to trying to add a column
from the task list view to the effort view.'''),
        Bug('''Budget couldn't be filled in in the executable Windows
distribution "LookupError: unknown encoding: latin1".'''),
        Bug('Loading files with the executable Windows distribution failed.', 
            '1185259')]),

Release('0.31', 'April 17, 2005',
    dependenciesChanged=[
        Dependency('''Task Coach migrated to Python 2.4.1 and wxPython
2.5.5.1. Added check to give friendly message if wxPython version is below 
the required version number.''')],
    bugsFixed=[
        Bug('''A unittest.py bug that was fixed in Python 2.4 revealed a
bug in test.py.''', '1181714'),
        Bug('''When searching for a task that is completed, while the
'show completed' switch is off, the search shows the path to
the task (i.e. parent tasks), but not the matched task itself.''', '1182528'),
        Bug('''When searching for tasks in the tree view, composite tasks
are expanded automatically to show the children that match
the search string.''', '1182528'),
        Bug('''Columns were hidden by setting their width to 0, but that did 
not make them entirely invisible on some Linux platforms.''', '1152566'),
        Bug('''When editing a subtask, sometimes its branch would be
collapsed.''', '1179266')],
    featuresAdded=[
        Feature('''In the task list and effort list the task column is 
automatically resized to take up the available space.'''),
        Feature('''Added columns to the task list view for: budget, 
total budget, budget left, and total budget left.'''),
        Feature('''Reorganized view menu, added extra task filters, 
added menu item to reset filters''', '1181762', '1178882', '1178780'),
        Feature('''The subject is selected in the task editor so that 
replacing it is a bit easier.''', '1180887')]),

Release('0.30', 'April 11, 2005',
    bugsFixed=[
        Bug('More than one task due today would crash Task Coach.',  
            '1180641')]),

Release('0.29', 'April 10, 2005',
    bugsFixed=[
        Bug('New effort in the context menu did not work in release 0.28.',
            '1178562'),
        Bug('''When selecting 'View' -> 'Completed tasks' in the task tree,
only completed root tasks were hidden.''', '1179372')],
    featuresAdded=[
        Feature('''What tab is active is now a persistent setting. This
includes the tabs and choices in the main window and the effort choices in
the task editor.''', '1178779'),
        Feature("Reordered 'View' -> 'Tasks due before end of' menu.", 
            '1178880'),
        Feature("Added a separate 'Budget' tab in the task editor."),
        Feature('''Taskbar icon now indicates whether task effort tracking
is on.''', '1178057'),
        Feature('Effort is sorted from most recent to least recent.', 
            '1179332'),
        Feature('''Changed task/subtask separator in the task list view
from '|' to ' -> '.''', '1179374')]),

Release('0.28', 'April 6, 2005',
    bugsFixed=[
        Bug('''Hitting return or double click to edit effort in the task
editor now works.''', '1172164'),
        Bug('''Subtasks with the same name would only be visible once in
the task tree view.''')],
    featuresAdded=[
        Feature('''You can hide composite tasks in the task list view so
that only leaf tasks are visible. Menu item 'View' -> 'Tasks with subtasks'.
Requested by Brian Crounse.''')]),

Release('0.27', 'April 4, 2005',
    featuresAdded=[
        Feature('Tasks can have a budget.')]),

Release('0.26', 'March 28, 2005',
    bugsFixed=[
        Bug('Marking a task completed did not stop effort tracking.', 
            '1159918'),
        Bug('Reading lots of efforts was slow.')],
    featuresAdded=[
        Feature('''Save button is disabled when saving is not necessary,
requested by Mike Vorozhbensky.''', '1164472'),
        Feature('''Effort records have a description field, requested by
Kent.''', '1167147')]),

Release('0.25', 'March 13, 2005',
    bugsFixed=[
        Bug('''The menu item 'Effort' -> 'New effort' did not work in
release 0.24.''')],
    featuresAdded=[
        Feature('XML export now includes effort records.'),
        Feature('''Effort per day, per week and per month view now also 
show total time spent (i.e. time including time spent on subtasks).''')]),

Release('0.24', 'March 10, 2005',
    bugsFixed=[
        Bug('''Saving a selection of tasks to a separate file would also
save all effort records to that file (instead of just the effort records
for the selected tasks), giving errors when loading that file.'''),
        Bug('''Deleting a task with effort records would not delete the
effort records.''')],
    featuresAdded=[
        Feature('''The tracking status of tasks is saved. So if you start 
tracking a task, quit Task Coach, and restart Task Coach later, effort for 
that task is still being tracked. Requested by Bob Hossley.''')]),

Release('0.23', 'February 20, 2005',
    bugsFixed=[
        Bug('''Fixed a couple of bugs in the unit tests, discovered by
Stephen Boulet and Jerome Laheurte on the Linux platform.''')]),

Release('0.22', 'February 17, 2005',
    bugsFixed=[
        Bug('''In the effort summary view, effort spent on a task in the
same month or week but in different years would erroneously be added.
E.g. effort in January 2004 and January 2006 would be added.'''),
        Bug('''The mechanism to prevent effort periods with a negative
duration (i.e.  a start time later than the stop time) in the effort editor
was invoked on each key stroke which caused inconvenient behaviour. Fixed
it by only invoking it when the user leaves the text or combo box.''')],
    featuresAdded=[
        Feature('''Added possibility to start tracking effort for a task, 
with start time equal to the end time of the previous effort period. This is 
for example convenient if you stop working on a task and then spend some time 
deciding on what to do next. This is the 'Start tracking from last stop time' 
menu item in the 'Effort' menu.'''),
        Feature('''(Re)Added the unittests to the source distribution.
See INSTALL.txt.'''),
        Feature('''Export to XML. Currently limited to tasks, effort is not
exported yet.''')]),

Release('0.21', 'February 9, 2005',
    bugsFixed=[
        Bug('''Setting the start date/time in the effort editor would change
the stop date/time while not strictly necessary to prevent negative 
durations.'''),
        Bug('''Refreshing the virtual ListCtrl failed under
wxPython2.5-gtk2-unicode-2.5.3.1-fc2_py2.3 and
wxPython-common-gtk2-unicode-2.5.3.1-fc2_py2.3. Reported by Stephen
Boulet.'''),
        Bug('''After iconizing the main window for a second time, the icon
in the task bar wouldn't be hidden anymore. Reported and fixed by Jerome
Laheurte.''')]),

Release('0.20', 'February 6, 2005',
    bugsFixed=[
        Bug('Reading .tsk files version 2 failed.'),
        Bug('''Completed child tasks were not hidden in the tree view when
'View->Completed tasks' was on.'''),
        Bug('Hiding the find panel did not clear the search filter.'),
        Bug('''When searching for tasks, not all matches were shown in the
tree view.'''),
        Bug('''Displaying time spent and total time spent in the list view
for more than a dozen tasks and efforts was slow. Used caching to speed it
up.'''),
        Bug('''Tool tips on the toolbar included mnemonics and accelerator
characters on Linux. Reported on python-2.3.4 and 
wxPython2.5-gtk2-unicode-2.5.3.1-fc2_py2.3 on Suse 9.2 by Stephen
Boulet.''')],
    featuresAdded=[
        Feature('''Effort can be viewed summarized per day, per week, and
per month.'''),
        Feature('''Effort for a specific task can be viewed (and edited) in
the task editor.'''),
        Feature('''Effort tracking can be stopped from the taskbar
menu.'''),
        Feature('''Size and position of the main window are saved in the
settings and restored on the next session. This also includes whether the
main window is iconized or not.'''),
        Feature('Splash screen can be turned off.')])
]

