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

import wx, sys, platform

# This module is meant to be imported like this: 
#   from taskcoachlib import operating_system
# so that the function calls read: 
#   operating_system.isWindows(), operating_system.isMac(), etc.

def isMac():
    return isPlatform('MAC')


def isWindows():
    return isPlatform('MSW')


def isGTK():
    return isPlatform('GTK')


def isPlatform(threeLetterPlatformAbbreviation, wxPlatform=wx.Platform):
    return '__WX%s__'%threeLetterPlatformAbbreviation == wxPlatform


def isWindows7_OrNewer(): # pragma: no cover
    if isWindows(): 
        major, minor = sys.getwindowsversion()[:2] # pylint: disable-msg=E1101
        return (major, minor) >= (6, 1)
    else:
        return False
    

def isMacOsXLion_OrNewer(): # pragma: no cover
    if isMac():
        return platform.release() >= '11.1.0'
    else:
        return False


def isMacOsXTiger_OrOlder(): # pragma no cover
    if isMac():
        return platform.release() <= '8.11.1' # Darwin release number for Tiger
    else:
        return False

