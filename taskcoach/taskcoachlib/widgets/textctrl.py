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

from taskcoachlib import i18n, operating_system
import wx
import webbrowser


UNICODE_CONTROL_CHARACTERS_TO_WEED = {}
for ordinal in range(0x20):
    if chr(ordinal) not in '\t\r\n':
        UNICODE_CONTROL_CHARACTERS_TO_WEED[ordinal] = None


class BaseTextCtrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super(BaseTextCtrl, self).__init__(parent, -1, *args, **kwargs)
        self.__data = None
        if operating_system.isGTK():
            self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
            self.__initial_value = self.GetValue()
            self.__undone_value = None

    def GetValue(self, *args, **kwargs):
        value = super(BaseTextCtrl, self).GetValue(*args, **kwargs)
        # Don't allow unicode control characters:
        return value.translate(UNICODE_CONTROL_CHARACTERS_TO_WEED)

    def SetValue(self, *args, **kwargs):
        super(BaseTextCtrl, self).SetValue(*args, **kwargs)
        if operating_system.isGTK():
            self.__initial_value = self.GetValue()

    def SetData(self, data):
        self.__data = data

    def GetData(self):
        return self.__data

    def on_key_down(self, event):
        ''' Check whether the user is pressing Ctrl-Z (or Ctrl-Y) and if so, 
            undo (or redo) the editing. '''
        if event.GetKeyCode() == ord('Z') and event.ControlDown() and \
           self.GetValue() != self.__initial_value:
            insertion_point = self.GetInsertionPoint()
            self.__undone_value = self.GetValue()
            super(BaseTextCtrl, self).SetValue(self.__initial_value)
            insertion_point = min(insertion_point, self.GetLastPosition())
            self.SetInsertionPoint(insertion_point)
        elif event.GetKeyCode() == ord('Y') and event.ControlDown() and \
           self.GetValue() != self.__undone_value and \
           (self.__undone_value is not None):
            insertion_point = self.GetInsertionPoint()
            super(BaseTextCtrl, self).SetValue(self.__undone_value)
            self.__undone_value = None
            insertion_point = min(insertion_point, self.GetLastPosition())
            self.SetInsertionPoint(insertion_point)
        else:
            event.Skip()


class SingleLineTextCtrl(BaseTextCtrl):
    pass


class MultiLineTextCtrl(BaseTextCtrl):
    CheckSpelling = True
    
    def __init__(self, parent, text='', *args, **kwargs):
        kwargs['style'] = kwargs.get('style', 0) | wx.TE_MULTILINE
        if not i18n.currentLanguageIsRightToLeft():
            # Using wx.TE_RICH will remove the RTL specific menu items
            # from the right-click menu in the TextCtrl, so we don't use 
            # wx.TE_RICH if the language is RTL.
            kwargs['style'] |= wx.TE_RICH | wx.TE_AUTO_URL
        super(MultiLineTextCtrl, self).__init__(parent, *args, **kwargs)
        self.__initializeText(text)
        self.Bind(wx.EVT_TEXT_URL, self.onURLClicked)
        try:
            self.__webbrowser = webbrowser.get()
        except:
            self.__webbrowser = None
        self.MacCheckSpelling(self.CheckSpelling)
        
    def onURLClicked(self, event):
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.ButtonDown() and self.__webbrowser:
            url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
            try:
                self.__webbrowser.open(url)
            except Exception, message:
                wx.MessageBox(unicode(message), i18n._('Error opening URL'))
     
    def __initializeText(self, text):
        self.AppendText(text)
        self.SetInsertionPoint(0)


class StaticTextWithToolTip(wx.StaticText):
    def __init__(self, *args, **kwargs):
        super(StaticTextWithToolTip, self).__init__(*args, **kwargs)
        label = kwargs['label']
        self.SetToolTip(wx.ToolTip(label))
