'''
Task Coach - Your friendly task manager
Copyright (C) 2010 Task Coach developers <developers@taskcoach.org>

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

from ultimatetreectrl import *
import wx

from taskcoachlib.i18n import _


class IconCell(CellBase):
    def __init__(self, *args, **kwargs):
        super(IconCell, self).__init__(*args, **kwargs)

        self.icon = None
        wx.EVT_PAINT(self, self.OnPaint)

    def GetIdentifier(self):
        return 'IconCell'

    def SetIcon(self, icon):
        self.icon = icon
        self.Refresh()

    def OnPaint(self, event):
        if self.icon is not None:
            dc = wx.PaintDC(self)
            w, h = self.GetSizeTuple()
            dc.DrawBitmap(wx.ArtProvider.GetBitmap(self.icon, wx.ART_FRAME_ICON, (16, 16)),
                          (w - 16) / 2, (h - 16) / 2, True)


class CategoryGrid(UltimateTreeCtrl):
    def __init__(self, parent, categories, taskList, iconProvider, *args, **kwargs):
        self.categories = categories
        self.taskList = taskList
        self.iconProvider = iconProvider

        self._maxDepth = 0

        super(CategoryGrid, self).__init__(parent, *args, **kwargs)

    def _adjust(self, indexPath):
        return (indexPath[0] - 1,) + indexPath[1:]

    def _findObject(self, objects, indexPath):
        obj = objects.rootItems()[indexPath[0]]
        for idx in indexPath[1:]:
            obj = obj.children()[idx]
        return obj

    def _findCategory(self, indexPath):
        return self._findObject(self.categories, indexPath)

    def _findTask(self, indexPath):
        return self._findObject(self.taskList, indexPath)

    def GetRootHeadersCount(self):
        return len(self.categories.rootItems()) + 1

    def GetHeaderChildrenCount(self, indexPath):
        if indexPath == (0,):
            return 0
        return len(self._findCategory(self._adjust(indexPath)).children())

    def GetHeaderText(self, indexPath):
        if indexPath == (0,):
            return _('Task')
        self._maxDepth = max(self._maxDepth, len(indexPath))
        return self._findCategory(self._adjust(indexPath)).subject()

    def GetRootCellsCount(self):
        return len(self.taskList.rootItems())

    def GetRowChildrenCount(self, indexPath):
        return len(self._findTask(indexPath).children())

    def GetRowHeight(self, indexPath):
        return max(20, 20 * self._maxDepth)

    def GetCellAttributes(self, indexPath, headerPath):
        task = self._findTask(indexPath)

        if headerPath == (0,):
            attrs = UltimateTreeCellAttributes(task.subject(),
                                               [wx.ArtProvider.GetBitmap(self.iconProvider(task, False),
                                                                         wx.ART_FRAME_ICON, (16, 16))])

            return attrs

    def GetCell(self, indexPath, headerPath):
        task = self._findTask(indexPath)
        category = self._findCategory(self._adjust(headerPath))

        cell = self.DequeueCell('IconCell', self.CreateIconCell)
        if category in task.categories():
            cell.SetIcon('checkmark_green_icon')
        else:
            cell.SetIcon('cross_red_icon')

        return cell

    def CreateTextCell(self, parent):
        return TextCell(parent, wx.ID_ANY)

    def CreateIconCell(self, parent):
        return IconCell(parent, wx.ID_ANY)

    def RefreshAllItems(self, count):
        p = self.SavePerspective()
        self._maxDepth = 0
        self.ReloadAll()
        self.FitHeader()
        self.LoadPerspective(p)
        self.Refresh()

    def RefreshItems(self, *args):
        self.RefreshAllItems(0)
