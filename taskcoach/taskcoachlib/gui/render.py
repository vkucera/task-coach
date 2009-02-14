# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

''' render.py - functions to render various objects, like date, time, etc. '''

from taskcoachlib.i18n import _


def date(date):
    ''' render a date (of type date.Date) '''
    return str(date)
    
def priority(priority):
    ''' Render an (integer) priority '''
    return str(priority)
   
def daysLeft(timeLeft, completedTask):
    ''' Render time left (of type date.TimeDelta) in days. '''
    if completedTask:
        return ''
    from taskcoachlib.domain import date
    if timeLeft == date.TimeDelta.max:
        return _('Infinite') # u'∞' 
    else:
        return str(timeLeft.days)

def timeSpent(timeSpent):
    ''' render time spent (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>" '''
    from taskcoachlib.domain import date
    if timeSpent == date.TimeDelta():
        return ''
    if timeSpent < date.TimeDelta():
        sign = '-'
    else:
        sign = ''
    return sign + '%d:%02d:%02d'%timeSpent.hoursMinutesSeconds()

def recurrence(recurrence):
    if not recurrence:
        return ''
    if recurrence.amount > 2:
        labels = [_('Every %(frequency)d days'), _('Every %(frequency)d weeks'),
                  _('Every %(frequency)d months'), _('Every %(frequency)d years')] 
    elif recurrence.amount == 2:
        labels = [_('Every other day'), _('Every other week'),
                  _('Every other month'), _('Every other year')]
    else:
        labels = [_('Daily'), _('Weekly'), _('Monthly'), _('Yearly')] 
    mapping = dict(zip(['daily', 'weekly', 'monthly', 'yearly'], labels))
    return mapping.get(recurrence.unit, recurrence.amount)%dict(frequency=recurrence.amount)

def budget(aBudget):
    ''' render budget (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>". '''
    return timeSpent(aBudget)
        
def dateTime(dateTime):
    if dateTime:
        return dateTime.strftime('%Y-%m-%d %H:%M')
    else:
        return ''
    
def dateTimePeriod(start, stop):
    if stop is None:
        return '%s - %s'%(dateTime(start), _('now'))
    elif start.date() == stop.date():
        return '%s %s - %s'%(date(start.date()), time(start), time(stop))
    else:
        return '%s - %s'%(dateTime(start), dateTime(stop))
            
def time(dateTime):
    return dateTime.strftime('%H:%M')
    
def month(dateTime):
    return dateTime.strftime('%Y %B')
    
def weekNumber(dateTime):
    # Would have liked to use dateTime.strftime('%Y-%U'), but the week number is one off
    # in 2004
    return '%d-%d'%(dateTime.year, dateTime.weeknumber())
    
def amount(aFloat):
    return '%.2f'%aFloat

def taskBitmapNames(task, hasChildren=None):
    ''' Return two bitmap names for the task, one for deselected tasks and
    one for selected tasks. The bitmaps depend on the state of the task and 
    whether the task has children. '''
     
    if hasChildren is None:
        hashildren = bool(task.children())
    bitmap = 'task'            
    if hasChildren:
        bitmap += 's'
    if task.completed():
        bitmap += '_completed'
    elif task.overdue():
        bitmap += '_overdue'
    elif task.dueToday():
        bitmap += '_duetoday'
    elif task.inactive():
        bitmap += '_inactive'
    if hasChildren:
        bitmap_selected = bitmap + '_open'
    else:
        bitmap_selected = bitmap
    if task.isBeingTracked():
        bitmap = bitmap_selected = 'start'
    return bitmap, bitmap_selected

