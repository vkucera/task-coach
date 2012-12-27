'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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


class TaskStatus(object):
    def __init__(self, statusString, pluralLabel, countLabel, hideMenuText,
                 hideHelpText, hideBitmap=None):
        self.statusString = statusString
        self.pluralLabel = pluralLabel
        self.countLabel = countLabel
        self.hideMenuText = hideMenuText
        self.hideHelpText = hideHelpText
        self.hideBitmap = hideBitmap
        
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.statusString)
        
    def __str__(self):
        return self.statusString
           
    def __eq__(self, other):
        return self.statusString == other.statusString
    
    def __neq__(self, other):
        return self.statusString != other.statusString
    
    def __nonzero__(self):
        return True


inactive = TaskStatus('inactive', _('Inactive tasks'), 
    _('Inactive tasks: %d (%d%%)'), _('Hide &inactive tasks'),
    _('Show/hide inactive tasks (uncompleted tasks without actual start date)'),
    hideBitmap='led_grey_icon+cross_red_icon')

late = TaskStatus('late', _('Late tasks'), 
    _('Late tasks: %d (%d%%)'), _('Hide &late tasks'), 
    _('Show/hide late tasks (inactive tasks with a planned start in the past)'))

active = TaskStatus('active', _('Active tasks'), 
    _('Active tasks: %d (%d%%)'), _('Hide &active tasks'),
    _('Show/hide active tasks (uncompleted tasks with an actual start date in the past)'))

duesoon = TaskStatus('duesoon', _('Due soon tasks'), 
    _('Due soon tasks: %d (%d%%)'), _('Hide &due soon tasks'),
    _('Show/hide due soon tasks (uncompleted tasks with a due date in the near future)'))

overdue = TaskStatus('overdue', _('Overdue tasks'), 
    _('Overdue tasks: %d (%d%%)'), _('Hide &over due tasks'),
    _('Show/hide over due tasks (uncompleted tasks with a due date in the past)'))

completed = TaskStatus('completed', _('Completed tasks'), 
    _('Completed tasks: %d (%d%%)'), _('Hide &completed tasks'),
    _('Show/hide completed tasks'), hideBitmap='led_green_icon+cross_red_icon')
