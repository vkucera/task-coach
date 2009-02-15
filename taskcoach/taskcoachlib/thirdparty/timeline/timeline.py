#! /usr/bin/env python
import wx

class TimeLine(wx.Panel):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', [])
        self.padding = kwargs.pop('padding', 3)
        self.adapter = kwargs.pop('adapter', DefaultAdapter())
        super(TimeLine, self).__init__(*args, **kwargs) 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize )
        self.OnSize(None)

    def Refresh(self):
        self.UpdateDrawing()
    
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self._buffer)

    def OnSize(self, event):
        # The buffer is initialized in here, so that the buffer is always
        # the same size as the Window.
        width, height = self.GetClientSizeTuple()
        if width <= 0 or height <= 0:
            return
        # Make new off-screen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._buffer = wx.EmptyBitmap(width, height)
        self.UpdateDrawing()

    def UpdateDrawing(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer)
        self.Draw(dc)
        
    def Draw(self, dc):
        ''' Draw the timeline on the device context. '''
        dc.BeginDrawing()
        brush = wx.Brush(wx.WHITE)
        dc.SetBackground(brush)
        dc.Clear()
        if self.model:
            self.min_start = float(self.adapter.start(self.model, recursive=True))
            self.max_stop = float(self.adapter.stop(self.model, recursive=True))
            self.length = self.max_stop - self.min_start
            self.width, self.height = dc.GetSize()
            self.LayoutParallelChildren(dc, self.model, 0, self.height)
        dc.EndDrawing()
        
    def DrawBox(self, dc, node, y, h):
        start, stop = self.adapter.start(node), self.adapter.stop(node)
        x = self.scaleX(start)
        w = self.scaleWidth(stop - start)
        dc.DrawRoundedRectangle(x, y, w, h, self.padding * 2)
        if h >= dc.GetTextExtent('ABC')[1]:
            dc.SetClippingRegion(x+1, y+1, w-2, h-2)
            dc.DrawText(self.adapter.label(node), x+2, y+2)
            dc.DestroyClippingRegion()
        seqHeight = min(20,h/(1+len(self.adapter.parallel_children(node))))    
        self.LayoutSequentialChildren(dc, node, y, seqHeight)
        self.LayoutParallelChildren(dc, node, y+seqHeight, h-seqHeight)
 
    def LayoutParallelChildren(self, dc, parent, y, h):
        children = self.adapter.parallel_children(parent)
        if not children:
            return
        childY = y
        h -= (len(children) - 1) # vertical space between children
        childHeight = h / len(children)
        for child in children:
            if childHeight >= self.padding:
                self.DrawBox(dc, child, childY, childHeight)
            childY += childHeight + 1

    def LayoutSequentialChildren(self, dc, parent, y, h):
        children = self.adapter.sequential_children(parent)
        if not children:
            return
        oldPen = dc.GetPen()
        dc.SetPen(wx.Pen(wx.BLACK, style=wx.DOT))
        for child in children:
            self.DrawBox(dc, child, y, h)
        dc.SetPen(oldPen)

    def scaleX(self, x):
        return self.scaleWidth(x - self.min_start)

    def scaleWidth(self, width):
        return (width / self.length) * self.width


class DefaultAdapter(object):
    def parallel_children(self, node):
        return node.parallel_children

    def sequential_children(self, node):
        return node.sequential_children

    def children(self, node):
        return self.parallel_children(node) + self.sequential_children(node)

    def start(self, node, recursive=False):
        starts = [node.start] 
        if recursive:
            starts.extend([self.start(child, True) \
                           for child in self.children(node)])
        return float(min(starts))

    def stop(self, node, recursive=False):
        stops = [node.stop]
        if recursive:
            stops.extend([self.stop(child, True) \
                          for child in self.children(node)])
        return float(max(stops))

    def label(self, node):
        return node.path

    
class TestApp(wx.App):
    ''' Basic application for holding the viewing Frame '''

    def __init__(self, size):
        self.size = size
        super(TestApp, self).__init__(0)

    def OnInit(self):
        ''' Initialise the application. '''
        wx.InitAllImageHandlers()
        self.frame = wx.Frame(None)
        self.frame.CreateStatusBar()
        model = self.get_model(self.size) 
        self.timeline = TimeLine(self.frame, model=model)
        self.frame.Show(True)
        return True

    def get_model(self, size):
        parallel_children, sequential_children = [], []
        if size > 0:
            parallel_children = [self.get_model(size-1) for i in range(size)]
        sequential_children = [Node('Seq 1', 30+10*size, 40+10*size, [], []),
                               Node('Seq 2', 80-10*size, 90-10*size, [], [])] 
        return Node('Node %d'%size, 0+5*size, 100-5*size, parallel_children, 
                    sequential_children)


class Node(object):
    def __init__(self, path, start, stop, subnodes, events):
        self.path = path
        self.start = start
        self.stop = stop
        self.parallel_children = subnodes 
        self.sequential_children = events

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r)'%(self.__class__.__name__, self.path, 
                                         self.start, self.stop, 
                                         self.parallel_children,
                                         self.sequential_children)
        

usage = 'timeline.py [size]'
        
def main():
    """Mainloop for the application"""
    import sys
    size = 3
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            print usage
        else:
            try:
                size = int(sys.argv[1])
            except ValueError:
                print usage
    else:
        app = TestApp(size)
        app.MainLoop()


if __name__ == "__main__":
    main()
