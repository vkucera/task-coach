# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 João Alexandre de Toledo <jtoledo@griffo.com.br>

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
from taskcoachlib.i18n import _
from taskcoachlib.domain import categorizable
from taskcoachlib import help
import task


def accelerator(key, modifier=None, mswKey=None, mswModifier=None):
    # Some accelerators only work on Windows (like INSERT)
    if '__WXMSW__' == wx.Platform:
        key = mswKey or key
        modifier = mswModifier
    shortCut = '+'.join([modifier, key]) if modifier else key
    return u'\t%s'%shortCut


class TaskList(categorizable.CategorizableContainer):
    # FIXME: TaskList should be called TaskCollection or TaskSet

    newItemMenuText = _('&New task...') + accelerator('N', 'Ctrl', 'INS')
    newItemHelpText = help.taskNew
    editItemMenuText = _('&Edit task...')
    editItemHelpText = help.taskEdit
    deleteItemMenuText = _('&Delete task') + accelerator('DEL')
    deleteItemHelpText = help.taskDelete
    newSubItemMenuText = _('New &subtask...') + accelerator('N', 'Shift+Ctrl', 'INS', 'Shift')
    newSubItemHelpText = help.taskNewSubtask 
    
    def _nrInterestingTasks(self, isInteresting):
        return len(self._getInterestingTasks(isInteresting))
    
    def _getInterestingTasks(self, isInteresting):
        return [task for task in self if isInteresting(task)] # pylint: disable-msg=W0621

    def nrCompleted(self):
        return self._nrInterestingTasks(task.Task.completed)

    def nrOverdue(self):
        return self._nrInterestingTasks(task.Task.overdue)
    
    def nrActive(self):
        return self._nrInterestingTasks(task.Task.active)

    def nrInactive(self):
        return self._nrInterestingTasks(task.Task.inactive)

    def nrDueSoon(self):
        return self._nrInterestingTasks(task.Task.dueSoon)
    
    def nrBeingTracked(self):
        return self._nrInterestingTasks(task.Task.isBeingTracked)
    
    def tasksBeingTracked(self):
        return self._getInterestingTasks(task.Task.isBeingTracked)        

    def allCompleted(self):
        nrCompleted = self.nrCompleted()
        return nrCompleted > 0 and nrCompleted == len(self)
            
    def efforts(self):
        result = []
        for task in self: # pylint: disable-msg=W0621
            result.extend(task.efforts())
        return result
        
    def originalLength(self):
        ''' Provide a way for bypassing the __len__ method of decorators. '''
        return len([t for t in self if not t.isDeleted()])
    
    def minPriority(self):
        return min(self.__allPriorities())
        
    def maxPriority(self):
        return max(self.__allPriorities())
        
    def __allPriorities(self):
        return [task.priority() for task in self if not task.isDeleted()] or (0,) # pylint: disable-msg=W0621
