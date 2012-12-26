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
        self.__visibleUICommands = list()
        super(ToolBar, self).__init__(window, style=wx.TB_FLAT|wx.TB_NODIVIDER)
        self.SetToolBitmapSize(size) 
        if operating_system.isMac():
            # Extra margin needed because the search control is too high
            self.SetMargins(0, 7)
        self.loadPerspective(window.getToolBarPerspective())
        
    def loadPerspective(self, perspective):
        for uiCommand in self.__visibleUICommands:
            if uiCommand is not None and not isinstance(uiCommand, int):
                uiCommand.unbind(self, uiCommand.id)
        self.Clear()
        commands = list()
        if perspective:
            index = dict([(command.__class__.__name__, command) for command in self.uiCommands()])
            index['Separator'] = None
            index['Spacer'] = 1
            for className in perspective.split(','):
                if className in index:
                    commands.append(index[className])
        else:
            commands = self.uiCommands()
        self.__visibleUICommands = commands[:]
        self.appendUICommands(*commands)
        self.Realize()

    def savePerspective(self):
        classes = list()
        for uiCommand in self.__visibleUICommands:
            if uiCommand is None:
                classes.append('Separator')
            elif isinstance(uiCommand, int):
                classes.append('Spacer')
            else:
                classes.append(uiCommand.__class__.__name__)
        return ','.join(classes)

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

