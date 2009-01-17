'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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
from taskcoachlib import persistence
from taskcoachlib.i18n import _


class PrinterSettings(object):
    def __init__(self):
        self.printData = wx.PrintData()
        self.pageSetupData = wx.PageSetupDialogData(self.printData)

    def updatePageSetupData(self, data):
        self.pageSetupData = wx.PageSetupDialogData(data)
        self.updatePrintData(data.GetPrintData())

    def updatePrintData(self, printData):
        self.printData = wx.PrintData(printData)
        self.pageSetupData.SetPrintData(self.printData)

printerSettings = PrinterSettings()


class HTMLPrintout(wx.html.HtmlPrintout):
    def __init__(self, aViewer, printSelectionOnly=False, *args, **kwargs):
        super(HTMLPrintout, self).__init__(*args, **kwargs)
        htmlText, count = persistence.viewer2html(aViewer, 
                                                  selectionOnly=printSelectionOnly)
        self.SetHtmlText(htmlText)
        self.SetFooter(_('Page') + ' @PAGENUM@/@PAGESCNT@', wx.html.PAGE_ALL)
        self.SetFonts('Arial', 'Courier')
        global printerSettings
        top, left = printerSettings.pageSetupData.GetMarginTopLeft()
        bottom, right = printerSettings.pageSetupData.GetMarginBottomRight()
        self.SetMargins(top, bottom, left, right)

                
class DCPrintout(wx.Printout):
    def __init__(self, viewer):
        self.viewer = viewer
        super(DCPrintout, self).__init__()
        
    def OnPrintPage(self, page):
        self.viewer.getWidget().Draw(self.GetDC())
        
    def GetPageInfo(self):
        return (1, 1, 1, 1)


def Printout(viewer, printSelectionOnly=False, *args, **kwargs):
    if hasattr(viewer.getWidget(), 'Draw'):
        return DCPrintout(viewer)
    else:
        return HTMLPrintout(viewer, printSelectionOnly, *args, **kwargs)