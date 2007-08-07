import wx, wx.lib.colourselect

class ColorSelect(wx.lib.colourselect.ColourSelect):            
    def MakeBitmap(self):
        ''' This code was copied and adapted from ColourSelect.MakeBitmap. '''
        bdr = 8
        width, height = self.GetSize()

        # yes, this is weird, but it appears to work around a bug in wxMac
        if "wxMac" in wx.PlatformInfo and width == height:
            height -= 1

        bmp = wx.EmptyBitmap(width-bdr, height-bdr)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetFont(self.GetFont())
        label = self.GetLabel()
        # Just make a little colored bitmap
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()

        if label:
            # Add a label to it
            dc.SetTextForeground(self.colour)
            dc.DrawLabel(label, (0,0, width-bdr, height-bdr),
                         wx.ALIGN_CENTER)

        dc.SelectObject(wx.NullBitmap)
        return bmp