'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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


class ToolBar(wx.ToolBar, uicommand.UICommandContainer):
    def __init__(self, window, uiCommands, size=(32, 32)):
        super(ToolBar, self).__init__(window, 
            style=wx.TB_TEXT|wx.TB_NODIVIDER|wx.TB_FLAT)
        self.SetToolBitmapSize(size) 
        self.appendUICommands(uiCommands, self.commandNames())
        self.Realize()

    def commandNames(self):
        return ['open', 'save', None, 'undo', 'redo', None, 'cut', 'copy', 
            'paste', None, 'new', 'newsub', 'edit', 'delete', None,
            'toggletaskcompletion', None, 'starteffort', 
            'stopeffort', None, 'search']
        
    def AppendSeparator(self):
        ''' This little adapter is needed for 
        uicommand.UICommandContainer.appendUICommands'''
        self.AddSeparator()

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToToolBar(self)

