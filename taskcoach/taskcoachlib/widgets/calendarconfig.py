'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

import wx, dialog
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty.wxScheduler import wxSCHEDULER_DAILY, wxSCHEDULER_WEEKLY, \
     wxSCHEDULER_MONTHLY, wxSCHEDULER_HORIZONTAL, wxSCHEDULER_VERTICAL
import wx.lib.colourselect as csel


class CalendarConfigDialog(dialog.Dialog):
    VIEWTYPES = [wxSCHEDULER_DAILY, wxSCHEDULER_WEEKLY, wxSCHEDULER_MONTHLY]
    VIEWORIENTATIONS = [wxSCHEDULER_HORIZONTAL, wxSCHEDULER_VERTICAL]
    VIEWFILTERS = [(False, False, False), (False, True, False), (True, False, False), (True, True, False), (True, True, True)]

    def __init__(self, settings, settingsSection, *args, **kwargs):
        self._settings = settings
        self._settingsSection = settingsSection
        super(CalendarConfigDialog, self).__init__(*args, **kwargs)

    def createInterior(self):
        return wx.Panel(self._panel)

    def indexOf(self, lst, v):
        for idx, value in enumerate(lst):
            if v == value:
                return idx

    def indexOfViewType(self, type_):
        return self.indexOf(self.VIEWTYPES, type_)

    def indexOfViewOrientation(self, orientation):
        return self.indexOf(self.VIEWORIENTATIONS, orientation)

    def indexOfViewFilter(self, flt):
        return self.indexOf(self.VIEWFILTERS, flt)

    def addItem(self, sizer, description, item1, item2, helpText):
        sizer.Add(wx.StaticText(self._interior, wx.ID_ANY, description), 0, wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 3)
        sizer.Add(item1, 0, wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 3)
        sizer.Add(item2, 0, wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 3)
        sizer.Add(wx.StaticText(self._interior, wx.ID_ANY, helpText), 0, wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 3)

    def fillInterior(self):
        # pylint: disable-msg=W0201
        sizer = wx.FlexGridSizer(0, 4)

        self._spanCount = wx.SpinCtrl(self._interior, wx.ID_ANY, '1')
        self._spanType = wx.Choice(self._interior, wx.ID_ANY)
        self._spanType.Append(_('Day(s)'))
        self._spanType.Append(_('Week(s)'))
        self._spanType.Append(_('Month'))

        self._spanCount.SetValue(self._settings.getint(self._settingsSection, 'periodcount'))
        self._spanType.SetSelection(self.indexOfViewType(self._settings.getint(self._settingsSection, 'viewtype')))

        self._type = wx.Choice(self._interior, wx.ID_ANY)
        self._type.Append(_('Horizontal'))
        self._type.Append(_('Vertical'))

        self._type.SetSelection(self.indexOfViewOrientation(self._settings.getint(self._settingsSection, 'vieworientation')))

        self._display = wx.Choice(self._interior, wx.ID_ANY)
        self._display.Append(_('Start and due date'))
        self._display.Append(_('Start date'))
        self._display.Append(_('Due date'))
        self._display.Append(_('All but unplanned'))
        self._display.Append(_('All'))

        self._display.SetSelection(self.indexOfViewFilter((self._settings.getboolean(self._settingsSection, 'shownostart'),
                                                           self._settings.getboolean(self._settingsSection, 'shownodue'),
                                                           self._settings.getboolean(self._settingsSection, 'showunplanned'))))

        self._shownow = wx.CheckBox(self._interior, wx.ID_ANY, '')
        self._shownow.SetValue(self._settings.getboolean(self._settingsSection, 'shownow'))

        hcolor = self._settings.get(self._settingsSection, 'highlightcolor')
        if not hcolor:
            # The highlight colour is too dark
            color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT )
            color = wx.Colour(int((color.Red() + 255) / 2),
                              int((color.Green() + 255) / 2),
                              int((color.Blue() + 255) / 2))
        else:
            color = wx.Colour(*tuple(map(int, hcolor.split(',')))) # pylint: disable-msg=W0141
        self._highlight = csel.ColourSelect(self._interior, wx.ID_ANY, size=(100, 20))
        self._highlight.SetColour(color)

        self._fontsize = wx.SpinCtrl(self._interior, wx.ID_ANY, self._settings.get(self._settingsSection, 'fontsize'))

        self.addItem(sizer, _('Span'), self._spanCount, self._spanType, _('Kind of period displayed and its count'))
        self.addItem(sizer, _('Orientation'), (0, 0), self._type, _('Calendar orientation'))
        self.addItem(sizer, _('Tasks'), (0, 0), self._display, _('Mandatory attributes of displayed tasks'))
        self.addItem(sizer, _('Show now'), (0, 0), self._shownow, _('Draw a line showing the current time'))
        self.addItem(sizer, _('Highlight'), (0, 0), self._highlight, _('Color used to highlight the current day'))
        self.addItem(sizer, _('Font size'), (0, 0), self._fontsize, _('Size of the font used to draw the task subject'))

        sizer.AddGrowableCol(3)

        self._interior.SetSizer(sizer)

        wx.EVT_CHOICE(self._spanType, wx.ID_ANY, self.OnChangeViewType)

    def OnChangeViewType(self, event): # pylint: disable-msg=W0613
        if self.VIEWTYPES[self._spanType.GetSelection()] == wxSCHEDULER_MONTHLY:
            self._spanCount.SetValue(1)
            self._spanCount.Enable(False)
        else:
            self._spanCount.Enable(True)

    def ok(self, event=None):
        self._settings.set(self._settingsSection, 'periodcount', str(self._spanCount.GetValue()))
        self._settings.set(self._settingsSection, 'viewtype', str(self.VIEWTYPES[self._spanType.GetSelection()]))
        self._settings.set(self._settingsSection, 'vieworientation', str(self.VIEWORIENTATIONS[self._type.GetSelection()]))
        shownostart, shownodue, showunplanned = self.VIEWFILTERS[self._display.GetSelection()]
        self._settings.set(self._settingsSection, 'shownostart', str(shownostart))
        self._settings.set(self._settingsSection, 'shownodue', str(shownodue))
        self._settings.set(self._settingsSection, 'showunplanned', str(showunplanned))
        self._settings.set(self._settingsSection, 'shownow', str(self._shownow.GetValue()))
        self._settings.set(self._settingsSection, 'fontsize', str(self._fontsize.GetValue()))

        color = self._highlight.GetColour()
        self._settings.set(self._settingsSection, 'highlightcolor', '%d,%d,%d' % (color.Red(), color.Green(), color.Blue()))

        self.EndModal(wx.ID_OK)
        super(CalendarConfigDialog, self).ok(event)
