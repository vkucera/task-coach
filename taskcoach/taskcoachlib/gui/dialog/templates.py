'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

import wx, os
from taskcoachlib import widgets, persistence
from taskcoachlib.i18n import _


class TemplatesDialog(widgets.Dialog):
    def __init__(self, settings, *args, **kwargs):
        self.settings = settings
        self.tasks = list()
        self.toDelete = list()

        super(TemplatesDialog, self).__init__(*args, **kwargs)

        self.disableOK()

        self.SetSize(wx.Size(400, 350))
        self.CentreOnParent()

    def createInterior(self):
        return wx.Panel(self, wx.ID_ANY)

    def fillInterior(self):
        self._templateList = wx.ListCtrl(self._interior, wx.ID_ANY, style=wx.LC_REPORT)
        self._templateList.InsertColumn(0, _('Template'))
        self._templateList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectionChanged)
        self._templateList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnSelectionChanged)

        for name in os.listdir(self.settings.pathToTemplatesDir()):
            if name.endswith('.tsktmpl'):
                filename = os.path.join(self.settings.pathToTemplatesDir(), name)
                task = persistence.TemplateXMLReader(file(filename, 'rU')).read()
                self.tasks.append((task, filename))

        self.tasks.sort(key=lambda item: item[0].subject())
        for task, filename in self.tasks:
            self._templateList.InsertStringItem(self._templateList.GetItemCount(), task.subject())

        self._templateList.SetColumnWidth(0, -1)

        self._btnDelete = wx.Button(self._interior, wx.ID_ANY, _("Delete"))
        self._btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self._btnDelete.Enable(False)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.Add(self._templateList, 1, wx.EXPAND|wx.ALL, 3)
        hsz.Add(self._btnDelete, 0, wx.ALL, 3)
        self._interior.SetSizer(hsz)

    def _GetSelection(self):
        selection = []
        idx = -1
        while True:
            idx = self._templateList.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if idx == -1:
                break
            selection.append(idx)
        return selection

    def OnSelectionChanged(self, event):
        self._btnDelete.Enable(bool(self._GetSelection()))

    def OnDelete(self, event):
        selection = self._GetSelection()
        selection.sort(lambda x, y: -cmp(x, y))

        for idx in selection:
            self._templateList.DeleteItem(idx)
            self.toDelete.append(self.tasks[idx])
            del self.tasks[idx]

        self.enableOK()

    def ok(self, event=None):
        for task, filename in self.toDelete:
            os.remove(filename)
        super(TemplatesDialog, self).ok(event=event)
