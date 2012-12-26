'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

import wx, uicommand
from taskcoachlib import operating_system
from taskcoachlib.thirdparty import aui


class _Toolbar(aui.AuiToolBar):
    def __init__(self, parent, style):
        super(_Toolbar, self).__init__(parent, agwStyle=aui.AUI_TB_NO_AUTORESIZE)

    def AddLabelTool(self, id, label, bitmap1, bitmap2, kind, **kwargs):
        long_help_string = kwargs.pop('longHelp', '')
        short_help_string = kwargs.pop('shortHelp', '')
        bitmap2 = self.MakeDisabledBitmap(bitmap1)
        super(_Toolbar, self).AddTool(id, label, bitmap1, bitmap2, kind, 
                                      short_help_string, long_help_string, None, None)

    def GetToolState(self, toolid):
        return self.GetToolToggled(toolid)

    def SetToolBitmapSize(self, size):
        self.__size = size

    def GetToolBitmapSize(self):
        return self.__size

    def GetToolSize(self):
        return self.__size

    def SetMargins(self, *args):
        if len(args) == 2:
            super(_Toolbar, self).SetMarginsXY(args[0], args[1])
        else:
            super(_Toolbar, self).SetMargins(*args)

    def MakeDisabledBitmap(self, bitmap):
        return bitmap.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
        
    
class ToolBar(_Toolbar, uicommand.UICommandContainerMixin):
    def __init__(self, window, size=(32, 32)):
        self.__window = window
        super(ToolBar, self).__init__(window, style=wx.TB_FLAT|wx.TB_NODIVIDER)
        self.SetToolBitmapSize(size) 
        if operating_system.isMac():
            # Extra margin needed because the search control is too high
            self.SetMargins(0, 7)
        self.appendUICommands(*self.uiCommands())
        self.Realize()
        
    def uiCommands(self):
        return self.__window.createToolBarUICommands()

    def AppendSeparator(self):
        ''' This little adapter is needed for 
        uicommand.UICommandContainerMixin.appendUICommands'''
        self.AddSeparator()

    def AppendStretchSpacer(self, proportion):
        self.AddStretchSpacer(proportion)

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToToolBar(self)

