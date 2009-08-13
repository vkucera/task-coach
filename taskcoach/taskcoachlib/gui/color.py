'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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


def taskColor(task, settings):
    ''' Return the current color of task, based on its status (completed,
        overdue, duesoon, inactive, or active). '''
    if task.completed():
        status = 'completed'
    elif task.overdue(): 
        status = 'overdue'
    elif task.dueSoon():
        status = 'duesoon'
    elif task.inactive(): 
        status = 'inactive'
    else:
        status = 'active'
    return taskColorForStatus(status, settings)


def taskColorForStatus(status, settings):
    ''' Return the task color for the status (one of 'completed', 'overdue', 
        'duesoon', 'inactive', or 'active'). '''
    return wx.Colour(*eval(settings.get('color', '%stasks'%status)))
