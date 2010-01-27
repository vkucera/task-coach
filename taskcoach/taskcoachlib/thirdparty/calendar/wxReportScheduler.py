#-----------------------------------------------------------------------------
# Name:        wxReportScheduler.py
# Purpose:     
#
# Author:      expo@expobrain.net
#
# Created:     2006/06/15
# Licence:     GPL
#-----------------------------------------------------------------------------
# -*- coding: utf-8 -*-

from wxSchedulerPrint import *
import wx
import calendar


class wxReportScheduler(wx.Printout):
    """
    This is a class whic demostrate how to use the in-memory wxSchedulerPrint() 
    object on wxPython printing framework.
    You can control wxScheduler in the same way on GUI.
    For other info on wxPrintOut class and methods check the wxPython 
    documentation (RTFM for nerds ;-) ).
    """
    def __init__(self, format, day, schedules):
        self._format    = format
        self._day       = day
        self._schedules = schedules
        
        wx.Printout.__init__(self)
            
    def _getScheduler(self, dc, day):
        """
        Return an in-memory wxSchedulerPrint() object for adding 
        schedules and print on current wxDC
        """
        scheduler = wxSchedulerPrint(dc)
        scheduler.SetViewType(self._format)
        scheduler.SetDate(day)
        
        return scheduler

    def OnPreparePrinting(self):
        self.base_OnPreparePrinting()
        
        self.pages = 1

    def OnPrintPage(self, page):
        """
        This code draw a wxScheduler scaled to fit page using date, format and 
        schedules passed by the user.
        Note there is no difference on manage scheduler and schedules beetwen 
        GUI and rinting framework
        """
        dc          = self.GetDC()
        scheduler   = self._getScheduler(dc, self._day)
        
        dcW,dcH = dc.GetSizeTuple()
        mm      = float(dcW) / dc.GetSizeMM().width
        marginL = 10 * mm
        marginR = 10 * mm
        marginT = 10 * mm
        marginB = 15 * mm
        dcW    -= marginL - marginR - 5
        dcH    -= marginT - marginB - 5
        
        size    = scheduler.GetViewSize()
        scaleX  = float(dcW) / size.width
        scaleY  = float(dcH) / size.height
        scale   = min(scaleX, scaleY)
        dc.SetUserScale(scale, scale)
        dc.SetDeviceOrigin(marginL / scale, marginT / scale)
        
        for schedule in self._schedules:
            scheduler.Add(schedule)
            
        schedSize = scheduler.GetViewSize()
        scheduler.Draw()
        
        return True

    def HasPage(self, page):
        if page <= self.pages:
            return True
        else:
            return False

    def GetPageInfo(self):
        return (1, self.pages, 1, 1)
