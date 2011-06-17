'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

if '__WXMSW__' in wx.PlatformInfo:
    import win32api

    class Display(object):
        """
        This class replaces wx.Display on MSW; the original only
        enumerates the displays at app initialization so when people
        start unplugging/replugging monitors things go wrong. Not all
        methods are implemented.
        """
        @staticmethod
        def GetCount():
            return len(win32api.EnumDisplayMonitors(None, None))

        @staticmethod
        def GetFromPoint(p):
            for idx, (_, _, (x, y, w, h)) in enumerate(win32api.EnumDisplayMonitors(None, None)):
                if p.x >= x and p.x < x + w and p.y >= y and p.y < y + h:
                    return idx
            return wx.NOT_FOUND

        @staticmethod
        def GetFromWindow(window):
            return Display.GetFromPoint(window.GetPosition())

        def __init__(self, index):
            self.hMonitor, _, (self.x, self.y, self.w, self.h) = win32api.EnumDisplayMonitors(None, None)[index]

        def GetClientArea(self):
            ns = win32api.GetMonitorInfo(self.hMonitor)
            return wx.Rect(*ns['Work'])

        def GetGeometry(self):
            ns = win32api.GetMonitorInfo(self.hMonitor)
            return wx.Rect(*ns['Monitor'])

        def GetName(self):
            ns = win32api.GetMonitorInfo(self.hMonitor)
            return ns['Device']

        def IsPrimary(self):
            ns = win32api.GetMonitorInfo(self.hMonitor)
            return bool(ns['Flags'] & 1)


    # Monkey-patching so the workaround applies to third party code as
    # well
    wx.Display = Display
