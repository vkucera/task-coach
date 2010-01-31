#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedule import wxSchedule
from wxSchedulerCore import *
import calendar
import string
import sys
import wx
import wxScheduleUtils as utils

if sys.version.startswith( "2.3" ):
   from sets import Set as set


# Events 
wxEVT_COMMAND_SCHEDULE_ACTIVATED = wx.NewEventType()
EVT_SCHEDULE_ACTIVATED = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_ACTIVATED )

wxEVT_COMMAND_SCHEDULE_DCLICK = wx.NewEventType()
EVT_SCHEDULE_DCLICK = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_DCLICK )

# Main class
class wxSchedulerPaint( object ):
	
	def __init__( self, *args, **kwds ):
		super( wxSchedulerPaint, self ).__init__( *args, **kwds )
		
		# If possible, enable autobuffered dc
		self._autoBufferedDC = hasattr( self, 'SetBackgroundStyle' )

		if self._autoBufferedDC:
			self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self._resizable		= False
		self._day_size		= DAY_SIZE_MIN
		self._week_size		= WEEK_SIZE_MIN
		self._month_cell	= MONTH_CELL_SIZE_MIN
		
		self._hourH		= 0
		self._offsetTop	= 0

		self._style = wxSCHEDULER_VERTICAL

		self._minHeight = 0

	def _doClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_ACTIVATED, point )
		
	def _doDClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_DCLICK, point )
		
	def _findSchedule( self, point ):
		"""
		Check if the point is on a schedule and return the schedule
		"""
		for coords in self._schedulesCoords:
			schedule, pointMin, pointMax = coords
			
			inX = ( pointMin.x <= point.x ) & ( point.x <= pointMax.x )
			inY = ( pointMin.y <= point.y ) & ( point.y <= pointMax.y )
			
			if inX & inY:
				return schedule.GetClientData()
		
		# Not accept the request outside our draw "real" area
		x, y = point.x, point.y
		
		if self._viewType == wxSCHEDULER_DAILY: 
			myWidth = self._day_size
		elif self._viewType == wxSCHEDULER_WEEKLY: 
			myWidth = self._week_size
		elif self._viewType == wxSCHEDULER_MONTHLY: 
			myWidth = self.GetViewSize()
		else: 
			return None
	
		if ( ( x < LEFT_COLUMN_SIZE or x > LEFT_COLUMN_SIZE + myWidth.width ) or 
				( y < self._offsetTop or y > self._day_size.height ) ):
			return None
		
		# Go and find the click
		if self._viewType in ( wxSCHEDULER_DAILY, wxSCHEDULER_WEEKLY ):
			# In case we don't even enter the loop
			myDate = None

			for i, hour in enumerate( self._lstDisplayedHours ):
				if y >= ( self._offsetTop + self._hourH * i ) and y < ( self._offsetTop + self._hourH * ( i + 1 ) ):
					myDate = utils.copyDateTime( self._lstDisplayedHours[i] )
					myDate.SetSecond( 0 )
					
					# Don't return yet
					if not self._viewType == wxSCHEDULER_WEEKLY:
						break
			
			if self._viewType == wxSCHEDULER_DAILY:
				return myDate
			
			elif myDate is not None:
				dayWidth = self._week_size.width / 7
				
				# Get the right day
				for weekday in xrange( 7 ):
					if ( x > LEFT_COLUMN_SIZE + dayWidth * weekday and x < LEFT_COLUMN_SIZE + dayWidth * ( weekday + 1 ) ):
						return self.GetWeekdayDate( weekday, myDate )
		
		elif self._viewType == wxSCHEDULER_MONTHLY:
			# TO-DO
			pass
		else:
			return None
		
	def _getNewSize( self, size, size_min ):
		"""
		Return a new size if size is greater than size_min else return size_min
		"""
		w, h = size.width, size.height
		
		if ( w < size_min.width ):
			w = size_min.width
		if ( h < size_min.height ):
			h = size_min.height
		
		return wx.Size( w, h )
		
	def _getSchedBlocks( self, schedules, day ):
		"""
		Consume schedules and create a list of blocks of one or more schedules 
		which are in collision.
		"""
		startH,endH = utils.copyDateTime( self._startingHour ), utils.copyDateTime( self._endingHour )
		
		# Set day to first day of month because I raise an exception if I change 
		# the month and this don't have more than current GetDay() value
		startH.SetDay( 1 )
		endH.SetDay( 1 )
		
		startH.SetYear( day.GetYear() )
		startH.SetMonth( day.GetMonth() )
		startH.SetDay( day.GetDay() )
		
		endH.SetYear( day.GetYear() )
		endH.SetMonth( day.GetMonth() )
		endH.SetDay( day.GetDay() )
		
		schedBlocks = []
		schedules = set( schedules )
		
		while len( schedules ) > 0:
			schedule = schedules.pop()
			
			# If schedule is on range for display create block else discard schedule
			if not ( ( schedule.start <= startH ) & ( schedule.end <= startH ) | ( schedule.start >= endH ) & ( schedule.end >= endH ) ):
				block = [ self._resizeSched( schedule, startH, endH ) ]
				
				# Find collisions, remove from set and add to block
				for collide in schedules:
					startBetween = schedule.start.IsBetween( collide.start, collide.end ) | collide.start.IsBetween( schedule.start, schedule.end )
					endBetween = schedule.end.IsBetween( collide.start, collide.end ) | collide.end.IsBetween( schedule.start, schedule.end )
					
					if ( schedule.start, schedule.end ) != ( collide.start, collide.end ):
						if startBetween & ( schedule.start == collide.end ):
							startBetween = False
						if endBetween & ( schedule.end == collide.start ):
							endBetween = False
						
					if startBetween & endBetween:
						collide = self._resizeSched( collide, startH, endH )
						block.append( collide )
						
				schedBlocks.append( block )
				schedules -= set( block )
			
		return schedBlocks
				
	def _getSchedInDay( self, schedules, day ):
		"""
		Filter schedules in day
		"""
		schedInDay = list()
		
		for schedule in schedules:
			if schedule.start.IsSameDate( day ) | schedule.end.IsSameDate( day ) | day.IsBetween( schedule.start, schedule.end ):
				newSchedule = schedule.Clone()
				# This is used to find the original schedule object in _findSchedule.
				newSchedule.clientdata	= schedule

				schedInDay.append( newSchedule )
		
		return schedInDay

	def _getSchedInPeriod( self, schedules, start, end):
		"""
		Returns a list of copied schedules that intersect with
		the  period  defined by	 'start'  and 'end'.  Schedule
		start and end are trimmed so as to lie between 'start'
		and 'end'.
		"""
		results = []

		for schedule in schedules:
			if schedule.start.IsLaterThan(end):
				continue
                        if start.IsLaterThan(schedule.end):
				continue

			newSchedule = schedule.Clone()
			# This is used to find the original schedule object in _findSchedule.
			newSchedule.clientdata	= schedule

			if start.IsLaterThan(schedule.start):
				newSchedule.start = utils.copyDateTime(start)
			if schedule.end.IsLaterThan(end):
				newSchedule.end = utils.copyDateTime(end)

                        results.append(newSchedule)

		return results

	def _splitSchedules( self, schedules ):
		"""
		Returns	 a list	 of lists  of schedules.  Schedules in
		each list are guaranteed not to collide.
		"""
		results = []
		current = []

		schedules = schedules[:] # Don't alter original list
		def compare(a, b):
			if a.start.IsEqualTo(b.start):
				return 0
			if a.start.IsEarlierThan(b.start):
				return -1
			return 1
		schedules.sort(compare)

		def findNext(schedule):
			# Among schedules that start after this one ends, find the "nearest".
			candidateSchedule = None
			minDelta = None
			for sched in schedules:
				if sched.start.IsLaterThan(schedule.end):
					delta = sched.start.Subtract(schedule.end)
					if minDelta is None or minDelta > delta:
						minDelta = delta
						candidateSchedule = sched
			return candidateSchedule

		while schedules:
			schedule = schedules[0]
			while schedule:
				current.append(schedule)
				schedules.remove(schedule)
				schedule = findNext(schedule)
			results.append(current)
			current = []

		return results

	def _paintDay( self, dc, day, offsetX, width, hourH ):
		"""
		Draw column width schedules
		"""
		dc.SetBrush( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
		
		offsetY = 0
		
		# Header day
		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		
		text = '%s %s %s' % ( day.GetWeekDayName( day.GetWeekDay() )[:3], day.GetDay(), day.GetMonthName( day.GetMonth() ) )
		textW, textH = dc.GetTextExtent( text )
		dayH = HEADER_COLUMN_SIZE
		offsetY += dayH
		
		self._offsetTop = offsetY
		
		dc.DrawRectangle( offsetX, 0, width, textH * 1.5 )
		dc.SetTextForeground( wx.BLACK )
		dc.DrawText( text, offsetX + ( width - textW ) / 2, textH * .25 )
		
		# Body
		dc.SetBrush( wx.Brush( DAY_BACKGROUND_BRUSH ) )
		dc.DrawRectangle( offsetX, offsetY, width, hourH * len( self._lstDisplayedHours ) )
			
		# Draw schedules
		# draw half hour separators
		for i, hour in enumerate( self._lstDisplayedHours ):
			dc.DrawLine( offsetX, offsetY + hourH * i, offsetX + width, offsetY + hourH * i )
		
		# calculate pixels/minute ratio
		minute = hourH / 30.0
		font.SetWeight( wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		
		startHours = utils.copyDate( day )
		startHours.SetHour( self._lstDisplayedHours[0].GetHour() )
		startHours.SetMinute( self._lstDisplayedHours[0].GetMinute() )
		
		endHours = utils.copyDate( day )
		endHours.SetHour( self._lstDisplayedHours[ - 1].GetHour() )
		endHours.SetMinute( self._lstDisplayedHours[ - 1].GetMinute() )
		
		schedules = self._getSchedInDay( self._schedules, day )
		blocks = self._getSchedBlocks( schedules, day )
		
		for block in blocks:
			# Set the number of slot wich I must divide the block for draw schedules
			slots = len( block )
			schedW = ( width - SCHEDULE_INSIDE_MARGIN * ( slots + 1 ) ) / slots

			for i,schedule in enumerate( block ):
				# coordinates
				startX = offsetX + SCHEDULE_INSIDE_MARGIN + i * ( SCHEDULE_INSIDE_MARGIN + schedW )
				
				startY = schedule.start - startHours
				startY = startY.GetMinutes() * minute
				startY += offsetY
				
				endH = schedule.end - schedule.start
				endH = endH.GetMinutes() * minute
				
				# Modify schedule if work hour's are hidden
				if self.GetShowWorkHour():
					startingPauseHour = utils.copyDateTime( self._startingPauseHour )
					endingPauseHour = utils.copyDateTime( self._endingPauseHour )
					startingPauseHour.SetDay( 1 )
					endingPauseHour.SetDay( 1 )
					startingPauseHour.SetYear( day.GetYear() ); startingPauseHour.SetMonth( day.GetMonth() ); startingPauseHour.SetDay( day.GetDay() )
					endingPauseHour.SetYear( day.GetYear() ); endingPauseHour.SetMonth( day.GetMonth() ); endingPauseHour.SetDay( day.GetDay() )
					
					# Check if start/stop are out pause
					startBetween = schedule.start.IsBetween( startingPauseHour, endingPauseHour )
					endBetween = schedule.end.IsBetween( startingPauseHour, endingPauseHour ) 
					
					if startBetween & endBetween:
						break
					else:
						if startBetween == True:
							diff = ( endingPauseHour - schedule.start ).GetMinutes() * minute
							startY += diff
							endH -= diff
						if endBetween == True:
							diff = ( schedule.end - startingPauseHour ).GetMinutes() * minute
							endH -= diff
							
					# Check if pause is during schedule
					startBetween = startingPauseHour.IsBetween( schedule.start, schedule.end )
					stopBetween = endingPauseHour.IsBetween( schedule.start, schedule.end )
					
					if startBetween & stopBetween:
						diff = ( endingPauseHour - startingPauseHour ).GetMinutes() * minute
						endH -= diff
						
					# Check if schedule is after pause
					if schedule.start > endingPauseHour:
						diff = ( endingPauseHour - startingPauseHour ).GetMinutes() * minute
						startY -= diff
				
				
				description = self._shrinkText( dc, schedule.description, schedW - 5 * 2, endH )
				
				# Go drawing
				dc.SetBrush( wx.Brush( schedule.color ) )
				dc.DrawRectangle( startX, startY, schedW, endH )
				
				runY = startY

				if schedule.icon:
					bitmap = wx.ArtProvider.GetBitmap( schedule.icon, wx.ART_FRAME_ICON, (16, 16) )
					dc.DrawBitmap( bitmap, startX + 5, runY, True )
					runY += 20

				dc.SetTextForeground( schedule.foreground )
				for line in description:
					dc.DrawText( line, startX + 5, runY )
					runY += dc.GetTextExtent( line )[1]
				
				self._schedulesCoords.append( ( schedule, wx.Point( startX, startY ), wx.Point( startX + schedW, startY + endH ) ) )

	def _paintPeriodHorizontal( self, dc, start, end, x, y, width ):
		"""
		Draws  schedules  as  horizontal bars,	with  variable
		height, depending on their description.
		"""
		blocks = self._splitSchedules(self._getSchedInPeriod(self._schedules, start, end))

		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )

		offsetY = y + SCHEDULE_INSIDE_MARGIN

		totalSpan = end.Subtract(start).GetMinutes()

		offsetY += SCHEDULE_INSIDE_MARGIN

		for block in blocks:
			slots = len( block )
			maxDY = 0

			for schedule in block:
				slots = len( block )
				spanStart = schedule.start.Subtract(start).GetMinutes()
				spanEnd = schedule.end.Subtract(start).GetMinutes()

				startX = x + int(1.0 * width * spanStart / totalSpan)
				endX = y + int(1.0 * width * spanEnd / totalSpan)

				text = self._shrinkText(dc, schedule.description, endX - startX - 2 * SCHEDULE_INSIDE_MARGIN, SCHEDULE_MAX_HEIGHT)
				textW, textH = 0, 0
				for line in text:
					tW, tH = dc.GetTextExtent(line)
					textW = max(textW, tW)
					textH += tH

				dc.SetBrush(wx.Brush(schedule.color))
				dc.DrawRectangle(startX, offsetY, endX - startX, textH + 2 * SCHEDULE_INSIDE_MARGIN)
				self._schedulesCoords.append((schedule, wx.Point(startX, offsetY),
							      wx.Point(endX, offsetY + textH + 2 * SCHEDULE_INSIDE_MARGIN)))

				localOffset = 0
				dc.SetTextForeground( schedule.foreground )
				for line in text:
					dc.DrawText(line, startX + SCHEDULE_INSIDE_MARGIN, offsetY + localOffset + SCHEDULE_INSIDE_MARGIN)
					localOffset += dc.GetTextExtent(line)[1]

				maxDY = max(maxDY, textH)

			offsetY += maxDY + 3 * SCHEDULE_INSIDE_MARGIN

		if self._minHeight != offsetY:
			self._minHeight = offsetY
			self._calcScrollBar()

	def _paintDaily( self, dc, day ):
		"""
		Display day schedules
		"""
		hourH = self._paintHours( dc, self._day_size.height )
		self._paintDay( dc, self.GetDate(), LEFT_COLUMN_SIZE, self._day_size.width, hourH )

	def _paintDailyHorizontal( self, dc, day ):
		startHours = utils.copyDate( day )
		startHours.SetHour( self._lstDisplayedHours[0].GetHour() )
		startHours.SetMinute( self._lstDisplayedHours[0].GetMinute() )
		startHours.SetSecond(0)

		endHours = utils.copyDate( day )
		endHours.SetHour( self._lstDisplayedHours[ - 1].GetHour() )
		endHours.SetMinute( self._lstDisplayedHours[ - 1].GetMinute() )
		endHours.SetSecond(0)

		x = LEFT_COLUMN_SIZE
		totalSpan = endHours.Subtract(startHours).GetMinutes()

		offsetY = 0
		width = self._day_size.width

		dc.SetBrush( wx.Brush( DAY_BACKGROUND_BRUSH ) )
		dc.DrawRectangle(x, 0, width, 32767)

		text = '%s %s %s' % ( day.GetWeekDayName( day.GetWeekDay() )[:3], day.GetDay(), day.GetMonthName( day.GetMonth() ) )
		textW, textH = dc.GetTextExtent( text )
		dc.SetTextForeground( wx.BLACK )
		dc.DrawText(text, int((width - textW) / 2), offsetY)
		offsetY += textH + SCHEDULE_INSIDE_MARGIN

		# Draw hours
		hourWidth = width / int(totalSpan / 60)

		maxDY = 0
		for i in xrange(startHours.GetHour(), endHours.GetHour() + 1):
			startX = x + int(1.0 * width * (i - startHours.GetHour()) * 60 / totalSpan)
			dc.DrawText('%d' % i, startX + 2, offsetY + 2)
			maxDY = max(maxDY, dc.GetTextExtent('%d' % i)[1])
			dc.DrawLine(startX, offsetY, startX, 32767) # Humph
		for i in xrange(startHours.GetHour(), endHours.GetHour()):
			startX = x + int(1.0 * width * (i - startHours.GetHour()) * 60 / totalSpan)
			dc.DrawLine(startX + hourWidth / 2, offsetY + maxDY + 1, startX + hourWidth / 2, 32767)

		offsetY += maxDY
		dc.DrawLine(x, offsetY + 1, x + width, offsetY + 1)

		height = self._paintPeriodHorizontal(dc, startHours, endHours, x, offsetY, width)

		# Gray out non worked hours
		dc.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INACTIVEBORDER)))

		startPause = utils.copyDateTime(self._startingPauseHour)
		startPause.SetSecond(0)

		endPause = utils.copyDateTime(self._endingPauseHour)
		endPause.SetSecond(0)

		startSpan = startPause.Subtract(startHours).GetMinutes()
		dc.DrawRectangle(x + int(1.0 * width * startSpan / totalSpan), offsetY,
				 int(1.0 * width * (endPause.Subtract(startHours).GetMinutes() - startSpan) / totalSpan) + 1, 32767)

	def _paintHours( self, dc, height ):
		"""
		Draw left column with hours
		Return the height of an half hour for draw the body of day
		"""
		offsetY = 0
		
		# Calculate header space
		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		
		w, h = dc.GetTextExtent( "Day" )
		dayH = HEADER_COLUMN_SIZE
		offsetY += dayH
		
		# Draw hours
		font.SetPointSize( 12 )
		font.SetWeight( wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		dc.SetTextForeground( wx.BLACK )
		hourW, hourH = dc.GetTextExtent( " 24" )
		
		if ( height - offsetY ) > ( len( self._lstDisplayedHours ) * hourH ):
			hourH = ( height - offsetY ) / len( self._lstDisplayedHours )

		for i, hour in enumerate( self._lstDisplayedHours ):
			# If hour is o'clock draw a different line
			#hour = self._lstDisplayedHours[i]
			if hour.GetMinute() == 0:
				dc.DrawLine( LEFT_COLUMN_SIZE * .75, offsetY, LEFT_COLUMN_SIZE, offsetY )
				dc.DrawText( hour.Format( ' %H' ), 5, offsetY )
			else:
				dc.DrawLine( LEFT_COLUMN_SIZE * .90, offsetY, LEFT_COLUMN_SIZE, offsetY )
			
			offsetY += hourH

		self._hourH = hourH
			
		return hourH
			
	def _paintMonthly( self, dc, day ):
		"""
		Draw month's calendar using calendar module functions
		"""
		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		
		# Draw month name
		text = "%s %s" % ( day.GetMonthName( day.GetMonth() ), day.GetYear() )
		textW, textH = dc.GetTextExtent( text )
		x = ( self._month_cell_size.width * 7 - textW ) / 2
		y = ( HEADER_COLUMN_SIZE - textH ) / 2
		offset = HEADER_COLUMN_SIZE
		dc.SetTextForeground( wx.BLACK )
		dc.DrawText( text, x, y )
		
		# Draw month grid
		font.SetWeight( wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		
		month = calendar.monthcalendar( day.GetYear(), day.GetMonth() + 1 )
		
		for w, monthWeek in enumerate( month ):
			for d, monthDay in enumerate( monthWeek ):
				cellW, cellH = self._month_cell_size.width, self._month_cell_size.height
				x = cellW * d
				y = offset + cellH * w
				
				if monthDay == 0:
					dc.SetBrush( wx.LIGHT_GREY_BRUSH )
				else:
					dc.SetBrush( wx.Brush( DAY_BACKGROUND_BRUSH ) )
					
				dc.DrawRectangle( x, y, cellW, cellH )
				
				if monthDay > 0:
					# Draw day number in upper right corner 
					day.SetDay( monthDay )
					monthDay = str( monthDay )
					textW, textH = dc.GetTextExtent( monthDay )
					x += cellW - SCHEDULE_INSIDE_MARGIN - textW
					y += SCHEDULE_INSIDE_MARGIN

					dc.SetTextForeground( wx.BLACK )
					dc.DrawText( monthDay, x, y )
					
					# Draw schedules for this day
					x = cellW * d + SCHEDULE_INSIDE_MARGIN
					y += textH + SCHEDULE_INSIDE_MARGIN
					textH = textH * 1.1
					spaceH = self._month_cell_size.height - SCHEDULE_INSIDE_MARGIN * 3 - textH
					maxSchedules = int( spaceH / textH ) - 1
					
					if maxSchedules > 0:
						schedules = self._getSchedInDay( self._schedules, day )
						for i, schedule in enumerate( schedules[:maxSchedules] ):
							textW = self._month_cell_size.width - SCHEDULE_INSIDE_MARGIN * 2
							text = "%s %s" % ( schedule.start.Format( '%H:%M' ), schedule.description )
							text = self._shrinkText( dc, text, textW, textH )[0]
							
							dc.SetBrush( wx.Brush( schedule.color ) )
							dc.DrawRectangle( x, y, textW, textH )
							dc.SetTextForeground( schedule.foreground )
							dc.DrawText( text, x + textH * .05, y + textH * .05 )
							
							self._schedulesCoords.append( ( schedule, wx.Point( x, y ), wx.Point( x + textW, y + textH ) ) )
							y += textH 

	def _paintMonthlyHorizontal( self, dc, day ):
		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )

                x = LEFT_COLUMN_SIZE
                offsetY = SCHEDULE_INSIDE_MARGIN
		width = self._month_cell_size.width * 7

		text = "%s %s" % ( day.GetMonthName( day.GetMonth() ), day.GetYear() )
		textW, textH = dc.GetTextExtent( text )
		dc.SetTextForeground( wx.BLACK )
		dc.DrawText(text, int((width - textW) / 2), offsetY)
		offsetY += textH + SCHEDULE_INSIDE_MARGIN

		start, count = calendar.monthrange(day.GetYear(), day.GetMonth() + 1)

		startDay = utils.copyDateTime(day)
		startDay.SetDay(1)
		startDay.SetHour(0)
		startDay.SetMinute(0)
		startDay.SetSecond(0)

		endDay = utils.copyDateTime(day)
		endDay.SetDay(count)
		endDay.SetHour(23)
		endDay.SetMinute(59)
		endDay.SetSecond(59)

		maxDY = 0
		for i in xrange(count):
			startX = x + int(1.0 * i * width / count)
			endX = x + int(1.0 * (i + 1) * width / count)
			text = '%d' % (i + 1)
			textW, textH = dc.GetTextExtent(text)
			dc.DrawText(text, startX + int((endX - startX - textW) / 2), offsetY)
			maxDY = max(maxDY, textH)
		offsetY += maxDY
		for i in xrange(count + 1):
			startX = x + int(1.0 * i * width / count)
			dc.DrawLine(startX, offsetY + 4, startX, 32675)

		dc.DrawLine(x, offsetY + 4, x + width, offsetY + 4)
		offsetY += SCHEDULE_INSIDE_MARGIN

		self._paintPeriodHorizontal(dc, startDay, endDay, x, offsetY, width)

	def _paintWeekly( self, dc, day ):
		"""
		Display weekly schedule
		"""
		width = self._week_size.width / 7
		
		# Cycle trough week's days
		hourH = self._paintHours( dc, self._week_size.height )
		days	 = []
		
		for weekday in xrange( 7 ):
			# Must do a copy of wxDateTime object else I append a reference of 
			# same object mupliplied for 7
			days.append( utils.copyDateTime( utils.setToWeekDayInSameWeek( day, weekday, self._weekstart ) ) )
			
		for weekday, day in enumerate( days ):
			self._paintDay( dc, day, LEFT_COLUMN_SIZE + width * weekday, width, hourH )

	def _paintWeeklyHorizontal( self, dc, day ):
		"""
		Display weekly schedule, in horizontal mode
		"""

		width = self._week_size.width
		x = LEFT_COLUMN_SIZE
		offsetY = SCHEDULE_INSIDE_MARGIN

		dc.SetBrush( wx.Brush( DAY_BACKGROUND_BRUSH ) )
		dc.DrawRectangle(x, 0, width, 32767)

		startDay = utils.copyDateTime(utils.setToWeekDayInSameWeek(day, 0, self._weekstart))

		endDay = utils.copyDateTime(utils.setToWeekDayInSameWeek(day, 6, self._weekstart))
		endDay.SetHour(23)
		endDay.SetMinute(59)
		endDay.SetSecond(59)

		totalSpan = endDay.Subtract(startDay).GetMinutes()

		font = dc.GetFont()
		font.SetPointSize( 8 )
		font.SetWeight( wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		dc.SetTextForeground( wx.BLACK )

		maxDY = 0
		for dayN in xrange(7):
			startX = x + int(1.0 * width * dayN * 24 * 60 / totalSpan)
			endX = x + int(1.0 * width * (dayN + 1) * 24 * 60 / totalSpan)

			theDay = utils.copyDateTime(utils.setToWeekDayInSameWeek(day, dayN, self._weekstart))

			text = '%s %s %s' % ( theDay.GetWeekDayName( theDay.GetWeekDay() )[:3], theDay.GetDay(), theDay.GetMonthName( theDay.GetMonth() ) )
			textW, textH = dc.GetTextExtent( text )
			dc.DrawText(text, startX + int((endX - startX - textW) / 2), offsetY)
			maxDY = max(maxDY, textH)

		for dayN in xrange(7):
			endX = x + int(1.0 * width * (dayN + 1) * 24 * 60 / totalSpan)
			dc.DrawLine(endX, offsetY, endX, 32767)

		offsetY += maxDY
		dc.DrawLine(x, offsetY + 4, x + width, offsetY + 4)

		offsetY += maxDY + SCHEDULE_INSIDE_MARGIN

		self._paintPeriodHorizontal(dc, startDay, endDay, x, offsetY, width)

	def _processEvt( self, commandEvent, point ):
		""" 
		Process the command event passed at the given point
		"""
		evt = wx.PyCommandEvent( commandEvent )
		sch = self._findSchedule( point )
		if isinstance( sch, wxSchedule ):
			mySch = sch
			myDate = None
		else:
			mySch = None
			myDate = sch
		
		evt.schedule = mySch
		evt.date = myDate
		evt.SetEventObject( self )
		self.ProcessEvent( evt ) 
	
	def _resizeSched( self, schedule, startH, endH ):
		"""
		Set start and/or end to startH or stopH if excedees limits
		Return None if the schedule is completly outside the limits
		"""
		if schedule.start < startH:
			schedule.start = utils.copyDateTime( startH )
			
		if schedule.end > endH:
			schedule.end = utils.copyDateTime( endH )
		
		return schedule 
	
	def _shrinkText( self, dc, text, width, height ):
		"""
		Truncate text at desired width
		"""
		MORE_SIGNAL		 = '...'
		SEPARATOR		 = " "
		
		textlist	 = list()	# List returned by this method
		words	 = list()	# Wordlist for itermediate elaboration
		
		# Split text in single words and split words when yours width is over 
		# available width
		text = text.replace( "\n", " " ).split()
		
		for word in text:
			if dc.GetTextExtent( word )[0] > width:
				# Cycle trought every char until word width is minor or equal
				# to available width
				partial = ""
				
				for char in word:
					if dc.GetTextExtent( partial + char )[0] > width:
						words.append( partial )
						partial = char
					else:
						partial += char
			else:
				words.append( word )
		
		# Create list of text lines for output
		textline = list()
		
		for word in words:
			if dc.GetTextExtent( string.join( textline + [word], SEPARATOR ) )[0] > width:
				textlist.append( string.join( textline, SEPARATOR ) )
				textline = [word]
				
				# Break if there's no vertical space available
				if ( len( textlist ) * dc.GetTextExtent( SEPARATOR )[0] ) > height:
					# Must exists almost one line of description
					if len( textlist ) > 1:
						textlist = textlist[: - 1]
						
					break
			else:
				textline.append( word )
				
		# Add remained words to text list
		if len( textline ) > 0:
			textlist.append( string.join( textline, SEPARATOR ) )
				
		return textlist
			
	def GetDatesRange( self ):
		"""
		Return min and max date displayed on current view type
		"""
		day = self.GetDate()
		min = utils.copyDate( day )
		max = utils.copyDate( day )
		max += wx.DateSpan( days = 1 )
		max -= wx.TimeSpan( 0, 0, 0, 1 )
		
		if self._viewType == wxSCHEDULER_DAILY:
			pass
		elif self._viewType == wxSCHEDULER_WEEKLY:
			utils.setToWeekDayInSameWeek( min, 0, wxSCHEDULER_WEEKSTART_SUNDAY )
			utils.SetToWeekDayInSameWeek( max, 6, wxSCHEDULER_WEEKSTART_SUNDAY )
		elif self._viewType == wxSCHEDULER_MONTHLY:
			min.SetDay( 1 )
			max.SetToLastMonthDay()
			max += wx.DateSpan( days = 1 )
			max -= wx.TimeSpan( 0, 0, 0, 1 )
			
		return ( min, max )

	def GetViewSize( self ):
		"""
		Return Current view size in pixels
		"""
		objsize = self.GetSize()
		if isinstance( self, wx.ScrolledWindow ):
			objsize -= wx.Size( 20, 20 )

		if self._viewType == wxSCHEDULER_DAILY:
			# Calculate day view size

			if self._style == wxSCHEDULER_HORIZONTAL:
				minSize = wx.Size(DAY_SIZE_MIN.width, self._minHeight)
			else:
				minSize = DAY_SIZE_MIN

			if self._resizable:
				objsize.width -= LEFT_COLUMN_SIZE
				objsize.height -= HEADER_COLUMN_SIZE
				
				self._day_size = self._getNewSize( objsize, minSize )
			else:
				self._day_size = DAY_SIZE_MIN
				
			size = wx.Size( LEFT_COLUMN_SIZE + self._day_size.width, self._day_size.height + HEADER_COLUMN_SIZE )
		elif self._viewType == wxSCHEDULER_WEEKLY:
			# Calculate week view size

			if self._style == wxSCHEDULER_HORIZONTAL:
				minSize = wx.Size(WEEK_SIZE_MIN.width, self._minHeight)
			else:
				minSize = WEEK_SIZE_MIN

			if self._resizable:
				objsize.width -= LEFT_COLUMN_SIZE
				objsize.height -= HEADER_COLUMN_SIZE
				
				self._week_size = self._getNewSize( objsize, minSize )
			else:
				self._week_size = WEEK_SIZE_MIN
			
			size = wx.Size( LEFT_COLUMN_SIZE + self._week_size.width, self._week_size.height + HEADER_COLUMN_SIZE )
		elif self._viewType == wxSCHEDULER_MONTHLY:
			# Calculate month view size

			day = self.GetDate()
			weeks = len( calendar.monthcalendar( day.GetYear(), day.GetMonth() + 1 ) )

			if self._style == wxSCHEDULER_HORIZONTAL:
				minSize = wx.Size(MONTH_CELL_SIZE_MIN.width, self._minHeight / weeks)
			else:
				minSize = MONTH_CELL_SIZE_MIN
				
			if self._resizable:
				objsize.height -= HEADER_COLUMN_SIZE
				objsize = wx.Size( objsize.width / 7, objsize.height / weeks )
				
				self._month_cell_size = self._getNewSize( objsize, minSize )
			else:
				self._month_cell_size = MONTH_CELL_SIZE_MIN
			
			size = wx.Size( self._month_cell_size.width * 7, self._month_cell_size.height * weeks + HEADER_COLUMN_SIZE )
			
		return size
		
	def OnPaint( self, evt = None ):
		self._schedulesCoords = list()	

		# Do the draw
		if self._dc == None:
			if self._autoBufferedDC:
				dc = wx.AutoBufferedPaintDC( self )
			else:
				dc = wx.PaintDC()
			
			self.PrepareDC( dc )
			
			scrollX, scrollY = self.CalcUnscrolledPosition( 0, 0 )
		else:
			dc = self._dc
			
			scrollX = scrollY = 0
			
		dc.SetBackground( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
		dc.SetPen( FOREGROUND_PEN )
		dc.Clear()

		dc.SetDeviceOrigin( -scrollX, - scrollY )

		# Get a copy of wxDateTime object
		day = utils.copyDate( self.GetDate() )

		if self._style == wxSCHEDULER_VERTICAL:
			if self._viewType == wxSCHEDULER_DAILY:
				self._paintDaily( dc, day )

			elif self._viewType == wxSCHEDULER_WEEKLY:
				self._paintWeekly( dc, day )

			elif self._viewType == wxSCHEDULER_MONTHLY:
				self._paintMonthly( dc, day )
		else:
			if self._viewType == wxSCHEDULER_DAILY:
				self._paintDailyHorizontal( dc, day )

			elif self._viewType == wxSCHEDULER_WEEKLY:
				self._paintWeeklyHorizontal( dc, day )

			elif self._viewType == wxSCHEDULER_MONTHLY:
				self._paintMonthlyHorizontal( dc, day )


	def SetResizable( self, value ):
		"""
		Draw proportionally of actual space but not down on minimun sizes
		The actual sze is retrieved by GetSize() method of derived object
		"""
		self._resizable = bool( value )

	def SetStyle(self, style):
		"""
		Sets  the drawing  style.  Values  for 'style'	may be
		wxSCHEDULER_VERTICAL	   (the	      default)	    or
		wxSCHEDULER_HORIZONTAL.
		"""
		self._style = style

	def GetStyle( self ):
		return self._style
