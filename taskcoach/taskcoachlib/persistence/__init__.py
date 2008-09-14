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

# This is the persistence package. It contains classes for reading and
# writing domain objects in different formats such as XML, ICS/vCalendar, ...

from ics.writer import ICSWriter
from xml.writer import XMLWriter
from xml.reader import XMLReader
from html.writer import HTMLWriter
from html.generator import viewer2html
from csv.generator import viewer2csv
from csv.writer import CSVWriter
from vcalendar.writer import VCalendarWriter
from vcalendar.vcal import VCalendarParser
from taskfile import TaskFile, AutoSaver
