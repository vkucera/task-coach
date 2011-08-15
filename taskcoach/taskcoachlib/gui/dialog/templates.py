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
                return False # pylint: disable-msg=W0702
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

    def appendTemplate(self, parentItem, task):
        item = self._templateList.AppendItem(parentItem, task.subject(), data=wx.TreeItemData(task))
        for child in task.children():
            self.appendTemplate(item, child)
        return item

    def fillInterior(self):
        # pylint: disable-msg=W0201
        self._templateList = wx.TreeCtrl(self._interior, wx.ID_ANY, style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE)
        self._templateList.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)

        self._templates = persistence.TemplateList(self.settings.pathToTemplatesDir())

        self._root = self._templateList.AddRoot('Root')
        for task in self._templates.tasks():
            item = self.appendTemplate(self._root, task)
            if '__WXMAC__' in wx.PlatformInfo:
                # See http://trac.wxwidgets.org/ticket/10085
                self._templateList.SetItemText(item, task.subject())

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
        self._subjectCtrl = wx.TextCtrl(self._editPanel)
        self._startDateTimeCtrl = TimeExpressionEntry(self._editPanel)
        self._dueDateTimeCtrl = TimeExpressionEntry(self._editPanel)
        self._completionDateTimeCtrl = TimeExpressionEntry(self._editPanel)
        self._reminderCtrl = TimeExpressionEntry(self._editPanel)
        self._editPanel.Enable(False)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.Add(self._templateList, 1, wx.EXPAND|wx.ALL, 3)
        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.Add(self._btnDelete, 0, wx.ALL, 3)
        vsz.Add(self._btnUp, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        vsz.Add(self._btnDown, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        vsz.Add(self._btnAdd, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        hsz.Add(vsz, 0, wx.ALL, 3)
        gsz = wx.FlexGridSizer(0, 2, 2, 2)
        ctrlOptions = dict(proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTRE_VERTICAL)
        textOptions = dict(flag=wx.ALIGN_CENTRE_VERTICAL)
        gsz.Add(wx.StaticText(self._editPanel, label=_('Subject')), **textOptions)
        gsz.Add(self._subjectCtrl, **ctrlOptions)
        gsz.Add(wx.StaticText(self._editPanel, label=_('Start date')), **textOptions)
        gsz.Add(self._startDateTimeCtrl, **ctrlOptions)
        gsz.Add(wx.StaticText(self._editPanel, label=_('Due date')), **textOptions)
        gsz.Add(self._dueDateTimeCtrl, **ctrlOptions)
        gsz.Add(wx.StaticText(self._editPanel, label=_('Completion date')), **textOptions)
        gsz.Add(self._completionDateTimeCtrl, **ctrlOptions)
        gsz.Add(wx.StaticText(self._editPanel, label=_('Reminder')), **textOptions)
        gsz.Add(self._reminderCtrl, **ctrlOptions)
        gsz.AddGrowableCol(1)
        self._editPanel.SetSizer(gsz)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(hsz, 1, wx.EXPAND|wx.ALL, 3)
        sz.Add(self._editPanel, 0, wx.EXPAND|wx.ALL, 3)
        self._interior.SetSizer(sz)

        for ctrl in (self._subjectCtrl, self._startDateTimeCtrl, self._dueDateTimeCtrl,
                     self._completionDateTimeCtrl, self._reminderCtrl):
            ctrl.Bind(wx.EVT_TEXT, self.OnValueChanged)

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

        if self._GetSelection().IsOk() and not self._changing:
            task = self._templateList.GetItemData(self._GetSelection()).GetData()
            task.setSubject(self._subjectCtrl.GetValue())
            for ctrl, name in [(self._startDateTimeCtrl, 'startdatetmpl'),
                               (self._dueDateTimeCtrl, 'duedatetmpl'),
                               (self._completionDateTimeCtrl, 'completiondatetmpl'),
                               (self._reminderCtrl, 'remindertmpl')]:
                setattr(task, name, ctrl.GetValue() or None)
        self._Check()

    def _GetSelection(self):
        return self._templateList.GetSelection()

    def OnSelectionChanged(self, event): # pylint: disable-msg=W0613
        self._changing = True
        try:
            selection = self._GetSelection()
            selectionAtRoot = False
            if selection.IsOk():
                selectionAtRoot = (self._templateList.GetItemParent(selection) == self._root)
            self._btnDelete.Enable(selectionAtRoot)
            self._btnUp.Enable(selectionAtRoot and self._templateList.GetPrevSibling(selection).IsOk())
            self._btnDown.Enable(selectionAtRoot and self._templateList.GetNextSibling(selection).IsOk())
            self._editPanel.Enable(selection.IsOk())
            self._editPanel.Enable(selection.IsOk())
            if selection.IsOk():
                task = self._templateList.GetItemData(selection).GetData()
                if task is None:
                    self._subjectCtrl.SetValue(u'')
                    self._startDateTimeCtrl.SetValue(u'')
                    self._dueDateTimeCtrl.SetValue(u'')
                    self._completionDateTimeCtrl.SetValue(u'')
                    self._reminderCtrl.SetValue(u'')
                else:
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
        task = self._templateList.GetItemData(self._GetSelection()).GetData()
        index = self._templates.tasks().index(task)
        self._templates.deleteTemplate(index)
        self._templateList.Delete(self._GetSelection())
        self._Check()

    def OnUp(self, event): # pylint: disable-msg=W0613
        selection = self._GetSelection()
        prev = self._templateList.GetPrevSibling(selection)
        prev = self._templateList.GetPrevSibling(prev)
        task = self._templateList.GetItemData(selection).GetData()
        self._templateList.Delete(selection)
        if prev.IsOk():
            item = self._templateList.InsertItem(self._root, prev, task.subject(), data=wx.TreeItemData(task))
        else:
            item = self._templateList.PrependItem(self._root, task.subject(), data=wx.TreeItemData(task))
        for child in task.children():
            self.appendTemplate(item, child)
        index = self._templates.tasks().index(task)
        self._templates.swapTemplates(index - 1, index)
        self._templateList.SelectItem(item)
        self._Check()

    def OnDown(self, event): # pylint: disable-msg=W0613
        selection = self._GetSelection()
        next = self._templateList.GetNextSibling(selection)
        task = self._templateList.GetItemData(selection).GetData()
        self._templateList.Delete(selection)
        item = self._templateList.InsertItem(self._root, next, task.subject(), data=wx.TreeItemData(task))
        for child in task.children():
            self.appendTemplate(item, task)
        index = self._templates.tasks().index(task)
        self._templates.swapTemplates(index, index + 1)
        self._templateList.SelectItem(item)
        self._Check()

    def OnAdd(self, event): # pylint: disable-msg=W0613
        task = Task(subject=_('New task template'))
        self._templates.addTemplate(task)
        self.appendTemplate(self._root, task)

        self._Check()

    def ok(self, event=None):
        self._templates.save()
        super(TemplatesDialog, self).ok(event=event)
