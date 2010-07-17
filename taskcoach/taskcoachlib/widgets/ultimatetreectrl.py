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

import wx, math


#=======================================
#{ Cells

class CellBase(wx.Panel):
    """
    Base class for cells.
    """

    def __init__(self, *args, **kwargs):
        super(CellBase, self).__init__(*args, **kwargs)

        wx.EVT_LEFT_UP(self, self._OnLeftUp)

    def _OnLeftUp(self, evt):
        self.GetParent().GetParent()._OnCellClicked(self, evt)

    def GetIdentifier(self):
        """
        This method should return a string identifier for the cell's
        type. See L{DequeueCell}.
        """

        raise NotImplementedError

#}

#=======================================
#{ Events

wxEVT_COMMAND_ROW_SELECTED = wx.NewEventType()
EVT_ROW_SELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_SELECTED)

wxEVT_COMMAND_ROW_DESELECTED = wx.NewEventType()
EVT_ROW_DESELECTED = wx.PyEventBinder(wxEVT_COMMAND_ROW_DESELECTED)

wxEVT_COMMAND_HEADER_LCLICKED = wx.NewEventType()
EVT_HEADER_LCLICKED = wx.PyEventBinder(wxEVT_COMMAND_HEADER_LCLICKED)

wxEVT_COMMAND_HEADER_RCLICKED = wx.NewEventType()
EVT_HEADER_RCLICKED = wx.PyEventBinder(wxEVT_COMMAND_HEADER_RCLICKED)

#}

#=======================================
#{ Style constants

ULTTREE_SINGLE_SELECTION        = 0x01

#}

def _shortenString(dc, s, w, margin=3):
    """
    Returns a shortened version of s that fits into w pixels (in
    width), adding an ellipsis in the middle of the string.
    """

    tw, th = dc.GetTextExtent(s)
    if tw + margin * 2 <= w:
        return s

    tw, th = dc.GetTextExtent('...')
    if tw + margin * 2 >= w:
        return ''

    m = int(len(s)/2)
    left = s[:m - 1]
    right = s[m + 1:]

    while True:
        r = left + '...' + right
        tw, th = dc.GetTextExtent(r)
        if tw + 2 * margin <= w:
            return r
        left = left[:-1]
        right = right[1:]


class Row(object):
    def __init__(self, x, y, w, h):
        super(Row, self).__init__()

        self.SetDimensions(x, y, w, h)

        self.cells = dict()

    def AddCell(self, indexPath, cell):
        self.cells[indexPath] = cell

    def Layout(self, tree):
        allPaths = self.cells.keys()
        heights = []

        count = tree.GetRootHeadersCount()

        for idx in xrange(count):
            heights.append(1.0 / max([len(p) for p in allPaths if p[0] == idx]))

        x = 0
        remain = self.w + self.x
        cw = 1.0 * (self.w + self.x) / count

        for idx in xrange(count):
            def _layout(indexPath, cell, cx, cy, cw, ch):
                h = int(math.ceil(self.h * heights[indexPath[0]]))
                if self.x > cx:
                    rect = (self.x, cy, cw - (self.x - cx), h)
                else:
                    rect = (cx, cy, cw, h)

                cell.SetDimensions(*rect)
                cell.Layout()

                xx = 0
                remain = cw
                count = tree.GetHeaderChildrenCount(indexPath)

                if count:
                    ccw = 1.0 * cw / count
                    for i in xrange(count):
                        if i == count -1:
                            w = remain
                        else:
                            w = int(math.ceil(ccw))

                        _layout(indexPath + (i,), self.cells[indexPath + (i,)],
                                cx + xx, cy + h, w, ch - h)

                        remain -= w
                        xx += w

            if idx == count - 1:
                w = remain
            else:
                w = int(math.ceil(cw))

            _layout((idx,), self.cells[(idx,)], x, self.y, w, self.h)

            remain -= w
            x += w

    def Refresh(self):
        for cell in self.cells.values():
            cell.Refresh()

    def Show(self, doShow=True):
        for cell in self.cells.values():
            cell.Show(doShow)

    def SetBackgroundColour(self, colour):
        for cell in self.cells.values():
            cell.SetBackgroundColour(colour)

    def SetDimensions(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

#=======================================
#{ Tree control

class UltimateTreeCtrl(wx.Panel):
    """
    Rows are identified by their index path. This is a tuple holding
    the path to the cell relative to the tree's top cells. For
    instance, (1, 3, 4) is the 5th child of the 4th child of the 2nd
    root row.
    """

    #====================
    #{ Data source

    def GetRootHeadersCount(self):
        """Return the number of root headers."""
        raise NotImplementedError

    def GetHeaderText(self, indexPath):
        """Return the title for the header."""
        raise NotImplementedError

    def GetHeaderChildrenCount(self, indexPath):
        """Return the number of children of the header."""
        raise NotImplementedError

    def GetRootCellsCount(self):
        """Return the number of root cells"""
        raise NotImplementedError

    def GetRowChildrenCount(self, indexPath):
        """Return the number of children for the given row"""
        raise NotImplementedError

    def GetRowHeight(self, indexPath):
        """Return the height of a row. Variable height is supported."""
        return 30

    def GetCell(self, indexPath, headerPath):
        """Return an actual cell; see L{DequeueCell} for usage pattern."""
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

    def DequeueCell(self, identifier, factory):
        """
        In order to avoid creating a new widget for each cell, those
        widgets (subclasses of L{CellBase}) should be designed to be
        reusable. Each type of widget should have a unique identifier
        (see L{GetIdentifier}); for each identifier a queue of unused
        widgets is maintained. This method returns an unused widget
        for the given identifier, which you can then update according
        to the actual underlying data.

        The second argument is a factory used to create a new widget
        in case there is no unused one for this identifier. It will be
        passed the new widget's parent as first argument.
        """
        if identifier in self._queues:
            queue = self._queues[identifier]
            if queue:
                cell = queue.pop()
                return cell

        cell = factory(self._contentView)

        return cell

    def _Queue(self, row):
        # Mark a cell as unused and put it back in its queue.

        for cell in row.cells.values():
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
        self._visibleRows = dict()
        self._buttons = list()
        self._selection = set()

        class _Sizer(wx.PySizer):
            def __init__(self, callback):
                self.__callback = callback
                super(_Sizer, self).__init__()

            def CalcMin(self):
                return (-1, self.__callback())

        self._headerView = wx.Panel(self, style=wx.FULL_REPAINT_ON_RESIZE)
        self._contentView = wx.ScrolledWindow(self)

        self._contentView.SetScrollRate(10, 10)
        self._contentView.SetSizer(_Sizer(self._ComputeHeight))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._headerView, 0, wx.EXPAND)
        sizer.Add(self._contentView, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.FitHeader()

        wx.EVT_SCROLLWIN(self._contentView, self._OnScrollContent)
        wx.EVT_PAINT(self._contentView, self._OnPaintContent)
        wx.EVT_LEFT_UP(self._contentView, self._OnLeftUpContent)
        wx.EVT_SIZE(self._contentView, self._OnSizeContent)

        wx.EVT_PAINT(self._headerView, self._OnPaintHeader)
        wx.EVT_LEFT_UP(self._headerView, self._OnLeftUpHeader)
        wx.EVT_RIGHT_UP(self._headerView, self._OnRightUpHeader)

    def Refresh(self):
        self._Relayout()
        super(UltimateTreeCtrl, self).Refresh()

        for cell in self._visibleRows.values():
            cell.Refresh()

    def Collapse(self, indexPath):
        """
        Collapse a row. Selected children will be deselected. Their
        own expanded state is not lost.
        """

        try:
            for path in self._ExpandedNode(indexPath):
                if path != indexPath and path in self._visibleRows:
                    if path in self._selection:
                        self._Deselect(path)
                    self._Queue(self._visibleRows[path])
                    del self._visibleRows[path]
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

    def FitHeader(self):
        count = self.GetRootHeadersCount()
        h = 0
        for idx in xrange(count):
            h = max(h, self._ComputeHeaderHeight((idx,)))

        self._headerView.SetSize((-1, h))

    def HeaderHitTest(self, x, y):
        for indexPath, xx, yy, w, h in self._bounds:
            if x >= xx and y >= yy and x < xx + w and y < yy + h:
                return indexPath
        return None

    def _headerHeight(self):
        if '__WXMAC__' in wx.PlatformInfo:
            return 16
        return 20

    def _ComputeHeaderHeight(self, indexPath):
        h = 0
        for idx in xrange(self.GetHeaderChildrenCount(indexPath)):
            h = max(h, self._ComputeHeaderHeight(indexPath + (idx,)))
        return h + self._headerHeight()

    def _Relayout(self):
        # Recompute visible rows

        self.Freeze()
        try:
            x0, y0 = self._contentView.GetViewStart()
            xu, yu = self._contentView.GetScrollPixelsPerUnit()
            x0 *= xu
            y0 *= yu
            w, h = self._contentView.GetClientSizeTuple()

            # XXXFIXME this should be optimized to avoid looping over
            # the whole mess

            currentPosition = 0
            for indexPath in self._Expanded():
                height = self.GetRowHeight(indexPath)

                if currentPosition + height < y0 or currentPosition >= y0 + h:
                    currentPosition += height + self.GetVerticalMargin()

                    if indexPath in self._visibleRows:
                        cell = self._visibleRows[indexPath]
                        self._Queue(cell)
                        del self._visibleRows[indexPath]

                    continue

                # At least partially visible row. Move it and show it.

                offset = 24 * len(indexPath)

                if indexPath in self._visibleRows:
                    row = self._visibleRows[indexPath]
                else:
                    row = Row(0, 0, 0, 0)

                    def queryCell(headerPath):
                        row.AddCell(headerPath, self.GetCell(indexPath, headerPath))
                        for i in xrange(self.GetHeaderChildrenCount(headerPath)):
                            queryCell(headerPath + (i,))

                    for idx in xrange(self.GetRootHeadersCount()):
                        queryCell((idx,))

                    self._visibleRows[indexPath] = row

                if indexPath in self._selection:
                    row.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
                else:
                    row.SetBackgroundColour(self.GetRowBackgroundColour(indexPath))

                row.SetDimensions(offset, currentPosition - y0, w - offset, height)
                row.Layout(self)
                row.Show()
                row.Refresh()

                currentPosition += height + self.GetVerticalMargin()
        finally:
            self.Thaw()

    def _Select(self, indexPath):
        self._selection.add(indexPath)

        evt = wx.PyCommandEvent(wxEVT_COMMAND_ROW_SELECTED)
        evt.indexPath = indexPath
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

        if indexPath in self._visibleRows:
            cell = self._visibleRows[indexPath]
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
            if indexPath in self._visibleRows:
                cell = self._visibleRows[indexPath]
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

    def _OnScrollContent(self, evt):
        self._Relayout()
        self.Refresh()

        evt.Skip()

    def _OnSizeContent(self, evt):
        self._Relayout()

        evt.Skip()

    def _OnPaintHeader(self, evt):
        dc = wx.PaintDC(self._headerView)
        dc.BeginDrawing()
        try:
            w, h = self._headerView.GetClientSizeTuple()

            self._bounds = []

            count = self.GetRootHeadersCount()

            if count:
                x = 0
                remain = w
                cw = 1.0 * w / count

                for idx in xrange(count):
                    if idx == count - 1:
                        w = remain
                    else:
                        w = int(math.ceil(cw))
                        remain -= w

                    self._DrawHeader(dc, (idx,), x, w)

                    x += w
        finally:
            dc.EndDrawing()

    def _DrawHeader(self, dc, indexPath, x, w):
        y = (len(indexPath) - 1) * self._headerHeight()

        self._bounds.append((indexPath, x, y, w, self._headerHeight()))

        txt = _shortenString(dc, self.GetHeaderText(indexPath), w)
        render = wx.RendererNative.Get()
        opts = wx.HeaderButtonParams()
        opts.m_labelText = txt
        render.DrawHeaderButton(self._headerView, dc, (int(x), y, int(w), self._headerHeight()),
                                wx.CONTROL_CURRENT, params=opts)

        count = self.GetHeaderChildrenCount(indexPath)

        if count:
            xx = 0
            remain = w
            cw = 1.0 * w / count

            for idx in xrange(count):
                if idx == count - 1:
                    w = remain
                else:
                    w = int(math.ceil(cw))
                    remain -= w

                self._DrawHeader(dc, indexPath + (idx,), x + xx, w)

                xx += w

    def _OnPaintContent(self, evt):
        # Draw lines between rows and expand buttons

        dc = wx.PaintDC(self._contentView)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()

        dc.BeginDrawing()
        try:
            render = wx.RendererNative.Get()

            for indexPath, row in self._visibleRows.items():
                w, h = self._contentView.GetClientSizeTuple()

                if indexPath in self._selection:
                    col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
                else:
                    col = self.GetRowBackgroundColour(indexPath)

                dc.SetBrush(wx.Brush(col))
                dc.SetPen(wx.Pen(col))
                dc.DrawRectangle(0, row.y, w, row.h)

                if self.GetRowChildrenCount(indexPath):
                    rect = (24 * (len(indexPath) - 1) + 4,
                            row.y + (row.h - 16) / 2,
                            16,
                            16)

                    if indexPath in self._expanded:
                        render.DrawTreeItemButton(self, dc, rect,
                                                  wx.CONTROL_EXPANDED)
                    else:
                        render.DrawTreeItemButton(self, dc, rect)

                dc.SetPen(wx.BLACK_PEN)
                dc.DrawLine(0, row.y + row.h, w, row.y + row.h)
        finally:
            dc.EndDrawing()

    def _OnLeftUpContent(self, evt):
        self._ProcessLeftUpContent(evt.GetX(), evt.GetY(), evt.CmdDown())

    def _OnLeftUpHeader(self, event):
        evt = wx.PyCommandEvent(wxEVT_COMMAND_HEADER_LCLICKED)
        evt.indexPath = self.HeaderHitTest(event.GetX(), event.GetY())
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

    def _OnRightUpHeader(self, event):
        evt = wx.PyCommandEvent(wxEVT_COMMAND_HEADER_RCLICKED)
        evt.indexPath = self.HeaderHitTest(event.GetX(), event.GetY())
        evt.SetEventObject(self)
        self.ProcessEvent(evt)

    def _OnCellClicked(self, cell, evt):
        x, y = cell.GetPositionTuple()
        self._ProcessLeftUpContent(x + evt.GetX(), y + evt.GetY(), evt.CmdDown())

    def _ProcessLeftUpContent(self, xc, yc, ctrl):
        for indexPath, row in self._visibleRows.items():
            if self.GetRowChildrenCount(indexPath):
                x, y, w, h = (24 * (len(indexPath) - 1) + 4,
                              row.y + (row.h - 16) / 2,
                              16,
                              16)

                if xc >= x and xc < x + w and \
                   yc >= y and yc < y + h:
                    self.Toggle(indexPath)
                    break
        else:
            for indexPath, row in self._visibleRows.items():
                if yc >= row.y and yc < row.y + row.h:
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
        sizer.Add(self.__text, 0, wx.ALL, 3)
        self.SetSizer(sizer)

        wx.EVT_PAINT(self, self.OnPaint)

    def OnPaint(self, evt):
        evt.Skip()

        dc = wx.PaintDC(self)
        w, h = self.GetSizeTuple()
        dc.SetPen(wx.GREEN_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, w, h)

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

    _headers = ('Root', [ ('Task', []),
                          ('Cat1',
                           [('SCat 1.1', []),
                            ('SCat 1.2', [])]),
                          ('Cat2',
                           []),
                          ('Cat3',
                           [('Scat 3.1', []),
                            ('SCat 3.2',
                             [('Scat 3.2.1', []),
                              ('Scat 3.2.2', [])])])])

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)

        EVT_ROW_SELECTED(self, self.OnCellSelected)
        EVT_ROW_DESELECTED(self, self.OnCellDeselected)
        EVT_HEADER_LCLICKED(self, self.OnHeaderLeftClicked)
        EVT_HEADER_RCLICKED(self, self.OnHeaderRightClicked)

    def _Get(self, indexPath, data):
        obj = data
        for idx in indexPath:
            obj = obj[1][idx]
        return obj

    def GetRootHeadersCount(self):
        return len(self._headers[1])

    def GetHeaderText(self, indexPath):
        return self._Get(indexPath, self._headers)[0]

    def GetHeaderChildrenCount(self, indexPath):
        return len(self._Get(indexPath, self._headers)[1])

    def GetRootCellsCount(self):
        return len(self.cells[1])

    def GetRowChildrenCount(self, indexPath):
        return len(self._Get(indexPath, self.cells)[1])

    def GetRowHeight(self, indexPath):
        return 150

    def GetRowBackgroundColour(self, indexPath):
        return wx.Colour(200, 100, 0)

    def GetCell(self, indexPath, headerPath):
        cell = self.DequeueCell('StaticText', self.CreateCell)
        text = self._Get(indexPath, self.cells)[0]
        cat = self._Get(headerPath, self._headers)[0]
        cell.SetLabel('%s (%s)' % (text, cat))

        return cell

    def OnCellSelected(self, evt):
        print 'Select', self._Get(evt.indexPath, self.cells)[0]

    def OnCellDeselected(self, evt):
        print 'Deselect', self._Get(evt.indexPath, self.cells)[0]

    def OnHeaderLeftClicked(self, evt):
        if evt.indexPath:
            print 'Click header', self._Get(evt.indexPath, self._headers)[0]
        else:
            print 'Click headers'

    def OnHeaderRightClicked(self, evt):
        if evt.indexPath:
            print 'Right click header', self._Get(evt.indexPath, self._headers)[0]
        else:
            print 'Right click headers'

    def CreateCell(self, parent):
        return TestCell(parent, wx.ID_ANY)


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
