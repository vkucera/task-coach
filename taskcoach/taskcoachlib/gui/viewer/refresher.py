'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Thomas Sonne Olesen <tpo@sonnet.dk>

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
from taskcoachlib.domain import date
from taskcoachlib import patterns

''' This module provides classes that implement refreshing strategies for
    viewers. '''

class MinuteRefresher(date.ClockMinuteObserver):
    ''' This class can be used by viewers to refresh themselves every minute
        to refresh attributes like time left. The user of this class is
        responsible for calling refresher.startClock() and stopClock(). '''

    def __init__(self, viewer):
        self.__viewer = viewer        
        super(MinuteRefresher, self).__init__()
        
    def onEveryMinute(self, event): # pylint: disable-msg=W0221,W0613
        try:
            self.__viewer.refresh()
        except wx._core.PyDeadObjectError:
            # Our viewer was deleted, stop observation
            self.removeInstance()


class SecondRefresher(date.ClockSecondObserver):
    ''' This class can be used by viewers to refresh themselves every second
        whenever items (tasks, efforts) are being tracked. '''
        
    def __init__(self, viewer, trackStartEventType, trackStopEventType):
        self.__viewer = viewer
        self.__presentation = viewer.presentation()
        self.__trackedItems = set()
        self.registerObserver(self.onStartTracking, eventType=trackStartEventType)
        self.registerObserver(self.onStopTracking, eventType=trackStopEventType)
        self.registerObserver(self.onItemAdded, 
                              eventType=self.__presentation.addItemEventType(),
                              eventSource=self.__presentation)
        self.registerObserver(self.onItemRemoved, 
                              eventType=self.__presentation.removeItemEventType(),
                              eventSource=self.__presentation)
        self.setTrackedItems(self.trackedItems(self.__presentation))

    def onItemAdded(self, event):
        self.addTrackedItems(self.trackedItems(event.values()))
        
    def onItemRemoved(self, event): 
        self.removeTrackedItems(self.trackedItems(event.values()))

    def onStartTracking(self, event):
        startedItems = [item for item in event.sources() \
                        if item in self.__presentation]
        self.addTrackedItems(startedItems)
        self.refreshItems(startedItems)

    def onStopTracking(self, event):
        stoppedItems = [item for item in event.sources() \
                        if item in self.__presentation]
        self.removeTrackedItems(stoppedItems)
        self.refreshItems(stoppedItems)

    def onEverySecond(self, event): # pylint: disable-msg=W0221,W0613
        self.refreshItems(self.__trackedItems)
        
    def refreshItems(self, items):
        try:
            self.__viewer.refreshItems(*items)
        except wx._core.PyDeadObjectError:
            # Our viewer was deleted, stop observation
            self.removeInstance()

    def setTrackedItems(self, items):
        self.__trackedItems = set(items)
        self.startClockIfNecessary()
        self.stopClockIfNecessary()
        
    def updatePresentation(self):
        self.__presentation = self.__viewer.presentation()
        self.setTrackedItems(self.trackedItems(self.__presentation))
        
    def addTrackedItems(self, items):
        if items:
            self.__trackedItems.update(items)
            self.startClockIfNecessary()

    def removeTrackedItems(self, items):
        if items:
            self.__trackedItems.difference_update(items)
            self.stopClockIfNecessary()

    def startClockIfNecessary(self):
        if self.__trackedItems:
            self.startClock()

    def stopClockIfNecessary(self):
        if not self.__trackedItems:
            self.stopClock()
            
    def currentlyTrackedItems(self):
        return list(self.__trackedItems)

    @staticmethod
    def trackedItems(items):
        return [item for item in items if item.isBeingTracked(recursive=True)]
