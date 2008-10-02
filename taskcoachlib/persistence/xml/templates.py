#-*- coding: UTF-8

'''
Task Coach - Your friendly task manager
Copyright (C) 2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

def getDefaultTemplates():
    templates = []
    templates.append(('dueTomorrow', '<?xml version="1.0" ?><?taskcoach release="0.71.0" tskversion="22"?><tasks><task duedatetmpl="Tomorrow()" startdatetmpl="Today()" status="2" subject="New task due tomorrow"/></tasks>\n'))
    _('New task due tomorrow')
    templates.append(('dueToday', '<?xml version="1.0" ?><?taskcoach release="0.71.0" tskversion="22"?><tasks><task duedatetmpl="Today()" startdatetmpl="Today()" status="2" subject="New task due today"/></tasks>\n'))
    _('New task due today')

    return templates
