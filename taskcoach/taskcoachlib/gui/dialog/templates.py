'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.domain.task import Task
from taskcoachlib import widgets, persistence
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty.deltaTime import nlTimeExpression


class TimeExpressionEntry(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(TimeExpressionEntry, self).__init__(*args, **kwargs)

        self.__defaultColor = self.GetBackgroundColour()
        self.__invalidColor = wx.Colour(128, 0, 0)

        wx.EVT_TEXT(self, wx.ID_ANY, self._onTextChanged)

    @staticmethod
    def isValid(value):
        if value:
            try:
                res = nlTimeExpression.parseString(value)
            except:
                return False
            return 'calculatedTime' in res
        return True # Empty is valid.

    def _onTextChanged(self, event):
        event.Skip()
        self.SetBackgroundColour(self.__defaultColor if self.isValid(self.GetValue()) else self.__invalidColor)


class TemplatesDialog(widgets.Dialog):
    def __init__(self, settings, *args, **kwargs):
        self.settings = settings

        self._changing = False

        super(TemplatesDialog, self).__init__(*args, **kwargs)

        self.disableOK()

        self.SetSize(wx.Size(400, 350))
        self.CentreOnParent()

    def createInterior(self):
        return wx.Panel(self._panel, wx.ID_ANY)

    def fillInterior(self):
        # pylint: disable-msg=W0201
        self._templateList = wx.ListCtrl(self._interior, wx.ID_ANY, style=wx.LC_REPORT)
        self._templateList.InsertColumn(0, _('Template'))
        self._templateList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectionChanged)
        self._templateList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnSelectionChanged)

        self._templates = persistence.TemplateList(self.settings.pathToTemplatesDir())

        for task in self._templates.tasks():
            self._templateList.InsertStringItem(self._templateList.GetItemCount(), task.subject())

        self._templateList.SetColumnWidth(0, -1)

        self._btnDelete = wx.Button(self._interior, wx.ID_ANY, _("Delete"))
        self._btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self._btnDelete.Enable(False)

        self._btnUp = wx.BitmapButton(self._interior, wx.ID_ANY,
                                     wx.ArtProvider.GetBitmap('arrow_up_icon', size=(32, 32)))
        self._btnUp.Bind(wx.EVT_BUTTON, self.OnUp)
        self._btnUp.Enable(False)

        self._btnDown = wx.BitmapButton(self._interior, wx.ID_ANY,
                                       wx.ArtProvider.GetBitmap('arrow_down_icon', size=(32, 32)))
        self._btnDown.Bind(wx.EVT_BUTTON, self.OnDown)
        self._btnDown.Enable(False)

        self._btnAdd = wx.BitmapButton(self._interior, wx.ID_ANY,
                                       wx.ArtProvider.GetBitmap('symbol_plus_icon', size=(32, 32)))
        self._btnAdd.Bind(wx.EVT_BUTTON, self.OnAdd)

        self._editPanel = wx.Panel(self._interior)
        self._subjectCtrl = wx.TextCtrl(self._editPanel, wx.ID_ANY, u'')
        self._startDateTimeCtrl = TimeExpressionEntry(self._editPanel, wx.ID_ANY, u'')
        self._dueDateTimeCtrl = TimeExpressionEntry(self._editPanel, wx.ID_ANY, u'')
        self._completionDateTimeCtrl = TimeExpressionEntry(self._editPanel, wx.ID_ANY, u'')
        self._reminderCtrl = TimeExpressionEntry(self._editPanel, wx.ID_ANY, u'')
        self._editPanel.Enable(False)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.Add(self._templateList, 1, wx.EXPAND|wx.ALL, 3)
        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.Add(self._btnDelete, 0, wx.ALL, 3)
        vsz.Add(self._btnUp, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        vsz.Add(self._btnDown, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        vsz.Add(self._btnAdd, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        hsz.Add(vsz, 0, wx.ALL, 3)
        gsz = wx.FlexGridSizer(0, 2)
        gsz.Add(wx.StaticText(self._editPanel, wx.ID_ANY, _('Subject')))
        gsz.Add(self._subjectCtrl, 1, wx.EXPAND)
        gsz.Add(wx.StaticText(self._editPanel, wx.ID_ANY, _('Start date')))
        gsz.Add(self._startDateTimeCtrl, 1, wx.EXPAND)
        gsz.Add(wx.StaticText(self._editPanel, wx.ID_ANY, _('Due date')))
        gsz.Add(self._dueDateTimeCtrl, 1, wx.EXPAND)
        gsz.Add(wx.StaticText(self._editPanel, wx.ID_ANY, _('Completion date')))
        gsz.Add(self._completionDateTimeCtrl, 1, wx.EXPAND)
        gsz.Add(wx.StaticText(self._editPanel, wx.ID_ANY, _('Reminder')))
        gsz.Add(self._reminderCtrl, 1, wx.EXPAND)
        gsz.AddGrowableCol(1)
        self._editPanel.SetSizer(gsz)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(hsz, 1, wx.EXPAND|wx.ALL, 3)
        sz.Add(self._editPanel, 0, wx.EXPAND|wx.ALL, 3)
        self._interior.SetSizer(sz)

        for ctrl in [self._subjectCtrl, self._startDateTimeCtrl, self._dueDateTimeCtrl,
                     self._completionDateTimeCtrl, self._reminderCtrl]:
            wx.EVT_TEXT(ctrl, wx.ID_ANY, self.OnValueChanged)

    def _Check(self):
        for task in self._templates.tasks():
            for name in ['startdatetmpl', 'duedatetmpl', 'completiondatetmpl', 'remindertmpl']:
                if not TimeExpressionEntry.isValid(getattr(task, name)):
                    self.disableOK()
                    return False
        self.enableOK()
        return True

    def OnValueChanged(self, event):
        event.Skip()

        if len(self._GetSelection()) == 1 and not self._changing:
            task = self._templates.tasks()[self._GetSelection()[0]]
            task.setSubject(self._subjectCtrl.GetValue())
            for ctrl, name in [(self._startDateTimeCtrl, 'startdatetmpl'),
                               (self._dueDateTimeCtrl, 'duedatetmpl'),
                               (self._completionDateTimeCtrl, 'completiondatetmpl'),
                               (self._reminderCtrl, 'remindertmpl')]:
                setattr(task, name, ctrl.GetValue() or None)
        self._Check()

    def _GetSelection(self):
        selection = []
        idx = -1
        while True:
            idx = self._templateList.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if idx == -1:
                break
            selection.append(idx)
        return selection

    def OnSelectionChanged(self, event): # pylint: disable-msg=W0613
        self._changing = True
        try:
            selection = self._GetSelection()
            self._btnDelete.Enable(bool(selection))
            self._btnUp.Enable(len(selection) == 1 and selection != [0])
            self._btnDown.Enable(len(selection) == 1 and selection != [len(self._templates) - 1])
            self._editPanel.Enable(len(selection) == 1)
            if len(selection) == 1:
                task = self._templates.tasks()[selection[0]]
                self._subjectCtrl.SetValue(task.subject())
                self._startDateTimeCtrl.SetValue(task.startdatetmpl or u'')
                self._dueDateTimeCtrl.SetValue(task.duedatetmpl or u'')
                self._completionDateTimeCtrl.SetValue(task.completiondatetmpl or u'')
                self._reminderCtrl.SetValue(task.remindertmpl or u'')
            else:
                self._subjectCtrl.SetValue(u'')
                self._startDateTimeCtrl.SetValue(u'')
                self._dueDateTimeCtrl.SetValue(u'')
                self._completionDateTimeCtrl.SetValue(u'')
                self._reminderCtrl.SetValue(u'')
        finally:
            self._changing = False

    def OnDelete(self, event): # pylint: disable-msg=W0613
        selection = self._GetSelection()
        selection.sort(lambda x, y: -cmp(x, y))

        for idx in selection:
            self._templates.deleteTemplate(idx)
            self._templateList.DeleteItem(idx)

        self._Check()

    def OnUp(self, event): # pylint: disable-msg=W0613
        selection = self._GetSelection()[0]
        self._templates.swapTemplates(selection - 1, selection)
        self._templateList.SetStringItem(selection, 0, self._templates.tasks()[selection].subject())
        self._templateList.SetStringItem(selection - 1, 0, self._templates.tasks()[selection - 1].subject())
        self._templateList.SetItemState(selection, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
        self._templateList.SetItemState(selection - 1, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)

        self._Check()

    def OnDown(self, event): # pylint: disable-msg=W0613
        selection = self._GetSelection()[0]
        self._templates.swapTemplates(selection, selection + 1)
        self._templateList.SetStringItem(selection, 0, self._templates.tasks()[selection].subject())
        self._templateList.SetStringItem(selection + 1, 0, self._templates.tasks()[selection + 1].subject())
        self._templateList.SetItemState(selection, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
        self._templateList.SetItemState(selection + 1, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)

        self._Check()

    def OnAdd(self, event): # pylint: disable-msg=W0613
        task = Task(subject=_('New task template'))
        self._templates.addTemplate(task)
        self._templateList.InsertStringItem(self._templateList.GetItemCount(), task.subject())

        self._Check()

    def ok(self, event=None):
        self._templates.save()
        super(TemplatesDialog, self).ok(event=event)
