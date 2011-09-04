# -*- coding: utf-8 -*-

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

''' render.py - functions to render various objects, like date, time, 
etc. ''' # pylint: disable-msg=W0105

import locale, codecs, re
from taskcoachlib.i18n import _
from taskcoachlib.domain import date as datemodule

# pylint: disable-msg=W0621

def priority(priority):
    ''' Render an (integer) priority '''
    return str(priority)
    
def timeLeft(timeLeft, completedTask):
    if completedTask:
        return ''
    if timeLeft == datemodule.TimeDelta.max:
        return _('Infinite')
    sign = '-' if timeLeft.days < 0 else ''
    timeLeft = abs(timeLeft)
    if timeLeft.days > 0:
        days = _('%d days')%timeLeft.days if timeLeft.days > 1 else _('1 day')
        days += ', '
    else:
        days = '' 
    hours_and_minutes = ':'.join(str(timeLeft).split(':')[:-1]).split(', ')[-1]
    return sign + days + hours_and_minutes

def timeSpent(timeSpent):
    ''' render time spent (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>" '''
    zero = datemodule.TimeDelta()
    if timeSpent == zero:
        return ''
    else:
        sign = '-' if timeSpent < zero else ''
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
    return mapping.get(recurrence.unit)%dict(frequency=recurrence.amount)

def budget(aBudget):
    ''' render budget (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>". '''
    return timeSpent(aBudget)

try:
    dateFormat = '%x' # Apparently, this may produce invalid utf-8 so test
    codecs.utf_8_decode(datemodule.Now().strftime(dateFormat))
except UnicodeDecodeError:
    dateFormat = '%Y-%m-%d'
timeFormat = '%H:%M' # Alas, %X includes seconds
dateTimeFormat = ' '.join([dateFormat, timeFormat])

def date(date): 
    ''' Render a date (of type date.Date) '''
    return '' if str(date) == '' else date.strftime(dateFormat)   
        
def dateTime(aDateTime):
    if not aDateTime or aDateTime == datemodule.DateTime():
        return ''
    timeIsMidnight = (aDateTime.hour, aDateTime.minute) in ((0, 0), (23, 59))
    year = aDateTime.year
    if year >= 1900:
        return aDateTime.strftime(dateFormat if timeIsMidnight else dateTimeFormat)
    else:
        result = dateTime(aDateTime.replace(year=year+1900))
        return re.sub(str(year+1900), str(year), result)
        
def dateTimePeriod(start, stop):
    if stop is None:
        return '%s - %s'%(dateTime(start), _('now'))
    elif start.date() == stop.date():
        return '%s %s - %s'%(date(start.date()), time(start), time(stop))
    else:
        return '%s - %s'%(dateTime(start), dateTime(stop))
            
def time(dateTime):
    return dateTime.strftime(timeFormat)
    
def month(dateTime):
    return dateTime.strftime('%Y %B')
    
def weekNumber(dateTime):
    # Would have liked to use dateTime.strftime('%Y-%U'), but the week number 
    # is one off in 2004
    return '%d-%d'%(dateTime.year, dateTime.weeknumber())
    
def monetaryAmount(aFloat):
    ''' Render a monetary amount, using the user's locale. '''
    return '' if round(aFloat, 2) == 0 else \
        locale.format('%.2f', aFloat, monetary=True)
        
def percentage(aFloat):
    ''' Render a percentage. '''
    return '' if round(aFloat, 0) == 0 else '%.0f%%'%aFloat

def exception(exception, instance):
    ''' Safely render an exception, being prepared for new exceptions. '''

    try:
        # In this order. Python 2.6 fixed the unicode exception problem.
        try:
            return unicode(instance)
        except UnicodeDecodeError:
            # On Windows, some exceptions raised by win32all lead to this
            # Hack around it
            result = []
            for val in instance.args:
                if isinstance(val, unicode):
                    result.append(val.encode('UTF-8'))
                else:
                    result.append(val)
            return unicode(result)
    except UnicodeEncodeError:
        return '<class %s>' % str(exception)
