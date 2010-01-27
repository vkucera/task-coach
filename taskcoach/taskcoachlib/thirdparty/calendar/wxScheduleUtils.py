# -*- coding: utf-8 -*-
import wx

def copyDate(value):
    """ Simple method for copy the date (Y,M,D).
    """
    return wx.DateTimeFromDMY(value.GetDay(), value.GetMonth(), value.GetYear())
        
def copyDateTime(value):
    """ Return a copy of input wxDateTime object
    """
    if value.IsValid():  
        return wx.DateTimeFromDMY(
            value.GetDay(), 
            value.GetMonth(),
            value.GetYear(),
            value.GetHour(),
            value.GetMinute(),
            value.GetSecond(),
            value.GetMillisecond(),
        )
    else:
        return wx.DateTime()

    
