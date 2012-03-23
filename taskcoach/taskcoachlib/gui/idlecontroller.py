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
from taskcoachlib.powermgt import IdleNotifier
from taskcoachlib.patterns import Observer
from taskcoachlib.domain import effort, date
from taskcoachlib.command import NewEffortCommand, EditEffortStopDateTimeCommand
from taskcoachlib.notify import NotificationFrameBase, NotificationCenter
from taskcoachlib.i18n import _


class WakeFromIdleFrame(NotificationFrameBase):
    def __init__(self, idleTime, effort, displayedEfforts, *args, **kwargs):
        self._idleTime = idleTime
        self._effort = effort
        self._displayed = displayedEfforts
        super(WakeFromIdleFrame, self).__init__(*args, **kwargs)

    def AddInnerContent(self, sizer, panel):
        sizer.Add(wx.StaticText(panel, wx.ID_ANY,
            _('No user input since %s. The following task was\nbeing tracked:') % \
                                self._idleTime))
        sizer.Add(wx.StaticText(panel, wx.ID_ANY,
            self._effort.task().subject()))

        btnNothing = wx.Button(panel, wx.ID_ANY, _('Do nothing'))
        btnStopAt = wx.Button(panel, wx.ID_ANY, _('Stop it at %s') % self._idleTime)
        btnStopResume = wx.Button(panel, wx.ID_ANY, _('Stop it at %s and resume now') % self._idleTime)

        sizer.Add(btnNothing, 0, wx.EXPAND|wx.ALL, 1)
        sizer.Add(btnStopAt, 0, wx.EXPAND|wx.ALL, 1)
        sizer.Add(btnStopResume, 0, wx.EXPAND|wx.ALL, 1)

        wx.EVT_BUTTON(btnNothing, wx.ID_ANY, self.DoNothing)
        wx.EVT_BUTTON(btnStopAt, wx.ID_ANY, self.DoStopAt)
        wx.EVT_BUTTON(btnStopResume, wx.ID_ANY, self.DoStopResume)

    def CloseButton(self, panel):
        return None

    def DoNothing(self, event):
        self._displayed.remove(self._effort)
        self.DoClose()

    def DoStopAt(self, event):
        self._displayed.remove(self._effort)
        EditEffortStopDateTimeCommand(newValue=self._idleTime, items=[self._effort]).do()
        self.DoClose()

    def DoStopResume(self, event):
        self._displayed.remove(self._effort)
        EditEffortStopDateTimeCommand(newValue=self._idleTime, items=[self._effort]).do()
        NewEffortCommand(items=[self._effort.task()]).do()
        self.DoClose()


class IdleController(Observer, IdleNotifier):
    def __init__(self, mainWindow, settings, effortList):
        self._mainWindow = mainWindow
        self._settings = settings
        self._effortList = effortList
        self._wentIdle = None
        self._displayed = set()

        super(IdleController, self).__init__()

        self.__trackedEfforts = self.__filterTrackedEfforts(self._effortList)

        self.registerObserver(self.onEffortAdded, 
                              eventType=self._effortList.addItemEventType(),
                              eventSource=self._effortList)
        self.registerObserver(self.onEffortRemoved, 
                              eventType=self._effortList.removeItemEventType(),
                              eventSource=self._effortList)
        self.registerObserver(self.onStartTracking,  
                              eventType=effort.Effort.trackStartEventType())
        self.registerObserver(self.onStopTracking, 
                              eventType=effort.Effort.trackStopEventType())
    
    @staticmethod
    def __filterTrackedEfforts(efforts):
        return [anEffort for anEffort in efforts if anEffort.isBeingTracked() \
                and not isinstance(anEffort, effort.BaseCompositeEffort)]
                
    def onEffortAdded(self, event):
        self.__trackedEfforts.extend(self.__filterTrackedEfforts(event.values()))

    def onEffortRemoved(self, event):
        for effort in event.values():
            if effort in self.__trackedEfforts:
                self.__trackedEfforts.remove(effort)
        
    def onStartTracking(self, event):
        self.__trackedEfforts.extend(self.__filterTrackedEfforts(event.sources()))
        
    def onStopTracking(self, event):
        for effort in event.sources():
            if effort in self.__trackedEfforts:
                self.__trackedEfforts.remove(effort) 

    def getMinIdleTime(self):
        return self._settings.getint('feature', 'minidletime') * 60

    def sleep(self):
        now = date.Now()
        self._wentIdle = date.DateTime(now.year, now.month, now.day,
                                       now.hour, now.minute)
        self._wentIdle -= date.TimeDelta(minutes=self._settings.getint('feature', 'minidletime'))

    def wake(self):
        wx.CallAfter(self.OnWake)

    def OnWake(self):
        for effort in self.__trackedEfforts:
            if effort not in self._displayed:
                self._displayed.add(effort)
                frm = WakeFromIdleFrame(self._wentIdle, effort, self._displayed, _('Notification'),
                                        icon=wx.ArtProvider.GetBitmap('taskcoach', wx.ART_FRAME_ICON, (16, 16)))
                NotificationCenter().NotifyFrame(frm)
