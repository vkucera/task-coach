'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib.i18n import _
from taskcoachlib import meta

# Help texts for menu items and toolbar buttons (so called uicommands). 
# At the moment this lists mostly the uicommands that have a keyboard shortcut 
# because we need to be able to reuse the help text in the help dialog.

editCut = _('Cut the selected item(s) to the clipboard')
editCopy = _('Copy the selected item(s) to the clipboard')
editPaste = _('Paste item(s) from the clipboard')
editPasteAsSubitem = _('Paste item(s) from the clipboard as subitem of the selected item')
editPreferences = _('Edit preferences')
editRedo = _('Redo the last command that was undone')
editSelectAll = _('Select all items in the current view')
editUndo = _('Undo the last command')
effortDelete = _('Delete the selected effort period(s)')
effortEdit = _('Edit the selected effort period(s)')
effortNew = _('Add an effort period to the selected task(s)')
fileClose = _('Close the current file')
fileQuit = _('Exit %s')%meta.name
fileOpen = _('Open a %s file')%meta.name
fileSave = _('Save the current file')
fileSaveAs = _('Save the current file under a new name')
help = _('Help about the program')
print_ = _('Print the current file')
printPageSetup = _('Setup the characteristics of the printer page')
search = _('Move keyboard focus from viewer to search control')
taskDecreasePriority = _('Decrease the priority of the selected task(s)')
taskDelete = _('Delete the selected task(s)')
taskEdit = _('Edit the selected task(s)')
taskIncreasePriority = _('Increase the priority of the selected task(s)')
taskMaxPriority = _('Make the selected task(s) the highest priority task(s)')
taskMinPriority = _('Make the selected task(s) the lowest priority task(s)')
taskNew = _('Insert a new task')
taskNewSubtask = _('Insert a new subtask into the selected task')
viewCollapseAll = _('Collapse all items with subitems')
viewExpandAll = _('Expand all items with subitems')
viewNextViewer = _('Activate the next open viewer')
viewPreviousViewer = _('Activate the previous open viewer')