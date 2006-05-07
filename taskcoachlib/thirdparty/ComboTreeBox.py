''' ComboTreeBox provides a ComboBox that pops up a tree instead of
    a list. 

    Not implemented: style=wx.CB_SORT 
    Supported platforms: wxMSW and wxMAC natively, wxGTK by means of a
                         workaround

    Author: Frank Niessink <frank@niessink.com>
    Copyright 2006, Frank Niessink
    License: wxWidgets license
    Version: 0.4
    Date: May 7, 2006
'''

import wx


class PopupFrame(wx.MiniFrame):
    ''' This is the frame that is popped up by ComboTreeBox. It contains
        the tree of items that the user can select one item from. Upon
        selection, or when focus is lost, the frame is hidden. '''

    def __init__(self, parent):
        super(PopupFrame, self).__init__(parent,
            style=wx.DEFAULT_FRAME_STYLE & wx.FRAME_FLOAT_ON_PARENT &
                  ~(wx.RESIZE_BORDER | wx.CAPTION)) 
        self._createInterior()
        self._bindEventHandlers()

    def _createInterior(self):
        self._tree = wx.TreeCtrl(self, 
            style=wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS)
        self._tree.AddRoot('Hidden root node')
        frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        frameSizer.Add(self._tree, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(frameSizer)

    def _bindEventHandlers(self):
        # On wxMac, the kill focus event doesn't work, but the
        # deactivate event does:
        if '__WXMAC__' in wx.PlatformInfo:
            self.Bind(wx.EVT_ACTIVATE, self.OnDeactivate)
        else:
            self._tree.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self._tree.Bind(wx.EVT_CHAR, self.OnChar)

    def OnKillFocus(self, event):
        # Hide the frame so it can be popped up again later.
        self.Hide()
        self.GetParent().SetFocus()
        event.Skip()

    def OnDeactivate(self, event):
        if not event.GetActive(): # Deactivate
            self.Hide()
            wx.CallAfter(self.GetParent().SetFocus)
        event.Skip()

    def OnActivate(self, event):
        self.Hide()
        self.GetParent().SetFocus()
        if self._tree.GetSelection() == self._tree.GetRootItem():
            text = ''
        else:
            text = self._tree.GetItemText(event.GetItem())
        self.GetParent().SetValueAndPostEvent(text)

    def OnChar(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Hide()
        event.Skip()

    def Show(self, *args, **kwargs):
        wx.CallAfter(self._tree.SetFocus)
        super(PopupFrame, self).Show(*args, **kwargs)

    def GetTree(self):
        return self._tree


class _BaseComboTreeBox(object):
    def __init__(self, *args, **kwargs):
        style = kwargs.pop('style', 0)
        if style & wx.CB_READONLY:
            style &= ~wx.CB_READONLY # We manage readonlyness ourselves
            self._readOnly = True
        else:
            self._readOnly = False
        super(_BaseComboTreeBox, self).__init__(style=style, *args, **kwargs)
        self._createInterior()
        self._bindEventHandlers()

    def _createInterior(self):
        self._popupFrame = PopupFrame(self)
        self._tree = self._popupFrame.GetTree()

    def _bindEventHandlers(self):
        self._text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self._button.Bind(wx.EVT_BUTTON, self.OnMouseClick)
        for eventType in self._buttonEventTypesToBind():
            self._button.Bind(eventType, self.OnMouseClick)

    def OnMouseClick(self, event):
        self.Popup()
        # We don't call event.Skip() to prevent popping up the
        # ComboBox's own box.

    def OnKeyDown(self, event):
        if (event.AltDown() or event.MetaDown()) and \
                event.GetKeyCode() == wx.WXK_DOWN:
            self.Popup()
        else:
            event.Skip()

    def Popup(self):
        comboBoxSize = self.GetSize()
        x, y = self.GetParent().ClientToScreen(self.GetPosition())
        y += comboBoxSize[1]
        width = comboBoxSize[0]
        height = 300
        self._popupFrame.SetDimensions(x, y, width, height)
        # On wxGTK, when the Combobox width has been increased a call 
        # to SetMinSize is needed to force a resize of the popupFrame: 
        self._popupFrame.SetMinSize((width, height)) 
        self._popupFrame.Show()
 
    def GetTree(self):
        return self._popupFrame.GetTree()

    def PostComboBoxSelectedEvent(self, text):
        event = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, 
                                self.GetId())
        event.SetString(text)
        self.GetEventHandler().ProcessEvent(event)

    def SetValueAndPostEvent(self, text):
        ''' Simulate selection of an item by the user. '''
        self._text.SetValue(text)
        self.PostComboBoxSelectedEvent(text)

    # The following methods are all part of the ComboBox API (actually
    # the ControlWithItems API) and have been adapted to take TreeItemIds 
    # as parameter and return TreeItemIds, rather than indices.

    def Append(self, itemText, parent=None, clientData=None):
        if parent is None:
            parent = self._tree.GetRootItem()
        return self._tree.AppendItem(parent, itemText, 
                                     data=wx.TreeItemData(clientData))

    def Clear(self):
        return self._tree.DeleteAllItems()
        
    def Delete(self, item):
        return self._tree.Delete(item)

    def FindString(self, string):
        item, cookie = self._tree.GetFirstChild(self._tree.GetRootItem())
        while item.IsOk():
            if self._tree.GetItemText(item) == string:
                return item
            else:
                item, cookie = self._tree.GetNextChild(item, cookie)
        return wx.NOT_FOUND

    def GetSelection(self):
        return self.FindString(self.GetValue())

    def GetString(self, item):
        if item.IsOk():
            return self._tree.GetItemText(item)
        else:
            return ''

    def GetStringSelection(self):
        return self.GetValue()

    def Insert(self, itemText, previous=None, parent=None, clientData=None):
        data = wx.TreeItemData(clientData)
        if parent is None:
            parent = self._tree.GetRootItem()
        if previous is None:
            return self._tree.InsertItemBefore(parent, 0, itemText, data=data)
        else:
            return self._tree.InsertItem(parent, previous, itemText, data=data)

    def IsEmpty(self):
        return self.GetCount() == 0

    def GetCount(self):
        # NB: We don't need to substract 1 for the hidden root item, because
        # the TreeCtrl does that for us
        return self._tree.GetCount() 

    def SetSelection(self, item):
        self._text.SetValue(self._tree.GetItemText(item))
        
    Select = SetSelection

    def SetString(self, item, string):
        self._tree.SetItemText(item, string)

    def SetStringSelection(self, string):
        self._text.SetValue(string)

    def GetValue(self):
        if self._text == self:
            return super(_BaseComboTreeBox, self).GetValue()
        else:
            return self._text.GetValue()

    def SetValue(self, value):
        if self._text == self:
            super(_BaseComboTreeBox, self).SetValue(value)
        else:
            self._text.SetValue(value)

    def GetClientData(self, item):
        return self._tree.GetPyData(item)

    def SetClientData(self, item, clientData):
        self._tree.SetPyData(item, clientData)


class _ComboTreeBox(_BaseComboTreeBox, wx.ComboBox):
    ''' The ComboTreeBox widget for wxMSW and wxMAC. '''

    def _createInterior(self):
        self._text = self
        if '__WXMAC__' in wx.PlatformInfo:
            self._button = self.GetChildren()[0] # The choice button
        else:
            self._button = self
        super(_ComboTreeBox, self)._createInterior()

    def _bindEventHandlers(self):
        if self._readOnly:
            self.Bind(wx.EVT_CHAR, self.OnChar)
        super(_ComboTreeBox, self)._bindEventHandlers()

    def _buttonEventTypesToBind(self):
        return (wx.EVT_LEFT_DOWN, wx.EVT_LEFT_DCLICK, 
                wx.EVT_MIDDLE_DOWN, wx.EVT_MIDDLE_DCLICK, 
                wx.EVT_RIGHT_DOWN, wx.EVT_RIGHT_DCLICK)

    def OnChar(self, event):
        # OnChar is only called when in read only mode. We don't call 
        # event.Skip() on purpose, to prevent the characters from being 
        # displayed in the text field.
        pass


class _GTKComboTreeBox(_BaseComboTreeBox, wx.Panel):
    ''' The ComboTreeBox widget for wxGTK. This is actually a work
        around because on wxGTK, there doesn't seem to be a way to intercept 
        mouse events sent to the Combobox. Intercepting those events is 
        necessary to prevent the Combobox from popping up the list and pop up
        the tree instead. So, until wxPython makes intercepting those events
        possible we build a poor man's Combobox ourselves using a TextCtrl and
        a BitmapButton.  '''

    def _createInterior(self):
        if self._readOnly:
            style = wx.TE_READONLY
        else:
            style = 0
        self._text = wx.TextCtrl(self, style=style)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, client=wx.ART_BUTTON)
        self._button = wx.BitmapButton(self, bitmap=bitmap)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(self._text, flag=wx.EXPAND, proportion=1)
        panelSizer.Add(self._button)
        self.SetSizerAndFit(panelSizer)
        super(_GTKComboTreeBox, self)._createInterior()

    def _buttonEventTypesToBind(self):
        return (wx.EVT_BUTTON,)


def ComboTreeBox(*args, **kwargs):
    ''' Factory function to create the right ComboTreeBox depending on
        platform. '''

    if '__WXGTK__' in wx.PlatformInfo:
        return _GTKComboTreeBox(*args, **kwargs)
    else:
        return _ComboTreeBox(*args, **kwargs)


# Demo

class DemoFrame(wx.Frame):
    def __init__(self):
        super(DemoFrame, self).__init__(None, title='ComboTreeBox Demo')
        panel = wx.Panel(self)
        panelSizer = wx.FlexGridSizer(2, 2)
        panelSizer.AddGrowableCol(1)
        for style, labelText in [(0, 'Default style:'), 
                                 (wx.CB_READONLY, 'Read-only style:')]:
            label = wx.StaticText(panel, label=labelText)
            panelSizer.Add(label, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, 
                           border=5)
            comboBox = self._createComboTreeBox(panel, style=style)
            panelSizer.Add(comboBox, flag=wx.EXPAND|wx.ALL, border=5)
        panel.SetSizerAndFit(panelSizer)
        self.Fit()

    def _createComboTreeBox(self, parent, style):
        comboBox = ComboTreeBox(parent, style=style)
        self._bindEventHandlers(comboBox)
        for i in range(20):
            parent = comboBox.Append('Item %d'%i)
            for j in range(20):
                comboBox.Append('Item %d.%d'%(i,j), parent)
        return comboBox
        
    def _bindEventHandlers(self, comboBox):
        for eventType, handler in [(wx.EVT_COMBOBOX, self.onItemSelected), 
                                   (wx.EVT_TEXT, self.onItemEntered)]:
            comboBox.Bind(eventType, handler)

    def onItemSelected(self, event):
        print 'You selected: %s'%event.GetString()

    def onItemEntered(self, event):
        print 'You entered: %s'%event.GetString()


# Unittests

import unittest

class ComboTreeBoxTest(unittest.TestCase):
    def setUp(self):
        self.comboBoxEventReceived = False
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame)
        self.tree = self.comboBox._popupFrame.GetTree()

    def onComboBox(self, event):
        self.comboBoxEventReceived = True

    def firstItem(self):
        return self.tree.GetFirstChild(self.tree.GetRootItem())[0]

    def testComboBoxIsEmptyByDefault(self):
        self.assertEqual(0, self.comboBox.GetCount())

    def testAddingOneItem(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(1, self.comboBox.GetCount())

    def testAddingTwoItems(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Append('Item 2')
        self.assertEqual(2, self.comboBox.GetCount())

    def testAddingTwoParentAndChild(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.Append('Item 2', item1)
        self.assertEqual(2, self.comboBox.GetCount())

    def testSelectingAnItemPutsItInTheComboBox(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Bind(wx.EVT_COMBOBOX, self.onComboBox)
        event = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_ITEM_ACTIVATED,
            self.tree.GetId())
        event.SetItem(self.tree.GetFirstVisibleItem())
        self.tree.GetEventHandler().ProcessEvent(event)
        self.failUnless(self.comboBoxEventReceived)

    def testClear(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Clear()
        self.assertEqual(0, self.comboBox.GetCount())

    def testDelete(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Delete(self.firstItem())
        self.assertEqual(0, self.comboBox.GetCount())

    def testGetSelection_NoSelection(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(wx.NOT_FOUND, self.comboBox.GetSelection())

    def testGetSelection_WithSelection(self):
        self.comboBox.Append('Item 1')
        self.comboBox.SetValue('Item 1')
        self.assertEqual(self.firstItem(), self.comboBox.GetSelection())

    def testFindString_NotPresent(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(wx.NOT_FOUND, self.comboBox.FindString('Item 2'))

    def testFindString_Present(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(self.firstItem(),
                         self.comboBox.FindString('Item 1'))

    def testGetString_NotPresent(self):
        self.assertEqual('', self.comboBox.GetString(self.firstItem()))

    def testGetString_Present(self):
        self.comboBox.Append('Item 1')
        self.assertEqual('Item 1', self.comboBox.GetString(self.firstItem()))

    def testGetStringSelection_NotPresent(self):
        self.assertEqual('', self.comboBox.GetStringSelection())

    def testGetStringSelection_Present(self):
        self.comboBox.SetValue('Item 1')
        self.assertEqual('Item 1', self.comboBox.GetStringSelection())

    def testInsertAsFirstItem(self):
        self.comboBox.Insert('Item 1')
        self.assertEqual('Item 1', self.comboBox.GetString(self.firstItem()))

    def testInsertAsFirstItemBeforeExistingItem(self):
        item1 = self.comboBox.Append('Item 1')
        item2 = self.comboBox.Insert('Item 2')
        self.assertEqual(item2, self.firstItem())

    def testInsertAsFirstChildBeforeExistingChild(self):
        parent = self.comboBox.Append('parent')
        child1 = self.comboBox.Append('child 1', parent)
        child2 = self.comboBox.Insert('child 2', parent=parent)
        self.assertEqual(child2, self.tree.GetFirstChild(parent)[0])

    def testSelect(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.Select(item1)
        self.assertEqual('Item 1', self.comboBox.GetValue())

    def testSetString(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetString(item1, 'Item 2')
        self.assertEqual('Item 2', self.comboBox.GetString(item1))

    def testSetStringSelection(self):
        self.comboBox.SetStringSelection('Hi')
        self.assertEqual('Hi', self.comboBox.GetStringSelection())

    def testAppendWithClientData(self):
        item1 = self.comboBox.Append('Item 1', clientData=[1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item1))

    def testInsertWithClientData(self):
        item1 = self.comboBox.Append('Item 1')
        item2 = self.comboBox.Insert('Item 2', previous=item1, 
                                     clientData=[1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item2))

    def testSetClientData(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetClientData(item1, [1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item1))
        

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in
        ['demo', 'test']):
        print "Usage: %s ['demo' | 'test' ]"%sys.argv[0]
        sys.exit(1)

    app = wx.App(False)
    if sys.argv[1] == 'test':
        # Remove the 'test' command line argument otherwise unittest.main 
        # will try to use it to load tests.
        del sys.argv[1] 
        unittest.main()
    elif sys.argv[1] == 'demo':
        frame = DemoFrame()
        frame.Show()
        app.MainLoop()

