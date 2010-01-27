#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

 
SCHEDULE_DEFAULT_COLOR  = wx.Color(247, 212, 57)  

#New event
wxEVT_COMMAND_SCHEDULE_CHANGE = wx.NewEventType()
EVT_SCHEDULE_CHANGE  = wx.PyEventBinder(wxEVT_COMMAND_SCHEDULE_CHANGE)

CATEGORIES = {"Work": wx.GREEN, 
              "Holiday": wx.GREEN,
              "Phone": wx.GREEN, 
              "Email": wx.GREEN, 
              "Birthday": wx.GREEN,
              "Ill": wx.GREEN,
              "At home": wx.GREEN, 
              "Fax": wx.GREEN, }
             
class wxSchedule(wx.EvtHandler):
    def __init__(self):
        # Use self.start and self.end for set the star and the end of the schedule.
        # If both start and end datetime have time set to 00:00 the schedule is
        # relative on entire day/days.
        super(wxSchedule, self).__init__()
        
        self._color = SCHEDULE_DEFAULT_COLOR
        self._description = ''
        self._done = False
        self._end = wx.DateTime().Now()
        self._notes = ''
        self._start = wx.DateTime().Now()
        self._category = "Work"
        self._clientdata = None
        
        #Need for freeze the event notification
        self._freeze = False 
    # -- Global methods
    def Freeze(self):
        #Freeze the event notification
        self._freeze = True
    
    def Thaw(self):
        #Wake up the event
        self._freeze = False
        self._eventNotification()
    
    def getData(self):
        """ Return wxSchdele data into a dict
        """
        data = dict( [ (attr, getattr(self, attr) ) 
                       for attr in ("category", "color", "description", 
                                    "done", "end", "notes","start", "clientdata")
                     ]
                   )
        return data
                        
    # -- Internal mehtods
    
    def _eventNotification(self):
        """ If not freeze, wake up and call the event notification
        """
        if self._freeze: return
        
        #Create the event and propagete it
        evt = wx.PyCommandEvent(wxEVT_COMMAND_SCHEDULE_CHANGE)
        
        evt.category = self._category
        evt.color = self._color
        evt.description = self._description
        evt.done = self._done
        evt.end = self._end
        evt.notes = self._notes
        evt.start = self._start
        evt.schedule = self
        evt.SetEventObject( self )
        
        self.ProcessEvent(evt)

    def __eq__(self, schedule):
        """ Control if the schedule passed are equal than me
        """
        if not isinstance(schedule, wxSchedule): return False
        return self.getData() == schedule.getData()
        
    def __repr__(self):
        return "%s: %s" % (super(wxSchedule, self).__repr__(), self.getData())
    
    # -- Property
    def setCategory(self, category):
        """ Set the color
        """
        if category not in CATEGORIES.keys():
            raise ValueError, "%s is not a valid category" % category
        
        self._category = category
        self._eventNotification()
    
    def getCategory(self):
        """ Return the current category
        """
        return self._category
    
    def setColor(self, color):
        """ Set the color
        """
        if not isinstance(color, wx.Color):
            raise ValueError, "Color can be only a wx.Color value"

        self._color = color
        self._eventNotification()
        
    def getColor(self):
        """ Return the color
        """
        return self._color

    def setDescription(self, descr):
        """ Set the description
        """
        if not isinstance(descr, (str, unicode)):
            raise ValueError, "Description can be only a str value"

        self._description = descr
        self._eventNotification()
        
    def getDescription(self):
        """ Return the description
        """
        return self._description

    def setDone(self, done):
        """ Are this schedule complete?
        """ 
        if not isinstance(done, bool):
            raise ValueError, "Done can be only a bool value"
        
        self._done = done
        self._eventNotification()
        
    def getDone(self):
        """ Return the done value
        """
        return self._done
    
    def setEnd(self, dateTime):
        """ Set the end
        """
        if not isinstance(dateTime, wx.DateTime):
            raise ValueError, "dateTime can be only a wx.DateTime value"

        self._end = dateTime
        self._eventNotification()
    
    def getEnd(self):
        """ Return the end
        """
        return self._end
                
    def setNotes(self, notes):
        """ Set the notes
        """
        if not isinstance(notes, basestring):
            raise ValueError, "notes can be only a str value"
       
        self._notes = notes
        self._eventNotification()

    def getNotes(self):
        """ Return the notes
        """
        return self._notes

    def setStart(self, dateTime):
        """ Set the start
        """
        if not isinstance(dateTime, wx.DateTime):
            raise ValueError, "dateTime can be only a wx.DateTime value"
        self._start = dateTime
        self._eventNotification()
    
    def getStart(self):
        """ Return the start
        """
        return self._start

    def SetClientData(self, clientdata):
        self._clientdata = clientdata
    
    def GetClientData(self):
        return self._clientdata
    
    category = property(getCategory, setCategory)
    color = property(getColor, setColor)
    description = property(getDescription, setDescription)
    done = property(getDone, setDone)
    start = property(getStart, setStart)
    end = property(getEnd, setEnd)
    notes = property(getNotes, setNotes)
    clientdata = property(GetClientData, SetClientData)
        
