#!/usr/bin/env python

''' ComboTreeBox provides a ComboBox that pops up a tree instead of
    a list. 

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
        if style & wx.CB_SORT:
            style &= ~wx.CB_SORT # We manage sorting ourselves
            self._sort = True
        else:
            self._sort = False
        super(_BaseComboTreeBox, self).__init__(style=style, *args, **kwargs)
        self._createInterior()
        self._bindEventHandlers()

    # Private methods

    def _createInterior(self):
        self._popupFrame = PopupFrame(self)
        self._tree = self._popupFrame.GetTree()

    def _bindEventHandlers(self):
        self._text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self._button.Bind(wx.EVT_BUTTON, self.OnMouseClick)
        for eventType in self._buttonEventTypesToBind():
            self._button.Bind(eventType, self.OnMouseClick)

    # Event handlers

    def OnMouseClick(self, event):
        self.Popup()
        # We don't call event.Skip() to prevent popping up the
        # ComboBox's own box.

    def OnKeyDown(self, event):
        if (event.AltDown() or event.MetaDown()) and \
                event.GetKeyCode() == wx.WXK_DOWN:
            self.Popup()
        else:
            def SelectItemJustTypedInIfPossible():
                item = self.FindString(self.GetValue())
                if item.IsOk():
                    self._tree.SelectItem(item)
            wx.CallAfter(SelectItemJustTypedInIfPossible)
            event.Skip()

    # Misc methods

    def Popup(self):
        ''' 
        Popup(self)

        Pops up the frame with the tree.
        '''
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
        '''
        GetTree(self) -> wx.TreeCtrl

        Returns the tree control that is popped up. 
        '''
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
        ''' 
        Append(self, String itemText, TreeItemId parent=None, PyObject
               clientData=None) -> TreeItemId

        Adds the itemText to the control, associating the given clientData 
        with the item if not None. If parent is None, itemText is added
        as a root item, else itemText is added as a child item of
        parent. The return value is the TreeItemId of the newly added
        item. '''    
        if parent is None:
            parent = self._tree.GetRootItem()
        item = self._tree.AppendItem(parent, itemText, 
                                     data=wx.TreeItemData(clientData))
        if self._sort:
            self._tree.SortChildren(parent)
        return item

    def Clear(self):
        '''
        Clear(self)
        
        Removes all items from the control.
        '''
        return self._tree.DeleteAllItems()
        
    def Delete(self, item):
        '''
        Delete(self, TreeItemId item)

        Deletes the item from the control. 
        '''
        return self._tree.Delete(item)

    def FindString(self, string, parent=None):
        ''' 
        FindString(self, String string, TreeItemId parent=None) -> TreeItemId
        
        Finds the *first* item in the tree with a label equal to the
        given string. If no such item exists, an invalid item is
        returned. 
        '''
        parent = parent or self._tree.GetRootItem()
        child, cookie = self._tree.GetFirstChild(parent)
        while child.IsOk():
            if self._tree.GetItemText(child) == string:
                return child
            else:
                result = self.FindString(string, child)
                if result.IsOk():
                    return result
            child, cookie = self._tree.GetNextChild(parent, cookie)
        return child

    def GetSelection(self):
        '''
        GetSelection(self) -> TreeItemId

        Returns the TreeItemId of the selected item or an invalid item
        if no item is selected.
        '''
        selectedItem = self._tree.GetSelection()
        if selectedItem.IsOk() and selectedItem != self._tree.GetRootItem():
            return selectedItem
        else:
            return self.FindString(self.GetValue())

    def GetString(self, item):
        '''
        GetString(self, TreeItemId item) -> String

        Returns the label of the given item.
        '''
        if item.IsOk():
            return self._tree.GetItemText(item)
        else:
            return ''

    def GetStringSelection(self):
        '''
        GetStringSelection(self) -> String

        Returns the label of the selected item or an empty string if no item 
        is selected.
        '''
        return self.GetValue()

    def Insert(self, itemText, previous=None, parent=None, clientData=None):
        '''
        Insert(self, String itemText, TreeItemId previous=None, TreeItemId
               parent=None, PyObject clientData=None) -> TreeItemId

        Insert an item into the control before the ``previous`` item 
        and/or as child of the ``parent`` item. The itemText is associated 
        with clientData when not None.
        '''
        data = wx.TreeItemData(clientData)
        if parent is None:
            parent = self._tree.GetRootItem()
        if previous is None:
            item = self._tree.InsertItemBefore(parent, 0, itemText, data=data)
        else:
            item = self._tree.InsertItem(parent, previous, itemText, data=data)
        if self._sort:
            self._tree.SortChildren(parent)
        return item

    def IsEmpty(self):
        '''
        IsEmpty(self) -> bool

        Returns True if the control is empty or False if it has some items.
        '''
        return self.GetCount() == 0

    def GetCount(self):
        '''
        GetCount(self) -> int

        Returns the number of items in the control.
        '''
        # Note: We don't need to substract 1 for the hidden root item, 
        # because the TreeCtrl does that for us
        return self._tree.GetCount() 

    def SetSelection(self, item):
        ''' 
        SetSelection(self, TreeItemId item) 

        Sets the provided item to be the selected item.
        '''
        self._tree.SelectItem(item)
        self._text.SetValue(self._tree.GetItemText(item))
        
    Select = SetSelection

    def SetString(self, item, string):
        '''
        SetString(self, TreeItemId item, String string)

        Sets the label for the provided item.
        '''
        self._tree.SetItemText(item, string)
        if self._sort:
            self._tree.SortChildren(self._tree.GetItemParent(item))

    def SetStringSelection(self, string):
        '''
        SetStringSelection(self, String string) -> bool

        Selects the item with the provided string in the control. 
        Returns True if the provided string has been selected, False if
        it wasn't found in the control.
        '''
        item = self.FindString(string)
        if item.IsOk():
            if self._text.GetValue() != string:
                self._text.SetValue(string)
            self._tree.SelectItem(item)
            return True
        else:
            return False

    def GetClientData(self, item):
        '''
        GetClientData(self, TreeItemId item) -> PyObject

        Returns the client data associated with the given item, if any.
        '''
        return self._tree.GetItemPyData(item)

    def SetClientData(self, item, clientData):
        '''
        SetClientData(self, TreeItemId item, PyObject clientData)

        Associate the given client data with the provided item.
        '''
        self._tree.SetItemPyData(item, clientData)

    def GetValue(self):
        '''
        GetValue(self) -> String

        Returns the current value in the combobox text field.
        '''
        if self._text == self:
            return super(_BaseComboTreeBox, self).GetValue()
        else:
            return self._text.GetValue()

    def SetValue(self, value):
        '''
        SetValue(self, String value)

        Sets the text for the combobox text field.

        NB: For a combobox with wxCB_READONLY style the string must be
        in the combobox choices list, otherwise the call to SetValue()
        is ignored.
        '''
        item = self.FindString(value)
        if self._readOnly and not item.IsOk():
            return
        if self._text == self:
            super(_BaseComboTreeBox, self).SetValue(value)
        else:
            self._text.SetValue(value)
        if item.IsOk():
            self._tree.SelectItem(item)


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

class ComboTreeBoxTestCase(unittest.TestCase):
    def firstItem(self):
        return self.tree.GetFirstChild(self.tree.GetRootItem())[0]


class ComboTreeBoxTest(ComboTreeBoxTestCase):
    def setUp(self):
        self.comboBoxEventReceived = False
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame)
        self.tree = self.comboBox._popupFrame.GetTree()

    def onComboBox(self, event):
        self.comboBoxEventReceived = True

    def selectItem(self, item):
        event = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_ITEM_ACTIVATED,
            self.tree.GetId())
        event.SetItem(item)
        self.tree.GetEventHandler().ProcessEvent(event)

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
        self.selectItem(self.tree.GetFirstVisibleItem())
        self.failUnless(self.comboBoxEventReceived)

    def testClear(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Clear()
        self.assertEqual(0, self.comboBox.GetCount())

    def testDelete(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Delete(self.firstItem())
        self.assertEqual(0, self.comboBox.GetCount())

    def testGetSelection_NoItems(self):
        self.failIf(self.comboBox.GetSelection().IsOk())

    def testGetSelection_NoSelection(self):
        self.comboBox.Append('Item 1')
        self.failIf(self.comboBox.GetSelection().IsOk())

    def testGetSelection_WithSelection(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetValue('Item 1')
        self.assertEqual(item1, self.comboBox.GetSelection())

    def testGetSelection_EquallyNamedNodes_SelectedInTree(self):
        item1 = self.comboBox.Append('Item')
        item2 = self.comboBox.Append('Item')
        self.tree.SelectItem(item2)
        self.assertEqual(item2, self.comboBox.GetSelection())

    def testGetSelection_EquallyNamedNodes_TypedInTextBox(self):
        item1 = self.comboBox.Append('Item')
        item2 = self.comboBox.Append('Item')
        self.comboBox.SetValue('Item')
        self.assertEqual(item1, self.comboBox.GetSelection())

    def testFindString_NotPresent(self):
        self.comboBox.Append('Item 1')
        self.failIf(self.comboBox.FindString('Item 2').IsOk())

    def testFindString_Present(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(self.firstItem(),
                         self.comboBox.FindString('Item 1'))

    def testFindString_Child(self):
        parent = self.comboBox.Append('Parent')
        child = self.comboBox.Append('Child', parent=parent)
        self.assertEqual(child, self.comboBox.FindString('Child'))

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

    def testSetStringSelection_ExistingString(self):
        self.comboBox.Append('Hi')
        self.comboBox.SetStringSelection('Hi')
        self.assertEqual('Hi', self.comboBox.GetStringSelection())

    def testSetStringSelection_NonExistingString(self):
        self.comboBox.SetStringSelection('Hi')
        self.assertEqual('', self.comboBox.GetStringSelection())

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


class SortedComboTreeBoxTest(ComboTreeBoxTestCase):
    def setUp(self):
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame, style=wx.CB_SORT)
        self.tree = self.comboBox._popupFrame.GetTree()

    def testAppend(self):
        itemB = self.comboBox.Append('B')
        itemA = self.comboBox.Append('A')
        self.assertEqual(itemA, self.firstItem())

    def testInsert(self):
        itemA = self.comboBox.Append('A')
        itemB = self.comboBox.Insert('B')
        self.assertEqual(itemA, self.firstItem())

    def testAppend_Child(self):
        itemA = self.comboBox.Append('A')
        itemA2 = self.comboBox.Append('2', parent=itemA)
        itemA1 = self.comboBox.Append('1', parent=itemA)
        self.assertEqual(itemA1, self.tree.GetFirstChild(itemA)[0])

    def testInsert_Child(self):
        itemA = self.comboBox.Append('A')
        itemA1 = self.comboBox.Append('1', parent=itemA)
        itemA2 = self.comboBox.Insert('2', parent=itemA)
        self.assertEqual(itemA1, self.tree.GetFirstChild(itemA)[0])
        
    def testSetString(self):
        itemB = self.comboBox.Append('B')
        itemC = self.comboBox.Append('C')
        self.comboBox.SetString(itemC, 'A')
        self.assertEqual(itemC, self.firstItem())


class ReadOnlyComboTreeBoxTesT(ComboTreeBoxTestCase):
    def setUp(self):
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame, style=wx.CB_READONLY)
        self.tree = self.comboBox._popupFrame.GetTree()

    def testSetValue_ToNonExistingValue(self):
        self.comboBox.SetValue('Ignored value')
        self.assertEqual('', self.comboBox.GetValue())

    def testSetValue_ToExistingValue(self):
        self.comboBox.Append('This works')
        self.comboBox.SetValue('This works')
        self.assertEqual('This works', self.comboBox.GetValue())


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

