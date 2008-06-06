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

''' Utilities for recurring dates. '''

import calendar
import timedelta, date

def _addDays(aDate, nrOfDays):
    return aDate + timedelta.TimeDelta(days=nrOfDays)

def _addMonth(aDate):
    year, month, day = aDate.year, aDate.month, aDate.day
    if month == 12: # If December, move to January next year
        year += 1
        month = 1
    else:
        month += 1
    while True: # Find a valid date in the next month
        try:
            return date.Date(year, month, day)
        except ValueError:
            day -= 1

def _addYear(aDate):
    if (calendar.isleap(aDate.year) and aDate.month <= 2 and aDate.day <=28) or \
       (calendar.isleap(aDate.year + 1) and aDate.month >=3): 
        days = 366
    else:
        days = 365
    return aDate + timedelta.TimeDelta(days=days)


def next(aDate, recurrence, frequency=1):
    ''' Compute the next date, starting from aDate, with a given recurrence.
        The recurrence can be 'daily', 'weekly', or 'monthly'. '''
    if date.Date() == aDate:
        return aDate
    if frequency > 1:
        aDate = next(aDate, recurrence, frequency-1)
    if recurrence == 'yearly':
        return _addYear(aDate)
    elif recurrence == 'monthly':
        return _addMonth(aDate)
    else:
        return _addDays(aDate, dict(daily=1, weekly=7)[recurrence])
