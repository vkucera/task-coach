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

import wx, sys

# This module is meant to be imported like this: from taskcoachlib import platform
# so that the function calls read: platform.isWindows(), platform.isGtk(), etc.

def isMac():
    return '__WXMAC__' == wx.Platform


def isWindows():
    return '__WXMSW__' == wx.Platform


def isWindows7_OrNewer():
    if isWindows():
        major, minor = sys.getwindowsversion()[:2]
        return (major, minor) >= (6, 1)
    else:
        return False
    


