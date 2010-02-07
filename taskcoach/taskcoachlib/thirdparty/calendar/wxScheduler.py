#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerCore import *
import wx.lib.scrolledpanel as scrolled


class wxScheduler( wxSchedulerCore, scrolled.ScrolledPanel ):

	def __init__( self, *args, **kwds ):
		kwds[ "style" ] = wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		
		super( wxScheduler, self ).__init__( *args, **kwds )
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnClick )
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightClick )
		self.Bind( wx.EVT_LEFT_DCLICK, self.OnDClick )
		self.Bind( wx.EVT_SCROLLWIN, self.OnScroll )

		self._calcScrollBar()
		
	def Refresh( self ):
		scrolled.ScrolledPanel.Refresh( self )
			
	# Events
	def OnClick( self, evt ):
		self._doClickControl( self._getEventCoordinates( evt ) )

	def OnRightClick( self, evt ):
		self._doRightClickControl( self._getEventCoordinates( evt ) )

	def OnDClick( self, evt ):
		self._doDClickControl( self._getEventCoordinates( evt ) )
		
	def OnScroll( self, evt ):
		evt.Skip()
		self.Refresh()
		
	def OnSize( self, evt ):
		self._calcScrollBar()
		self.Refresh()
		evt.Skip()
		
	def Add( self, *args, **kwds ):
		wxSchedulerCore.Add( self, *args, **kwds )
		self._controlBindSchedules()
		
	def SetResizable( self, value ):
		"""
		Call derived method and force wxDC refresh
		"""
		wxSchedulerPaint.SetResizable( self, value )
		self._calcScrollBar()
		
	def _controlBindSchedules( self ):
		"""
		Control if all the schedules into self._schedules
		have its EVT_SCHEDULE_CHANGE binded
		"""
		currentSc = set( self._schedules )
		bindSc = set( self._schBind )
		
		for sc in ( currentSc - bindSc ):
			sc.Bind( EVT_SCHEDULE_CHANGE, lambda x: wx.CallAfter( self.Refresh ) )
			self._schBind.append( sc )
		
	def _calcScrollBar( self ):
		width, height = self.GetViewSize()
		self.SetScrollbars( 20, 20, width / 20, height / 20 )
		self.Refresh()
			
	def _getEventCoordinates( self, event ):
		""" 
		Return the coordinates associated with the given mouse event.

		The coordinates have to be adjusted to allow for the current scroll
		position.
		"""
		originX, originY = self.GetViewStart()
		unitX, unitY = self.GetScrollPixelsPerUnit()
		
		coords = wx.Point( 
			event.GetX() + ( originX * unitX ),
			event.GetY() + ( originY * unitY ) 
				)
		
		return coords

	def SetViewType( self, view=None ):
		wxSchedulerCore.SetViewType( self, view )
		self._calcScrollBar()
		self.Refresh()
		
