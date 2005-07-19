from domain import *

releases = [
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

