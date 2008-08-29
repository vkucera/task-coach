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

import wx
from taskcoachlib import meta, patterns
from taskcoachlib.i18n import _
from taskcoachlib.domain import date

        
class TaskBarIcon(date.ClockObserver, wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList, settings, 
            defaultBitmap='taskcoach', tickBitmap='tick', tackBitmap='tack', 
            *args, **kwargs):
        super(TaskBarIcon, self).__init__(*args, **kwargs)
        self.__window = mainwindow
        self.__taskList = taskList
        self.__settings = settings
        self.__bitmap = self.__defaultBitmap = defaultBitmap
        self.__tickBitmap = tickBitmap
        self.__tackBitmap = tackBitmap
        self.__iconSize = self.__determineIconSize()
        self.__iconCache = {}
        patterns.Publisher().registerObserver(self.onAddItem,
            eventType=self.__taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveItem, 
            eventType=self.__taskList.removeItemEventType())
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType='task.track.start')
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType='task.track.stop')
        patterns.Publisher().registerObserver(self.onChangeDueDate,
            eventType='task.dueDate')
        if '__WXGTK__' == wx.Platform:
            self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.onLeftClick)
        else:
            self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, mainwindow.restore)
        self.__setTooltipText()
        self.__setIcon()

    # Event handlers:

    def onAddItem(self, event):
        self.__setTooltipText()
        self.__startTicking()
        
    def onRemoveItem(self, event):
        self.__setTooltipText()
        self.__stopTicking()

    def onStartTracking(self, event):
        self.__setTooltipText()
        self.__startTicking()

    def onStopTracking(self, event):
        self.__setTooltipText()
        self.__stopTicking()

    def onChangeDueDate(self, event):
        self.__setTooltipText()
        self.__setIcon()

    def onEverySecond(self, *args, **kwargs):
        if self.__settings.getboolean('window', 
            'blinktaskbariconwhentrackingeffort'):
            self.__toggleTrackingBitmap()
            self.__setIcon()

    def onLeftClick(self, event):
        if self.__window.IsIconized():
            self.__window.restore(None)
        else:
            self.__window.Iconize()

    # Menu:

    def setPopupMenu(self, menu):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.popupTaskBarMenu)
        self.popupmenu = menu

    def popupTaskBarMenu(self, event):
        self.PopupMenu(self.popupmenu)

    # Getters:

    def tooltip(self):
        return self.__tooltipText
        
    def bitmap(self):
        return self.__bitmap

    def defaultBitmap(self):
        return self.__defaultBitmap
            
    # Private methods:

    def __startTicking(self):
        if self.__taskList.nrBeingTracked() > 0 and not self.isClockStarted():
            self.startClock()
            self.__toggleTrackingBitmap()
            self.__setIcon()

    def __stopTicking(self):
        if self.__taskList.nrBeingTracked() == 0 and self.isClockStarted():
            self.stopClock()
            self.__setDefaultBitmap()
            self.__setIcon()

    toolTipMessages = \
        [('nrOverdue', _('one task overdue'), _('%d tasks overdue')),
         ('nrDueToday', _('one task due today'), _('%d tasks due today')),
         ('nrBeingTracked', _('tracking effort for one task'), 
                        _('tracking effort for %d tasks'))]
    
    def __setTooltipText(self):
        textParts = []
        for getCountMethodName, singular, plural in self.toolTipMessages:
            count = getattr(self.__taskList, getCountMethodName)()
            if count == 1:
                textParts.append(singular)
            elif count > 1:
                textParts.append(plural%count)
        text = ', '.join(textParts)
        if text:
            self.__tooltipText = u'%s - %s'%(meta.name, text)
        else:
            self.__tooltipText = meta.name

    def __setDefaultBitmap(self):
        self.__bitmap = self.__defaultBitmap

    def __toggleTrackingBitmap(self):
        if self.__bitmap == self.__tickBitmap:
            self.__bitmap = self.__tackBitmap
        else:
            self.__bitmap = self.__tickBitmap

    def __setIcon(self):
        icon = self.__getIcon(self.__bitmap, self.__iconSize)
        self.SetIcon(icon, self.__tooltipText)
        
    def __getIcon(self, bitmap, iconSize):
        ''' Return the icon, converting alpha channel to mask. Use a cache
            to prevent leakage of GDI object count. '''
        try:
            return self.__iconCache[(bitmap, iconSize)]
        except KeyError:
            bmp = wx.ArtProvider_GetBitmap(bitmap, wx.ART_FRAME_ICON, iconSize)
            image = wx.ImageFromBitmap(bmp)
            image.ConvertAlphaToMask()
            # How to create an empty icon ?
            icon = wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON, iconSize)
            icon.CopyFromBitmap(image.ConvertToBitmap())
            self.__iconCache[(bitmap, iconSize)] = icon
            return icon

    def __determineIconSize(self):
        if '__WXMAC__' in wx.PlatformInfo:
            return (128, 128)
        else:
            return (16, 16)

