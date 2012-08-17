# -*- coding: utf-8 -*-

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

''' render.py - functions to render various objects, like date, time, 
etc. '''  # pylint: disable=W0105

from taskcoachlib.domain import date as datemodule
from taskcoachlib.i18n import _
from taskcoachlib import operating_system
import datetime
import codecs
import locale
import re

# pylint: disable=W0621


def priority(priority):
    ''' Render an (integer) priority '''
    return str(priority)

 
def timeLeft(time_left, completed_task):
    ''' Render time left as a text string. Returns an empty string for 
        completed tasks and for tasks without planned due date. Otherwise it 
        returns the number of days, hours, and minutes left. '''
    if completed_task or time_left == datemodule.TimeDelta.max:
        return ''
    sign = '-' if time_left.days < 0 else ''
    time_left = abs(time_left)
    if time_left.days > 0:
        days = _('%d days') % time_left.days if time_left.days > 1 else \
               _('1 day')
        days += ', '
    else:
        days = '' 
    hours_and_minutes = ':'.join(str(time_left).split(':')[:-1]).split(', ')[-1]
    return sign + days + hours_and_minutes


def timeSpent(timeSpent, showSeconds=True):
    ''' Render time spent (of type date.TimeDelta) as
        "<hours>:<minutes>:<seconds>" or "<hours>:<minutes>" '''
    zero = datemodule.TimeDelta()
    if timeSpent == zero:
        return ''
    else:
        sign = '-' if timeSpent < zero else ''
        hours, minutes, seconds = timeSpent.hoursMinutesSeconds()
        return sign + '%d:%02d' % (hours, minutes) + \
               (':%02d' % seconds if showSeconds else '')


def recurrence(recurrence):
    ''' Render the recurrence as a short string describing the frequency of
        the recurrence. '''
    if not recurrence:
        return ''
    if recurrence.amount > 2:
        labels = [_('Every %(frequency)d days'), 
                  _('Every %(frequency)d weeks'),
                  _('Every %(frequency)d months'),
                  _('Every %(frequency)d years')] 
    elif recurrence.amount == 2:
        labels = [_('Every other day'), _('Every other week'),
                  _('Every other month'), _('Every other year')]
    else:
        labels = [_('Daily'), _('Weekly'), _('Monthly'), _('Yearly')] 
    mapping = dict(zip(['daily', 'weekly', 'monthly', 'yearly'], labels))
    return mapping.get(recurrence.unit) % dict(frequency=recurrence.amount)


def budget(aBudget):
    ''' Render budget (of type date.TimeDelta) as 
        "<hours>:<minutes>:<seconds>". '''
    return timeSpent(aBudget)


try:
    dateFormat = '%x'  # Apparently, this may produce invalid utf-8 so test
    codecs.utf_8_decode(datemodule.Now().strftime(dateFormat))
except UnicodeDecodeError:
    dateFormat = '%Y-%m-%d'

dateFunc = lambda dt=None: datetime.datetime.strftime(dt, dateFormat)  # datemodule.Date is not a class

if operating_system.isWindows():
    import pywintypes, win32api
    timeFunc = lambda dt=None: win32api.GetTimeFormat(0x400, 0x02, None if dt is None else pywintypes.Time(dt), None)
else:
    language_and_country = locale.getlocale()[0]
    if language_and_country and ('_US' in language_and_country or 
                                 '_United States' in language_and_country):
        timeFormat = '%I:%M %p'
    else: 
        timeFormat = '%H:%M'  # Alas, %X includes seconds (see http://stackoverflow.com/questions/2507726)
    timeFunc = lambda dt=None: datemodule.DateTime.strftime(dt, timeFormat)

dateTimeFunc = lambda dt=None: u'%s %s' % (dateFunc(dt), timeFunc(dt))


def date(aDate): 
    ''' Render a date (of type date.Date) '''
    if str(aDate) == '':
        return ''
    year = aDate.year
    if year >= 1900:
        return dateFunc(aDate)
    else:
        result = date(datemodule.Date(year + 1900, aDate.month, aDate.day))
        return re.sub(str(year + 1900), str(year), result)


def dateTime(aDateTime):
    if not aDateTime or aDateTime == datemodule.DateTime():
        return ''
    timeIsMidnight = (aDateTime.hour, aDateTime.minute) in ((0, 0), (23, 59))
    year = aDateTime.year
    if year >= 1900:
        return dateFunc(aDateTime) if timeIsMidnight else dateTimeFunc(aDateTime)
    else:
        result = dateTime(aDateTime.replace(year=year + 1900))
        return re.sub(str(year + 1900), str(year), result)

   
def dateTimePeriod(start, stop):
    if stop is None:
        return '%s - %s' % (dateTime(start), _('now'))
    elif start.date() == stop.date():
        return '%s %s - %s' % (date(start.date()), time(start), time(stop))
    else:
        return '%s - %s' % (dateTime(start), dateTime(stop))
    
    
def time(dateTime):
    dateTime = dateTime.replace(year=2000)  # strftime doesn't handle years before 1900
    return timeFunc(dateTime)

    
def month(dateTime):
    return dateTime.strftime('%Y %B')

    
def weekNumber(dateTime):
    # Would have liked to use dateTime.strftime('%Y-%U'), but the week number 
    # is one off in 2004
    return '%d-%d' % (dateTime.year, dateTime.weeknumber())


def monetaryAmount(aFloat):
    ''' Render a monetary amount, using the user's locale. '''
    return '' if round(aFloat, 2) == 0 else \
        locale.format('%.2f', aFloat, monetary=True)


def percentage(aFloat):
    ''' Render a percentage. '''
    return '' if round(aFloat, 0) == 0 else '%.0f%%' % aFloat


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
