#!/usr/bin/env python

## Task Coach - Your friendly task manager
## Copyright (C) 2010 Task Coach developers <developers@taskcoach.org>

## Task Coach is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## Task Coach is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

This widget is yet another tree control implementation, in pure
Python. Rows may actually contain arbitrary wxPython controls. Column
headers may be hierarchical, with subheaders. It is virtual: at any
moment, only visible rows actually use up memory, allowing for any
number of rows (well, 2^31 at most, but this may change in the
future). It will soon provide Mac OS-like drag and drop: dropping a
row as a child or sibling of another row, with pretty visual cue.

The design is inspired from UIKit's UITableView.

"""

import wx


#=======================================
#{ Cells

class CellBase(wx.Panel):
    """
    Base class for rows.
    """

    def __init__(self, *args, **kwargs):
        super(CellBase, self).__init__(*args, **kwargs)

        wx.EVT_LEFT_UP(self, self._OnLeftUp)

    def _OnLeftUp(self, evt):
        self.GetParent()._OnCellClicked(self, evt)

    def GetIdentifier(self):
        """
        This method should return a string identifier for the cell's
        type. See L{DequeueRow}.
        """

        raise NotImplementedError

#}

#=======================================
#{ Events

wxEVT_COMMAND_ROW_SELECTED = wx.NewEventType()
EVT_ROW_SELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_SELECTED)

wxEVT_COMMAND_ROW_DESELECTED = wx.NewEventType()
EVT_ROW_DESELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_DESELECTED)

#}

#=======================================
#{ Style constants

ULTTREE_SINGLE_SELECTION        = 0x01

#}

#=======================================
#{ Tree control

class UltimateTreeCtrlContent(wx.ScrolledWindow):
    """
    Rows are identified by their index path. This is a tuple holding
    the path to the cell relative to the tree's top cells. For
    instance, (1, 3, 4) is the 5th child of the 4th child of the 2nd
    root row.
    """

    #====================
    #{ Data source

    def GetRootCellsCount(self):
        """Return the number of root cells"""
        raise NotImplementedError

    def GetRowChildrenCount(self, indexPath):
        """Return the number of children for the given row"""
        raise NotImplementedError

    def GetRowHeight(self, indexPath):
        """Return the height of a row. Variable height is supported."""
        return 30

    def GetRow(self, indexPath):
        """Return an actual row; see L{DequeueRow} for usage pattern."""
        raise NotImplementedError

    def GetRowBackgroundColour(self, indexPath):
        """Return the background colour of a row. Default is white."""
        return wx.WHITE

    #}

    #====================
    #{ Metrics

    def GetVerticalMargin(self):
        """Return the vertical margin, i.e. number of pixels between
        two rows. Default is 1."""
        return 1

    #}

    #====================
    #{ Reusable cells

    def DequeueRow(self, identifier, factory):
        """
        In order to avoid creating a new widget for each row, those
        widgets (subclasses of L{CellBase}) should be designed to be
        reusable. Each type of widget should have a unique identifier
        (see L{GetIdentifier}); for each identifier a queue of unused
        widgets is maintained. This method returns an unused widget
        for the given identifier, which you can then update according
        to the actual underlying data.

        The second argument is a factory used to create a new widget
        in case there is no unused one for this identifier.
        """
        if identifier in self._queues:
            queue = self._queues[identifier]
            if queue:
                cell = queue.pop()
                return cell

        cell = factory()

        return cell

    def _Queue(self, cell):
        # Mark a cell as unused and put it back in its queue.

        queue = self._queues.get(cell.GetIdentifier(), [])
        queue.append(cell)
        self._queues[cell.GetIdentifier()] = queue
        cell.Show(False)

    #}

    def __init__(self, *args, **kwargs):
        """
        @keyword treeStyle: And OR of UltimateTreeCtrl style constants.
        """

        self.__style = kwargs.pop('treeStyle', 0)

        super(UltimateTreeCtrl, self).__init__(*args, **kwargs)

        self._queues = dict()
        self._expanded = set()
        self._visibleCells = dict()
        self._buttons = list()
        self._selection = set()

        class _Sizer(wx.PySizer):
            def __init__(self, callback):
                self.__callback = callback
                super(_Sizer, self).__init__()

            def CalcMin(self):
                return (-1, self.__callback())

        self.SetScrollRate(10, 10)
        self.SetSizer(_Sizer(self._ComputeHeight))

        wx.EVT_SCROLLWIN(self, self._OnScroll)
        wx.EVT_SIZE(self, self._OnSize)
        wx.EVT_PAINT(self, self._OnPaint)

        wx.EVT_LEFT_UP(self, self._OnLeftUp)

    def Refresh(self):
        self._Relayout()
        super(UltimateTreeCtrl, self).Refresh()
        for cell in self._visibleCells.values():
            cell.Refresh()

    def Collapse(self, indexPath):
        """
        Collapse a row. Selected children will be deselected. Their
        own expanded state is not lost.
        """

        try:
            for path in self._ExpandedNode(indexPath):
                if path != indexPath and path in self._visibleCells:
                    if path in self._selection:
                        self._Deselect(path)
                    self._Queue(self._visibleCells[path])
                    del self._visibleCells[path]
            self._expanded.remove(indexPath)
        except KeyError:
            pass

        self.Refresh()
        self.SetSize(self.GetSize())

    def Expand(self, indexPath):
        """
        Expand a row. Expansion state of children is restored.
        """

        self._expanded.add(indexPath)
        self.Refresh()
        self.SetSize(self.GetSize())

    def Toggle(self, indexPath):
        """
        Toggle a row expansion status.
        """

        if indexPath in self._expanded:
            self.Collapse(indexPath)
        else:
            self.Expand(indexPath)

    def _Relayout(self):
        # Recompute visible rows

        self.Freeze()
        try:
            x0, y0 = self.GetViewStart()
            xu, yu = self.GetScrollPixelsPerUnit()
            x0 *= xu
            y0 *= yu
            w, h = self.GetClientSizeTuple()

            # XXXFIXME this should be optimized to avoid looping over
            # the whole mess

            currentPosition = 0
            for indexPath in self._Expanded():
                height = self.GetRowHeight(indexPath)

                if currentPosition + height < y0 or currentPosition >= y0 + h:
                    currentPosition += height + self.GetVerticalMargin()

                    if indexPath in self._visibleCells:
                        cell = self._visibleCells[indexPath]
                        self._Queue(cell)
                        del self._visibleCells[indexPath]

                    continue

                # At least partially visible cell. Move it and show it.

                if indexPath in self._visibleCells:
                    cell = self._visibleCells[indexPath]
                else:
                    cell = self.GetRow(indexPath)
                    self._visibleCells[indexPath] = cell

                    if indexPath in self._selection:
                        cell.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
                    else:
                        cell.SetBackgroundColour(self.GetRowBackgroundColour(indexPath))

                offset = 24 * len(indexPath)
                cell.SetDimensions(offset, currentPosition - y0, w - offset, height)
                cell.Layout()
                cell.Show()
                cell.Refresh()

                currentPosition += height + self.GetVerticalMargin()
        finally:
            self.Thaw()

    def _Select(self, indexPath):
        self._selection.add(indexPath)

        evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_SELECTED)
        evt.indexPath = indexPath
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

        if indexPath in self._visibleCells:
            cell = self._visibleCells[indexPath]
            cell.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

    def _Deselect(self, indexPath):
        try:
            self._selection.remove(indexPath)

            evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_DESELECTED)
            evt.indexPath = indexPath
            evt.SetEventObject(self)
            self.ProcessEvent(evt)
        except KeyError:
            pass
        else:
            if indexPath in self._visibleCells:
                cell = self._visibleCells[indexPath]
                cell.SetBackgroundColour(self.GetRowBackgroundColour(indexPath))

    def _Expanded(self):
        """
        Generator which iterates over all rows, avoiding children of
        collapsed rows.
        """
        for idx in xrange(self.GetRootCellsCount()):
            for child in self._ExpandedNode((idx,)):
                yield child

    def _ExpandedNode(self, indexPath):
        """
        Generator which iterates over all children of a row (including
        itself), avoiding children of collapsed rows.
        """

        yield indexPath

        if indexPath in self._expanded:
            for idx in xrange(self.GetRowChildrenCount(indexPath)):
                for child in self._ExpandedNode(indexPath + (idx,)):
                    yield child

    def _ComputeHeight(self):
        height = 0

        for indexPath in self._Expanded():
            height += self.GetRowHeight(indexPath) + self.GetVerticalMargin()

        if height:
            return height - self.GetVerticalMargin()

        return 0

    def _OnScroll(self, evt):
        self._Relayout()
        self.Refresh()

        evt.Skip()

    def _OnSize(self, evt):
        self._Relayout()

        evt.Skip()

    def _OnPaint(self, evt):
        # Draw lines between rows and expand buttons

        dc = wx.PaintDC(self)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        dc.BeginDrawing()
        try:
            render = wx.RendererNative.Get()

            for indexPath, cell in self._visibleCells.items():
                cx, cy = cell.GetPositionTuple()
                cw, ch = cell.GetClientSizeTuple()
                w, h = self.GetClientSizeTuple()

                if indexPath in self._selection:
                    col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
                else:
                    col = self.GetRowBackgroundColour(indexPath)

                dc.SetBrush(wx.Brush(col))
                dc.SetPen(wx.Pen(col))
                dc.DrawRectangle(0, cy, w, ch)

                if self.GetRowChildrenCount(indexPath):
                    rect = (24 * (len(indexPath) - 1) + 4,
                            cy + (ch - 16) / 2,
                            16,
                            16)

                    if indexPath in self._expanded:
                        render.DrawTreeItemButton(self, dc, rect,
                                                  wx.CONTROL_EXPANDED)
                    else:
                        render.DrawTreeItemButton(self, dc, rect)

                dc.SetPen(wx.BLACK_PEN)
                dc.DrawLine(0, cy + ch, w, cy + ch)
        finally:
            dc.EndDrawing()

    def _OnLeftUp(self, evt):
        self._ProcessLeftUp(evt.GetX(), evt.GetY(), evt.CmdDown())

    def _OnCellClicked(self, cell, evt):
        x, y = cell.GetPositionTuple()
        self._ProcessLeftUp(x + evt.GetX(), y + evt.GetY(), evt.CmdDown())

    def _ProcessLeftUp(self, xc, yc, ctrl):
        for indexPath, cell in self._visibleCells.items():
            if self.GetRowChildrenCount(indexPath):
                x, y = cell.GetPositionTuple()
                w, h = cell.GetClientSizeTuple()

                x, y, w, h = (24 * (len(indexPath) - 1) + 4,
                              y + (h - 16) / 2,
                              16,
                              16)

                if xc >= x and xc < x + w and \
                   yc >= y and yc < y + h:
                    self.Toggle(indexPath)
                    break
        else:
            for indexPath, cell in self._visibleCells.items():
                x, y = cell.GetPositionTuple()
                w, h = cell.GetClientSizeTuple()

                if yc >= y and yc < y + h:
                    if ctrl:
                        if indexPath in self._selection:
                            self._Deselect(indexPath)
                        else:
                            if self.__style & ULTTREE_SINGLE_SELECTION:
                                for path in set(self._selection):
                                    self._Deselect(path)
                            self._Select(indexPath)
                    else:
                        already = False
                        for path in set(self._selection):
                            if path == indexPath:
                                already = True
                            else:
                                self._Deselect(path)
                        if not already:
                            self._Select(indexPath)

                    self.Refresh()
                    break
            else:
                for indexPath in set(self._selection):
                    self._Deselect(indexPath)

#}


#==============================================================================
# Test

class TestCell(CellBase):
    def __init__(self, *args, **kwargs):
        super(TestCell, self).__init__(*args, **kwargs)

        self.__text = wx.StaticText(self, wx.ID_ANY, '')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__text, 0, wx.ALL|wx.ALIGN_CENTRE, 3)
        self.SetSizer(sizer)

    def SetLabel(self, label):
        self.__text.SetLabel(label)

    def GetIdentifier(self):
        return 'StaticText'


class Test(UltimateTreeCtrl):
    cells = ('Root', [('Cell #1', [('Subcell #1.1', [])]),
                      ('Cell #2', [('Subcell #2.1', [('Subsubcell #2.1.1', [])]),
                                   ('Subcell #2.2', [])]),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', []),
                      ('Dummy cell', [])])

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)

        EVT_ROW_SELECTED(self, self.OnCellSelected)
        EVT_ROW_DESELECTED(self, self.OnCellDeselected)

    def _Get(self, indexPath, data):
        obj = data
        for idx in indexPath:
            obj = obj[1][idx]
        return obj

    def GetRootCellsCount(self):
        return len(self.cells[1])

    def GetRowChildrenCount(self, indexPath):
        return len(self._Get(indexPath, self.cells)[1])

    def GetRowHeight(self, indexPath):
        return 50

    def GetRowBackgroundColour(self, indexPath):
        return wx.Colour(200, 100, 0)

    def GetRow(self, indexPath):
        cell = self.DequeueRow('StaticText', self.CreateCell)
        text = self._Get(indexPath, self.cells)[0]
        cell.SetLabel(text)

        return cell

    def OnCellSelected(self, evt):
        print 'Select', self._Get(evt.indexPath, self.cells)[0]

    def OnCellDeselected(self, evt):
        print 'Deselect', self._Get(evt.indexPath, self.cells)[0]

    def CreateCell(self):
        return TestCell(self, wx.ID_ANY)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, wx.ID_ANY, 'Test frame')

        self.tree = Test(self, wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)


class App(wx.App):
    def OnInit(self):
        Frame().Show()
        return True


if __name__ == '__main__':
    App(0).MainLoop()
