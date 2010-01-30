#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
import wx

#New event
wxEVT_COMMAND_SCHEDULE_CHANGE = wx.NewEventType()
EVT_SCHEDULE_CHANGE = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_CHANGE )


# Constants
			 
			 
class wxSchedule( wx.EvtHandler ):
	
	SCHEDULE_DEFAULT_COLOR = wx.Color( 247, 212, 57 )  
	CATEGORIES = {
		"Work"		: wx.GREEN,
		"Holiday"	: wx.GREEN,
		"Phone"		: wx.GREEN,
		"Email"		: wx.GREEN,
		"Birthday"	: wx.GREEN,
		"Ill"		: wx.GREEN,
		"At home"	: wx.GREEN,
		"Fax"		: wx.GREEN, 
	}
	
	def __init__( self ):
		"""
		Use self.start and self.end for set the star and the end of the schedule.
		If both start and end datetime have time set to 00:00 the schedule is
		relative on entire day/days.
		"""
		super( wxSchedule, self ).__init__()
		
		self._color			= self.SCHEDULE_DEFAULT_COLOR
		self._category		= "Work"
		self._description	= ''
		self._notes			= ''
		self._end			= wx.DateTime().Now()
		self._start			= wx.DateTime().Now()
		self._done			= False
		self._clientdata	= None
		self._icon			= None
		
		# Need for freeze the event notification
		self._freeze = False 
	
	def __getattribute__(self, name):
		if name[:3] in [ 'get', 'set' ]:
			warnings.warn( "getData() is deprecated, use GetData() instead", DeprecationWarning, stacklevel=2 )
			
			name = name[0].upper() + name[1:]
		
		return super( wxSchedule, self ).__getattribute__( name )
		
	# Global methods
	def Freeze( self ):
		# Freeze the event notification
		self._freeze = True
	
	def Thaw( self ):
		# Wake up the event
		self._freeze = False
		self._eventNotification()
		
	def GetData(self):
		"""
		Return wxSchedule data into a dict
		"""
		attributes = [ 
			"category", 
			"color", 
			"description", 
			"done", 
			"end", 
			"notes",
			"start", 
			"clientdata",
			"icon",
		]
		data = dict()
					 
		for attribute in attributes:
			data[ attribute ] = self.__getattribute__( attribute )
		
		return data
						
	# Internal methods
	
	def _eventNotification( self ):
		""" If not freeze, wake up and call the event notification
		"""
		if self._freeze: return
		
		#Create the event and propagete it
		evt = wx.PyCommandEvent( wxEVT_COMMAND_SCHEDULE_CHANGE )
		
		evt.category	= self._category
		evt.color		= self._color
		evt.description	= self._description
		evt.done		= self._done
		evt.end			= self._end
		evt.notes		= self._notes
		evt.start		= self._start
		evt.icon		= self._icon
		evt.schedule	= self
		
		evt.SetEventObject( self )
		
		self.ProcessEvent( evt )

	def __eq__( self, schedule ):
		"""
		Control if the schedule passed are equal than me
		"""
		# Is not a wxSchedule
		if not isinstance( schedule, wxSchedule ): 
			return False
		
		# Check wxSchedules attributes
		return self.GetData() == schedule.GetData()
		
	# Properties
	def SetCategory( self, category ):
		"""
		Set the color
		"""
		if category not in self.CATEGORIES.keys():
			raise ValueError, "%s is not a valid category" % category
		
		self._category = category
		self._eventNotification()
	
	def GetCategory( self ):
		""" 
		Return the current category
		"""
		return self._category
	
	def SetColor( self, color ):
		"""
		Set the color
		"""
		if not isinstance( color, wx.Color ):
			raise ValueError, "Color can be only a wx.Color value"

		self._color = color
		self._eventNotification()
		
	def GetColor( self ):
		""" 
		Return the color
		"""
		return self._color

	def SetDescription( self, description ):
		"""
		Set the description
		"""
		if not isinstance( description, basestring ):
			raise ValueError, "Description can be only a str value"

		self._description = description
		self._eventNotification()
		
	def GetDescription( self ):
		"""
		Return the description
		"""
		return self._description

	def SetDone( self, done ):
		""" 
		Are this schedule complete?
		""" 
		if not isinstance( done, bool ):
			raise ValueError, "Done can be only a bool value"
		
		self._done = done
		self._eventNotification()
		
	def GetDone( self ):
		"""
		Return the done value
		"""
		return self._done
	
	def SetEnd( self, dtEnd ):
		"""
		Set the end
		"""
		if not isinstance( dtEnd, wx.DateTime ):
			raise ValueError, "dateTime can be only a wx.DateTime value"

		self._end = dtEnd
		self._eventNotification()
	
	def GetEnd( self ):
		""" 
		Return the end
		"""
		return self._end
				
	def SetNotes( self, notes ):
		""" 
		Set the notes
		"""
		if not isinstance( notes, basestring ):
			raise ValueError, "notes can be only a str value"
	   
		self._notes = notes
		self._eventNotification()

	def GetNotes( self ):
		""" 
		Return the notes
		"""
		return self._notes

	def SetStart( self, dtStart ):
		""" Set the start
		"""
		if not isinstance( dtStart, wx.DateTime ):
			raise ValueError, "dateTime can be only a wx.DateTime value"
		
		self._start = dtStart
		self._eventNotification()
	
	def GetStart( self ):
		""" 
		Return the start
		"""
		return self._start
	
	def GetIcon(self):
		return self._icon
	
	def SetIcon(self, value):
		self._icon = value
		
		self._eventNotification()

	def SetClientData( self, clientdata ):
		self._clientdata = clientdata
	
	def GetClientData( self ):
		return self._clientdata
	
	category = property( GetCategory, SetCategory )
	color = property( GetColor, SetColor )
	description = property( GetDescription, SetDescription )
	done = property( GetDone, SetDone )
	start = property( GetStart, SetStart )
	end = property( GetEnd, SetEnd )
	notes = property( GetNotes, SetNotes )
	clientdata = property( GetClientData, SetClientData )
	icon = property( GetIcon, SetIcon )
